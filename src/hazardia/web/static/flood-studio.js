import {getLanguage, locale} from '/i18n.js';
import {scheduledTiles} from '/scheduled-tiles.js';
import {drawRescueRoutes} from '/flood-rescue.js';

const $ = id => document.getElementById(id);
const tr = (it, en) => getLanguage() === 'en' ? en : it;
const integer = n => n.toLocaleString(locale(), {maximumFractionDigits: 0});
const centimetres = n => (100 * n).toLocaleString(locale(), {maximumFractionDigits: 1}) + ' cm';
const clock = m => '+' + String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0');
const sampleDate = value => new Intl.DateTimeFormat(locale(), {
  day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Rome', timeZoneName: 'short'
}).format(new Date(value));
const jobParam = new URLSearchParams(location.search);
const rescueArchive = 'job-78cd5d14b5234865b715bd8f090c0caf';
const example = 'job-57b87e7d3e044dbc90b5c0418460a87b';
const job = jobParam.get('flood-job') || (jobParam.get('flood-rescue') === '1' ? rescueArchive : example);
const equalResources = job === example && jobParam.get('flood-edition') !== 'first';
const asset = (kind, file) => {
  const edition = kind === 'containment' && equalResources ? 'equal-resources/' : '';
  return '/assets/flood-' + kind + '/' + job + '/' + edition + file;
};
const rescueMode = () => mode === 'rescue';
let mode = jobParam.get('flood-rescue') === '1' ? 'rescue' : 'containment';
let data, rescue, manual, initialManual, minute = 0, playFrame = null, drawer = null, failure = false;
let maps = [], synchronising = false;
let differences, highlightDifferences = true;
const imageCache = new Map();
const left = $('flood-left'), right = $('flood-right');
const text = (id, value) => { $(id).textContent = value; };
function node(tag, label = '', className = '') {
  const el = document.createElement(tag);
  el.className = className;
  el.textContent = label;
  return el;
}
const siteLabel = s => tr('Sezione ', 'Section ') + s.site;
const byId = id => data.cases.find(c => c.id === id);
const activationHour = plan => plan.activation_hour ?? data.capture_start_hour ?? 2;
const planLabel = plan => siteLabel(plan) + ' · ' + clock(activationHour(plan) * 60);
const currentFrames = () => rescueMode() ? rescue?.frames : data && byId(data.baseline)?.frames;
const place = () => data?.title || (job === rescueArchive ? 'L’Aquila' : '');

function comparisonHour(bothWithdrawing = false) {
  if (!data || rescueMode()) return null;
  const manualFrames = byId(manual).frames;
  const gains = byId(data.optimized).frames.map((frame, hour) => {
    const reference = manualFrames[hour];
    if (bothWithdrawing && !(reference.captured_m3_s > 0 && frame.captured_m3_s > 0)) return 0;
    return reference.closed_roads - frame.closed_roads;
  });
  const peak = Math.max(0, ...gains);
  if (!peak) return null;
  let bestStart = 0, bestLength = 0, length = 0;
  for (let hour = 0; hour < gains.length; hour++) {
    length = gains[hour] === peak ? length + 1 : 0;
    if (length > bestLength) {
      bestLength = length;
      bestStart = hour + 1 - length;
    }
  }
  return bestStart + Math.floor((bestLength - 1) / 2);
}

function openingHour() {
  return comparisonHour(true) ?? comparisonHour() ?? 0;
}

