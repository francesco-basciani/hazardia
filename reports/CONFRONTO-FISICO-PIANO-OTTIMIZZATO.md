# Confronto fisico del piano ottimizzato — 19 ottobre 2026

**Esito:** PASS integrazione fisica e confronto controllato; **FAIL riduzione del criterio prudenziale sulle priorità** in questo pilot. La superficie media simulata diminuisce dell’1,094%, ma il criterio prudenziale resta8. Il proxy ideale del solver prevedeva0: non sostituisce la verifica fisica. Nessuna efficacia operativa dimostrata.

Prova separata, disponibile nella VM: `/?view=results&case=optimized-physical-fonte-vetica-20261019&section=compare`. Contiene soltanto riferimento senza interventi e due squadre ipotetiche posizionate dal solver; nessun intervento nascosto. Il caso originario conserva i suoi due scenari e le due nuove esecuzioni richieste; workspace principale invariato. Nessun riordino o cancellazione dei casi precedenti.

## Esperimento preregistrato

Run `optimized-physical-20261019`, preregistrazione VM `runs/optimized-physical-20261019/preregister.json`, copia privata `experiments/runs/optimized-physical-20261019`. Base sorgenti pubblicata74748b8d1d52b5c635c316e8af00c7abef74adec; modifiche di audit/UI successive, nessuna modifica ai motori. Il checkout Git storico della VM riporta19f81dae+dirty: i manifest registrano anche gli hash dei sorgenti effettivi, non si presenta quel checkout come identico al commit di consegna. Versioni e metriche in `reports/optimized-physical/runtime.json`.

- Decisione verificata `decision-d22818d65e2f40b9987ee72f7643186e`, già calcolata nella sessione precedente: due squadre a terra, attive dal minuto60; aree ideali di rimozione combustibile proposte presso i due poligoni WorldCover esposti. Non inventario reale di squadre né efficacia calibrata.
- Confronto `ideal-native-ee81c4a50a2847288db97f06f9904d32`.
- A `job-c7999234d3e74a63845d3439a0eba08c`; B `job-4bcbd12dc46d4fa4b6d0ffa18142551c`.
- Riferimento congelato `job-ebe51c3a0c4b4832bda1ab3f117e6ec6`; stesso innesco ipotetico, DEM, WorldCover2021 riclassificato, griglia, seed1729,8realizzazioni, inizializzazione hFFMC da168h e calendario numerico A/B. Durata72h,288campioni a15min.
- Previsione meteorologica reale **precedentemente acquisita e congelata**, non nuova acquisizione né osservazioni dell’incendio. Inizio18/10/2026 ore18UTC; forcing distribuito vento/umidità combustibile aggiornato72volte. Meteo SHA256 `7740eac2e95ef7a59a8a0b4993e6e7b482d51b91804af7ab812e9802a9b0aa11` identico. Stessa stima da temperatura, umidità atmosferica, pioggia e vento; RH e moisture non equiparate.

Ipotesi fissata prima dei run: misurare differenze senza presumere beneficio; distinguere esaurimento dei fronti, crescita lenta, errore di replay e termine dell’orizzonte. Nessun tuning per ottenere una superficie minore o una durata maggiore.

## Risultati nativi

| Ora | A, superficie media ha | B, superficie media ha |
|---|---:|---:|
| +1h |0,57375|0,57375|
| +12h |103,48875|103,48875|
| +24h |338,91750|338,91750|
| +36h |631,91250|615,28500|
| +48h |962,30250|940,02750|
| +60h |1228,16250|1214,80875|
| +72h |1229,20875|1215,76500|

B−A finale =−13,44375ha, circa−1,094%;15.219celle con probabilità finale diversa. Prima differenza degli array a+24h45min: l’intervento è attivo da+1h, ma il fronte raggiunge più tardi le zone protette. I log nativi registrano200celle di combustibile modificate a+1h, nessuna modifica inA. Non si ridisegna il raster per fingere una riduzione.

Indice nativo prudenziale (massimo locale pesato)8→8: **nessun miglioramento di questo criterio**, nonostante il proxy di copertura prevedesse0. La componente media pesata scende6,61905→1,08254; il blend scelto robust=1 usa però il massimo, non questa media. Il selettore precedente dichiaraB migliore soltanto per lo spareggio sulla superficie. Corretto il testo dell’interfaccia per distinguere pareggio, miglioramento e peggioramento; non si deduce “abitati salvati”. La fascia di valutazione attorno agli asset e la copertura ideale non assicurano la stessa riduzione nel motore: questo disallineamento richiede qualificazione/ottimizzazione con feedback fisico.

## Perché sembra fermarsi

Nessun taglio a3h in questi run:288campioni e durata nativa259200s verificati. La crescita rallenta molto dopo circa+60h, ma l’ultima crescita campionata è a+71h45 inA e+72h inB. A fine previsione restano eventi di fronte in4/8realizzazioniA e3/8B (57/52eventi nella coda nativa): non sono fiamme osservate né una certificazione di incendio spento.

L’umidità stimata del combustibile passa da circa15–20% a+48h a36,6–100% a+60h. Il rallentamento coincide con questo cambiamento delle forzanti. È compatibile con il funzionamento del modello; non è un’attribuzione causale isolata alla pioggia, che richiederebbe un esperimento controllato aggiuntivo. Non si forza artificialmente la propagazione. A+72h termina la previsione configurata: evoluzione successiva NOT RUN. I casi legacy di3h conservano il proprio orizzonte e non diventano automaticamente previsioni più lunghe.

