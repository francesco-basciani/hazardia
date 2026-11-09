> **Aggiornamento25ottobre2026:** codice e repository WII sono stati estratti in [../WII](../../WII/README.md). Le istruzioni storiche con namespace `hazardia.wii` e worker embedded sono superate dalla [guida autonoma](WII-AUTONOMO.md). API, dati e schemi salvati rimangono compatibili.

# Wildfire Ignition Intelligence

Stato25ottobre2026: add-on locale per ricerca con copertura del catalogo Italia e pilota storico Abruzzo2005–2025. La mappa regionale stima suscettibilità annuale su registrazioni; coordinate di eventi e vere origini rimangono distinte. Probabilità calibrate dei veri inneschi e previsione meteo giornaliera non qualificate. [Pilota, database e risultati](../reports/WII-ABRUZZO-PILOTA-20261025.md), [specifica](../SPEC.md).

## Installazione e attivazione

Tutti i comandi seguenti si eseguono nella VM Linux esistente, dalla directory `hazardia-runtime/app`; `RUNTIME` indica `/home/hazardia/hazardia-runtime`. Nessun runtime scientifico sul Mac.

```sh
PYTHONPATH=src ../core-env/bin/python scripts/install_wii.py --runtime /home/hazardia/hazardia-runtime
PYTHONPATH=src ../core-env/bin/python scripts/install_wii.py --runtime /home/hazardia/hazardia-runtime --install
PYTHONPATH=src ../wii-env/bin/python -m hazardia.wii --runtime /home/hazardia/hazardia-runtime enable
```

La prima riga è preflight; la seconda installa il lock `requirements/wii.txt` in `wii-env` Python3.12, riusando in sola lettura le dipendenze numeriche del fire-env. Non modifica fire-env/core-env/decision-env. Software aggiuntivo misurato circa412MiB, separato dalla quota dati256MiB; mantenere almeno2GiB liberi. L'ambiente già installato nell'istanza locale non va reinstallato per usare la console.

Riavviare la dashboard con `scripts/web_service.py` **soltanto quando nessun job/supervisore è attivo**. L'istanza consegnata è già abilitata. Aprire [WII](http://127.0.0.1:8080/wii.html), oppure il collegamento in **Dati e fonti** della dashboard. Per disattivare, eseguire la CLI con azione `disable` e riavviare in sicurezza: archivi conservati, nessun import WII/DB/worker/acquisizione/controllo WII quando disabilitato. La sola sonda `/api/wii/status` resta disponibile e il piccolo loader non aggiunge UI.

## Uso della console

- **Eventi ed evidenze**: filtro data/area, paginazione coerente allo stesso `as_of`, cluster visuali, scheda originale/storia/evidenze e revisione motivata dei duplicati. “Posizione non disponibile” conserva gli eventi privi di punto. Il cluster non fonde incidenti. Le aree osservate sono un livello indipendente.
- **Fonti e acquisizione**: selezione geografica/fonti, registro JSON versionato con controllo revisione, testo autorizzato e URL/feed, stato delle acquisizioni. DPC RSS selezionato ha aggiornamento automatico ogni6h; nessun crawler ricorsivo. Un nuovo giornale deve avere diritti/accesso verificati nel registro prima dell'attivazione. Una fonte assente non significa assenza di incendio.
- **Modello e scenari**: metriche retrospettive, calcolo esplorativo24/48/72h, pulsante “Mostra stima selezionata”, campionamento e caricamento scenari salvati. Le mappe viola rappresentano il modello, i punti blu candidati, le origini istituzionali verdi; nessuna equivalenza con propagazione o hotspot.
- Per campionare prodotti non qualificati occorre la scelta esplicita esplorativa. Selezionare il membro e una previsione congelata compatibile prima di PROPAGATOR. Copertura/tempi/fuel devono essere validi; Piemonte non usa forzanti dell'Abruzzo per fallback. Il caso senza inneschi termina senza simulazione. I risultati sono propagazioni condizionali, con collegamenti immutabili a scenario/request/job/prodotti.
- La UI offre meteo e monitoraggio attraverso il collegamento alla console esistente. Non aggiunge nuovi layer meteo fittizi né una schermata di dispatch operativo. Il confronto fisico resta nelle funzioni di simulazione esistenti; l'API decisionale WII richiede conseguenze complete esplicite.

