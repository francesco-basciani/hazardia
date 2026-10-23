# Mappa e Monitoraggio — incremento del 23 ottobre 2026

Run: `map-evolution-20261023`. Base applicativa: `bbb33922ea8b6ef10c3921e5974df0ec77e7126a` con modifiche documentali preesistenti preservate. Checkpoint locale precedente: `checkpoint-2026-10-23-prima-modifiche-strutturali`. Commit finale: cronologia Git e PUBLICATION.json. Reviewer: Codex self-check, non valutazione indipendente.

## Mandato e riferimento

Riferimento letto in locale: God's Eye View, commit `224745bd0aa1050f73bded841ecc467c3ad1ce7c`, MIT. Analizzati `src/maps/{imagery,terrain,controller,defaultSources}.js`, il catalogo fonti e i provider `weather`, `wind/gfs`, `wind/ifs`: separazione fra sorgente e visualizzazione, fallback esplicito, costruzione lazy del terreno, gestione delle risposte superate, pannelli richiudibili. Non importato il prodotto completo, i suoi servizi a pagamento o le sue decorazioni. L'architettura HAZARDIA, PROPAGATOR, HMC/Continuum, REFlEx, decision engine, safety checker, job e scenari restano quelli precedenti. MyDewetra resta un riferimento architetturale; nessun requisito di parità.

L'utente ha confermato di non possedere una licenza Esri e ha scelto le alternative gratuite. Tutto il backend, l'acquisizione e la trasformazione dei dati, anche dei tasselli cartografici e del terreno sperimentale, restano nella stessa VM. Rendering e interazione avvengono nel browser; nessuna acquisizione cartografica diretta dal browser verso fornitori esterni è stata introdotta.

## Risultati e limiti per requisito

| ID | Esito | Evidenza e comportamento |
|---|---|---|
| MAP-01 baseline | PASS | Browser IAB1280×720; mappa prima1254×450 a y214,8; fonte satellitare bloccata dal vecchio tetto cumulativo. Screenshot e baseline JSON privati. |
| MAP-02 navigazione | PASS | Ricerca esplicita via Open-Meteo Geocoding/GeoNames, coordinate globali, risultati disambiguati; Dakar/Senegal verificata con20tasselli e valori meteo reali. Ritorno all'area di studio e vista iniziale; rotella disabilitata. Nessuna copertura geografica dei dati scientifici dedotta dalla sola cartografia. |
| MAP-03 sfondi | PASS | EOX Sentinel-2 cloudless2024 e ortofoto Abruzzo2018–2019; OSM selezionabile, ritaglio offline distinto e limitato. Fallback dopo errori della sorgente attiva, risposte/errori tardivi ignorati, fallback dell'ortofoto al mosaico sottostante. Test negative fixture, non outage provocato sui fornitori. |
| MAP-04 stato | PASS | Cambio sfondo conserva zoom8, preset e timestamp frazionato `2026-10-23T21:10:43.200Z`. Controllo CUA. Il cambio del campo meteo mantiene l'istante selezionato se coperto; non aggiunge risoluzione temporale fisica. |
| MAP-05 cache/HTTP | PASS | Cache su disco e RAM limitate, single-flight per tassello, fino a4richieste upstream indipendenti, coda16, cooldown errori. Cache-Control e validator del fornitore; TTL di ripiego OSM7giorni; ETag e304 nel servizio locale. Contatori storici conservati separatamente, non azzerati. |
| MAP-06 Esri | BLOCKED / alternativa autorizzata | Nessuna licenza idonea disponibile. Nessun livello Esri attivo o interruttore fittizio. Verifica delle condizioni ufficiali e scelta esplicita dell'utente. |
| MAP-07 Cesium | FAIL visivo; non adottato | Prova concreta Cesium1.138.0: WebGL,81indicatori meteo, celle FIRE, raster FLOOD e provider quantized-mesh;150.268byte di terreno consultati nella fase iniziale. La vista finale mostra cielo/punti senza una superficie terrestre utilizzabile. Metadati/caricamenti non costituiscono PASS della resa. Conservato laboratorio riproducibile, senza voce nella navigazione principale e senza seconda implementazione completa. |
| MAP-08 meteo | PASS tecnico | ICON Global/Open-Meteo e vento ICON-EU già integrati, campi attuali verificati anche in Senegal; temperature,UR,probabilità,vento,pioggia,nuvole selezionabili. Accumuli1/3/6/12/24/48h e bollettini DPC zonali preesistenti preservati. Interpolazione grafica e passo dei campioni distinti dal dettaglio nativo. |
| MAP-09 osservazioni | PASS tecnico | Nuovo radar SRI Radar-DPC realmente scaricato e riproiettato nella VM; intensità in mm/h, colori, trasparenza sotto0,1mm/h, tratteggio dei pixel mancanti. Pluviometri MeteoHub conservati e raccolti sotto Osservazioni. |
| MAP-10 tempo e missing | PASS | Radar segue l'intervallo5min contenente l'ora selezionata; controlli su host e timestamp del file restituito. Per ore future, oltre24h o non disponibili: nessun radar sostitutivo. Prova CUA: a10:00Z futura all'atto del controllo, immagine rimossa e messaggio esplicito. Nessun aggiornamento delle forzanti fisiche dagli strati visuali. |
| MAP-11 interfaccia | PASS tecnico | Mappa1254×575 a y113 nello stesso desktop: +27,8% di altezza. Strumenti e livelli compatti, gruppi Meteo/Territorio/Osservazioni/Simulazioni, legende richiudibili. Tablet768×1024 e mobile375×812 senza overflow orizzontale; screenshot emulati, non dispositivi fisici. |
| MAP-12 regressione | PASS tecnico |52test core/web nella VM +2test geo,6073assert/check JavaScript puri; UI del confronto72h esistente con due scenari/8realizzazioni caricata, nessun nuovo job lanciato.170input/prodotti/workspace identici;8file casi/workspace identici all'audit del22ottobre.95job:82SUCCEEDED,8CANCELLED,5ERROR invariati. |
| MAP-13 qualificazione estesa | NOT RUN | Nuovo benchmark completo≥30esecuzioni indipendenti per fixture, Safari fisico,4K/DPR2, heap/GPU, soak e nuova matrice axe. Nessuna chiusura QR-11…14 o scientifica M5–M7. |

