import {getLanguage, locale} from '/i18n.js';

const tr = (it, en) => getLanguage() === 'en' ? en : it;
const latLng = ([lon, lat]) => [lat, lon];
const number = (value, digits = 2) => value.toLocaleString(locale(), {maximumFractionDigits: digits});
const stateName = state => ({
  open: tr('Percorribile secondo la regola', 'Passable under the rule'),
  closed: tr('Interrotto secondo la regola', 'Closed under the rule'),
  unknown: tr('Non valutabile', 'Not assessable')
})[state];
const outcome = state => ({
  available: tr('Percorso di riferimento disponibile', 'Reference route available'),
  detour: tr('Deviazione su archi valutati', 'Detour on assessed roads'),
  interrupted: tr('Accesso interrotto nel grafo dello scenario', 'Access interrupted in the scenario graph'),
  indeterminate: tr('Accesso indeterminato', 'Access indeterminate'),
  no_reference: tr('Nessun percorso nel grafo di riferimento', 'No route in the reference graph'),
  unsnapped: tr('Aggancio alla rete non disponibile', 'Road-network snap unavailable')
})[state];
const reasonName = reason => ({
  structure_depth_unqualified: tr('Struttura sopraelevata o coperta: profondità in carreggiata non verificata',
    'Elevated or covered structure: depth on the carriageway is unverified'),
  maximum_at_or_above_threshold: tr('Profondità massima pari o superiore alla soglia', 'Maximum depth at or above the threshold'),
  outside_grid: tr('Parte del tratto fuori griglia', 'Part of the segment outside the grid'),
  nodata: tr('Celle NoData lungo il tratto', 'NoData cells along the segment'),
  full_valid_coverage_below_threshold: tr('Copertura valida completa sotto soglia', 'Full valid coverage below threshold')
})[reason];
const styles = {
  reference: {color: '#bca9fa', weight: 8, opacity: .95},
  scenario: {color: '#37d9b7', weight: 4, opacity: 1},
  possible: {color: '#fff1b0', weight: 3, dashArray: '5 7', opacity: 1},
  closed: {color: '#ff6268', weight: 8, dashArray: '9 5', opacity: 1},
  unknown: {color: '#ffcd65', weight: 8, dashArray: '2 5', opacity: 1}
};

function node(tag, text, className) {
  const element = document.createElement(tag);
  if (text) element.textContent = text;
  if (className) element.className = className;
  return element;
}

function labeledSelect(label, entries, selected, onChange) {
  const wrapper = node('label', label);
  const select = node('select');
  select.setAttribute('aria-label', label);
  for (const [value, text] of entries) select.add(new Option(text, value));
  select.value = selected;
  select.onchange = () => onChange(select.value);
  wrapper.append(select);
  return wrapper;
}

function depthText(depth) {
  if (depth.state === 'outside') return tr('fuori griglia', 'outside grid');
  if (depth.state === 'nodata') return 'NoData';
  return depth.depth_m === 0 ? tr('0 m · zero valido', '0 m · valid zero') : number(depth.depth_m, 3) + ' m';
}

