# Copertura del terreno e squadre nelle finestre degli scenari

Run `scenario-drop-coverage-20261017`, base `bed2f94fde68eed96e9264cfd229a1b67cd720f1` + modifiche; SHA consegna nel commit Git/PUBLICATION.json. Reviewer Codex self-check.

## Cause verificate

**PASS diagnosi:** lo stato utente rev59 contiene3 scenari con innesco comune fuori dalla griglia fisica disponibile; alcuni interventi sono fuori copertura e alcune linee superano anche il limite esistente di2km. Le fotografie satellitari non delimitavano il dominio del modello. L'API rifiutava il caso con OUTSIDE_COVERAGE dopo la preparazione, senza creare job. Il numero3 non è la causa.

**PASS diagnosi:** il gestore pointerup confrontava soltanto il rettangolo di #map. Le altre finestre ricevevano solo annotazioni non trascinabili; quindi un rilascio su di esse veniva ignorato. Era un difetto della UI.

## Correzioni eseguite

**PASS** il rilascio di una categoria determina mappa e scenario destinatari e proietta le coordinate con quella mappa. La risorsa viene aggiunta soltanto al destinatario; gli inneschi rimangono comuni. Le squadre sulle altre finestre sono trascinabili senza prima premere Modifica. Clic sull'icona apre lo scenario e l'ispettore per linea/area/orario; trascinare sospende la timeline. Per piccoli schermi resta disponibile selezione categoria + tocco sulla mappa destinataria. Riferimento senza interventi preservato; un inserimento esplicito nel riferimento crea un'alternativa, senza ereditare squadre.

**PASS** endpoint locale GET /api/firelab/coverage, derivato dalla griglia reale e proiettato nell'ambiente geospaziale già installato nella VM. Cache vincolata allo SHA256 di grid.json; nessuna nuova libreria o sorgente. Il poligono rappresenta l'interno a margine2celle richiesto dal preparatore: EPSG:32633,1024×1024 celle30m, bordo densificato32 punti per lato. Serve per preflight cartografico, mentre la verifica proiettata nel preparatore resta autoritativa. Non certifica assenza di nodata o validità operativa del combustibile.

**PASS** confine tratteggiato su ogni finestra, messaggio conciso con dettagli per scenario e pulsante Mostra area simulabile. Il pulsante cambia solo l'inquadratura. I calcoli con inneschi/geometrie fuori copertura vengono bloccati prima dell'invio; le intestazioni segnalano il problema invece di Pronto da calcolare. Controllo preliminare anche delle linee oltre2km. Il backend conserva la verifica indipendente e l'errore è spiegato in italiano. Nessun punto spostato, nessuna geometria ritagliata automaticamente.

**BLOCKED per il caso attuale:** il terreno è ancora il dominio di ricerca già preparato nell'area aquilana, circa30,6km per lato utili. La zona scelta dall'utente richiede un nuovo dominio, relativa copertura delle forzanti e verifica degli input. Non è stato introdotto un generatore di terreno globale né estesa la copertura con DEM o meteo inventati. Il vincolo è dei dati preparati, non una limitazione territoriale dell'architettura generica. Anche dentro il dominio, un fronte che raggiunge il margine produce DOMAIN_EXIT, non una previsione completa ritagliata.

## Prove e comandi

Tutto il calcolo nel runtime UTM Ubuntu22.04 ARM64 esistente; browser QA Chrome155 su Mac solo client,375/768/1440. Riavvio servizio dopo verifica zero job QUEUED/RUNNING. Nessuna installazione, acquisizione geospaziale o aumento risorse. Il meteo mantiene cache e quote esistenti.

**PASS13 test unitari** nella VM:

```sh
PYTHONPATH=src ../core-env/bin/python -m unittest discover -s tests/unit -p test_firelab.py -v
```

**PASS18 verifiche browser dedicate +33 regressioni=51**,6axe senza violazioni rilevate. Script tests/browser/scenario-drop-coverage.cjs e tests/browser/clean-authoring.cjs, con HAZARDIA_PLAYWRIGHT_PATH, HAZARDIA_BROWSER_EXECUTABLE e HAZARDIA_AXE_PATH configurati come nelle precedenti prove. Il test dedicato finale usa una fixture isolata riproducibile di3 scenari, mai scritta nel workspace reale; i primi run riproducevano il workspace realmente segnalato. Verificati drop su seconda/terza mappa, spostamento di una squadra già presente, innesco comune anche aggiunto sulle altre mappe, inserimento tramite selezione+tocco/click, assenza di risorse nascoste, layout e copertura. Workspace reale prima/dopo identico.30 feedback overlay/3mappe: p50 **16,60ms**, p95 **30,00ms**, max **37,00ms**; costo interazione locale, non benchmark fisico/FPS.

**PASS3 job nativi reali di3ore**,12frame ciascuno a900s, seed1729,2realizzazioni, innesco42.35/13.38, replay storico2024-07-13T13Z, moisture manuale10%, combustibile uniforme legacy5. Input inviato a POST /api/firelab/scenario nella VM, poi polling GET /api/firelab/<job>. Per gli interventi: fuel_removal da minuto0, linea [[42.3498,13.3794],[42.3502,13.3806]], orologio comune[0]. Dati/input/risultati completi e script congelato nella directory raw; richieste/prodotti conservati anche nella VM.

| Caso | Job | Stato | Celle combustibile modificate | Area media finale ha |
|---|---|---|---:|---:|
| Nessun intervento | job-829b63e742164f69ad38f7ab42cefaa4 | PASS/SUCCEEDED | 0 |18,675|
| Squadra a terra | job-d86aeee699d647e7aa3350a769815932 | PASS/SUCCEEDED |5|0,09|
| Canadair | job-dd3f062f03f04a14bcd7cbcf7933e80f | PASS/SUCCEEDED |5|0,09|

La stessa sottrazione ideale di combustibile produce lo stesso risultato per le due categorie: **non dimostra efficacia reale né differenze fra squadre e Canadair**. L'intervento è immediato vicino all'innesco, senza modellazione di arrivo/logistica/capacità. Questi numeri provano esecuzione e consumo dell'input, non riduzione di rischio qualificata. La prova negativa fuori dominio riproduce OUTSIDE_COVERAGE e verifica assenza di nuovi job. Tutti i job di prova sono separati dai3scenari utente, non caricati nella dashboard come esempi.

**FAIL preservato:** prima verifica browser controllava l'avviso prima della risposta asincrona di copertura; aggiornato il probe per attendere la disponibilità del dato. Nessun artefatto sovrascritto. **NOT RUN:** nuovo territorio selezionato, nuovo confronto72h/forecast live, dispositivi touch fisici, soaks/skill/validazione operativa. **BLOCKED** fullM5–M7 invariati: fuel/moisture, efficacia/logistica e qualificazione.

Raw `experiments/runs/scenario-drop-coverage-20261017`: coverage.json, unit.log, final-release/verification.json e screenshot, regression/verification.json, native/verification.json, native-probe.py, source-manifest.json. Replica dei dati della prova in VM `~/hazardia-runtime/runs/scenario-drop-coverage-20261017`; artifact originali immutati. Prossimo incremento utile: preparazione del territorio scelto, copertura meteorologica corrispondente e verifica fisica, preservando gli input utente.
