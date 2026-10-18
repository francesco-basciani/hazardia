# Interventi durante il replay: finestra, tempo e significato dell’effetto

Run `midrun-edit-20261018`,18ottobre2026, base `93b67850c3b9d9b1f84a47b06159955b2d33858c`+dirty; SHA consegna in Git/PUBLICATION.json. Reviewer: Codex self-check. Tutti i calcoli e gli input rimangono nella VM UTM4vCPU/8GiB/19GiB. Nessun nuovo simulatore, dipendenza, servizio o dataset.

## Difetti riprodotti e correzioni

**FAIL prima:** replay della versione precedente su workspace QA isolato: trascinando un Canadair nella seconda mappa durante Riproduci, lo scenario destinatario si sposta nella prima finestra; il tempo continua fino al rilascio. Il corpo salvato contiene la squadra nel corretto scenario, ma la disposizione rende fuorviante il risultato. `browser-before/verification.json` conserva i due FAIL, stesso browser e risultati reali dichiarati, script precedente congelato nel raw.

**PASS dopo:** ordine delle finestre stabile rispetto all’ordine degli scenari, anche quando cambia quello selezionato. Pointerdown della palette mette subito in pausa e fissa l’attivazione al tempo effettivamente visibile, prima di trascinare. L’ispettore si apre per la squadra inserita anche nella mappa secondaria. A fine orizzonte il drop viene rifiutato con istruzione di tornare indietro: eliminato il precedente inserimento silenzioso al minuto4319 quando la timeline era a72ore.

Un secondo problema emerge dal percorso di calcolo precedente: un nuovo forecast spostava l’origine verso una futura ora valida. **PASS dopo:** se cambiano soltanto le risorse di un risultato FORECAST, `/api/firelab/branch` ricalcola con gli stessi inneschi, terreno, meteo, seme, durata e inizio del genitore, conservando la provenienza. Non acquisisce una nuova previsione né presenta il replay congelato come forecast fresco. Nuovi inneschi/parametri/meteo rimangono nel percorso esplicito di nuova preparazione. Le modifiche alle sole risorse preferiscono sempre il risultato proprio dello scenario: un test intermedio ha rilevato la selezione del risultato di un altro scenario compatibile, corretta prima della verifica finale.

Il calcolo rimane asincrono, con4preparazioni ammesse, preparatore seriale, timeout30s e worker nativi esistenti, cancellazione e errori classificati. Il tempo del replay resta fermo durante il calcolo, poi torna all’ora interrotta e riprende. Anche i comandi di calcolo riprendono dalla timeline corrente; non viene introdotto un checkpoint interno di PROPAGATOR.

## Canadair, barriera e area già raggiunta

I nuovi Canadair ed elicotteri usano per default le azioni **native PROPAGATOR** lungo una linea. Il selettore **Effetto nel modello** distingue questa scelta dalla precedente **barriera ideale con rimozione del combustibile**. Le configurazioni salvate mantengono il proprio effetto: nessuna conversione nascosta. Le aree poligonali richiedono esplicitamente fuel_removal, mentre le azioni native supportano linee. Disegnare un’area rende visibile questa selezione nell’ispettore.

Sorgente esaminata nella VM: `propagator/io/actions.py` e `core/propagator.py`, pin upstream invariati. CanadairAction rasterizza25punti percentuali sulla linea e22nel buffer; HelicopterAction22/20con dispersione deterministica; il binding nativo aggiunge umidità all’azione. Non è la simulazione di un volo, di una massa d’acqua o di spegnimento certificato. Le differenti parametrizzazioni upstream non qualificano l’efficacia reale delle categorie. Nessuna modifica al sorgente CIMA.

La superficie colorata deriva da `compute_fire_probability()`, media delle celle raggiunte nelle realizzazioni. È **area cumulativamente raggiunta**, non una mappa delle fiamme attive. La legenda ora lo dichiara. Un intervento può modificare l’evoluzione successiva; non deve cancellare la superficie precedentemente bruciata. Vedere una zona arancione “tagliata” non costituisce un criterio corretto di accettazione di questo prodotto. Una vera mappa di fiamme attive/spegnimento richiede prodotti e qualificazione ulteriori: non viene fabbricata dai PNG.

