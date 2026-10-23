# Livelli selezionati e traffico visuale — 23 ottobre 2026

Run `layers-traffic-20261023`, base `f213132bc9c93bad021760aefcef203b608a4f29` + modifiche elencate nel manifest locale. Incremento di FR-MAP-WORKBENCH-01: nessuna sostituzione dei motori CIMA, del decision engine o dei contratti. M5–M7 scientifici restano BLOCKED. Reviewer: Codex self-check.

## Cosa è effettivamente disponibile

| Livello | Esito e copertura verificata | Fonte / tempo / limite |
|---|---|---|
| Vento, temperatura, UR, nuvole, pioggia, probabilità | PASS, mantenuti gli overlay e la timeline esistenti; acquisizione per vista nella VM | Open-Meteo / ICON, previsto; risoluzione nativa distinta dalla griglia di campionamento e dall’interpolazione visuale. Nessuna nuova forzante scientifica implicita |
| Accumuli e attenzione per zone | PASS preesistente, riutilizzato senza duplicati; nessuna nuova qualificazione scientifica | Zone DPC, accumuli previsti1/3/6/12/24/48h, bollettini ufficiali distinti dalle soglie sperimentali |
| Radar pioggia osservata | PASS preesistente, mantenuto nel gruppo sensori | Radar-DPC SRI, mm/h e ora5min, missing distinto dall’asciutto; nessuna sostituzione di un’ora futura con l’ultima osservazione |
| Pluviometri | PASS preesistente, riutilizzato | ItaliaMeteo/MeteoHub; misure puntuali con tempo/qualità, non copertura areale continua |
| Idrometri | BLOCKED nel nuovo incremento | Nessuna serie locale di livello idrometrico acquisita e qualificata. Un corso d’acqua OSM non è un idrometro. Nessun interruttore vuoto |
| Anomalie termiche satellitari | BLOCKED per dati locali live | FIRMS richiede una MAP_KEY gratuita, attualmente non configurata. Due URL CSV tentati rispondono404. EFFIS WMS pubblicizza `viirs.hs`, ma la query datata sul bbox Abruzzo non restituisce feature: non dimostra assenza d’incendi o copertura utile. Nessun layer spacciato per incendio confermato |
| Perimetri osservati | BLOCKED per prodotto locale datato verificabile | Il riferimento usa NIFC/WFIGS statunitense: non adottato per l’Italia. EFFIS WFS va in timeout; WMS pubblicizza aree bruciate, ma la query sul pilot restituisce GML vuoto e metadata bbox anomalo. Non usare come perimetro di Fonte Vetica né confrontare geometrie inventate con PROPAGATOR |
| Immagini recenti Sentinel-2 | PASS per due anteprime reali e impronte, area L’Aquila | CDSE STAC → quicklook CREODIAS, acquisizioni21/10/2026 10:00:41Z e16/10/2026 10:00:29Z; nuvole99,46% e20,01% sull’intera tessera33TUH. Browser riceve entrambe le immagini343×343 dalla VM. Non sono immagini in tempo reale |
| Raster satellitare recente analitico sulla mappa | BLOCKED in questo incremento | Le quicklook non sono raster analitici georettificati. Confronto fra date nel pannello, impronte selezionabili sulla mappa; nessuna deformazione arbitraria dell’anteprima sul territorio. Accesso full-resolution CDSE richiede percorso/credenziali e verifica dedicati; non scaricato il prodotto da~716MB |
| Sfondo satellitare | PASS preesistente e separato | EOX cloudless2024 / ortofoto Abruzzo2018–19 / OSM; non confondere con acquisizioni recenti. Nessun Esri |
| Dighe, acque, edifici, sanità, ferrovie, elettricità, abitati | PASS catalogo parziale OSM preesistente, simboli migliorati per diga/fiume/torrente/canale | Disponibilità dipende dall’estratto, non censimento completo. Il caricamento area mantiene fonte, attributi ed epoca. Non è stata verificata la presenza di una diga specifica nel piccolo estratto traffico |
| Popolazione | BLOCKED per conteggi utilizzabili | GeoNames e WorldCover distinguono località/edificato; non deducono persone, occupazione o vulnerabilità. GHSL è un candidato, non un layer già acquisito |
| Risorse, inneschi, risultati | PASS preesistente, preservato | Catalogo simulato con date e legende proprie, scenari/risorse nello studio FIRE. Non attribuire il tempo della timeline Monitoraggio a un risultato congelato |
| Strade per traffico visuale | PASS nuova acquisizione reale | OSM API0.6, bbox `[13.376,42.346,13.384,42.354]`,1221 segmenti diretti dopo filtro barriere;4,79km circa di rete unica prima del filtro finale. Snapshot parziale, non routing operativo |
| Percorsi di risorse e chiusure osservate | NOT RUN / BLOCKED | Non introdotto un nuovo calcolatore di percorsi delle risorse; nessun feed verificato di chiusure attuali. Il gruppo Accessibilità lo dichiara |
| Traffico reale | NOT RUN | Nessun flusso osservato sovrapposto o inferito dai veicoli animati |