## Architettura e dati

`src/hazardia/wii`: `contracts` definisce semantica/versioni, `acquisition` il collector, `intelligence` l'estrazione, `inventory` SQLite/R-tree, `datasets` gli adapter, `features` fattori e disponibilità, `modeling`/`reference` modelli, `scenarios` il campionatore, `propagator` l'adapter nativo, `decisions` l'interoperabilità, `service`/`worker` i task. Il pacchetto è opzionale e non sostituisce catalogo, motori o solver.

Stato persistente `web-state/wii`: database separato WAL, revisioni append-only, documenti minimizzati, assertions con span o record binario+SHA, relazioni, R-tree, snapshot dataset, artefatti JSON e task. `PRAGMA user_version=1` riguarda soltanto gli indici WII: timestamp indicizzati UTC a microsecondi fissi, evidenze originali intatte. Nessuna migrazione del workspace esistente. Modelli serializzati come JSON di coefficienti/metadati, mai pickle eseguibile.

Piemonte: zip ufficiale CC BY4.0,1997–2025, SHA7810341ffef65a8d31f69d6a313bef615bbb89dbfbc1069ee91c4af527796afe. Join verificato6767righe/6764punti/2126perimetri; tre record senza geometria. Coordinate32632 trasformate4326, precisione nativa non inventata, perimetri mai trasformati in origini. Contenuto già scaricato1.79MB. Feed DPC CC BY4:50voci/34documenti unici; la selezione corrente non ha fornito nuovi incidenti qualificabili. Italian spaCy blank+regole, non modello statistico addestrato: inglese esplicito REVIEW_REQUIRED. Gazetteer esistente a20regioni: localizzazioni regionali restano aree, mai centroidi.

FIRMS: adapter VIIRS/MODIS conserva orario UTC/confidenza sensore/scan/track, non probabilità d'innesco. Live richiede `FIRMS_MAP_KEY` nell'ambiente del server, mai JSON/UI/log/URL persistiti con segreto. EFFIS: adapter WFS GeoJSON bounded; endpoint interrogato non ha risposto al GetCapabilities nel limite20s, quindi acquisizione reale non qualificata. FWI/DC WMS esistenti restano indicatori di pericolo. FireNews non viene acquisito senza accesso/diritti verificati.

Collector: sorgente revisionata con permesso processing, HTTPS stesso host, risoluzione DNS pubblica e connessione TLS vincolata all'IP verificato, robots, minimo60s/host, massimo2MiB/risposta, quote fonte+64MiB payload/giorno globali, condizionali HTTP, errori403/429 espliciti. Nessun bypass. Un worker con coda4, deadline120s o1800s training, RSS2GiB, thread numerici1, cancellazione process-group e ripresa con stato interrotto. Quota dati256MiB e riserva disco2GiB; stop esplicito anziché eliminazione di archivi. La durata training/import non è il vincolo decisionale60s.

## Definizione statistica

Il baseline congelato usa griglia EPSG3035 da10km e mesi di calendario con offset area×durata, componenti stagionali e densità storica calcolata solo dal training. `mu=exposure*exp(X beta)` e `P(N>=1)=-expm1(-mu)`. Il supporto è terreno amministrativo, non maschera combustibile. Training1997–2018, calibrazione2019–2021, test2022–2025; holdout spaziale con fascia20km. I conteggi0 significano0registrazioni nel dataset, non assenza vera accertata. Modello disponibile **EXPERIMENTAL_UNCALIBRATED**, target **P_REGISTERED_ORIGIN_PROXY_PER_CELL_INTERVAL**. Il trasferimento a24–72h assume intensità mensile costante: non è validato, non include meteo.