## Prova nativa preregistrata

Protocollo nel raw prima dei due run. Genitore FonteVetica `job-2065f1b44e7f422ab7098d9d3cfc8f04`,72ore dal18/10 ore13UTC, seme1729,2realizzazioni, terreno e forzanti precedenti congelati. Un’unica linea fissata a lat42,414 da lon13,72 a13,77, attiva al minuto1440. Una variante applica fuel_removal, l’altra CanadairAction nativa. Geometria fissata prima degli esiti; nessuna ottimizzazione per ottenere un miglioramento.

| Esito finale72h | Riferimento | Barriera ideale | Canadair nativo |
| --- | ---: | ---: | ---: |
| Superficie media raggiunta |2552,85ha|2431,125ha|2625,705ha|
| Celle con probabilità finale diversa dal riferimento |—|12905|12201|
| Celle di combustibile modificate a24h |0|140|0|
| Celle con azione sull’umidità a24h |0|0|418|
| Campioni prima di24h identici al genitore |—|95|95|

Job barriera `job-13bc29b4f45d451686d8cacb85c48e81`; Canadair `job-c2a47751b4284eaeb3594f9362c011d5`. PASS integrità di10asset e1188artefatti manifestati, inclusi576campioni e576PNG, stessi input non-plan, opzioni e validità. PASS la probabilità finale in entrambe le varianti conserva quella delle celle già raggiunte a24h. Audit `tests/native/fire_midrun_audit.py`, risultati pubblicabili in `reports/midrun-edit/native-audit.json`.

**Risultato negativo:** in questa prova il Canadair NON riduce la superficie finale rispetto al riferimento. Le due realizzazioni/seme unico, la geometria e il modello ideale non consentono una conclusione di efficacia o inefficacia reale. La variazione dell’evoluzione stocastica non garantisce un miglioramento monotono della superficie campionata. Il confronto resta riportato integralmente, senza ritoccare soglie, geometria o colori per farlo apparire migliore.

## Verifiche

PASS81controlli browser finali:14midrun (vero trascinamento con mouse durante il replay),23authoring,22ricalcolo e22clock;6axe senza violazioni su375/768/1440. Nei test browser i workspace e i trasporti di calcolo sono isolati: le risposte controllate non contano come fisica nativa. PASS2test VM di ammissione; PASS2preparazioni reali negative con seed diverso e linea fuori dominio, classificate SOURCE_MISMATCH/DOMAIN_SPAN senza nuovi job. FAIL intermedio del test di lineage corretto preferendo il proprio genitore. Tutti i tentativi sono conservati.

Configurazioni del workspace principale identiche (revisione84→85, solo contatore; origine dell’incremento non attribuita) e JSON del caso FonteVetica rev20 identico; nessuna prova precaricata o modifica automatica dei loro interventi. Un riavvio ordinario del backend a coda vuota, nessuna installazione o acquisizione esterna; pin CIMA verificati prima della consegna. Report dei gate scientifici precedenti invariati: BLOCKED efficacia/logistica, fuel/moisture, skill e fullM5–M7; NOT RUN nuovi ensemble/held-out/p95/FPS/soak/dispositivi fisici, checkpoint e modello di spegnimento attivo.

Comandi VM, da app con PYTHONPATH=src e PROJ_LIB=/usr/share/proj:

```sh
/home/hazardia/hazardia-runtime/core-env/bin/python -m unittest discover -s tests/unit -p test_fire_branch.py -v
/home/hazardia/m0/fire-env/bin/python tests/native/fire_midrun_audit.py /home/hazardia/hazardia-runtime job-2065f1b44e7f422ab7098d9d3cfc8f04 '{"barrier":"job-13bc29b4f45d451686d8cacb85c48e81","canadair":"job-c2a47751b4284eaeb3594f9362c011d5"}'
```

Nuovo replay via POST locale `/api/firelab/branch`, header X-Hazardia-Research:1, body `{job_id,input}`. Seguire preparation_id fino a SUCCEEDED, poi il job nativo. Il servizio verifica identità degli input e geometria prima di accodare. Su una nuova VM occorrono prima i dati/genitori reali; questi ID non sono fixture incluse nel repository.
