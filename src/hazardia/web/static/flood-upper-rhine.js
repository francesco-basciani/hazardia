import {getLanguage, locale} from '/i18n.js';
import {mountRhineDemo} from '/flood-upper-rhine-demo.js?v=3';
import {scheduledTiles} from '/scheduled-tiles.js';

const $ = id => document.getElementById(id);
const tr = (it, en) => getLanguage() === 'en' ? en : it;
const el = (tag, text = '', className = '') => {
  const element = document.createElement(tag);
  element.textContent = text;
  element.className = className;
  return element;
};
const svg = (tag, attributes = {}) => {
  const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, value);
  return element;
};
const number = (value, precision = 0) => new Intl.NumberFormat(locale(), {maximumFractionDigits: precision}).format(value);
const flow = value => number(value) + ' m³/s';
const signed = (value, precision = 0) => new Intl.NumberFormat(locale(), {
  maximumFractionDigits: precision, signDisplay: 'exceptZero'
}).format(value);
const relative = hour => '+' + hour + ' h';
const siteName = site => site.id === 'altenheim' ? tr('Altenheim I e II', 'Altenheim I and II') : site.name;
const basePath = '/assets/flood-upper-rhine/2013-v1/';
const maxauSource = 'https://pegelonline.wsv.de/gast/stammdaten?pegelnr=23700200';
const spatialComparison = '/?view=results&lab=flood&flood-hour=25';
const charts = ['#ffb45c', '#7ac5ff', '#81e4bb', '#c4a8ff'];
const range = $('flood-time');
const status = $('status');
const interventionJump = $('flood-jump-difference');
const compareOnMap = el('button', '', 'rhine-demo-open');
compareOnMap.type = 'button';
compareOnMap.disabled = true;
$('flood-example').after(compareOnMap);
let event, selection, plans, atlas, manualBenchmark, pairDemo, hour = 0, timer, activeDrawer, request = 0;
let maps = [], syncing = false;
let atlasVisible = true, atlasFailed = false;
let interventionHour = null;

const works = () => atlas?.works.features ?? [];
const locationOf = site => works().find(feature => feature.properties.id === site.id)?.properties.anchor ?? site.point;
const isFlowing = rate => rate > .01;
const currentBenchmark = () => selection?.pair ? pairDemo.manual : manualBenchmark?.[selection?.mask];

function mostConcurrentIntake(manual, optimised) {
  let bestHour = null, bestShared = -1, bestTotal = 0;
  for (let t = 0; t < event.reference.length; t++) {
    const first = manual.sites.filter(site => isFlowing(site.intake[t])).length;
    const second = optimised.sites.filter(site => isFlowing(site.intake[t])).length;
    const shared = Math.min(first, second);
    const total = first + second;
    if (total && (shared > bestShared || (shared === bestShared && total > bestTotal))) {
      bestHour = t;
      bestShared = shared;
      bestTotal = total;
    }
  }
  return bestHour;
}

function caption(t) {
  const date = new Date(Date.UTC(2013, 4, 31, t));
  return new Intl.DateTimeFormat(locale(), {
    timeZone: 'UTC', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', hourCycle: 'h23'
  }).format(date);
}

async function load(name) {
  const response = await fetch(basePath + name + '.json');
  if (!response.ok) throw new Error('Replay data unavailable');
  return response.json();
}

async function bestPairComparison() {
  const pairs = [];
  for (let i = 0; i < event.sites.length; i++) {
    for (let j = i + 1; j < event.sites.length; j++) pairs.push((1 << i) | (1 << j));
  }
  const manuals = pairs.map(mask => manualBenchmark?.[mask]).filter(plan => plan?.options.filter(Boolean).length === 2);
  if (manuals.length !== pairs.length || !pairs.length) return null;
  const optimised = await Promise.all(pairs.map(async mask => ({mask, plan:await load('optimal-' + mask)})));
  const best = optimised.filter(({plan}) => plan.sites.filter(site => site.intake.some(isFlowing)).length === 2)
    .sort((a, b) => a.plan.peak - b.plan.peak)[0];
  return best ? {manual:manuals.sort((a, b) => a.peak - b.peak)[0], optimised:best,
    candidates:pairs.length * event.manual_windows.length ** 2} : null;
}