Estrattori riusabili per DEM/slope/aspect, raster nearest/mean su celle quadrate, distanze vettoriali metriche con copertura, meteo con controllo issue/availability e lacune. Questi componenti non significano che tutti i fattori siano stati acquisiti sul Piemonte o entrino nel baseline. Mancano archivio previsionale issue-time, inventario completo/precisione certificata, validazione multicentro e valutazione indipendente della calibrazione. Nessuna conclusione causale o utilità operativa.

Scenari: processo congiunto Poisson indipendente condizionato dichiarato, non dedotto dalla sola calibrazione marginale. Metodi IID, strati zero/positivo, strati spaziali ovest/est e importance mixture con supporto completo. Masse target/proposal e pesi di stima distinti; supporti continui punto/tempo, posizione uniforme sulla maschera, seed propagazione separato. La massa senza eventi e coda oltre16inneschi sono esplicite; membri non supportati non vengono scartati o rinormalizzati in segreto. Pesi importance non sono probabilità individuali di evento. L'adapter decisionale rifiuta conseguenze incomplete/stati irrisolti.

Decision contract0.7: modalità RESEARCH_PROBABILISTIC, pesi PROBABILISTIC_RESEARCH e target di ensemble espliciti; benefici ideali restano SYNTHETIC_RESEARCH. Riusa `bounded_decide`, HiGHS, verifier indipendente e rolling horizon. Il prodotto probabilistico non certifica efficacia interventi, sicurezza o autorità operativa. Contratti0.5/0.6 preservati.

## API

Base `/api/wii`; POST stessa origine, `Content-Type: application/json`, `X-Hazardia-Research: 1`, corpo≤64KiB. Ogni task richiede `idempotency_key`; chiave riusata con corpo diverso409. Risposta202 `{task_id,...}`, polling GET task, terminali SUCCEEDED/ERROR/CANCELLED/TIMEOUT. Errori espliciti, coda piena429. Risposte finite JSON; nessun import scientifico nel request handler.

| Metodo e suffisso | Contratto principale |
| --- | --- |
| GET `/status`, `/sources` | Qualificazione, worker, quote/stati; registro e revisione |
| POST `/sources` | `expected_revision`, `sources`, `selection:{regions,source_ids}` |
| GET `/events` | `bbox=west,south,east,north`, `from`, `until`, opzionali `as_of,cursor,limit,source_id` |
| GET `/events/unlocated`, `/events/{id}` | Intervallo/`as_of`; dettaglio/evidenze/storia |
| POST `/ingestions` | `source_id,text,external_id`, opzionale `published_at` |
| POST `/acquisitions` | `source_id`, opzionale URL stesso host |
| POST `/datasets/piemonte` | `source_id:piemonte-origins`; opzionale snapshot zip sotto runtime/runs |
| POST `/reviews/duplicate` | `event_id,canonical_id,expected_revision,reason`; null separa |
| POST `/observations/firms` | `source_id,product,bounds,days,day`; credenziale solo ambiente |
| POST `/observations/effis` | `source_id,bounds` |
| GET `/observations` | `artifact_id,bbox,limit`≤500; candidati bbox, troncamento esplicito |
| POST `/training` | Baseline Piemonte congelato; nessuna scelta automatica vincitore sul test |
| GET `/models`, `/artifacts`, `/artifacts/{id}` | Catalogo/dato JSON con provenienza |
| POST `/predictions` | `model_id,valid_from,valid_until` |
| POST `/scenarios` | `product_id,count,seed,method,exploratory`, opzionale `impacts` |
| POST `/executions` | `scenario_set_id,member_id,start_at,hours,forcing_id`, parametri nativi bounded |
| GET `/executions/{id}` | Ricevuta/preparazione/job/prodotti condizionali |
| POST `/decisions` | `base_problem`0.6, `scenario_set_id,consequence_by_event,benefit_by_option` completi |
| GET `/tasks/{id}`; POST `/tasks/{id}/cancel` | Stato persistente/cancellazione bounded |

