# Interfaccia orientata alla mappa —19ottobre2026

Richiesta utente: riesaminare `https://wildfire.geospace.es/operational-map` e rifare lo stile pulito prendendone spunto, con interesse per OpenStreetMap. Incremento di presentazione FR24–28/QR11–14, nessuna sostituzione dei modelli o nuovo hazard. Run `clean-room-20261019`, parent `1940037` + modifiche, SHA finale in Git/PUBLICATION.json. Reviewer stesso agente Codex.

## Modifiche

Riferimento esaminato nel browser: navigazione laterale bianca, mappa centrale, pannello dei livelli separato, gerarchia tipografica sobria. Il sito dichiara EFFIS/hotspot/modelli: non ne abbiamo verificato l’accuratezza né copiato dati, logo o asset. In HAZARDIA: navigazione laterale desktop, compatta superiore mobile; palette chiara con accento verde petrolio; ricerca sopra la mappa; controlli Centra/Configura/Criticità/Livelli uniformi44px; meteo e catalogo OSM raggruppati nel pannello laterale desktop o sotto la mappa sui formati stretti. Date, fonti e limiti restano accessibili in sezioni apribili. Avviso di ricerca sempre visibile, dettagli espandibili. Stile condiviso con lo studio, scenari e controlli preesistenti conservati. Mappe mai zoomate dallo scroll della pagina, proprietà Leaflet invariata. La navigazione aggiorna il parametro `view` e mantiene il caso selezionato anche ricaricando.

Nuovo sfondo opzionale **OpenStreetMap · cartografia stradale** nel Monitoraggio, oltre al satellite e ritaglio offline esistenti. Nomi nativi incorporati nelle tessere; i nomi GeoNames aggiuntivi vengono soppressi su OSM per evitare duplicazioni. Il controllo dei nomi aggiuntivi non può cancellare le etichette incorporate nelle tessere. La visualizzazione non aumenta la risoluzione del simulatore.

Consultazione OSM attraverso la VM, endpoint fissoHTTPS identificato con User-Agent HAZARDIA e riferimento all’origine locale, cachePNG7giorni, richieste condizionaliETag dopo scadenza, limite32MiB complessivi/cache, payload1MiB, quattro slot e sedici ammissioni massime, coordinate4–19 controllate. Nessun prefetch, archivio offline OSM, scansione geografica o nuova dipendenza. Attribution visibile. Referrer-Policy same-origin consente il riferimento alla VM per il proxy; non invia referrer ai siti esterni. Sfondo stradale usato solo per consultazione, nessuna inferenza di percorribilità/accessibilità o sicurezza.

## Verifiche effettive

| Attività | Esito | Evidenza |
|---|---|---|
| Riferimento esterno | PASS | Esame visuale IAB del19ottobre; webtext non accessibile, browser con mappa effettivamente caricata |
| Monitoraggio1440/768/375, assenza overflow, mappa visibile,7variabili,4pulsanti44px, tre sfondi | PASS | `layout-final.json`, tre record monitor e misureDOM reali |
| Studio incorporato1440/768/375, controlloRiproduci unico, mappe con altezza limitata | PASS | tre record studio:660/460/460px, nessun overflow. Prima fase di caricamento; non prova di nuovi risultati fisici |
| Pannello livelli nascondi/ripristina, configurazione, criticità | PASS | `ui-final.json`, interazioni effettive IAB |
| OSM reale nell’area visualizzata | PASS |9/9tesserePNG caricate;269.883B acquisiti complessivi nella VM, cacheper7giorni. Nessuna scansione di zoom/aree per scaricare dati |
| Cache/identificazione, rifiuto coordinate invalide, errori immagine, budget | PASS |4unitariVM `test_osm_tiles.py`, fixture dichiarata |
| Proxy immagini preesistenti | PASS |5regressioniVM `test_maps.py` |
| ErroreHTTP non memorizzato per7giorni | PASS | coordinateinvalide400, Cache-Control no-cache;PNG200cacheprivata7giorni |
| Motori e dati utente | PASS con distinzione |145pin invariati, coda/contenuti conservati dopo riavvio; caso invariato. Workspace principale revisione118→119, contenuto identico; non dichiarare hash completo invariato |
| Nuovi calcoli fisici/solver e validazione del rischio | NOT RUN | UI non dimostra efficacia o accuratezza scientifica; fullM5–M7 BLOCKED invariati |
| Nuova matriceaxe, dispositivi fisici, FPS/p95/soak | NOT RUN | Verifica dimensionale browser non equivale a tutti i gateQR |

Backend riavviato tre volte solo a coda fisica vuota. Prima richiesta di riavvio rifiutata dal controllo perché erano attivi calcoli già avviati: attesi senza cancellarli. Nessun nuovo job fisico lanciato dalla verifica. Gli input e il codice scientifico non sono stati cambiati.

## Negativi conservati

- Primo viewport mobile dello studio: interazione fra `svh` e autoaltezzaiframe portava la mappa oltre3.600px. Corretto con altezza massima esplicita; ripetute misure finali. `layout-initial.json` conservato: il primo oracolo controllava solo larghezza/altezza minima ed era insufficiente; report finale usa anche limite superiore.
- Il menu meteo ereditava posizionamento assoluto nel dock. Corretto a flusso normale, margini e dimensioni coerenti.
- Prima provaOSM4/9tessere: ammissione troppo stretta e cache delle risposte d’errore. Corretto breve accodamento limitato, cachelunga soltanto suiPNG200 e versioneURLclient aggiornata. Alla fine9/9realmente caricate, nessun risultato fittizio.
- Primo confronto completo workspace FAIL per la sola revisione118→119; confronto dei contenuti PASS. Recordoriginario in `runtime-verification.log`, nessuna sovrascrittura dello stato dell’utente.
- Harnessbrowser: accesso diretto al documentoframe non supportato dal read-onlyscope, corretto con frameLocator; cattura screenshot transitoria non disponibile, osservazione successiva riuscita. Nessun errore di questi harness conteggiato come prova del modello.

## Ripetibilità e fonti

Nella VM, dalla directory `/home/hazardia/hazardia-runtime/app`, eseguire `PYTHONPATH=src /home/hazardia/hazardia-runtime/core-env/bin/python -m unittest discover -s tests/unit -p test_osm_tiles.py -v`; ripetere sostituendo il pattern con `test_maps.py`. BrowserQA tramite CUA, dimensioni1440×1000,768×1000,375×1000, poi ripristino dimensioni normali. Raw, log, screenshot e misure in `experiments/runs/clean-room-20261019`; riepilogo pubblicabile `reports/clean-room/verification.json`.

[Interfaccia di riferimento](https://wildfire.geospace.es/operational-map), [OSMF Tile Usage Policy](https://operations.osmfoundation.org/policies/tiles/), [attribuzione/licenza](https://www.openstreetmap.org/copyright). ServizioOSM best-effort, opzionale, senza SLA; nessuna capacità operativa dedotta dalle tessere. Scelta: riusare i controlli/eventi esistenti e introdurre uno strato di presentazione condiviso, invece di riscrivere simulatori, stato scenari o dipendenzeUI. Nessuna nuova infrastruttura di hosting o pubblicazione del servizio; normale sorgenteGitHub autorizzato. Nessuna conclusione H1–H3.