function fit(site) {
  if (!maps.length) return;
  syncing = true;
  try {
    const features = site ? works().filter(item => item.properties.id === site.id) : works();
    const area = L.latLngBounds(site ? [locationOf(site)] : [...event.sites.map(locationOf), event.maxau]);
    for (const feature of features) area.extend(L.geoJSON(feature).getBounds());
    for (const {map} of maps) {
      map.invalidateSize({pan:false});
      map.fitBounds(area, {padding: [32, 34], animate: false, maxZoom: site ? 13 : 10});
    }
  } finally { syncing = false; }
}

function showDrawer(kind, focusIndex) {
  activeDrawer = kind;
  $('flood-right').hidden = !kind;
  const body = $('flood-right-content');
  body.replaceChildren();
  if (!kind) return;
  const heading = $('flood-right-title');
  if (kind === 'examples') {
    heading.textContent = tr('Esempi', 'Examples');
    const upper = el('button', tr('Alto Reno · 2013', 'Upper Rhine · 2013'));
    upper.onclick = () => showDrawer(null);
    const teramo = el('button', tr('Teramo · confronto delle aree allagate', 'Teramo · flood extent comparison'));
    teramo.onclick = () => parent.location.assign(spatialComparison);
    body.append(upper, teramo);
  } else if (kind === 'manual' && event) {
    heading.textContent = tr('Scegli le casse e le finestre', 'Choose polders and windows');
    body.append(el('p', selection.pair ? tr(
      'Nel confronto a due casse puoi cambiare le finestre del piano manuale. Per ricalcolare l’ottimizzato sul tuo insieme di casse, cambia la disponibilità.',
      'In the two-polder comparison you can change the manual plan’s windows. Change availability to use the optimised plan for your set of polders.') :
      tr('La disponibilità vale per entrambi i piani. L’ottimizzato modula i prelievi tra +36 h e +72 h.',
        'Availability applies to both plans. The optimised plan varies intake from +36 h to +72 h.')));
    event.sites.forEach((site, index) => {
      const group = el('fieldset', '', 'rhine-site-control');
      group.append(el('legend', siteName(site)));
      const toggle = el('input');
      toggle.type = 'checkbox';
      toggle.checked = Boolean(selection.mask & (1 << index));
      const availability = el('label', tr(' Disponibile', ' Available'));
      availability.prepend(toggle);
      const windowLabel = el('label', tr('Finestra manuale', 'Manual window'));
      const select = el('select');
      select.add(new Option(tr('Nessun prelievo', 'No intake'), 0));
      event.manual_windows.forEach(([start, end], i) => select.add(new Option(relative(start) + ' → ' + relative(end), i+1)));
      select.value = selection.manual[index];
      select.disabled = !toggle.checked;
      windowLabel.append(select);
      toggle.onchange = () => {
        selection.mask ^= 1 << index;
        if (!toggle.checked) selection.manual[index] = 0;
        selection.pair = false;
        showDrawer('manual', index);
        refresh();
      };
      select.onchange = () => {
        selection.manual[index] = Number(select.value);
        refresh();
      };
      const locate = el('button', tr('Inquadra la cassa', 'Zoom to polder'));
      locate.type = 'button';
      locate.onclick = () => { showDrawer(null); fit(site); };
      group.append(availability, windowLabel, locate);
      body.append(group);
      if (index === focusIndex) toggle.focus();
    });
  } else {
    heading.textContent = tr('Dati e ipotesi', 'Data and assumptions');
    body.append(el('p', tr(
      'Il replay calcola portate a Maxau. Lo strato blu mostra profondità di una piena frequente dell’Atlante del Reno ed è comune ai tre scenari. I contorni evidenziano le casse usate nel piano.',
      'The replay calculates discharge at Maxau. The blue layer shows frequent-flood depths from the Rhine Atlas and is shared by all three scenarios. Outlines show the polders used in each plan.')));
    body.append(el('p', tr(
      'Verde indica prelievo o accumulo, viola indica rilascio e grigio indica una cassa inattiva. La tinta dell’opera mostra lo stato della cassa.',
      'Green shows intake or storage, purple shows release and grey shows an idle polder. The fill colour indicates the polder state.')));
    body.append(el('p', tr(
      'La curva di riferimento è la stima pubblicata senza misure di ritenzione. La curva osservata comprende le manovre storiche. Entrambe sono digitalizzate dalla figura 26.',
      'The reference curve is the published estimate without retention measures. The observed curve includes historical operations. Both were digitised from figure 26.')));
    body.append(el('p', tr(
      'Ritardi fissi, portate di rilascio e finestre sono ipotesi dell’esercizio. L’ottimizzazione non riproduce le regole ufficiali delle paratoie.',
      'Fixed delays, release rates and windows are exercise assumptions. The optimisation does not reproduce the official gate rules.')));
    if (event) {
      for (const [label, url] of [[tr('Rapporto della piena 2013 · figura 26', '2013 flood report · figure 26'), event.source],
        ['PEGELONLINE · Maxau', maxauSource], [tr('Regole di manovra · riferimento 2020', 'Operating rules · 2020 reference'), event.rules_source],
        ...(atlas ? [[tr('Atlante del Reno · profondità e perimetri', 'Rhine Atlas · depths and outlines'), atlas.source]] : []),
        ...event.sites.map(site => [siteName(site), site.source])]) {
        const link = el('a', label);
        link.href = url;
        link.target = '_blank';
        link.rel = 'noopener';
        body.append(link, el('br'));
      }
      const link = el('a', tr('Scarica dati e parametri del replay', 'Download replay data and parameters'));
      link.href = basePath + 'event.json';
      link.download = 'upper-rhine-2013.json';
      body.append(el('br'), link);
    }
  }
}