## Verifica riproducibile

Nella VM, `PYTHONPATH=src ../wii-env/bin/python -m unittest discover -s tests/wii -v` esegue58test allo snapshot nazionale. I357test esistenti usano core-env, le11suite client Node. `tests/integration/verify_wii_native.py` verifica il motore reale su processo d'innesco sintetico dichiarato. `tests/integration/benchmark_wii.py` misura100krecord/celle e30decisioni; scala sintetica non prova capacità predittiva. Comandi, input, hash, errori iniziali e risultati effettivi sono in `reports/wii-implementation/`; nessun risultato inventato o esito negativo rimosso.

## Italia intera — aggiornamento24ottobre2026

Il requisito dati è nazionale, non limitato al Piemonte. Sono importati12.662record EFFIS2016–2026,3.853eventi Puglia2017–2024 e il gazetteer italiano11.859località/20regioni. La mappa iniziale è Italia; tabella/aggregati regionali distinguono origini, segnalazioni e catalogo delle aree bruciate. I record EFFIS privi di poligono preciso si consultano per regione e rimangono senza punto, non vengono geocodificati come origini.367associazioni regionali EFFIS non risolte sono conservate. [Dati, prove e limiti nazionali](../reports/WII-ITALIA-20261024.md).

In **Fonti e acquisizione → Archivi Italia**, su una nuova installazione acquisire prima **GeoNames**, poi **EFFIS** e infine gli inventari regionali desiderati, come **Puglia**. Il dizionario consente di associare prudentemente i nomi del catalogo alle regioni; senza dizionario le localizzazioni restano irrisolte. In **Notizie storiche** scegliere editore/pagina: la scoperta autorizzata alimenta una coda persistente, elaborata dal worker esistente rispettando diritti/robots/quote. Sono attivi VVF nazionale, Pressenza e MET; ANSA resta disabilitata per divieto esplicito di mining. La prova iniziale6articoli ha prodotto5candidati, non un censimento nazionale completo. Fonti diverse possono riferirsi allo stesso rogo. Gli articoli stranieri espliciti vengono esclusi dal conteggio nazionale; dati e motivazioni restano tracciati.

API aggiuntive: POST `/national/setup`; POST `/datasets/italy` con `dataset:effis|puglia|geonames`; POST `/coverage/refresh`; GET `/coverage`; GET `/coverage/events` con `region`, `limit`≤500, `cursor`, `coverage_id`, opzionali date `from/until`; POST `/news/discover` con `source_id:pressenza-italy|vvf-italy-news,page:1..50`; GET `/news/backfill`. Task sempre con `idempotency_key` e header originali. Lo snapshot regionale consente paginazione coerente anche dopo correzioni. Acquisizione di poligoni EFFIS per viewport con assi GML espliciti e massimo100record; la prova reale Calvanico ha restituito24perimetri.

**Rettifica della sezione precedente:** il timeout EFFIS era l'esito iniziale del GetCapabilities, non indisponibilità permanente: il percorso WFS nazionale e i poligoni bounded sono ora verificati. Il limite documenti rimane2MiB; soltanto gli adapter dataset strutturati revisionati ammettono fino a16MiB, con quote fonte/globali e riserva disco invariate. La fonte nazionale non rende calibrato il modello: quello distribuito rimane un esperimento Piemonte, senza estensione automatica a tutta Italia.


## Modello nazionale e punti individuali —24ottobre2026

La mappa iniziale mostra punti documentati e l'ultimo prodotto nazionale disponibile, con dataUTC; i riepiloghi regionali restano nel pannello dati. Verde=origine istituzionale; ambra=posizione incidente riportata; viola=celle del modello; blu=candidato condizionale campionato. La copertura puntuale nativa attuale è Piemonte/Puglia.5km è lato cella, non una garanzia di errore; il modello usa smoothing10km ed è privo di nuove forzanti meteo/combustibili nazionali.