Fonti principali: [CDSE STAC](https://documentation.dataspace.copernicus.eu/APIs/STAC.html), [FIRMS API](https://firms.modaps.eosdis.nasa.gov/api/), [FIRMS MAP_KEY](https://firms.modaps.eosdis.nasa.gov/api/map_key/), [CEMS accesso ai dati](https://emergency.copernicus.eu/data/), [OSM API map](https://wiki.openstreetmap.org/wiki/API_v0.6#Retrieving_map_data_by_bounding_box:_GET_/api/0.6/map), [licenza OSM](https://www.openstreetmap.org/copyright). EFFIS: endpoint WMS `https://maps.effis.emergency.copernicus.eu/effis`, capabilities salvate nel run. Reference God's Eye View MIT, commit224745bd0aa1050f73bded841ecc467c3ad1ce7c: esaminati traffic/source e firePerimeters; nessun codice di modelli di congestione o feed US importato.

Qualità dell’aria: la prova CAMS puntuale precedente non è una stima del fumo dell’incendio. Webcam, immagini stradali, aerei e fulmini: NOT RUN, nessun controllo nominale senza dati/diritti verificati. Livelli esplicitamente esclusi dall’utente non aggiunti.

## Uso del traffico

Monitoraggio → **Livelli → Scenari e simulazioni → Traffico stradale simulato**. Sempre disattivato al caricamento, anche quando esiste una configurazione salvata.

1. Centrare la zona desiderata, scegliere il raggio0,2–2km e premere **Usa area intorno al centro**. Il rettangolo di acquisizione interno è limitato a0,06° per lato e non modifica il dominio di PROPAGATOR. In aree dense ridurre il raggio: risposta oltre4MiB viene rifiutata.
2. Attivare il livello. Scegliere preset ipotetico scarso/ordinario/intenso o modificare densità0–200 veicoli/km, massimo0–400, seed e velocità delle9categorie stradali1–130km/h.
3. **Riprendi/Pausa**, **Reset** e velocità1/2/5/10× controllano soltanto il traffico. Il suo tempo in secondi non è la timeline meteorologica o del simulatore fisico. Reset rigenera la stessa popolazione per configurazione, rete e codice identici.
4. **Chiusure ipotetiche ON** e tocco su una strada escludono la via OSM. In alternativa inserire l’ID della via in **Apri/chiudi via · ipotesi**. Linee rosse tratteggiate indicano chiusure ipotetiche del traffico, distinte dalle linee elettriche fucsia del catalogo e spiegate dalla legenda; i punti gialli sono veicoli simulati. Nessuna chiusura è osservata. Elenco degli ID chiusi sempre nel testo di stato.
5. **Salva configurazione nella VM**, poi **Carica configurazione salvata** ripristinano area, seed, velocità, densità, massimo e chiusure. Lo stato di riproduzione non viene salvato o avviato implicitamente.

La dicitura **Traffico simulato — scenario ipotetico** resta sulla mappa quando il livello è attivo. Le risorse HAZARDIA mantengono i propri simboli: nessun veicolo visuale diventa una squadra.

Modello: camminatori pseudocasuali su archi orientati e nodi OSM, passo fisso0,1s. Segue `oneway=yes/-1/no`, impliciti autostrada/rotatoria, accesso motorcar/motor_vehicle/vehicle/access. Esclude vie delle relazioni di restrizione restituite, restrizioni condizionali/direzionali non interpretate e segmenti con barriere non dichiarate accessibili. Questo è un sottoinsieme conservativo, **non un solver completo delle restrizioni stradali**. Nel pilot44vie non dichiarano il senso e assumono doppio senso,14vie escluse per relazioni,2per accesso. Relazioni esterne, barriere e attributi assenti possono rendere incompleto il grafo.

Nessun modello di code, capacità, precedenze, semafori o interazioni fra veicoli. Ai capolinea senza uscita si genera un ricambio sintetico; non è una congestione o una rotta origine-destinazione. Densità e velocità sono ipotesi, non dati di traffico. **Nessun collegamento a tempi di intervento, ottimizzatore, evacuazione o risultati scientifici.** Un futuro collegamento richiederà contratto esplicito, dati e validazione separati.

## Vincoli e riproduzione

Nuovi backend nella stessa VM: `hazardia.web.traffic` e `recent_imagery`, sola libreria standard. Nessuna nuova dipendenza privilegiata o servizio commerciale. Acquisizioni in thread separati dai worker fisici; una per servizio, timeout25/20s, risposte4MiB OSM/2MiB STAC/2MiB per immagine. Traffico8aree/giorno, cache48MiB; immagini6ricerche/giorno, cache24MiB. Sono limiti locali prudenziali, non disponibilità illimitata del fornitore. Snapshot della rete riusati e datati, non aggiornamento automatico in tempo reale. Nessun prefetch nazionale o scraping di servizi chiusi.

La configurazione persistita è `web-state/visual-traffic/config.json`; grafo e risposta XML conservati nello stesso servizio con SHA256. Ripetibilità richiede **stesso snapshot XML/grafo, configurazione, seed, passo numerico e versione del codice**. Un nuovo snapshot OSM può cambiare il risultato anche con lo stesso seed. I file non devono essere cancellati per fingere una prova fredda. Immagini e catalogo sono in `web-state/recent-imagery/`, separati dagli asset cartografici e dai job.

Comandi verificati nella VM, da `~/hazardia-runtime/app`:

```sh
PYTHONPATH=src:tests/unit:tests/web ../core-env/bin/python -m unittest test_traffic test_recent_imagery test_consultation_cache test_radar_service test_map_navigation test_maps test_regional_satellite test_osm_tiles test_map_weather test_bootstrap test_fire_workspace test_fire_cases -v
```

Test JavaScript dello strato di rendering, eseguiti sul client di sviluppo con Node16.20.2 (non runtime scientifico né backend sul Mac):

```sh
node tests/web/traffic-model.test.mjs
node tests/web/traffic-model.test.mjs /percorso/traffic-graph-v2.json
```

Il secondo argomento è lo snapshot HTTP `{status,graph}` salvato dal servizio. Nessuna suite Node installata nella VM per questo incremento.

## Prestazioni del pilot

Con400veicoli sul grafo reale, canvas1254×575 e meteo/territorio attivi, finestra correlata di300disegni: p95 del solo disegno traffico0,70ms; p95 dell’intervallo fra disegni48,7ms. Il tetto di disegno è30Hz, **non una garanzia di30fps**: aggiornamenti mappa/meteo e browser contribuiscono alla variabilità. Non è stato misurato un confronto causale completo con/senza traffico né un benchmark Safari. Cache osservate:1.262.450byte traffico e1.755.530byte catalogo/anteprime; niente richieste di rete a ogni frame. Il limite puro12000archi/400veicoli è un test del modello sul client, non della latenza totale della mappa. Snapshot, tempi e ambiente nell’estratto JSON.

## Verifiche e risultati negativi

- PASS68test Python nella VM, inclusi nuovi16controlli di traffico/immagini e52regressioni di cache,radar,navigazione,meteo,workspace/casi.
- PASS JS: determinismo, seed diverso, chiusure, rete vuota/tutta chiusa, massimo0, input non finito; grafo reale1221archi,400veicoli e36.000passi ripetuti identici; via28404014 esclusa in una prova separata.
- PASS limite sintetico12000archi/400veicoli su30ripetizioni del solo modello,300passi/posizioni per ripetizione. Non sono30benchmark indipendenti della dashboard e non sono la verifica della deadline60s.
- PASS browser: traffico inizialmente spento, carica area, preset400, pausa/ripresa senza reset del tempo, reset, salvataggio/lettura chiusura nella VM, dicitura esplicita; anteprime ricevute realmente343×343, due date/nuvolosità distinte. Viewport375×812 e768×1024 senza overflow orizzontale; desktop1280×720.
- FAIL iniziali conservati: estratto OSM troppo grande rifiutato; redirect thumbnail non ancora ammesso; errore CSS `contain:strict` azzerava la dimensione visuale del canvas nonostante il loop funzionasse. La revisione finale del diff ha inoltre individuato una riscrittura accidentale del CSS con testo JavaScript: foglio originale ripristinato e controllato prima della consegna. Corretti area/allowlist/domain e dimensionamento esplicito; **la prima misura del loop non provava che i veicoli fossero visibili**. Screenshot successivo controllato mostra veicoli sulle strade.
- BLOCKED: dati locali di anomalie/perimetri/idrometri/popolazione qualificati, raster satellitare analitico recente e chiusure osservate come sopra. Non aggiunti selettori vuoti.
- NOT RUN: Safari fisico, lungo soak/memoria, benchmark completo multi-dispositivo, validazione di traffico/code/evacuazione, confronto nuovo delle fisiche CIMA. Non dedurre nuove conclusioni RQ1–RQ3.

Evidenze private host/VM: `experiments/runs/layers-traffic-20261023/` e `/home/hazardia/hazardia-runtime/runs/layers-traffic-20261023/`. Estratto pubblico senza immagini territoriali o runtime personale: `reports/layers-traffic/verification.json`. Il test di integrità confronta311file di workspace/casi con il preregistrato;95job precedenti, nessun job nuovo per consultazione o traffico. Spazio VM19GiB,4,4GiB disponibili durante le verifiche; RAM/vCPU invariati.

Prossimo incremento eseguibile: acquisire una fonte locale datata effettivamente positiva per anomalie/perimetri o idrometri, qualificarla con copertura e missing, poi collegarla come osservazione. La MAP_KEY FIRMS gratuita richiede la configurazione dell’utente; nessun account creato o termine accettato automaticamente. Il traffico resta indipendente.
