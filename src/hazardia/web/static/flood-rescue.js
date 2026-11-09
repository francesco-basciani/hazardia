import {getLanguage, locale} from '/i18n.js';
import {scheduledTiles} from '/scheduled-tiles.js';

const tr = (it, en) => getLanguage() === 'en' ? en : it;
const labels = {
  none: () => tr('Senza soccorso', 'No rescue'),
  fifo: () => tr('Ordine di chiamata', 'Call order'),
  optimized: () => tr('Piano ottimizzato', 'Optimised plan')
};
const point = ([x, y]) => [y, x];
const clock = minute => '+' + String(Math.floor(minute / 60)).padStart(2, '0') + ':' + String(minute % 60).padStart(2, '0');
const meters = value => value.toLocaleString(locale(), {maximumFractionDigits: 3}) + ' m';
function element(tag, text = '') {
  const node = document.createElement(tag);
  node.textContent = text;
  return node;
}

export function drawRescueRoutes(routes, data, frame, plan) {
  routes.clearLayers();
  const condition = data.roads[frame.index].calls;
  const critical = data.problem.calls.find(call => call.priority === 'critical');
  const prior = data.plans.find(item => item.id === 'optimized').missions.find(item => item.call === critical.id);
  if (!condition[critical.id].round_trip && prior) {
    for (const line of [prior.outbound_line, prior.return_line]) {
      L.polyline(line.map(point), {color: '#f3ddab', weight: 4, dashArray: '4 6'}).addTo(routes);
    }
    for (const edge of condition[critical.id].blocker_geometry) {
      L.polyline([point(edge.a), point(edge.b)], {color: edge.state === 'closed' ? '#ff4e59' : '#ffe172',
        weight: 7}).addTo(routes).bindPopup(element('span',
        (edge.name || edge.id) + ' · ' + (edge.max_depth_m === null ? '—' : meters(edge.max_depth_m))));
    }
  }
  for (const mission of plan.missions.filter(item => item.hour === frame.index)) {
    L.polyline(mission.outbound_line.map(point), {color: '#70ffcd', weight: 6}).addTo(routes);
    L.polyline(mission.return_line.map(point), {color: '#e4fff4', weight: 2, dashArray: '5 5'}).addTo(routes);
  }
  L.circleMarker(point(data.problem.base), {radius: 9, color: '#fff', fillColor: '#1a577a', fillOpacity: 1})
    .addTo(routes).bindTooltip(tr('Base e consegna simulate', 'Simulated base and handoff'), {permanent: true});
  for (const call of data.problem.calls) {
    const criticalCall = call.priority === 'critical';
    L.circleMarker(point(call.point), {radius: 8, color: '#fff',
      fillColor: criticalCall ? '#d63861' : '#a76517', fillOpacity: 1})
      .addTo(routes).bindTooltip(call.id + (criticalCall ? tr(' · Via Mariana', ' · Via Mariana') : ''),
        {permanent: true}).bindPopup(element('span', call.id + ' · ' + call.people +
        tr(' persone simulate · profondità al punto ', ' simulated people · point depth ') +
        (condition[call.id].depth.depth_m === null ? '—' : meters(condition[call.id].depth.depth_m))));
  }
}