Acquisire gli anni completi da Fonti→Archivi Italia→Perimetri EFFIS (almeno tre anni consecutivi). API POST `/api/wii/datasets/italy/spatial` con `year`2016–2025 e chiave idempotenza; un anno già importato viene riutilizzato. Limiti e ritardi del collector restano obbligatori; i429/rate-limit non si aggirano. Modello e scenari→Valuta baseline addestra ora Italia tramite POST `/api/wii/training/italy`; il vecchio `/training` Piemonte resta compatibile. Le ultime due annualità sono validation/test, mai refit implicito. Modelli e prodotti nazionali hanno etichetta separata dal Piemonte.

GET `/api/wii/locations` restituisce punti nativi (max15.000, `truncated`, `bbox`, `from`, `until`), nessun centroide areale. Mostra tutti i punti documentati abilita il downloadGeoJSON con fonte/precisione/incertezza. Selezionare un punto apre coordinateWGS84 ed evidenza originale. Selezionare uno scenario salvato o Genera scenari mostra i singoli candidati; cliccarli apre longitudine, latitudine, tempo, supporto e incertezza. I membri sono alternative; non sommare i punti come eventi simultanei. Un prodotto scaduto conserva la propria data, non diventa una previsione corrente.

L'estrattore0.4 supporta coordinate WGS84 etichettate nel periodo dell'incendio. I nomi di località non diventano coordinate di origine. Le sei notizie attualmente archiviate non hanno punti utilizzabili: la ricostruzione giornalistica puntuale nazionale resta incompleta. Il prodotto nazionale è `P_RECORDED_FIRE_SUPPORT_PROXY_PER_CELL_INTERVAL`, solo esplorativo; l'ammissione calibrata continua a richiedere il target vero e revisione indipendente. Rapporto: `reports/WII-MODELLO-ITALIA-20261024.md`.


## Database strutturato, crawler e rischio per area —25ottobre2026

Questa sezione aggiorna l'apertura della mappa e l'estrattore descritti sopra. La vista iniziale **Rischio innesco** mostra13.063celle su tutta Italia, con intervallo UTC esplicito. Cinque classi confrontano densità prevista per km²/giorno e media nazionale: verde scuro <0,25; verde chiaro0,25–0,75; giallo0,75–1,5; arancio1,5–3; rosso≥3. Grigio significa dato mancante. È **suscettibilità relativa sperimentale del proxy registrazioni**, non allerta ufficiale né probabilità calibrata di veri inneschi; la colorazione non aggiunge nuove forzanti meteo. Cliccare una cella mostra classe, indice, superficie, periodo e qualificazione. Il livello dei punti documentati rimane selezionabile separatamente.

**Database strutturato** espone ID/revisione, data e intervallo, tipo, località/comune/codice, coordinate native, precisione/incertezza, vegetazione, superficie, cause riportate e confermate distinte, infrastrutture, condizioni e provenienza. Le assenze restano NULL con motivo. Sono record di fonti e menzioni da rivedere, non un conteggio deduplicato degli inneschi italiani. La vista SQL `event_record_revisions` consulta gli originali senza duplicare grandi geometrie; paginazione stabile `as_of`/`cursor`. Località e superficie native Piemonte sono mantenute. Un comune individuato in una notizia dà un supporto areale, mai un centroide presentato come innesco.

**Esporta database SQLite** produce uno snapshot scaricabile: `event_rows` contiene campi tipizzati, `document_refs` le fonti documentali, `source_refs` licenze/attribuzione, `location_qualities` e `missing_field_sets` normalizzano testi ripetuti. La vista `fire_events` ricompone le schede. Esempio: `SELECT event_id, municipality_name, longitude, latitude, location_precision, burned_area_ha FROM fire_events;`. Le geometrie complete restano nel database operativo originale e sono raggiungibili tramite `geometry_reference`; l'export compatto non sostituisce l'archivio di evidenze.

