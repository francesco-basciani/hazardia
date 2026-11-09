export function mountRhineDemo({tr, el, svg, number, relative, charts, load, siteNames, pauseReplay}) {
  const button = el('button');
  button.type = 'button';
  button.setAttribute('aria-haspopup', 'dialog');
  document.querySelector('.rhine-graph-key').append(button);

  const dialog = el('dialog', '', 'rhine-demo');
  const header = el('header');
  const heading = el('h2');
  heading.id = 'rhine-demo-title';
  dialog.setAttribute('aria-labelledby', heading.id);
  const close = el('button');
  close.type = 'button';
  close.onclick = () => dialog.close();
  header.append(heading, close);
  const body = el('div', '', 'rhine-demo-body');
  dialog.append(header, body);
  document.body.append(dialog);

  let data, loading, full = false, redraw;
  const resize = new ResizeObserver(() => { if (dialog.open) redraw?.(); });
  resize.observe(body);

  function render() {
    button.textContent = tr('Grafico · 2 casse', 'Chart · 2 polders');
    heading.textContent = tr('Alto Reno · Manuale e ottimizzato', 'Upper Rhine · Manual and optimised');
    close.textContent = tr('Chiudi', 'Close');
    if (!dialog.open || !data) return;
    const {series, candidates} = data;
    const [reference, manual, optimised] = series;
    const delta = manual.peak - optimised.peak;
    const volume = plan => plan.sites.reduce((sum, site) =>
      sum + site.intake.reduce((total, rate) => total + rate, 0) * .0036, 0);
    const [manualVolume, optimisedVolume] = [volume(manual), volume(optimised)];
    const names = [
      tr('Senza interventi', 'No retention'),
      tr('Miglior piano manuale', 'Best manual plan'),
      tr('Piano ottimizzato', 'Optimised plan')
    ];
    const subtitle = el('p', tr(
      `Stessa piena di riferimento. Ogni piano può usare due delle tre casse disponibili, con i limiti propri di ciascuna opera. Il manuale è il migliore fra ${candidates} combinazioni di siti e finestre fisse. L’obiettivo è ridurre il picco a Maxau.`,
      `Same reference flood. Each plan can use two of the three available polders, subject to each facility’s limits. The manual plan is the best of ${candidates} combinations of sites and fixed windows. The objective is to lower the peak at Maxau.`));
    const result = el('p', tr('Riduzione del picco rispetto al manuale', 'Peak reduction versus manual'), 'rhine-demo-result');
    result.prepend(el('strong', `${number(delta, 1)} m³/s · ${number(100 * delta / manual.peak, 1)}%`));
    const legend = el('ul', '', 'rhine-demo-legend');
    series.forEach((plan, index) => {
      const item = el('li');
      item.style.setProperty('--curve-colour', charts[index]);
      item.append(el('span', names[index]), el('strong', number(plan.peak, 1) + ' m³/s'),
        el('small', tr('Picco a ', 'Peak at ') + relative(plan.q.indexOf(plan.peak))));
      if (index) item.append(el('small', siteNames(plan)));
      legend.append(item);
    });
    const toolbar = el('div', '', 'rhine-demo-chart-bar');
    const axis = el('strong', tr('Portata a Maxau · m³/s', 'Discharge at Maxau · m³/s'));
    const toggle = el('button', full ? tr('Torna al picco', 'Focus on peak') : tr('Intera piena', 'Full flood'));
    toggle.type = 'button';
    toolbar.append(axis, toggle);
    const chart = svg('svg', {role:'img', 'aria-label':tr('Idrogrammi dei tre scenari con i picchi evidenziati',
      'Discharge curves for the three scenarios with peaks marked')});
    const difference = el('p', tr(
      `Volume prelevato durante la piena: ${number(manualVolume, 2)} milioni di m³ nel manuale e ${number(optimisedVolume, 2)} nell’ottimizzato (${number(100 * (manualVolume - optimisedVolume) / manualVolume, 1)}% in meno).`,
      `Volume diverted during the flood: ${number(manualVolume, 2)} million m³ in the manual plan and ${number(optimisedVolume, 2)} in the optimised plan (${number(100 * (manualVolume - optimisedVolume) / manualVolume, 1)}% less).`));
    const limit = el('p', tr(
      'Il manuale usa finestre fisse. L’ottimizzatore modula i prelievi ora per ora: la sua portata può essere più alta in alcune ore. Il modello sperimentale stima la portata a Maxau. La piena dell’Atlante visibile sulla mappa è un riferimento comune.',
      'The manual plan uses fixed windows. The optimiser varies hourly intake, so its discharge can be higher in some hours. The experimental model estimates discharge at Maxau. The Atlas flood extent on the map is a shared reference.'), 'rhine-demo-note');

    redraw = () => {
      const width = Math.floor(chart.clientWidth);
      if (!width) return;
      const height = 242, left = 53, right = width - 12, bottom = height - 30;
      const last = reference.q.length - 1;
      const peaks = series.map(plan => plan.q.indexOf(plan.peak));
      const start = full ? 0 : Math.max(0, Math.floor((Math.min(...peaks) - 5) / 5) * 5);
      const end = full ? last : Math.min(last, Math.ceil((Math.max(...peaks) + 8) / 5) * 5);
      const window = series.map(plan => plan.q.slice(start, end + 1));
      const tick = full ? 500 : 250;
      const low = Math.floor(Math.min(...window.flat()) / tick) * tick;
      const high = Math.ceil(Math.max(...window.flat()) / tick) * tick;
      const x = t => left + (right - left) * (t - start) / (end - start);
      const y = q => bottom - (bottom - 12) * (q - low) / (high - low);
      const label = (value, attributes) => {
        const node = svg('text', attributes);
        node.textContent = value;
        chart.append(node);
      };
      chart.setAttribute('viewBox', `0 0 ${width} ${height}`);
      chart.replaceChildren();
      for (let q = low; q <= high; q += tick) {
        chart.append(svg('line', {x1:left, x2:right, y1:y(q), y2:y(q), stroke:'#385363'}));
        label(number(q), {x:left - 7, y:y(q) + 4, 'text-anchor':'end'});
      }
      const interval = full ? (width < 540 ? 48 : 24) : (width < 430 ? 10 : 5);
      for (let t = Math.ceil(start / interval) * interval; t <= end; t += interval) {
        label(relative(t), {x:x(t), y:bottom + 19, 'text-anchor':t === end ? 'end' : 'middle'});
      }
      window.forEach((curve, index) => {
        const points = curve.map((q, i) => `${x(start + i).toFixed(1)},${y(q).toFixed(1)}`);
        chart.append(svg('polyline', {points:points.join(' '), stroke:charts[index], fill:'none',
          'stroke-width':index ? 3 : 2, ...(index ? {} : {'stroke-dasharray':'5 4'})}));
      });
      series.forEach((plan, index) => chart.append(svg('circle', {
        cx:x(peaks[index]), cy:y(plan.peak), r:5, fill:charts[index], stroke:'#102332', 'stroke-width':2
      })));
    };
    toggle.onclick = () => {
      full = !full;
      toggle.textContent = full ? tr('Torna al picco', 'Focus on peak') : tr('Intera piena', 'Full flood');
      redraw();
    };
    body.replaceChildren(subtitle, result, legend, toolbar, chart, difference, limit);
    redraw();
  }

  button.onclick = async () => {
    pauseReplay();
    dialog.showModal();
    if (data) { render(); return; }
    if (loading) return;
    body.textContent = tr('Caricamento del confronto…', 'Loading comparison…');
    loading = true;
    try { data = await load(); render(); }
    catch { body.textContent = tr('Confronto non disponibile. Chiudi e riapri per riprovare.',
      'Comparison unavailable. Close and reopen to retry.'); }
    finally { loading = false; }
  };
  document.addEventListener('hazardia-language', render);
  render();
}