function mapViews() {
  maps = Array.from({length: 3}, (_, index) => {
    const section = el('section', '', 'scenario-map-card');
    const heading = el('div', '', 'scenario-map-heading');
    const title = el('strong'), peak = el('output', '', 'scenario-area-badge');
    const operations = el('span', '', 'rhine-operations');
    const noPolders = el('span');
    operations.append(noPolders);
    heading.append(title, peak, operations);
    const comparison = el('p', '', 'rhine-comparison');
    heading.append(comparison);
    const stage = el('div', '', 'map-stage'), mapDiv = el('div', '', 'map');
    stage.append(mapDiv);
    section.append(heading, stage);
    $('scenario-maps').append(section);
    const map = L.map(mapDiv, {zoomControl: false, scrollWheelZoom: false, minZoom: 6, maxZoom: 16});
    L.control.zoom({position:'topright'}).addTo(map);
    map.attributionControl.setPrefix(false);
    scheduledTiles('/api/maps/osm/{z}/{x}/{y}', {
      attribution:'© OpenStreetMap contributors · ODbL', keepBuffer:0, updateWhenIdle:true
    }).addTo(map);
    const inundation = atlas && L.imageOverlay(basePath + 'atlas-frequent.png', atlas.bounds, {
      attribution:'Atlante del Reno / Rhine Atlas · IKSR, BfG', className:'rhine-inundation'
    }).on('error', () => { atlasFailed = true; updateMapLegend(); }).addTo(map);
    const gaugeLabel = el('div', '', 'rhine-gauge');
    gaugeLabel.style.setProperty('--scenario-colour', charts[index]);
    const gaugeValue = el('strong'), gaugeDelta = el('small');
    gaugeLabel.append(el('span', 'Maxau'), gaugeValue, gaugeDelta);
    const gauge = L.circleMarker(event.maxau, {
      radius:6, color:'#122332', fillColor:charts[index], fillOpacity:1, interactive:false
    }).addTo(map);
    gauge.bindTooltip(gaugeLabel, {permanent:true, direction:'left', offset:[-8, 0], className:'rhine-gauge-tooltip'});
    const markers = event.sites.map((site, siteIndex) => {
      const label = el('strong'), volume = el('small');
      const symbol = el('div', '', 'rhine-marker-label');
      const pin = el('b', String(siteIndex + 1), 'rhine-marker-number');
      pin.setAttribute('aria-hidden', 'true');
      symbol.append(label, volume);
      const iconBody = el('div');
      iconBody.append(pin, symbol);
      const marker = L.marker(locationOf(site), {
        icon:L.divIcon({html:iconBody, className:'rhine-marker' + (siteIndex === 0 ? ' is-west' : ''),
          iconSize:[26,26], iconAnchor:[13,13]})
      });
      const focusSite = () => { showDrawer(null); fit(site); };
      marker.on('click', focusSite);
      const feature = works().find(item => item.properties.id === site.id);
      const outline = feature && L.geoJSON(feature, {style: {color:'#d2deeb', weight:2, fillOpacity:.1}})
        .on('click', focusSite);
      const siteLink = el('button', '', 'rhine-site-link');
      siteLink.type = 'button';
      siteLink.onclick = focusSite;
      operations.append(siteLink);
      return {label, volume, marker, outline, siteLink};
    });
    map.on('moveend', () => {
      if (syncing || !maps.every(item => item.map._loaded)) return;
      syncing = true;
      try {
        for (const other of maps) if (other.map !== map) other.map.setView(map.getCenter(), map.getZoom(), {animate:false});
      } finally { syncing = false; }
    });
    return {map, title, peak, gauge, gaugeValue, gaugeDelta, noPolders, comparison, markers, inundation};
  });
  fit();
  new ResizeObserver(() => maps.forEach(({map}) => map.invalidateSize({pan:false}))).observe($('scenario-maps'));
}