Il crawler usa Pressenza e VVF nei diritti revisionati:1–5pagine,1–60articoli per campagna, profondità massima2, quote globali/fonte e almeno60s per host. Frontiera, tentativi, stato e risultati persistono; pausa/ripresa, deduplicazione URL/versione estrattore, retry classificati. I feed recenti sono integrati con riferimenti storici già acquisiti. Sono esclusi URL non ammessi e sorgenti con diritti non risolti. Nessuna fonte a pagamento o aggiramento robots. L'estrattore0.5.4 distingue più menzioni nello stesso articolo e non usa il comune della sede dei soccorritori come luogo dell'incendio. Le cause rimangono dichiarazioni/ipotesi, mai conferme automatiche; le menzioni non risolte non vengono aggiunte come etichette vere al modello.

Confini comunali semplificati ISTAT/geojson-italy, CC BY4.0, commit `ba3347df3a53352891109f8198c597a0273684c0`:7.895confini validi in20regioni, Miagliano escluso per geometria nativa non valida. La geometria2026 non prova l'accuratezza storica del punto.

API aggiuntive (prefisso `/api/wii`): GET `/inventory?limit=100&source_id=…&place=…&cursor=…&as_of=…`, GET `/inventory/summary`, POST `/inventory/export` con chiave idempotenza, GET `/inventory/exports/{task_id}.sqlite`; GET `/riskmap?artifact_id={probability_id}`; GET `/crawler`; POST `/crawler/runs` con `idempotency_key,source_ids,pages,max_articles`; POST `/crawler/runs/{run_id}/pause` oppure `/resume`; POST `/datasets/italy/municipalities`. Gli header di ricerca e i controlli d'origine esistenti restano obbligatori per le scritture. Un solo worker nella VM, nessuna modifica alla fisica.


## Calibrazione e verifica storica —25ottobre2026

**Validazione storica** mostra l'esperimento congelato: train2022/cal2023, test2024 e nuovo EFFIS2025; origini Piemonte2025 separate dalle coordinate incidenti Puglia2024 e dai supporti frazionari dei perimetri. Risultati completi, baseline,20regioni e5blocchi geografici. DownloadJSON e rapporto `reports/WII-CALIBRAZIONE-ITALIA-20261025.md`. Il2024 era già stato visto; test Piemonte2025 e baseline regolarizzate aggiunti con supplemento dichiarato, senza cambiare coefficienti sul test.

POST `/api/wii/calibration/italy` avvia il worker con `idempotency_key` e opzionale `base_model_id`; accetta il protocollo congelato2022/23/24 e richiede lo snapshot2025 già acquisito. GET stesso endpoint restituisce `available,evaluation_id,report`. Controlli origine/header/quote e cancellazione esistenti invariati. Il task può richiedere fino30min, ma la prova reale è durata circa12s; nessuna promessa operativa dedotta. Su nuova installazione creare prima gli snapshot nazionali2022–24 e il modello, acquisire il holdout con lo script documentato e passare il suo ID reale, non l'ID interno del manifest.

Famiglia `NATIONAL_SPATIAL_SUPPORT_CALIBRATED`: riferimento alla base immutabile e fattori di correzione globali/mensili/regionali, non pickle eseguibile. I fattori sono **regionali**, non nuove etichette comunali. Le probabilità dei veri inneschi restano EXPERIMENTAL_UNCALIBRATED; il calibro dell'intensità dei registri non identifica il processo reale quando la rilevazione è incompleta. Il prodotto aggiornato25ott08UTC→26ott08UTC è mostrato sulla mappa, mantenendo legenda relativa e stato di ricerca. Puglia2024 peggiora: nessun vincitore scelto sul test.

