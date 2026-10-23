# Caricamento immagini: correzioni e misure

La mappa conserva le immagini riuscite e non passa più automaticamente al piccolo ritaglio Sentinel dopo due errori. I caricamenti delle tessere sono limitati a quattro per documento, condivisi fra mappe e fonti; le immagini di viste abbandonate vengono cancellate dalla coda. Cache nella VM e richieste HTTP del browser conservano gli stessi URL, TTL e validator: niente parametri casuali di retry che aggirino la cache. Nessuna ricompressione o riduzione della risoluzione richiesta.

Run `imagery-loading-20261023`, base `6381777` con modifiche documentali preesistenti conservate. VM unica6vCPU/16GiB/disco19GiB. Reviewer Codex self-check.

## Diagnosi verificata

1. Il vecchio controller sostituiva l’intero sfondo dopo due errori di tessera, passando infine al ritaglio locale. Quel ritaglio copre soltanto42,30–42,40N/13,32–13,44E: il grande vuoto dello screenshot non rappresenta semplicemente un’immagine che deve ancora arrivare. Il testo dello screenshot e il selettore confermano che era attivo il ritaglio, non uno sfondo geografico completo.
2. La cache riservava il massimo payload per ogni richiesta simultanea e poteva rispondere `CACHE_FULL` mentre un’altra richiesta occupava temporaneamente lo spazio. Nella riproduzione controllata con sorgente sintetica: prima2successi/2rifiuti, dopo4successi/0rifiuti, stesso limite1.500.000byte, nessun superamento e riserve finali0. Non è un benchmark della rete esterna.
3. Le tessere di zoom abbandonati e i vecchi retry a800/2200/5000ms potevano continuare a occupare richieste, mentre il proxy ritarda15secondi i retry dopo un errore della fonte. Le mappe di confronto moltiplicavano i caricamenti. La nuova coda usa immagini native e ammissione equa fra layer/mappe; nessun Blob o doppia copia dei raster.

## Correzioni

- Controller non bloccato da una richiesta di stato prima della prima immagine. Mantiene immagini parziali e ortofoto già riuscite; se serve aggiunge OSM sotto alle immagini. Il ritaglio offline è solo una scelta esplicita. Restano zoom, centro, meteo, ora e geometrie.
- Coda client condivisa≤4; rimozione delle richieste non ancora partite, cancellazione delle immagini abbandonate, gestione sia `tileunload` sia `tileabort` di Leaflet. Rimossi i vecchi retry con URL casuali dallo studio. Applicata a Monitoraggio, studio FIRE/peer e pagine cartografiche legacy che usavano gli stessi sfondi.
- Cache: attesa limitata delle riserve concorrenti, payload massimo del provider invece del massimo generico (satellite512KiB, ortofoto1MiB, OSM512KiB). Cache disco di consultazione **64MiB per fonte**: satellite/ortofoto prima16MiB, OSM prima32MiB. Massimo totale di questi tre archivi192MiB, senza aumentare il disco della VM o la RAM assegnata.
- Restano inalterati limiti di traffico16MiB/ora e32MiB/giorno per fonte, sorgenti, TTL, revalidazione304, attribuzioni, divieto di prefetch/esportazione massiva e conservazione delle tessere fresche. Contatori persistenti non azzerati; RAM cache invariata. I limiti reali continuano a produrre un errore esplicito.

Il nuovo helper ha inizialmente mostrato uno stallo dopo zoom rapidi: Leaflet annulla alcune tessere con `tileabort`, senza il solo `tileunload` previsto dalla prima versione. Negativo conservato in `client-stall-initial.json`; corretto il rilascio della coda e aggiunto un test che riproduce questo evento. Un avviso rimasto dopo tessere successivamente riuscite è stato corretto tracciando gli errori delle tessere correnti.

## Verifiche ed esiti

| Verifica | Esito | Risultato |
|---|---|---|
| Riproduzione rifiuti transitori cache | PASS |2/4→4/4 richieste riuscite nello stesso fixture controllato |
| Cache persistente, TTL,304, no-store, quota e limite disco veri | PASS |11test cache, inclusi3nuovi, nella suite81testVM |
| Coda equa/cancellazione/rilascio una volta | PASS |15check JS |
| Adapter immagini e aborti Leaflet | PASS |7check JS, stallo iniziale corretto |
| Fallback preserva tessere e non sceglie ritaglio automaticamente | PASS |17check JS |
| Regressione meteo | PASS |16check viewport e6013check render |
| Vista ampia e zoom rapidi IAB | PASS |2560×1100, zoom fino14,110/110 immagini caricate, coda0, picco4, modalità satellite conservata |
| Confronto FIRE esistente | PASS |due mappe visibili1280×720, tessere presenti caricate, coda comune0, terza mappa piano nascosta, nessun errore console |
| Integrità scientifica e workspace | PASS |311file invariati,95job identici, nessun calcolo scientifico avviato |
| Fonti esterne sempre veloci/disponibili | BLOCKED come garanzia |la disponibilità esterna e le quote non sono eliminabili con più CPU |
| Benchmark indipendente freddo, Safari reale, dispositivi fisici/soak | NOT RUN |non dedotti dalla singola sessione IAB |

Nella sessione ampia sono conservate148risorse tessera: p50~170ms,p95~322ms, massimo463ms. **Sono durate delle richieste già avviate, escludono l’attesa della coda e non sono il tempo totale per riempire la vista.** p95 intervallo requestAnimationFrame~17,6ms, campione correlato; non certificazione di fluidità su tutti i dispositivi. Il primo campione diagnostico a501ms aveva già tessere visibili, ma il campionatore è a500ms e il percorso era caldo: niente claim di avvio freddo sotto mezzo secondo.

Nel guest,30letture sequenziali per ciascuna tessera già consultata: p95satellite~0,54ms eortofoto~0,64ms, tutteHTTP200. È il riuso della cache locale, non una misura della velocità del fornitore. Durante le prove i contatori fonte sono cresciuti di624.180byte per satellite e1.113.472byte per ortofoto; OSM invariato. Nessuna pulizia di dati scientifici né nuova installazione, fornitore commerciale o incremento risorse VM.

## Comandi e tracciabilità

Nella VM, da `~/hazardia-runtime/app`:

```sh
PYTHONPATH=src:tests/unit:tests/web ../core-env/bin/python -m unittest test_consultation_cache test_maps test_osm_tiles test_regional_satellite test_map_navigation test_bootstrap test_traffic test_recent_imagery test_radar_service test_map_weather test_fire_workspace test_fire_cases test_observed_layers
```

Client di sviluppo: `node tests/browser/{basemap-state,tile-queue,scheduled-tiles,viewport-weather-state,weather-render-plan}.mjs`, eseguiti singolarmente. Nessun nuovo pacchetto. Gli URL delle immagini restano quelli del proxy VM.

Raw e preregistrazione: `experiments/runs/imagery-loading-20261023/` e `~/hazardia-runtime/runs/imagery-loading-20261023/`; estratto `reports/imagery-loading/verification.json`. Screenshot locali nella cartella report. I risultati dei simulatori, le forzanti, il decision engine, i worker e i gate scientifici M5–M7 restano invariati. Per Safari occorre ricaricare la pagina per usare il nuovo codice; eventuali ulteriori lentezze vanno misurate distinguendo attesa fonte, cache, coda e rendering.