const graph = el('section', '', 'rhine-graph');
const mapLegend = el('div', '', 'rhine-map-legend');
mapLegend.setAttribute('role', 'status');
const graphLegend = el('div', '', 'rhine-graph-key');
const curveLabels = el('div', '', 'rhine-curve-labels');
const manualPeakJump = el('button');
const loadBestManual = el('button');
manualPeakJump.type = loadBestManual.type = 'button';
manualPeakJump.disabled = true;
loadBestManual.hidden = true;
graphLegend.append(curveLabels, manualPeakJump, loadBestManual);
const graphScale = el('div', '', 'rhine-graph-scale');
graphScale.setAttribute('aria-hidden', 'true');
for (const value of [4500, 3500, 2500]) {
  const tick = el('span', String(value));
  tick.style.top = (74 - (value - 1800)*.024) + 'px';
  graphScale.append(tick);
}
const graphPlot = el('div', '', 'rhine-graph-plot');
const graphic = svg('svg', {viewBox:'0 0 1000 76', preserveAspectRatio:'none', 'aria-hidden':'true'});
graphPlot.append(graphScale, graphic);
graph.append(mapLegend, graphLegend, graphPlot);
$('scenario-maps').after(graph);
let cursor;
const plotX = t => 4 + 992*t / Number(range.max);

function updateMapLegend() {
  const available = Boolean(atlas) && !atlasFailed;
  const toggle = $('flood-differences');
  toggle.hidden = false;
  toggle.disabled = !available;
  toggle.setAttribute('aria-pressed', String(available && atlasVisible));
  toggle.textContent = tr('Piena statica · Atlante', 'Static flood · Atlas');
  const label = available ? (atlasVisible
    ? tr('Blu · piena frequente statica dell’Atlante', 'Blue · static frequent flood from the Atlas')
    : tr('Mappa di riferimento nascosta', 'Reference map hidden'))
    : tr('Mappa di riferimento non disponibile', 'Reference map unavailable');
  mapLegend.replaceChildren(el('strong', label));
  if (available && atlasVisible) {
    for (const [depth, colour] of atlas.depths) {
      const value = el('span', tr(depth.replaceAll('.', ','), depth), 'rhine-map-swatch');
      value.style.setProperty('--depth-colour', colour);
      mapLegend.append(value);
    }
  }
  const compare = el('a', tr('Vedi le aree allagate simulate a Teramo', 'See simulated flood extents in Teramo'));
  compare.href = spatialComparison;
  compare.target = '_top';
  mapLegend.append(el('span', tr('Esito degli scenari · portata a Maxau', 'Scenario result · discharge at Maxau')), compare);
}

function drawGraph() {
  if (!plans) return;
  const series = [event.reference, plans.manual.q, plans.optimised.q, event.observed];
  graphic.replaceChildren();
  for (const value of [4500, 3500, 2500]) {
    const y = 74 - (value - 1800)*.024;
    graphic.append(svg('line', {x1:0, x2:1000, y1:y, y2:y, stroke:'#36515f', 'vector-effect':'non-scaling-stroke'}));
  }
  series.forEach((curve, index) => {
    const path = curve.map((q, t) => (t ? 'L' : 'M') + plotX(t).toFixed(2) + ' ' + (74 - (q-1800)*.024).toFixed(2));
    graphic.append(svg('path', {d:path.join(' '), stroke:charts[index], fill:'none', 'stroke-width':2,
      'vector-effect':'non-scaling-stroke', ...(index === 3 ? {'stroke-dasharray':'4 3'} : {})}));
  });
  cursor = svg('line', {y1:0, y2:76, stroke:'#fff', 'vector-effect':'non-scaling-stroke'});
  graphic.append(cursor);
}