function updateWithdrawal(item, plan, frame, hour) {
  const show = equalResources && !rescueMode();
  item.withdrawal.hidden = !show;
  if (!show) return;
  const flow = frame.captured_m3_s.toLocaleString(locale(), {maximumFractionDigits: 2});
  item.flow.textContent = tr('Prelievo ora', 'Withdrawal now') + ' · ' + flow + ' m³/s';
  item.withdrawal.classList.toggle('is-withdrawing', frame.captured_m3_s > 0);
  if (item.schedule.dataset.plan !== plan.id) {
    item.schedule.dataset.plan = plan.id;
    item.schedule.replaceChildren(...plan.frames.map(sample => {
      const tick = node('i', '', sample.captured_m3_s > 0 ? 'withdrawal-on' : '');
      tick.title = clock(sample.index * 60) + ' · ' +
        sample.captured_m3_s.toLocaleString(locale(), {maximumFractionDigits: 2}) + ' m³/s';
      return tick;
    }));
  }
  const selected = item.schedule.children[hour];
  item.schedule.querySelector('.selected-hour')?.classList.remove('selected-hour');
  selected?.classList.add('selected-hour');
}
const depthKey = [
  ['#1481eb', 'Profondità dell’acqua', 'Water depth'],
  ['#4de0c3', 'Acqua ≥1 cm meno profonda', 'Depth reduced by ≥1 cm'],
  ['#ffae34', 'Acqua ≥1 cm più profonda', 'Depth increased by ≥1 cm']
];
function updateMapKey() {
  const legend = $('flood-map-key');
  legend.hidden = rescueMode() || !data;
  const items = differences && highlightDifferences ? depthKey : depthKey.slice(0, 1);
  const key = [getLanguage(), items.length].join(':');
  if (legend.dataset.key === key) return;
  legend.dataset.key = key;
  legend.setAttribute('aria-label', tr('Legenda dell’alluvione','Flood map legend'));
  legend.replaceChildren(...items.map(([colour, it, en]) => {
    const item = node('li');
    const swatch = node('i');
    swatch.style.background = colour;
    item.append(swatch, document.createTextNode(tr(it,en)));
    return item;
  }));
  if (items.length > 1) {
    legend.append(node('li',tr('Rispetto a nessun intervento','Compared with no intervention'),'flood-map-key-note'));
  }
}
const bounds = () => {
  if (rescueMode()) return L.latLngBounds([rescue.problem.base, ...rescue.problem.calls.map(c => c.point)].map(([x,y]) => [y,x]));
  return L.latLngBounds(currentFrames()[0].bounds);
};

function setup() {
  maps = Array.from({length: 3}, (_, index) => {
    const section = node('section', '', 'scenario-map-card');
    const heading = node('div', '', 'scenario-map-heading');
    const title = node('strong'), badge = node('output', '', 'scenario-area-badge'), detail = node('span');
    const comparison = node('p', '', 'scenario-explanation flood-depth-comparison');
    const impact = node('p', '', 'flood-road-impact');
    const withdrawal = node('div', '', 'flood-withdrawal');
    const flow = node('span');
    const schedule = node('div', '', 'flood-withdrawal-hours');
    schedule.setAttribute('aria-hidden', 'true');
    withdrawal.append(flow, schedule);
    heading.append(title, badge, comparison, detail, impact, withdrawal);
    const stage = node('div', '', 'map-stage'), element = node('div', '', 'map');
    element.setAttribute('role', 'region');
    stage.append(element);
    section.append(heading, stage);
    $('scenario-maps').append(section);
    const map = L.map(element, {scrollWheelZoom: false, preferCanvas: true, zoomControl: false, attributionControl: true, maxZoom: 19});
    L.control.zoom({position: 'topright'}).addTo(map);
    map.attributionControl.setPrefix(false);
    map.attributionControl.addAttribution('© Regione Abruzzo · Ortofoto 2018–2019');
    if (job === rescueArchive) {
      L.imageOverlay('/assets/satellite.png', [[42.30, 13.32], [42.40, 13.44]], {pane: 'tilePane'}).addTo(map);
    }
    scheduledTiles('/api/maps/ortho/{z}/{x}/{y}', {minZoom: 8, maxZoom: 19, keepBuffer: 1, updateWhenIdle: true}).addTo(map);
    L.control.scale({imperial:false}).addTo(map);
    const water = L.layerGroup().addTo(map), markers = L.layerGroup().addTo(map);
    const changeLayer = L.layerGroup().addTo(map);
    const changePane = map.createPane('depthDifferencePane');
    changePane.style.zIndex = '410';
    changePane.style.pointerEvents = 'none';
    map.on('moveend', () => {
      if (synchronising || !map._loaded) return;
      synchronising = true;
      try {
        for (const other of maps) if (other.map !== map && other.map._loaded) other.map.setView(map.getCenter(), map.getZoom(), {animate: false});
      } finally { synchronising = false; }
    });
    return {index, map, element, title, badge, detail, impact, comparison, withdrawal, flow, schedule, water, markers, changeLayer, key: null};
  });
  new ResizeObserver(() => {
    for (const {map} of maps) map.invalidateSize({pan:false});
  }).observe($('scenario-maps'));
}
function center() {
  if (!maps.length || (rescueMode() ? !rescue : !data)) return;
  synchronising = true;
  try {
    const first = maps[0].map;
    first.fitBounds(bounds(), {padding: rescueMode() ? [45, 118] : [16, 35], maxZoom: 15, animate:false});
    for (const {map} of maps.slice(1)) map.setView(first.getCenter(), first.getZoom(), {animate:false});
  } finally { synchronising = false; }
}
function choose(id) {
  manual = id;
  if (drawer === 'manual') showDrawer('manual');
  update();
}
function drawSite(item, plan, frame) {
  item.markers.clearLayers();
  if (!plan.point) return;
  const rate = frame.captured_m3_s;
  const withdrawing = rate > 0;
  const hasVolume = Number.isFinite(frame.stored_m3) && data.capacity_m3 > 0;
  const fraction = hasVolume ? Math.max(0, Math.min(1, frame.stored_m3 / data.capacity_m3)) : 0;
  const fill = Math.round(15 * fraction);
  const state = withdrawing ? rate.toLocaleString(locale(), {maximumFractionDigits: 2}) + ' m³/s'
    : Number.isFinite(rate) ? tr('Prelievo fermo', 'No withdrawal') : tr('Dato assente', 'No flow data');
  const title = tr('Invaso S', 'Storage S') + plan.site;
  const diagram = node('div');
  const card = node('div', '', 'flood-intervention-card');
  const tank = node('span', '', 'flood-intervention-tank');
  tank.innerHTML = `<svg viewBox="0 0 28 28" aria-hidden="true">
    <rect x="4" y="${24 - fill}" width="20" height="${fill}"/>
    <path d="M3 7v17h22V7"/>
  </svg>`;
  const labels = node('span', '', 'flood-intervention-labels');
  labels.append(node('strong', title), node('span', state));
  card.append(tank, labels);
  const connector = node('div', '', 'flood-intervention-connector');
  connector.innerHTML = '<svg viewBox="0 0 134 22" aria-hidden="true"><path d="M67 15V3m-5 5 5-5 5 5"/><circle cx="67" cy="19" r="3"/></svg>';
  diagram.append(card, connector);
  const icon = L.divIcon({html: diagram, className: 'flood-intervention' + (withdrawing ? ' is-withdrawing' : ''),
    iconSize: [134,66], iconAnchor: [67,63], tooltipAnchor: [0,-63]});
  const volume = hasVolume ? integer(frame.stored_m3) + ' / ' + integer(data.capacity_m3) + ' m³'
    : tr('Volume non disponibile', 'Storage volume unavailable');
  const tooltip = node('span', title + ' · ' + state + ' · ' + volume);
  const marker = L.marker(plan.point, {icon, alt: tooltip.textContent}).addTo(item.markers).bindTooltip(tooltip);
  marker.getElement()?.setAttribute('aria-label', tooltip.textContent);
  if (item.index === 1) marker.on('click', () => showDrawer('manual'));
}
function matchingDifference(selection, frame, index) {
  const change = differences?.cases?.[selection.id]?.[index];
  const reference = byId(data.baseline).frames[index];
  if (change?.at === frame.at && change.variant_sha256 === frame.raster_sha256 &&
      change.reference_sha256 === reference.raster_sha256) return change;
  return null;
}