Gli overlay cumulativi dei risultati salvati conservano le proprie date; la legenda li distingue dal meteo corrente. Il replay con meteo congelato e confronto temporale resta in Simulazioni e risorse. Non vengono ridatati come previsioni attuali.

## Politica sostenibile di consultazione

La precedente cache satellitare solo RAM perdeva le immagini dopo un riavvio; il contatore permanente rimaneva vicino al tetto64MiB. Il proxy OSM, pur dichiarando quattro slot, serializzava rete e cache con un unico lock e aveva anch'esso un blocco cumulativo.

Ora la rete non tiene il lock dell'indice: richieste duplicate condividono un risultato; tessere diverse possono progredire in parallelo. Cache disco:32MiB OSM,16MiB EOX,16MiB ortofoto; RAM rispettivamente4/8/16MiB. Terreno del laboratorio separato:8MiB disco/2MiB RAM. Tetti di traffico per cache:16MiB nell'ultima ora e32MiB nelle ultime24h. Non sono promesse di traffico gratuito illimitato. Il raggiungimento della finestra limita i nuovi download senza impedire i cache hit e si risolve con lo scorrere del tempo. Nessun prefetch, esportazione o archivio offline di nuovi territori. Gli oggetti freschi sono conservati; si espellono solo oggetti scaduti. Un disco pieno di oggetti freschi resta un limite esplicito con possibilità di altro sfondo, non motivo per ridurre di nascosto il TTL o aumentare la VM.

Contatore satellitare storico65.017.285byte preservato nel file originale e nel campo `legacy_downloaded_bytes`; il totale comprende il traffico successivo. Il vecchio tetto è descritto come `legacy_limit_bytes`, non come limite ancora attivo. Le risorse UTM restano4vCPU/8GiB RAM/disco19GiB, entro20GiB autorizzati; disco libero all'avvio4,5GiB. Cesium:22.454.377byte dal registry npm ufficiale con verifica SHA512, nessun install script o privilegio. Cache radar32MiB e massimo12tentativi/24h con almeno60s tra tentativi. I prodotti generati restano separati dai dati scientifici dei simulatori.

La cache meteo di visualizzazione può scegliere il campo fresco più adatto alla singola vista tramite GET con bounds, senza cambiare lo snapshot condiviso né consumare quota. I controlli65s/48acquisizioni al giorno già presenti restano invariati per nuovi download. Risposte di navigazioni superate ignorate/annullate. I metadati di copertura sono indicizzati; una memo di2campi evita di ripetere la normalizzazione, controllando comunque gli hash dei byte normalizzati, grezzi e della ricevuta. Il test di alterazione del dato continua a fallire correttamente.

## Misure: cosa confrontano realmente