function draw() {
  range.value = hour;
  $('flood-now').textContent = caption(hour) + ' · ' + relative(hour);
  $('flood-prev').disabled = hour === 0;
  $('flood-next').disabled = hour === Number(range.max);
  $('play').textContent = timer ? tr('Pausa', 'Pause') : tr('▶ Riproduci', '▶ Play');
  if (!plans) return;
  const names = [tr('Senza ritenzione', 'No retention'), tr('Piano manuale', 'Manual plan'),
    tr('Piano ottimizzato', 'Optimised plan'), tr('Osservata · 2013', 'Observed · 2013')];
  const results = [plans.reference, plans.manual, plans.optimised];
  curveLabels.replaceChildren(el('strong', 'Maxau · m³/s'), ...names.map((name, index) => {
    const label = el('span', name);
    label.style.borderColor = charts[index];
    return label;
  }));
  cursor.setAttribute('x1', plotX(hour));
  cursor.setAttribute('x2', plotX(hour));
  maps.forEach(({title, peak, gauge, gaugeValue, gaugeDelta, noPolders, comparison, markers}, index) => {
    const result = results[index];
    title.textContent = (index + 1) + ' · ' + [
      tr('Senza casse', 'No polders'), tr('Manuale', 'Manual'), tr('Ottimizzato', 'Optimised')
    ][index];
    peak.textContent = tr('Picco ', 'Peak ') + number(result.peak, 1) + ' m³/s';
    gaugeValue.textContent = number(result.q[hour], 1) + ' m³/s';
    const hourlyDelta = index === 2 ? result.q[hour] - plans.manual.q[hour] :
      result.q[hour] - plans.reference.q[hour];
    gaugeDelta.textContent = index
      ? signed(hourlyDelta, 1) + ' m³/s ' + (index === 2 ? tr('sul manuale', 'vs manual') : tr('sul riferimento', 'vs baseline'))
      : tr('Portata di riferimento', 'Baseline discharge');
    gauge.getTooltip().update();
    const participants = result.participants ?? [];
    noPolders.hidden = participants.some(Boolean);
    noPolders.textContent = tr('Nessuna cassa', 'No polders');
    if (index === 2) {
      const deltaPeak = result.peak - plans.manual.peak;
      comparison.textContent = tr('Picco sul manuale ', 'Peak vs manual ') + signed(deltaPeak, 1) + ' m³/s (' +
        signed(100 * deltaPeak / plans.manual.peak, 1) + '%)';
    } else {
      comparison.textContent = tr('Ora del picco ', 'Peak hour ') + relative(result.q.indexOf(result.peak));
    }
    markers.forEach(({label, volume, marker, outline, siteLink}, siteIndex) => {
      siteLink.hidden = !participants[siteIndex];
      if (!participants[siteIndex]) {
        marker.remove();
        outline?.remove();
        return;
      }
      if (!maps[index].map.hasLayer(marker)) {
        marker.addTo(maps[index].map);
        outline?.addTo(maps[index].map);
      }
      const site = event.sites[siteIndex];
      siteLink.textContent = (siteIndex + 1) + ' ' + siteName(site);
      siteLink.title = tr('Inquadra la cassa ', 'Zoom to polder ') + siteName(site);
      const state = result.sites?.[siteIndex];
      const intake = state?.intake[hour] ?? 0;
      const release = state?.release[hour] ?? 0;
      const stored = state?.storage[hour] ?? 0;
      const active = isFlowing(intake) || isFlowing(release);
      const point = marker.getElement();
      point.classList.toggle('is-active', active);
      point.classList.toggle('is-release', isFlowing(release));
      point.classList.toggle('is-storing', stored > .1);
      const colour = isFlowing(release) ? '#7651b9' : (active || stored > .1) ? '#008874' : '#566a7c';
      outline?.setStyle({color:colour, fillColor:colour, weight:3, fillOpacity:active || stored > .1 ? .32 : .14});
      label.textContent = siteName(site);
      const metrics = [
        ...(active ? [(isFlowing(release) ? '↑ ' + flow(release) : '↓ ' + flow(intake))] : []),
        ...(stored > .1 ? [number(stored / 1e6, 2) + ' Mm³'] : []),
        ...(!active && stored <= .1 && participants[siteIndex] ? [tr('In piano', 'In plan')] : [])
      ];
      volume.textContent = metrics.join('\n');
      const summary = tr('Accumulati ', 'Stored ') + number(stored / 1e6, 2) + ' / ' +
        number(site.working_capacity_m3 / 1e6, 2) + tr(' milioni m³', ' million m³');
      point.setAttribute('aria-label', [label.textContent, ...metrics, summary].join(' · '));
      if (marker.getTooltip()) marker.setTooltipContent(summary);
      else marker.bindTooltip(summary, {direction:'top'});
    });
  });
}