function updateComparison(item, change, hasIntervention) {
  item.comparison.hidden = rescueMode();
  if (rescueMode()) return;
  item.comparison.classList.toggle('has-change', !!change?.shallower_cells);
  if (!hasIntervention) {
    item.comparison.textContent = tr('Riferimento per il confronto', 'Comparison baseline');
  } else if (!change) {
    item.comparison.textContent = tr('Confronto di profondità non disponibile', 'Depth comparison unavailable');
  } else {
    const parts = [];
    if (change.shallower_cells) {
      parts.push('−' + centimetres(change.max_reduction_m) +
        ' max · ' + integer(change.shallower_cells) + tr(' celle meno profonde', ' shallower cells'));
    }
    if (change.deeper_cells) {
      parts.push('+' + centimetres(change.max_increase_m) + ' max · ' +
        integer(change.deeper_cells) + tr(' celle più profonde', ' deeper cells'));
    }
    item.comparison.textContent = parts.join(' / ') ||
      tr('Nessuna variazione di almeno 1 cm', 'No change of 1 cm or more');
  }
}

function update() {
  const loaded = rescueMode() ? !!rescue : !!data;
  const index = Math.min((currentFrames()?.length || 1) - 1, Math.floor(minute / 60));
  updateMapKey();
  $('play').disabled = !loaded;
  $('flood-edit-site').disabled = !data;
  $('flood-edit-site').hidden = rescueMode();
  $('flood-differences').hidden = rescueMode() || !differences || !data;
  $('flood-differences').setAttribute('aria-pressed', String(highlightDifferences));
  const usefulHour = equalResources && loaded ? comparisonHour() : null;
  const jump = $('flood-jump-difference');
  jump.hidden = usefulHour === null;
  if (usefulHour !== null) {
    jump.textContent = tr('Divario massimo', 'Largest gap') + ' · ' + clock(usefulHour * 60);
  }
  $('flood-time').disabled = !loaded;
  $('flood-prev').disabled = !loaded || minute === 0;
  $('flood-next').disabled = !loaded || minute >= maxMinute();
  $('flood-time').value = minute;
  text('flood-now', clock(minute));
  text('play', playFrame !== null ? tr('Ⅱ Pausa','Ⅱ Pause') : tr('▶ Riproduci','▶ Play'));
  if (!loaded) {
    text('status', failure || (data && rescueMode()) ? tr('Replay non disponibile per questo risultato.', 'No replay for this result.') :
      tr('Caricamento del replay…','Loading replay…'));
    $('scenario-maps').hidden = true;
    return;
  }
  $('scenario-maps').hidden = false;
  const variants = rescueMode() ? ['none','fifo','optimized'].map(id => rescue.plans.find(p => p.id === id)) :
    [data.baseline, manual, data.optimized].map(byId);
  const titles = rescueMode() ? [tr('Senza soccorso','No rescue'),tr('Ordine di chiamata','Call order'),tr('Soccorso ottimizzato','Optimised rescue')] :
    [tr('Senza contenimento','No containment'),tr('Intervento manuale','Manual intervention'),tr('Intervento ottimizzato','Optimised intervention')];
  for (const item of maps) {
    const selection = variants[item.index], frame = (rescueMode() ? rescue.frames : selection.frames)[index];
    const url = asset(rescueMode() ? 'rescue' : 'containment', frame.png);
    const change = rescueMode() ? null : matchingDifference(selection, frame, index);
    const diffUrl = highlightDifferences && change?.png ? asset('containment', change.png) : null;
    const key = [mode, selection.id, index, getLanguage(), diffUrl].join(':');
    item.title.textContent = titles[item.index];
    item.element.setAttribute('aria-label', titles[item.index]);
    if (item.key !== key) {
      item.imageFailed = false;
      item.differenceFailed = false;
      item.changeLayer.clearLayers();
      if (diffUrl) {
        const overlay = L.imageOverlay(diffUrl, frame.bounds, {pane: 'depthDifferencePane', className: 'flood-difference-overlay'});
        overlay.on('error', () => { if (item.key === key) { item.differenceFailed = true; update(); } });
        overlay.addTo(item.changeLayer);
      }
      item.water.clearLayers();
      const depth = L.imageOverlay(url, frame.bounds, {opacity: .93}).addTo(item.water);
      depth.on('error', () => { if (item.key === key) { item.imageFailed = true; update(); } });
      if (rescueMode()) drawRescueRoutes(item.markers, rescue, frame, selection);
      else drawSite(item, selection, frame);
      item.key = key;
    }
    item.impact.hidden = rescueMode();
    updateWithdrawal(item, selection, frame, index);
    if (rescueMode()) {
      const delivered = selection.missions.filter(m => m.delivery <= minute).reduce((n,m) => n + rescue.problem.calls.find(c => c.id === m.call).people, 0);
      const people = rescue.problem.calls.reduce((n,c) => n+c.people, 0);
      item.badge.textContent = delivered + '/' + people;
      item.detail.textContent = tr('Persone consegnate (simulate)', 'People delivered (simulated)');
    } else {
      item.badge.textContent = centimetres(frame.max_depth_m);
      item.badge.title = tr('Massima profondità modellata nella griglia','Maximum modelled depth in grid');
      item.detail.textContent = selection.site
        ? tr('1 invaso', '1 storage unit') + ' · ' + integer(data.capacity_m3) + ' m³ · ' + data.capture_m3_s.toLocaleString(locale()) + ' m³/s · ' + planLabel(selection)
        : tr('0 invasi', '0 storage units');
      const gap = item.index === 2 ? frame.closed_roads - variants[1].frames[index].closed_roads : 0;
      const delta = gap ? ' (' + (gap < 0 ? '−' : '+') + integer(Math.abs(gap)) + ')' : '';
      item.impact.textContent = integer(frame.closed_roads) + tr(' tratti chiusi ora', ' closed segments now') + delta +
        ' · ' + integer(selection.closed_road_hours) + tr(' tratti·ora', ' segment-hours');
      item.impact.title = tr('Chiusure a quest’ora, differenza rispetto al manuale e totale nel periodo.',
        'Closures at this hour, difference from the manual plan and total across the replay.');
    }
    updateComparison(item, change, item.index !== 0);
    if (equalResources && !rescueMode() && item.index === 2 &&
        frame.raster_sha256 === variants[1].frames[index].raster_sha256) {
      item.comparison.textContent = tr('Stessa mappa di profondità del manuale a quest’ora',
        'Same depth map as the manual plan at this hour');
      item.comparison.classList.remove('has-change');
    }
    if (item.differenceFailed) item.comparison.textContent += tr(' · Livello non disponibile', ' · Overlay unavailable');
    if (!rescueMode() && Number.isSafeInteger(frame.positive_cells) && frame.positive_cells >= 0) {
      item.comparison.prepend(integer(frame.positive_cells) + tr(' celle con acqua · ', ' wet cells · '));
    }
    if (item.imageFailed) item.detail.textContent += tr(' · Immagine non disponibile',' · Image unavailable');
    const next = (rescueMode() ? rescue.frames : selection.frames)[index+1];
    if (next) {
      const nextUrl = asset(rescueMode() ? 'rescue' : 'containment', next.png);
      if (!imageCache.has(nextUrl)) {
        const preload = new Image();
        preload.src = nextUrl;
        imageCache.set(nextUrl, preload);
      }
    }
  }
  const at = (rescueMode() ? rescue.frames : byId(data.baseline).frames)[index].at;
  const context = data?.title ? place() + ' · ' + currentFrames().length + ' h · ' : '';
  text('status', context + tr('Esercitazione · ', 'Exercise · ') + sampleDate(at) + ' · HMC–REFlEx');
}
function maxMinute() {
  const hours = currentFrames()?.length || 1;
  return rescueMode() ? hours * 60 - 1 : (hours - 1) * 60;
}
function setMinute(value) { minute = Math.max(0, Math.min(maxMinute(), value)); update(); }
function stop() {
  if (playFrame !== null) cancelAnimationFrame(playFrame);
  playFrame = null;
  update();
}
function play() {
  if (playFrame !== null) return stop();
  if (minute >= maxMinute()) setMinute(0);
  let last = performance.now(), carry = 0;
  function tick(now) {
    const step = rescueMode() ? 1 : 60;
    carry += Math.min(250, now - last) * 60 / Number($('flood-speed').value);
    last = now;
    if (carry >= step) {
      const advance = Math.floor(carry / step) * step;
      carry -= advance;
      setMinute(minute + advance);
    }
    if (minute >= maxMinute()) stop();
    else playFrame = requestAnimationFrame(tick);
  }
  playFrame = requestAnimationFrame(tick);
  update();
}