Sulle mappe ora si legge **fine previsione72h** e quanti membri conservano fronti; “fronti esauriti” viene mostrato soltanto quando il campo nativo lo indica. La riproduzione è verificata oltre+24h, pausa/seek e meteo comune. Corretto anche il disallineamento dei breakpoint: a larghezza iframe1188px gli strumenti rimanevano aperti prima delle mappe; ora sono apribili nello stesso breakpoint1200px della disposizione verticale.

## Registro delle verifiche

| Attività | Esito | Evidenza |
|---|---|---|
| Due run fisici completi; input e prodotti per checksum | PASS |10asset,1188artefatti; `verification.json`13assert |
| Identità terreno/meteo/semi/clock e sole risorse differenti | PASS |hash statici uguali;8seed worker uguali;288frameA uguali al riferimento |
| Interventi consumati e differenza degli array | PASS |200celle modificate a1h; primi3campioni pre1h identici; prima divergenza24,75h |
| Miglioramento indice prudenziale sulle priorità | FAIL |8→8 contro proxy previsto0; nessuna riduzione del criterio scelto |
| Superficie media minore nel singolo pilot | PASS descrittivo |−13,44375ha; non stima di efficacia o significatività |
| Stato finale e causa del limite temporale | PASS entro lo scope |72h completi, fronti residui, nessun successo oltre72h dichiarato |
| UI reale e responsive | PASS |3layout1440/768/375;2mappe, nessun overflow; play24,5→34,922h, pausa; stato72h/4–3membri |
| Formatter pareggio/perdita/beneficio e termine/esaurimento | PASS |12assert `tests/browser/fire-comparison-status.mjs`; sintassi moduliPASS |
| Integrità e isolamento | PASS |145pin invariati; esattamente2nuovi job; main invariata, due scenari originari preservati; case dedicato opt-in |
| Generatore caso e ID già presente | PASS |3assertVM: caso temporaneo a2scenari da prodotti reali, FileExistsError su ID esistente, caso reale invariato; `case-generator.json` |
| Nuovi p95/30ripetizioni,axe/FPS/soak, ulteriori orizzonti e ablation meteo | NOT RUN |nessuna conclusione da campioni singoli |
| Efficacia/logistica, calibrazione, inventari completi e fullM5–M7 | BLOCKED |qualifiche scientifiche e operative invariate |

A196,68s eB135,58s, picchiRSS campionati2,804/2,813GB. Prove singole, non benchmarkp95. StessaVM4vCPU/8GiB/19GiB; nessun restart, installazione, privilegio, acquisizione massiva, costo o deployment. WarningTBB versione non compatibile, layer parallelo disabilitato come nei run precedenti; worker fissato1thread, motore non alterato. Nessun dispatch.

Negativi di harness conservati: preregistrazione scritta correttamente ma stampa finale usava chiave `duration_seconds` assente; click iframe non affidabile e lettura attributo duranteplay in timeout, poi azioni/stato accessibile verificati; pannello strumenti troppo alto su desktop corretto prima del nuovo giro layout. Non sono fallimenti fisici né misure di runtime. Screenshot `experiments/runs/optimized-physical-20261019/iab-pair.png`.

## Ripetibilità e prossimo incremento

Nella VM, da `/home/hazardia/hazardia-runtime/app`:

```sh
PYTHONPATH=src PROJ_LIB=/usr/share/proj /home/hazardia/m0/reflex-env/bin/python tests/native/optimized_physical_audit.py --runtime /home/hazardia/hazardia-runtime --comparison ideal-native-ee81c4a50a2847288db97f06f9904d32 --out /tmp/optimized-pair-audit.json
PYTHONPATH=src /home/hazardia/hazardia-runtime/core-env/bin/python scripts/prepare_optimized_comparison_case.py --runtime /home/hazardia/hazardia-runtime --comparison ideal-native-ee81c4a50a2847288db97f06f9904d32 --case nuovo-confronto-ottimizzato
```

Il primo legge i prodotti reali già presenti; il secondo prepara un nuovo caso a due mappe senza nuovi run, rifiutando ID esistenti. Per ricalcolare dalla UI, dichiarare esplicitamente i mezzi, calcolare il posizionamento e usare **Calcola scenario ottimizzato e riferimento**. Produce nuovi job con input congelati, non aggiorna implicitamente il meteo storico.

Riepiloghi in `reports/optimized-physical`. Reviewer: stesso agenteCodex, self-check. Questo è un pilot a un solo seme con8membri, non8repliche indipendenti. Dopo gli interventi il percorso di consumo RNG può divergere; la concordanza iniziale e dei semi non prova numeri casuali per-cella accoppiati. Territorio/fuel/moisture e azioni restano non calibrati; inventario FonteVetica privo di ferrovie/cavi/sanità non significa assenza sul terreno. Prossimo incremento secondo piano: quantificare varianza e disallineamento proxy–fisica con feedback, ensemble e vincoli di efficacia/logistica prima di dichiarare protezione delle priorità. Nessuna estensione di dominio o sostituzione PROPAGATOR.