| Misura | Prima / confronto | Dopo | Limite |
|---|---|---|---|
| Altezza mappa desktop |450px |575px | Stesso browser1280×720, layout modificato. |
| Primo sfondo già disponibile |502,2ms nella baseline | 501,2ms nel campione finale | Sonda a500ms: non misura differenze inferiori al campionamento; fonti/cache diverse. Nessuna accelerazione generale dedotta. |
| Primo meteo |502,2ms baseline;2.501,8ms nell'incremento intermedio | 1.002,2ms nel campione finale | Registrato il peggioramento intermedio, non nascosto. Una singola navigazione non è un p95. |
| Endpoint meteo con cache, stesso campo | Pilot intermedio10letture: circa467–487ms | Pilot finale10letture:15,91–19,61ms | Confronto interno durante l'implementazione; sequenziale, non30run indipendenti né prestazione end-to-end. |
| Una tessera EOX, cache vuota | Non forzata la cancellazione delle cache precedenti |609,93ms di rete; mediana10hit RAM0,0188ms; dopo ricreazione del servizio0,199ms disco | Una tessera già consultata, cache diagnostica isolata; stesso SHA,1richiesta upstream. N=1 per la rete, nessuna pretesa di p95. |
| UI con risultati FIRE/FLOOD sovrapposti | Baseline specifica NOT RUN | Campione120intervalli:rAFp9517,6ms; vento p95draw0,30ms/intervallo34,3ms | Campioni correlati di rendering, non throughput scientifico o p95 di tutte le interazioni. |

I tempi di una singola richiesta/tessera non sono il tempo necessario a disegnare tutta la mappa. Nessun FPS globale è dedotto dal solo costo del canvas del vento. Il laboratorio3D non supera il controllo visivo: i suoi contatori di frame non provano prestazioni utili.

## Fonti: scelte e alternative