function showDrawer(kind) {
  drawer = kind;
  left.hidden = kind !== 'menu';
  right.hidden = !kind || kind === 'menu';
  $('flood-menu').setAttribute('aria-expanded', String(!left.hidden));
  if (!kind) return;
  const panel = $(kind === 'menu' ? 'flood-left-content' : 'flood-right-content');
  panel.replaceChildren();
  const paragraph = (it,en) => panel.append(node('p',tr(it,en)));
  const action = (it,en,fn) => {
    const btn = node('button',tr(it,en)); btn.type = 'button'; btn.onclick = fn; panel.append(btn);
  };
  const download = (kind,file) => {
    const link = node('a',file); link.href = asset(kind,file); link.download = file; panel.append(link,document.createElement('br'));
  };
  const title = value => text('flood-right-title',value);
  if (kind === 'menu') {
    if (data) {
      action('Sito manuale', 'Manual site', () => { if (rescueMode()) switchMode('containment'); showDrawer('manual'); });
      action('Criterio di ottimizzazione', 'Optimisation objective', () => showDrawer('objective'));
    }
    action('Dati e ipotesi', 'Data and assumptions', () => showDrawer('source'));
  } else if (kind === 'manual') {
    title(tr('Configura l’invaso manuale','Configure manual storage'));
    paragraph('Usi un solo invaso, con la stessa capacità e lo stesso prelievo massimo dell’ottimizzatore.',
      'You use one storage unit with the same capacity and maximum withdrawal as the optimised plan.');
    const plans = data.cases.filter(plan => plan.point && plan.strategy !== 'dispatch');
    const selected = byId(manual);
    const sites = [...new Map(plans.map(plan => [plan.site, plan])).values()];
    const site = node('select');
    site.id = 'flood-manual-site';
    for (const plan of sites) site.add(new Option(siteLabel(plan), String(plan.site)));
    site.value = String(selected.site);
    const start = node('select');
    start.id = 'flood-manual-start';
    const starts = data.activation_hours ?? [activationHour(selected)];
    for (const hour of starts) start.add(new Option(clock(hour * 60), String(hour)));
    start.value = String(selected.strategy === 'dispatch' ? starts[0] : activationHour(selected));
    function selectPlan(event) {
      const plan = plans.find(item => item.site === Number(site.value) && activationHour(item) === Number(start.value));
      if (plan) choose(plan.id);
      $(event.target.id)?.focus();
    }
    site.onchange = start.onchange = selectPlan;
    const siteLabelNode = node('label',tr('Sezione di intervento','Intervention section'));
    siteLabelNode.htmlFor = site.id;
    panel.append(siteLabelNode, site);
    if (starts.length > 1) {
      const startLabel = node('label',tr('Ora di attivazione','Activation time'));
      startLabel.htmlFor = start.id;
      panel.append(startLabel,start);
    }
    const best = byId(data.optimized);
    if (best.strategy === 'dispatch') {
      if (selected.id === best.id) {
        paragraph('Il manuale usa la stessa sequenza oraria dell’ottimizzatore.',
          'The manual scenario uses the same hourly schedule as the optimised plan.');
      } else {
        action('Copia piano ottimizzato', 'Copy optimised plan', () => choose(best.id));
      }
      action('Ripristina il piano manuale di riferimento', 'Restore reference manual plan', () => choose(initialManual));
      if (initialManual !== data.manual) {
        paragraph('Il riferimento è il miglior piano a prelievo continuo tra quelli valutati.',
          'The reference is the best continuous withdrawal plan among those evaluated.');
      }
    }
  } else if (kind === 'objective') {
    title(tr('Criterio di ottimizzazione','Optimisation objective'));
    paragraph('Con la stessa risorsa del manuale, sceglie il piano con meno tratti·ora chiusi. A parità, preferisce meno celle·ora allagate.',
      'With the same resource as the manual plan, it selects the plan with the fewest closed segment-hours. Ties favour fewer inundated cell-hours.');
    const baseline = byId(data.baseline);
    const manualPlan = byId(manual);
    const best = byId(data.optimized);
    for (const [label, plan] of [[tr('Senza intervento','No intervention'), baseline], [tr('Manuale','Manual'), manualPlan],
        [tr('Ottimizzato','Optimised'), best]]) {
      panel.append(node('p',label + (plan.site ? ' · ' + planLabel(plan) : '') + ' · ' +
        integer(plan.closed_road_hours) + tr(' tratti·ora chiusi',' closed segment-hours')));
    }
    if (best.strategy === 'dispatch') {
      paragraph('Il piano ottimizzato usa ore di prelievo separate per conservare la capacità dell’invaso.',
        'The optimised plan schedules individual withdrawal hours to conserve storage capacity.');
      panel.append(node('p',tr('Prelievo alle ore ', 'Withdrawal hours ') +
        best.active_hours.map(hour => clock(hour * 60)).join(', ')));
    }
    const options = node('details');
    options.append(node('summary',tr('Piani valutati','Evaluated plans')));
    for (const plan of data.cases.filter(item => item.site)) {
      options.append(node('p',planLabel(plan) + (plan.strategy === 'dispatch' ? tr(' · a ore', ' · hourly') : '') + ' · ' + integer(plan.closed_road_hours) +
        tr(' tratti·ora chiusi',' closed segment-hours')));
    }
    panel.append(options);
    paragraph('Soglia ipotetica: 10 cm. Ponti, viadotti e archi senza dati sufficienti restano non valutabili.', 'Hypothetical threshold: 10 cm. Bridges, viaducts and roads without enough data remain unassessed.');
  } else if (kind === 'legend') {
    title(tr('Legenda','Legend'));
    const ul = node('ul','','depth-key');
    const row = (colour, label) => {
      const li = node('li'), swatch = node('i');
      swatch.style.background = colour;
      li.append(swatch,document.createTextNode(label)); ul.append(li);
    };
    row('#1481eb',tr('Acqua modellata · più intensa dove più profonda','Modelled water · stronger blue for deeper water'));
    if (rescueMode()) {
      row('#70ffcd',tr('Percorso del mezzo nello scenario','Vehicle route for this scenario'));
      row('#ff4e59',tr('Tratto interrotto sul percorso prioritario','Closed segment on the priority route'));
      row('#ffe172',tr('Tratto non valutabile sul percorso prioritario','Unassessed segment on the priority route'));
    } else {
      if (differences) {
        row(depthKey[1][0],tr('Profondità ridotta di almeno 1 cm rispetto al riferimento','At least 1 cm shallower than the baseline'));
        row('#ffae34',tr('Profondità aumentata di almeno 1 cm rispetto al riferimento','At least 1 cm deeper than the baseline'));
      }
      if (differences) paragraph('I bordi sono smussati a video. Valori e conteggi usano le celle originali.',
        'Edges are smoothed for display. Values and counts use the original cells.');
      row('#116e68',tr('Invaso ipotetico e punto di prelievo','Hypothetical storage unit and withdrawal point'));
      paragraph('La freccia indica la deviazione verso l’invaso ed è verde durante il prelievo. Il riempimento del simbolo indica la frazione di capacità occupata.',
        'The arrow shows diversion into storage and turns green during withdrawal. The fill shows the fraction of storage capacity used.');
    }
    panel.append(ul);
    paragraph('Trasparente: profondità zero o senza dati. La trasparenza non indica che una strada sia percorribile.', 'Transparent: zero depth or no data. Transparency does not establish road access.');
  } else if (kind === 'example') {
    title(tr('Esempi','Examples'));
    action('Alto Reno · casse di laminazione · 2013', 'Upper Rhine · retention polders · 2013', () => {
      parent.location.assign('/?view=results&lab=flood&flood-case=upper-rhine');
    });
    action('Teramo · Tordino e Vezzola · 48 h','Teramo · Tordino and Vezzola · 48 h', () => {
      if (job !== example || !equalResources) {
        const parentUrl = new URL('/?view=results&lab=flood', location.origin);
        parent.location.assign(parentUrl);
        return;
      }
      showDrawer(null); choose(initialManual); switchMode('containment'); setMinute(openingHour() * 60); center();
    });
  } else {
    title(tr('Dati e ipotesi','Data and assumptions'));
    paragraph('HMC–REFlEx · mappe calcolate separatamente per ogni portata oraria HMC. L’ora identifica il campione di portata.',
      'HMC–REFlEx · independent maps for each hourly HMC discharge. The displayed hour identifies the discharge sample.');
    if (data?.title) {
      paragraph('Caso ipotetico su terreno reale. Pioggia e invaso sono ipotesi di ricerca. Il dominio copre parte del bacino.',
        'Hypothetical case on real terrain. Rainfall and storage are research assumptions. The domain covers part of the catchment.');
      const archive = node('a',tr('Archivio del replay di soccorso','Archived rescue replay'));
      archive.href = '/?view=results&lab=flood&flood-rescue=1&flood-job=' + rescueArchive;
      archive.target = '_top';
      panel.append(archive, document.createElement('br'));
    }
    if (rescueMode()) {
      paragraph('Stessa piena di riferimento per tutti i piani di soccorso. Richieste e mezzi sono ipotetici; HiGHS dà precedenza alle consegne prioritarie.', 'All rescue plans share the reference flood. Calls and vehicles are hypothetical; HiGHS prioritises critical deliveries.');
      if (rescue) for (const file of ['frames.json','rescue-problem.json','plans.json','audit.json']) download('rescue',file);
    } else {
      if (data) {
        const settings = integer(data.capacity_m3) + ' m³ · ' +
          data.capture_m3_s.toLocaleString(locale()) + ' m³/s';
        paragraph('Risorse identiche: un invaso per piano, capacità e prelievo massimo di ' + settings + '.',
          'Equal resources: one storage unit per plan, with capacity and maximum withdrawal of ' + settings + '.');
        paragraph('Il prelievo riduce le portate nella sezione e a valle. L’esercizio assume che l’acqua rimanga nell’invaso per tutta la finestra.',
          'Withdrawal reduces discharge at and downstream of the section. The exercise holds stored water for the rest of the window.');
      }
      if (data) for (const file of ['view.json','protocol.json']) download('containment',file);
      if (differences) download('containment','differences/index.json');
    }
    if (job === rescueArchive) {
      const href = '/?view=results&lab=evacuation&flood-access=1&flood-job=' + job;
      const link = node('a',tr('Accesso ai presidi · massimo della piena di riferimento','Healthcare access · reference flood maximum'));
      link.href = href;
      link.target = '_top';
      panel.append(link);
    }
  }
}