Per i nuovi grandi prodotti probabilistici la tabella artifacts può contenere un envelope `hazardia.wii.lossless-artifact/0.1.0` e un payload gzip sotto `payloads/`. Usare `Inventory.read_artifact` per il contratto completo. SHA/dimensioni/percorso/cap16MiB di espansione sono verificati; µ/p non cambiano e le API/scenari ricevono il JSON originale. Artefatti precedenti intatti; WII disabilitato continua a non avere effetti. Gli identificatori artifact sono opachi: non presumere una lunghezza fissa del digest.

Per ricalcolare senza scritture: `hazardia.wii.calibration.run(store,runtime,base_id,persist=False)`. Replay già verificato con digest esatti. Non presentare un basso Brier su eventi rari come accuratezza99,9%, o85,5%del supporto EFFIS come quota di origini previste. La verifica puntuale2025 riguarda105record Piemonte/101celle-giorno, non tutte le origini italiane.


## Abruzzo · pilota2005–2025

[Apri la vista regionale](http://127.0.0.1:8080/wii.html?pilot=abruzzo). Stesso SQLite `web-state/wii/wii.sqlite`, tabelle tipizzate `abruzzo_*`,21snapshot originali e7versioni negative,1.914perimetri e363coordinate native di eventi. I nuovi testi autorizzati del crawler sono completi in `document_texts`, gzip/SHA. L’export SQLite comprende le geometrie regionali originali, versioni, attributi, punti e prodotti; il vecchio registro nazionale mantiene la propria vista, senza sommare record come eventi unici.

| API | Funzione |
|---|---|
| GET `/api/wii/abruzzo` | Stato per anno, conteggi e prodotti qualificati per il solo uso esplorativo |
| POST `/api/wii/abruzzo/start` `{}` | Inizializza coda storica bounded; un worker condiviso, host>=60s |
| GET `/api/wii/abruzzo/events?year=2025&limit=100` | Perimetri/attributi di un anno, massimo500record, troncamento esplicito |
| GET `/api/wii/abruzzo/points` |363coordinate native di eventi, mai centroidi o vere origini certificate |
| POST `/api/wii/abruzzo/validate` | Task con `idempotency_key`; rifiuta storico incompleto o test senza supporto |
| GET `/api/wii/abruzzo/products/<id>` | Mappa/valutazione checksummed, espansione gzip limitata16MiB |
| POST `/api/wii/inventory/export` | Export SQLite nazionale e pilota, originale regionale incluso |

Il pilota acquisisce lo strato0principale; strati non boschivi separati non inclusi. Per2018/2020–2025usa direttamente il formato nativo ESRI JSON con CRS dichiarato, evitando il difetto GeoJSON delle coordinate NULL. Collector generico HTTPS invariato; adapter regionale HTTP6080ristretto a host/percorso/anni fissi, DNS pubblico pinning e quote comuni. Licenza regionale CC BY-NC3.0, ricerca non commerciale con attribuzione. Non aumentare le quote né cancellare archivi per consentire refresh.

Fit2005–2018/cal2019–2021/test2022–2025; nessun rifit sui test. Mappa annuale508celle5km, classi relative alla media Abruzzo. Quota delle198coordinate test nel20%area=36,9%, contro24,8%provinciale; bias del totale+34%. Non è una previsione del giorno o una probabilità qualificata d’innesco; date di segnalazione/accertamento e precisione delle coordinate rimangono esplicite. [Protocollo, risultati, limiti e verifiche](../reports/WII-ABRUZZO-PILOTA-20261025.md).

## Integrazione come plugin
Dal25ottobre2026 WII dispone di entry approvato, port Host, manifest/versione, API v1 e renderer nella mappa HAZARDIA principale. La console e le API operative rimangono compatibili; dati SQLite e originali restano nel runtime Linux. [Guida completa e contratto API](WII-PLUGIN.md).

## WII autonomo — 25 ottobre 2026

WII dispone ora di [avvio e console autonomi](WII-AUTONOMO.md) sulla porta8081. HAZARDIA è un client API opzionale; l’archivio WII rimane locale e invariato.