- **EOX**: Sentinel-2 cloudless2024, [CC BY-NC-SA4.0](https://www.eox.at/2025/03/sentinel-2-cloudless-2024/); consultazione non commerciale della ricerca. Mosaico, non immagine attuale. Ortofoto Abruzzo2018–2019 dove disponibili, non copertura mondiale di dettaglio20cm.
- **OSM**: [Tile Usage Policy](https://operations.osmfoundation.org/policies/tiles/), attribuzione, identificazione dell'app, TTL/validator, nessun bulk/prefetch. Geocoding: Open-Meteo/GeoNames, CC BY4.0; non Nominatim automatico a ogni tasto.
- **Esri**: l'item World Imagery e il [riepilogo ufficiale](https://www.esri.com/content/dam/arcgisonline/docs/tou_summary.pdf) richiedono condizioni/licenza idonee e non autorizzano il libero riservizio/offline. La descrizione “keyless” nel riferimento non sostituisce i termini ufficiali. Utente: nessuna licenza, alternative gratuite.
- **Previsioni**: [DWD ICON/Open-Meteo](https://open-meteo.com/en/docs/dwd-api), dati globali0,1°(~11km) e ICON-EU0,0625°(~7km). La griglia di campionamento della vista può essere molto più rada e viene dichiarata; l'interpolazione non recupera fenomeni non campionati. Emissione non dichiarata dal fornitore conservata come sconosciuta, non inventata dall'ora di download. [Piano gratuito](https://open-meteo.com/en/pricing), non commerciale e senza garanzia di servizio.
- **GFS/IFS**: analizzati i provider GRIB del riferimento: inventari, range GET, componenti10u/10v e riduzione alla griglia visuale. Alternative globali reali; non introdotte in questo incremento come doppio sistema di previsione, poiché ICON già alimenta le variabili richieste e rimane separato dalle forzanti dei casi. La scelta non è una prova che un modello sia scientificamente migliore.
- **nowCOAST**: radar CONUS non adatto all'Italia. Il riferimento include anche IR satellitare globale, distinto dalle stime di pioggia: non importato automaticamente. Scelta italiana: [Radar-DPC](https://mappe.protezionecivile.gov.it/it/mappe-e-dashboard-rischi/piattaforma-radar/), [APIv2](https://dpc-radar.readthedocs.io/it/radar_v2/api.html), SRI in mm/h, aggiornamento5min, griglia nominale1km, CC BY-SA. API attuale restituisce il bucket `s3-prod-dpc-radar`, diverso dall'esempio documentale: host esatto ammesso e data del prodotto verificata. Nessuna richiesta del browser a URL S3 firmate.
- **Osservazioni puntuali/zone**: MeteoHub/ItaliaMeteo e reti accreditate dichiarate; bollettini e zone DPC, EFFIS e contesto territoriale esistenti preservati. Quantità di pioggia, pericolosità, osservazioni e allerta ufficiale non sono intercambiabili.
- **Aria**: prova reale Open-Meteo/CAMS su42,35N13,38E:24ore PM2.5/PM10/EAQI restituite, unità verificate. [Documentazione](https://open-meteo.com/en/docs/air-quality-api). Non è una previsione del fumo dell'incendio simulato: nessun pulsante vuoto o layer di fumo inventato aggiunto.
- **Terreno sperimentale**: [Re:Earth/Mapterhorn](https://github.com/reearth/reearth-terrain), CC BY4.0/attribuzioni NGA. Primo accesso403 registrato; accesso con identificazione dell'app e successivi dati reali non promossi a successo visivo. Cesium1.138.0 Apache-2.0, asset solo nella VM e bootstrap opzionale riproducibile.

## Riproduzione e gestione dei negativi

Comandi eseguiti nella VM, dalla directory applicativa:

```sh
PYTHONPATH=src:tests/unit:tests/web ../core-env/bin/python -m unittest test_consultation_cache test_radar_service test_map_navigation test_maps test_regional_satellite test_osm_tiles test_map_weather test_bootstrap test_fire_workspace test_fire_cases -v
PYTHONPATH=src /home/hazardia/m0/reflex-env/bin/python tests/native/test_radar_render.py
```

Controlli JavaScript puri, senza pilotaggio browser alternativo a CUA:

```sh
node tests/browser/rain-clarity.mjs
node tests/browser/weather-render-plan.mjs
node tests/browser/viewport-weather-state.mjs
node tests/browser/rain-series.mjs
node tests/browser/basemap-state.mjs
```

Browser reale pilotato tramite CUA: caricamento, sfondi, pausa, istanti frazionati, radar futuro mancante, ricerca Dakar, sidebar e layout375/768/1280; confronto esistente72h/2scenari/8membri caricato senza lanciare simulazioni. Gli input fisici salvati sono immutati.

Diagnostica opzionale: aggiungere `diagnostics=1` alla URL per leggere `document.documentElement.dataset.mapMetrics`; sonda locale, buffer limitati, nessuna telemetria, inattiva nella pagina normale. Prova cache riproducibile nella VM, una sola tessera già vista dall'utente:

```sh
PYTHONPATH=src ../core-env/bin/python scripts/map_cache_probe.py --out /percorso/nuovo --tile 8 137 94
../core-env/bin/python scripts/install_map_lab.py --assets /home/hazardia/hazardia-runtime/web-assets
```

Il secondo comando installa solo gli asset ufficiali del laboratorio opzionale `/map-lab.html`; non migra la mappa principale. Non eseguire la diagnostica su griglie di territori o zoom per popolare preventivamente una cache.

Negativi conservati nei raw: prima selezione della vecchia tab non più associata alla sessione; sonda iniziale con accesso diretto a Performance non disponibile nel contesto CUA e selettore canvas poi corretto;403 iniziali su documentazione/terreno; lettura del PDF come UTF-8 fallita prima dell'estrazione PDF; host radar diverso dall'esempio; vecchio test che rifiutava il livello globale3 poi aggiornato al requisito globale; test OSM con opener catturato prima del mock, corretto con iniezione esplicita; sovrapposizione iniziale sidebar/controlli Leaflet risolta con isolamento degli stacking context; WebAssembly bloccato inizialmente dal CSP del laboratorio, poi abilitato soltanto lì; vista3D ancora FAIL; regressione intermedia della prima comparsa del meteo e thrashing dell'indice64su80snapshot, corretto con indice persistente e RAM limitata128metadati/2campi. Il CSP di produzione resta `script-src 'self'` e `connect-src 'self'`.

Raw privati: `experiments/runs/map-evolution-20261023/` e directory VM omonima. Estratto pubblico: `reports/map-evolution/verification.json`. Gli archivi/immagini dei fornitori, dischi VM, chiavi e lavoro indipendente `paper/` non vengono pubblicati.

## Stato scientifico e prossimo incremento

PASS tecnico non significa efficacia antincendio, skill idrologica, copertura completa degli ostacoli o autorizzazione operativa. Nessun nuovo run PROPAGATOR/HMC/REFlEx, confronto di efficacia, calibrazione o invio operativo. FullM5–M7 e P0 scientifici ancora BLOCKED. Per un'eventuale adozione3D occorre prima correggere il rendering terrestre e verificare editing di inneschi/risorse, timeline e prestazioni su fixture fissate; questo incremento conserva una sola mappa principale funzionante. Benchmark estesi e verifiche sui dispositivi fisici restano esplicitamente NOT RUN.