export function floodAccess(maps) {
  const panel = node('details', '', 'flood-access');
  panel.id = 'flood-access';
  panel.hidden = true;
  panel.dataset.i18nSkip = '';
  const title = node('summary');
  const body = node('div', '', 'flood-access-body');
  panel.append(title, body);
  const mapPair = document.getElementById('map-pair');
  const layout = node('div', '', 'flood-access-layout');
  mapPair.before(layout);
  layout.append(panel, mapPair);
  const css = node('link');
  css.rel = 'stylesheet';
  css.href = '/flood-access.css';
  document.head.append(css);

  const groups = maps.map(map => {
    map.createPane('floodAccess');
    map.getPane('floodAccess').style.zIndex = 550;
    return L.layerGroup().addTo(map);
  });
  let product = null;
  let request = null;
  let data = null;
  let replayIndex = 0;
  let originId = '';
  let destinationId = '';
  let edgeId = '';
  let notice = '';

  function chooseDefault() {
    const replay = data.replays[replayIndex];
    const pair = replay.pairs[replay.default_pair];
    originId = pair.origin;
    destinationId = pair.destination;
    edgeId = '';
  }

  function setSegment(id, fit = false) {
    edgeId = id;
    render();
    if (fit) {
      const edge = data.edges[edgeId];
      maps.forEach(map => map.fitBounds([latLng(edge.a), latLng(edge.b)],
        {padding: [65, 65], maxZoom: 17, animate: false}));
    }
  }

  function render(fit = false) {
    title.textContent = tr('Accesso stradale ai presidi sanitari', 'Road access to mapped healthcare sites');
    const active = document.activeElement;
    const activeLabel = body.contains(active) ? active.getAttribute('aria-label') : null;
    groups.forEach(group => group.clearLayers());
    body.replaceChildren();
    if (!panel.open || !product) return;
    if (!data) {
      const status = node('p', notice || tr('Caricamento del replay…', 'Loading the replay…'));
      status.setAttribute('role', 'status');
      body.append(status);
      return;
    }

    const replay = data.replays[replayIndex];
    const pair = replay.pairs.find(value => value.origin === originId && value.destination === destinationId);
    const origin = data.origins.find(value => value.id === originId);
    const destination = data.destinations.find(value => value.id === destinationId);
    const counts = data.summary[replayIndex];
    const controls = node('div', '', 'flood-access-controls');
    controls.append(
      labeledSelect(tr('Centro abitato o località', 'Settlement or locality'), data.origins.map(x => [x.id, x.name]),
        originId, value => {originId = value; edgeId = ''; render(true);}),
      labeledSelect(tr('Presidio mappato', 'Mapped healthcare site'), data.destinations.map(x => [x.id, x.name]),
        destinationId, value => {destinationId = value; edgeId = ''; render(true);}),
      labeledSelect(tr('Soglia ipotetica', 'Assumed depth threshold'), data.replays.map((r, i) =>
        [String(i), number(r.threshold_m * 100) + ' cm']), String(replayIndex), value => {
        replayIndex = Number(value); edgeId = ''; render();
      })
    );
    const status = node('p', outcome(pair.status), 'flood-access-status');
    status.setAttribute('role', 'status');
    const distance = path => path ? number(path.distance_m / 1000, 3) + ' km' : '—';
    const lengths = [
      tr('Riferimento ', 'Reference ') + distance(pair.reference),
      tr('Scenario su archi valutati ', 'Scenario on assessed roads ') + distance(pair.scenario)
    ];
    if (pair.possible) lengths.push(tr('Percorso possibile da verificare ', 'Possible route requiring verification ') + distance(pair.possible));
    body.append(controls, status, node('p', lengths.join(' · ')),
      node('p', tr('Profondità al punto della località: ', 'Depth at the locality point: ') + depthText(origin.depth) +
        tr(' · Agganci stimati alla rete: ', ' · Estimated snaps to the network: ') +
        number(origin.snap_distance_m, 0) + ' / ' + number(destination.snap_distance_m, 0) + ' m.', 'flood-access-note'));

    const legend = node('ul', '', 'flood-access-legend');
    for (const [key, text] of [
      ['reference', tr('Riferimento', 'Reference')],
      ['scenario', tr('Scenario', 'Scenario')],
      ['closed', tr('Interrotto', 'Closed')],
      ...(pair.possible ? [['possible', tr('Percorso possibile', 'Possible route')]] : []),
      ['unknown', tr('Non valutabile sui percorsi', 'Not assessable along routes')]
    ]) {
      const item = node('li', text);
      item.style.setProperty('--route-color', styles[key].color);
      legend.append(item);
    }
    body.append(legend);

    const arcs = pair.explanatory_arcs.length ? pair.explanatory_arcs :
      [...new Set([...(pair.reference?.arcs || []), ...(pair.scenario?.arcs || [])])];
    if (!arcs.includes(edgeId)) edgeId = arcs[0] || '';
    if (edgeId) {
      const edge = data.edges[edgeId];
      const assessment = replay.edges[edgeId];
      const inspector = node('div', '', 'flood-access-inspector');
      inspector.append(labeledSelect(
        pair.explanatory_arcs.length ? tr('Tratto che spiega l’esito', 'Segment explaining the outcome') :
          tr('Ispeziona un tratto del percorso', 'Inspect a route segment'),
        arcs.map(id => [id, (data.edges[id].name || tr('Strada senza nome', 'Unnamed road')) + ' · ' + id]),
        edgeId, id => setSegment(id, true)));
      const zoom = node('button', tr('Inquadra tratto', 'Zoom to segment'));
      zoom.type = 'button';
      zoom.onclick = () => setSegment(edgeId, true);
      inspector.append(zoom);
      const coverage = edge.coverage;
      const percent = value => number(value * 100, 1) + '%';
      const maximum = edge.max_depth_m === null ? '—' : number(edge.max_depth_m, 3) + ' m';
      body.append(inspector, node('p', stateName(assessment.state) + ' · ' + reasonName(assessment.reason) +
        tr(' · Massimo al suolo ', ' · Ground maximum ') + maximum +
        (edge.max_depth_cell ? tr(' · Cella [riga, colonna] ', ' · Cell [row, column] ') + edge.max_depth_cell.join(', ') : '') +
        tr(' · Valido ', ' · Valid ') + percent(coverage.valid) + ' · NoData ' + percent(coverage.nodata) +
        tr(' · Fuori griglia ', ' · Outside grid ') + percent(coverage.outside), 'flood-access-note'));
    }

    const provenance = node('details');
    provenance.append(node('summary', tr('Prodotto, copertura e artefatti', 'Product, coverage and artefacts')));
    const h = data.hydraulic;
    provenance.append(
      node('p', 'HMC–REFlEx · ' + tr('profondità massima (m) sulla finestra ', 'window maximum depth (m) ') +
        h.valid_from + ' → ' + h.valid_until + '. ' +
        tr('Scenario statico senza orari delle interruzioni. I run positivi usano un impulso di pioggia sintetico.',
          'Static scenario without closure times. The positive-depth runs use a synthetic rainfall pulse.')),
      node('p', h.job_id + ' · ' + h.grid.crs + ' · ' + h.grid.shape.join(' × ') + ' · NoData ' +
        h.nodata + ' · SHA-256 ' + h.layer.sha256),
      node('p', tr('Massimo delle celle attraversate per una lunghezza positiva. Tratti strutturali non valutabili. ' +
        'Per gli altri, un massimo valido ≥ soglia interrompe il tratto. La percorribilità richiede copertura completa sotto soglia.',
        'Maximum of cells intersected along a positive length. Structural segments are not assessable. ' +
        'Elsewhere, a valid maximum ≥ threshold closes the segment. Passability requires full coverage below the threshold.')),
      node('p', tr('Metrica: lunghezza stradale sullo stesso grafo diretto. Aggancio al nodo più vicino entro 150 m. ' +
        'Accessi finali, completezza della rete e operatività dei presidi restano da verificare.',
        'Metric: road distance on the same directed graph. Nearest-node snaps within 150 m. ' +
        'Final access links, network completeness and facility operation remain unverified.')),
      node('p', data.network.attribution + ' · ' + data.network.license + ' · ' +
        Object.entries(counts.pairs).map(([key, value]) => value + ' ' + outcome(key)).join(' / '))
    );
    const links = node('div', '', 'flood-access-links');
    for (const [file, label] of [
      ['maximum-depth.tif', tr('Raster di profondità', 'Depth raster')],
      ['hydraulic.json', tr('Metadati idraulici', 'Hydraulic metadata')],
      ['road-depth.json', tr('Copertura per arco', 'Coverage per edge')],
      ['routing.json', tr('Esiti e percorsi', 'Outcomes and routes')]
    ]) {
      const link = node('a', label);
      link.href = '/assets/flood-access/' + h.job_id + '/' + file;
      link.download = h.job_id + '-' + file;
      links.append(link);
    }
    provenance.append(links);
    body.append(provenance);
    if (activeLabel) {
      [...body.querySelectorAll('select[aria-label]')].find(
        select => select.getAttribute('aria-label') === activeLabel
      )?.focus({preventScroll: true});
    }

    const coords = [origin.point, destination.point].map(latLng);
    groups.forEach((group, i) => {
      const addPath = (path, style) => {
        if (!path?.arcs.length) return;
        const edges = path.arcs.map(id => data.edges[id]);
        const points = [latLng(edges[0].a), ...edges.map(edge => latLng(edge.b))];
        if (i === 0) coords.push(...points);
        L.polyline(points, {...styles[style], pane: 'floodAccess', interactive: false}).addTo(group);
      };
      addPath(pair.reference, 'reference');
      addPath(pair.scenario, 'scenario');
      addPath(pair.possible, 'possible');
      for (const id of pair.explanatory_arcs) {
        const edge = data.edges[id];
        L.polyline([latLng(edge.a), latLng(edge.b)], {...styles[replay.edges[id].state], pane: 'floodAccess'})
          .addTo(group).on('click', () => setSegment(id));
      }
      if (edgeId) {
        const edge = data.edges[edgeId];
        L.polyline([latLng(edge.a), latLng(edge.b)], {color: '#fff', weight: 3, dashArray: '2 5',
          pane: 'floodAccess', interactive: false}).addTo(group);
      }
      for (const [endpoint, color] of [[origin, '#d9caff'], [destination, '#5ce6c9']]) {
        L.circleMarker(latLng(endpoint.point), {radius: 7, fillColor: color, fillOpacity: 1, color: '#152638',
          weight: 2, pane: 'floodAccess'}).addTo(group).bindTooltip(node('span', endpoint.name), {permanent: true});
        if (endpoint.snapped_point) L.polyline([latLng(endpoint.point), latLng(endpoint.snapped_point)], {
          pane: 'floodAccess', color, weight: 2, dashArray: '2 4', interactive: false
        }).addTo(group);
      }
    });
    if (fit) requestAnimationFrame(() => {
      if (!panel.open || !data || originId !== pair.origin || destinationId !== pair.destination) return;
      maps.forEach(map => {
        if (map.getSize().x > 0) map.fitBounds(coords, {padding: [45, 45], maxZoom: 16, animate: false});
      });
    });
  }

  async function load() {
    request?.abort();
    if (!panel.open || !product) return render();
    if (data) return render(true);
    const controller = new AbortController();
    request = controller;
    const selected = product;
    notice = '';
    render();
    try {
      const response = await fetch('/assets/flood-access/' + selected.id + '/view.json', {signal: controller.signal});
      if (!response.ok) throw new Error('unavailable');
      const raw = await response.text();
      if (raw.length > 4 * 1024 * 1024) throw new Error('invalid');
      const value = JSON.parse(raw);
      if (value.schema !== 'hazardia.flood-access-view/1' || value.hydraulic.job_id !== selected.id ||
          value.hydraulic.catalog_sha256 !== selected.reference.sha256 ||
          value.hydraulic.layer.sha256 !== selected.reference.sha256 || value.hydraulic.support !== 'window_maximum') {
        throw new Error('invalid');
      }
      if (controller.signal.aborted) return;
      data = value;
      replayIndex = 0;
      chooseDefault();
      render(true);
    } catch (error) {
      if (controller.signal.aborted) return;
      data = null;
      notice = error.message === 'unavailable' ?
        tr('Replay di accessibilità non disponibile per questo prodotto.', 'No accessibility replay is available for this product.') :
        tr('Replay non leggibile o non coerente con il prodotto selezionato.', 'The replay is unreadable or does not match the selected product.');
      render();
    }
  }

  panel.ontoggle = () => {
    if (!panel.open) request?.abort();
    requestAnimationFrame(() => maps.forEach(map => map.invalidateSize({pan: false})));
    void load();
  };
  document.addEventListener('hazardia-language', () => render());
  return {
    setScenario(scenario) {
      const next = scenario && /^job-[a-f0-9]{32}$/.test(scenario.id) ? scenario : null;
      if (next?.id === product?.id && next?.reference.sha256 === product?.reference.sha256) return;
      request?.abort();
      product = next;
      data = null;
      panel.hidden = !product;
      requestAnimationFrame(() => maps.forEach(map => map.invalidateSize({pan: false})));
      if (product && new URLSearchParams(location.search).get('flood-access') === '1') panel.open = true;
      void load();
    }
  };
}