function pause() {
  clearInterval(timer);
  timer = null;
}

function go(target) {
  hour = Math.max(0, Math.min(target, Number(range.max)));
  draw();
}

async function refresh({atManualPeak = false} = {}) {
  const generation = ++request;
  pause();
  draw();
  $('play').disabled = true;
  manualPeakJump.disabled = true;
  loadBestManual.disabled = true;
  status.textContent = tr('Caricamento dei piani…', 'Loading plans…');
  const mask = selection.pair ? pairDemo.optimised.mask : selection.mask;
  try {
    const [manual, optimised] = await Promise.all([
      load('manual-' + selection.manual.join('')), selection.pair ? pairDemo.optimised.plan : load('optimal-' + mask)
    ]);
    if (generation !== request) return;
    const firstLoad = !plans;
    for (const plan of [manual, optimised]) {
      plan.participants = plan.sites.map(site => site.intake.some(isFlowing));
    }
    plans = {reference:{q:event.reference, peak:Math.max(...event.reference)}, manual, optimised};
    interventionHour = mostConcurrentIntake(manual, optimised);
    interventionJump.hidden = interventionHour === null;
    if (atManualPeak) hour = manual.q.indexOf(manual.peak);
    else if (firstLoad && interventionHour !== null) hour = interventionHour;
    drawGraph();
    draw();
    $('play').disabled = false;
    manualPeakJump.disabled = false;
    updateBenchmark();
    status.textContent = tr('Alto Reno · 31 maggio–7 giugno 2013 · esercizio sulla portata a Maxau',
      'Upper Rhine · 31 May–7 June 2013 · Maxau discharge exercise');
  } catch {
    if (generation === request) status.textContent = tr('Piani non disponibili. Cambia selezione per riprovare.',
      'Plans unavailable. Change the selection to retry.');
  }
}

function updateBenchmark() {
  const best = currentBenchmark();
  loadBestManual.hidden = !best;
  if (!best) return;
  const selected = best.options.every((option, index) => option === selection.manual[index]);
  loadBestManual.disabled = selected;
  loadBestManual.textContent = selected
    ? tr('Miglior manuale in uso', 'Best manual in use')
    : tr('Prova il miglior manuale', 'Try best manual');
  loadBestManual.title = tr('Miglior picco fra le finestre disponibili ', 'Lowest peak among available windows ') + flow(best.peak);
}

function labels() {
  const entries = [
    ['flood-example','Esempi','Examples'],
    ['flood-edit-site','Scegli le casse','Choose polders'], ['flood-reset','Inizio','Start'],
    ['flood-legend','Fonti','Sources'], ['center-ignitions','Inquadra tutte','Fit all polders'],
    ['flood-jump-difference','Vai ai prelievi','Jump to intakes'],
    ['flood-prev','← 1 h','← 1 h'], ['flood-next','1 h →','1 h →']
  ];
  for (const [id,it,en] of entries) $(id).textContent = tr(it,en);
  compareOnMap.textContent = tr('Confronto · 2 casse', 'Compare · 2 polders');
  compareOnMap.title = tr('Confronta la scelta delle casse al picco del miglior manuale',
    'Compare the choice of polders at the best manual plan’s peak');
  range.setAttribute('aria-label', tr('Ora del replay', 'Replay hour'));
  manualPeakJump.textContent = tr('Vai al picco manuale', 'Jump to manual peak');
  updateBenchmark();
  $('flood-speed').setAttribute('aria-label', tr('Velocità del replay', 'Replay speed'));
  graph.setAttribute('aria-label', tr('Portate a Maxau: riferimento, scenari e osservazione storica',
    'Discharge at Maxau: reference, scenarios and historic observation'));
  $('flood-close-right').setAttribute('aria-label', tr('Chiudi', 'Close'));
  if (activeDrawer) showDrawer(activeDrawer);
  updateMapLegend();
  draw();
}