function switchMode(next) {
  stop();
  mode = next;
  document.body.classList.toggle('flood-spatial-compare', equalResources && !rescueMode());
  const range = $('flood-time');
  range.step = rescueMode() ? 1 : 60;
  range.max = maxMinute();
  minute = Math.min(maxMinute(), rescueMode() ? minute : Math.floor(minute / 60) * 60);
  $('flood-containment').setAttribute('aria-pressed', String(!rescueMode()));
  $('flood-rescue-tab').setAttribute('aria-pressed', String(rescueMode()));
  showDrawer(null);
  update();
  center();
}

function localise() {
  document.title = 'HAZARDIA · ' + tr('Alluvione','Flood');
  for (const [id,it,en] of [
    ['flood-menu','☰ Simulazioni','☰ Simulations'],['flood-example','Esempi','Examples'],['flood-legend','Legenda','Legend'],
    ['center-ignitions','Inquadra','Fit map'],['flood-containment','Contenimento','Containment'],['flood-rescue-tab','Soccorso','Rescue'],
    ['flood-reset','Inizio','Start'],['flood-edit-site','Sito manuale','Manual site'],['flood-prev','← 1 h','← 1 h'],['flood-next','1 h →','1 h →'],
    ['flood-left-title','Simulazioni','Simulations'],['flood-differences','Differenze ≥1 cm','Differences ≥1 cm']
  ]) text(id,tr(it,en));
  $('flood-time').setAttribute('aria-label',tr('Tempo dello scenario','Scenario time'));
  $('flood-speed').setAttribute('aria-label',tr('Velocità di riproduzione','Playback speed'));
  $('flood-speed').options[0].textContent = tr('1 h / 1,5 s','1 h / 1.5 s');
  $('flood-speed').options[1].textContent = tr('1 h / 0,75 s','1 h / 0.75 s');
  for (const id of ['flood-close-left','flood-close-right']) $(id).setAttribute('aria-label',tr('Chiudi','Close'));
  if (drawer) showDrawer(drawer);
  update();
}