export function floodRescue() {
  const panel = element('details');
  panel.className = 'flood-rescue';
  panel.id = 'flood-rescue';
  panel.hidden = true;
  panel.dataset.i18nSkip = '';
  const heading = element('summary');
  const info = element('p');
  const body = element('section');
  const mapNode = element('div');
  mapNode.className = 'flood-rescue-map';
  const readout = element('div');
  readout.className = 'flood-rescue-readout';
  body.append(readout, mapNode);
  panel.append(heading, info, body);
  document.getElementById('flood-access').parentElement.before(panel);
  const css = element('link');
  css.rel = 'stylesheet';
  css.href = '/flood-rescue.css';
  document.head.append(css);
  let scenario = null, data = null, controller = null, map = null, water = null, routes = null;
  let index = -1, drawnPlan = null, minute = 0, planId = 'optimized', timer = null, controls = null;

  function stop() {
    if (timer !== null) clearInterval(timer);
    timer = null;
    if (controls) controls.play.textContent = tr('Riproduci', 'Play');
  }

  function resetMap() {
    if (map) map.remove();
    map = null;
    water = null;
    routes = null;
    index = -1;
    drawnPlan = null;
    controls = null;
    readout.replaceChildren();
  }

  function initializeMap() {
    mapNode.setAttribute('role', 'region');
    mapNode.setAttribute('aria-label', tr('Mappa della piena e del soccorso', 'Flood and rescue map'));
    map = L.map(mapNode, {preferCanvas: true, scrollWheelZoom: false, maxZoom: 19});
    L.imageOverlay('/assets/satellite.png', [[42.30, 13.32], [42.40, 13.44]], {pane: 'tilePane'}).addTo(map);
    scheduledTiles('/api/maps/ortho/{z}/{x}/{y}', {minZoom: 8, maxZoom: 19,
      keepBuffer: 1, updateWhenIdle: true, attribution: 'Ortofoto 2018–2019 © Regione Abruzzo'}).addTo(map);
    map.attributionControl.addAttribution('© OpenStreetMap contributors · ODbL');
    L.control.scale({imperial: false}).addTo(map);
    const places = [data.problem.base, ...data.problem.calls.map(item => item.point)].map(point);
    map.fitBounds(places, {padding: [35, 48], maxZoom: 16, animate: false});
    water = L.layerGroup().addTo(map);
    routes = L.layerGroup().addTo(map);
  }

  function drawMap(frame, plan) {
    water.clearLayers();
    L.imageOverlay(asset(frame.png), frame.bounds, {opacity: .8}).addTo(water);
    drawRescueRoutes(routes, data, frame, plan);
  }

  function asset(file) {
    return '/assets/flood-rescue/' + scenario.id + '/' + file;
  }

  function update() {
    const frame = data.frames[Math.floor(minute / 60)];
    const plan = data.plans.find(item => item.id === planId);
    if (frame.index !== index || planId !== drawnPlan) {
      drawMap(frame, plan);
      index = frame.index;
      drawnPlan = planId;
    }
    controls.time.value = minute;
    controls.now.textContent = clock(minute) + ' · ' + frame.at.slice(11, 16) + ' UTC ' +
      tr('del campione HMC', 'HMC sample');
    const closed = data.roads[frame.index].counts.closed || 0;
    controls.hazard.textContent = tr('Mappa oraria · profondità massima ', 'Hourly map · maximum depth ') +
      meters(frame.max_depth_m) + ' · ' + closed + tr(' archi interrotti a 10 cm', ' arcs closed at 10 cm');
    const demand = data.problem.calls.reduce((sum, call) => sum + call.people, 0);
    for (const item of data.plans) {
      const served = item.missions.filter(mission => mission.delivery <= minute);
      const total = served.reduce((sum, mission) =>
        sum + data.problem.calls.find(call => call.id === mission.call).people, 0);
      controls.cards[item.id].textContent = labels[item.id]() + ' · ' + total + '/' + demand + ' ' +
        tr('consegnati', 'delivered') + ' · ' + tr('a fine piano ', 'at end ') + item.objective[1] + '/' + demand;
    }
    controls.missions.replaceChildren();
    for (const call of data.problem.calls) {
      const mission = plan.missions.find(item => item.call === call.id);
      const state = mission ? (minute >= mission.delivery ? tr('Consegnati', 'Delivered') :
        minute >= mission.departure ? tr('In missione', 'In transit') : tr('Pianificato', 'Scheduled')) :
        minute < call.release ? tr('Non ancora richiesta', 'Not yet requested') : tr('Senza missione', 'Unassigned');
      const label = call.id + (call.priority === 'critical' ? tr(' · prioritaria', ' · priority') : '') +
        ' · ' + state + (mission ? ' · ' + mission.vehicle + ' · ' + clock(mission.departure) + ' → ' + clock(mission.delivery) : '');
      controls.missions.append(element('li', label));
    }
    const r2 = data.roads[frame.index].calls.R2;
    const localDepth = r2.depth.depth_m === null ? tr('non valutabile', 'not assessable') : meters(r2.depth.depth_m);
    controls.reason.textContent = r2.round_trip
      ? tr('R2 · andata e ritorno disponibili nel grafo orario.', 'R2 · round trip available in the hourly graph.')
      : 'R2 · ' + tr('profondità al punto ', 'pickup depth ') + localDepth + tr(
          ' · andata e ritorno indisponibili. In rosso i tratti sopra soglia.',
          ' · no round trip. Red marks segments at or above threshold.');
  }

  function show() {
    heading.textContent = tr('Evoluzione alluvione e piani di soccorso', 'Flood evolution and rescue plans');
    if (!panel.open || !data) return;
    if (!map) initializeMap();
    const select = element('select');
    select.setAttribute('aria-label', tr('Piano di soccorso', 'Rescue plan'));
    for (const item of data.plans) select.add(new Option(labels[item.id](), item.id));
    select.value = planId;
    select.onchange = () => {planId = select.value; update();};
    const play = element('button', timer === null ? tr('Riproduci', 'Play') : tr('Pausa', 'Pause'));
    play.type = 'button';
    play.onclick = () => {
      if (timer !== null) return stop();
      if (minute >= Number(time.max)) minute = 0;
      update();
      play.textContent = tr('Pausa', 'Pause');
      timer = setInterval(() => {
        minute = Math.min(Number(time.max), minute + 5);
        update();
        if (minute >= Number(time.max)) stop();
      }, 350);
    };
    const time = element('input');
    time.type = 'range';
    time.min = 0;
    time.max = data.frames.length * 60 - 1;
    time.setAttribute('aria-label', tr('Tempo simulato', 'Simulated time'));
    time.oninput = () => {stop(); minute = Number(time.value); update();};
    const now = element('strong');
    const hazard = element('p');
    const reason = element('p');
    reason.className = 'flood-rescue-reason';
    const bar = element('div');
    bar.className = 'flood-rescue-time';
    bar.append(select, play, time, now);
    const comparison = element('div');
    comparison.className = 'flood-rescue-plans';
    const cards = {};
    for (const item of data.plans) {
      cards[item.id] = element('strong');
      comparison.append(cards[item.id]);
    }
    const missions = element('ul');
    missions.className = 'flood-rescue-missions';
    const provenance = element('details');
    provenance.append(element('summary', tr('Regole, mezzi e dati', 'Rules, fleet and data')));
    provenance.append(element('p', tr(
      'HMC fornisce portate orarie. Ogni mappa REFlEx è calcolata separatamente per la portata del campione. ' +
      'Nel soccorso si assume che la mappa valga per la sua ora. Tempi di arrivo dell’acqua e riapertura effettiva delle strade richiedono un modello dinamico.',
      'HMC supplies hourly discharges. Each REFlEx map is calculated independently for the sample discharge. ' +
      'The rescue exercise holds each map for its hour. Water arrival and actual road reopening require a dynamic model.')));
    provenance.append(element('p', tr(
      'Richieste e mezzi ipotetici. V1: 2 posti, disponibile da +01:00. V2: 4 posti, da +02:00. ' +
      'Andata, carico e ritorno entro la stessa ora, su archi valutati sotto 10 cm. ' +
      'HiGHS massimizza prima le consegne prioritarie, poi le consegne totali e infine minimizza il tempo di viaggio.',
      'Synthetic calls and fleet. V1: 2 seats, ready at +01:00. V2: 4 seats, ready at +02:00. ' +
      'Outbound trip, pickup and return within one hour on assessed roads below 10 cm. ' +
      'HiGHS maximises priority deliveries, then total deliveries, then minimises travel time.')));
    for (const file of ['frames.json', 'rescue-problem.json', 'plans.json', 'audit.json']) {
      const link = element('a', file);
      link.href = asset(file);
      link.download = file;
      provenance.append(link, document.createTextNode(' '));
    }
    readout.replaceChildren(bar, hazard, comparison, reason, missions, provenance);
    controls = {play, time, now, hazard, reason, cards, missions};
    update();
    requestAnimationFrame(() => map?.invalidateSize({pan: false}));
  }

  async function load() {
    controller?.abort();
    if (!panel.open || !scenario) return;
    if (data) return show();
    const request = new AbortController();
    controller = request;
    const id = scenario.id;
    info.textContent = tr('Caricamento replay…', 'Loading replay…');
    try {
      const response = await fetch(asset('view.json'), {signal: request.signal});
      if (!response.ok) throw new Error('missing');
      const raw = await response.text();
      if (raw.length > 2 * 1024 * 1024) throw new Error('invalid');
      const value = JSON.parse(raw);
      if (value.schema !== 'hazardia.flood-rescue-view/1' || value.job_id !== id ||
          value.qualification !== 'RESEARCH_HOURLY_QUASI_STATIC' || value.frames.length !== 6) throw new Error('invalid');
      if (request.signal.aborted) return;
      data = value;
      info.textContent = tr('Esercitazione · mappe orarie da HMC–REFlEx · pioggia, richieste e mezzi ipotetici.',
                           'Exercise · hourly HMC–REFlEx maps · synthetic rain, calls and vehicles.');
      show();
    } catch {
      if (request.signal.aborted) return;
      data = null;
      resetMap();
      info.textContent = tr('Replay temporale non disponibile per questo risultato.', 'No temporal replay for this result.');
    }
  }

  panel.ontoggle = () => {
    if (panel.open) void load();
    else {
      controller?.abort();
      stop();
    }
  };
  document.addEventListener('hazardia-language', () => show());
  show();
  return {
    setScenario(next) {
      if (next?.id === scenario?.id) return;
      controller?.abort();
      stop();
      resetMap();
      scenario = next && /^job-[a-f0-9]{32}$/.test(next.id) ? next : null;
      data = null;
      minute = 0;
      info.textContent = '';
      panel.hidden = !scenario;
      if (scenario && new URLSearchParams(location.search).get('flood-rescue') === '1') panel.open = true;
      void load();
    }
  };
}