document.body.classList.add('upper-rhine');
$('flood-menu').hidden = true;
$('flood-containment').parentElement.hidden = true;
$('flood-edit-site').onclick = () => showDrawer(activeDrawer === 'manual' ? null : 'manual');
$('flood-differences').onclick = () => {
  atlasVisible = !atlasVisible;
  for (const {map, inundation} of maps) {
    if (atlasVisible) inundation.addTo(map);
    else inundation.remove();
  }
  updateMapLegend();
};
$('flood-legend').onclick = () => showDrawer(activeDrawer === 'data' ? null : 'data');
$('flood-example').onclick = () => showDrawer(activeDrawer === 'examples' ? null : 'examples');
$('flood-close-right').onclick = () => showDrawer(null);
$('center-ignitions').onclick = () => fit();
interventionJump.onclick = () => {
  if (interventionHour === null) return;
  pause();
  fit();
  go(interventionHour);
};
manualPeakJump.onclick = () => {
  pause();
  go(plans.manual.q.indexOf(plans.manual.peak));
};
loadBestManual.onclick = () => {
  selection.manual = [...currentBenchmark().options];
  if (activeDrawer === 'manual') showDrawer('manual');
  refresh();
};
$('flood-reset').onclick = () => { pause(); go(0); };
$('flood-prev').onclick = () => { pause(); go(hour-1); };
$('flood-next').onclick = () => { pause(); go(hour+1); };
range.oninput = () => { pause(); go(Number(range.value)); };
$('play').onclick = () => {
  if (timer) { pause(); draw(); return; }
  if (hour === Number(range.max)) go(0);
  timer = setInterval(() => {
    if (hour + 1 >= Number(range.max)) pause();
    go(hour + 1);
  }, Number($('flood-speed').value));
  draw();
};
document.addEventListener('hazardia-language', labels);
document.addEventListener('visibilitychange', () => { if (document.hidden) { pause(); draw(); } });
window.addEventListener('message', message => {
  if (message.origin !== location.origin || message.source !== parent || message.data?.type !== 'hazardia-flood-visible') return;
  if (!message.data.visible) { pause(); draw(); }
  else requestAnimationFrame(() => maps.forEach(({map}) => map.invalidateSize({pan:false})));
});
labels();

try {
  event = await load('event');
  if (event.schema !== 'hazardia.upper-rhine/1') throw new Error('Invalid replay');
  const [context, benchmark] = await Promise.all([
    load('atlas').catch(() => null), load('manual-benchmark').catch(() => null)
  ]);
  atlas = context?.schema === 'hazardia.upper-rhine-atlas/1' ? context : null;
  manualBenchmark = benchmark;
  pairDemo = await bestPairComparison().catch(() => null);
  updateMapLegend();
  const allSites = (1 << event.sites.length) - 1;
  const usePair = Boolean(pairDemo) && new URLSearchParams(location.search).get('flood-demo') !== '0';
  selection = {mask:allSites, pair:usePair, manual:[...(usePair ? pairDemo.manual.options : event.default_manual)]};
  range.max = event.reference.length - 1;
  range.step = 1;
  range.disabled = false;
  hour = event.reference.indexOf(Math.max(...event.reference));
  mapViews();
  $('flood-edit-site').disabled = false;
  await refresh({atManualPeak:usePair});
  if (pairDemo) {
    compareOnMap.disabled = false;
    compareOnMap.onclick = () => {
      selection = {mask:allSites, pair:true, manual:[...pairDemo.manual.options]};
      showDrawer(null);
      fit();
      refresh({atManualPeak:true});
    };
    mountRhineDemo({
      tr, el, svg, number, relative, charts,
      siteNames: plan => event.sites.filter((_, i) => plan.sites[i].intake.some(isFlowing)).map(siteName).join(' · '),
      pauseReplay() { pause(); draw(); },
      async load() {
        const manual = await load('manual-' + pairDemo.manual.options.join(''));
        const reference = {q:event.reference, peak:Math.max(...event.reference)};
        return {series:[reference, manual, pairDemo.optimised.plan], candidates:pairDemo.candidates};
      }
    });
  }
} catch {
  status.textContent = tr('Replay Alto Reno non disponibile.', 'Upper Rhine replay unavailable.');
}