async function fetchBundle(kind, schema, file = 'view.json') {
  if (!/^job-[a-f0-9]{32}$/.test(job)) throw new Error('Invalid job');
  const response = await fetch(asset(kind,file));
  if (!response.ok) throw new Error('Missing replay');
  const value = await response.json();
  if (value.schema !== schema || value.job_id !== job) throw new Error('Invalid replay');
  return value;
}
if (jobParam.get('flood-case') === 'upper-rhine') {
  import('/flood-upper-rhine.js?v=extents-1');
} else {
$('play').onclick = play;
$('flood-differences').onclick = () => { highlightDifferences = !highlightDifferences; update(); };
$('flood-edit-site').onclick = () => showDrawer(drawer === 'manual' ? null : 'manual');
$('flood-reset').onclick = () => { stop(); setMinute(0); };
$('flood-jump-difference').onclick = () => {
  const hour = comparisonHour();
  if (hour !== null) { stop(); setMinute(hour * 60); }
};
$('flood-prev').onclick = () => { stop(); setMinute(minute - 60); };
$('flood-next').onclick = () => { stop(); setMinute(minute + 60); };
$('flood-time').oninput = event => { const target = Number(event.target.value); stop(); setMinute(target); };
$('flood-menu').onclick = () => showDrawer(drawer === 'menu' ? null : 'menu');
$('flood-example').onclick = () => showDrawer(drawer === 'example' ? null : 'example');
$('flood-legend').onclick = () => showDrawer(drawer === 'legend' ? null : 'legend');
$('center-ignitions').onclick = center;
$('flood-close-left').onclick = $('flood-close-right').onclick = () => showDrawer(null);
$('flood-containment').onclick = () => switchMode('containment');
$('flood-rescue-tab').onclick = () => switchMode('rescue');
document.addEventListener('hazardia-language', localise);
document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); });
window.addEventListener('message', event => {
  if (event.origin !== location.origin || event.source !== window.parent || event.data?.type !== 'hazardia-flood-visible') return;
  if (!event.data.visible) stop();
  else requestAnimationFrame(() => maps.forEach(({map}) => map.invalidateSize({pan:false})));
});
localise();
Promise.allSettled([
  fetchBundle('containment','hazardia.flood-containment-view/1'),
  job === example ? Promise.resolve(null) : fetchBundle('rescue','hazardia.flood-rescue-view/1'),
  fetchBundle('containment','hazardia.flood-depth-differences/1','differences/index.json')
]).then(([containment, rescueResult, depthDifferences]) => {
  data = containment.value;
  rescue = rescueResult.value;
  $('flood-rescue-tab').hidden = !rescue;
  $('flood-containment').hidden = !data;
  if (!rescue && data) mode = 'containment';
  if (depthDifferences.value?.threshold_m === .01) differences = depthDifferences.value;
  initialManual = data?.manual;
  if (equalResources && data && jobParam.get('flood-manual') !== 'original') {
    const continuousPlans = data.cases.filter(plan => plan.point && plan.strategy !== 'dispatch');
    continuousPlans.sort((a, b) => a.closed_road_hours - b.closed_road_hours ||
      a.wet_cell_hours - b.wet_cell_hours || a.site - b.site || activationHour(a) - activationHour(b));
    initialManual = continuousPlans[0]?.id ?? initialManual;
  }
  manual = initialManual;
  if (data || rescue) {
    if (!data && rescue) mode = 'rescue';
    $('scenario-maps').hidden = false;
    setup();
  }
  failure = !data && !rescue;
  const requestedHour = jobParam.get('flood-hour');
  const startHour = requestedHour === null ? (equalResources ? openingHour() : null) : Number(requestedHour);
  if (Number.isSafeInteger(startHour) && startHour >= 0) {
    minute = Math.min(startHour, Math.floor(maxMinute() / 60)) * 60;
  }
  switchMode(mode);
});
}
