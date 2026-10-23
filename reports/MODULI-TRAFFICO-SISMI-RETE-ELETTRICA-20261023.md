# Moduli indipendenti: traffico, terremoti e rete elettrica

Dal pannello sinistro del Monitoraggio sono disponibili tre voci dedicate, con parametri nel pannello destro: **Traffico simulato**, **Terremoti osservati**, **Rete alta tensione**. Possono essere attivate insieme a meteo, incendi e alluvioni. Sono spente al caricamento della pagina.

Run `modules-power-quakes-20261023`, base `faf2703` con modifiche documentali preesistenti conservate. VM Linux unica: 6 vCPU, 16 GiB RAM, disco 19 GiB. Reviewer: Codex self-check. Questo incremento non introduce un simulatore sismico, un modello di congestione o un nuovo accoppiamento al decision engine.

## Cosa si può provare

- **Traffico simulato:** aprire il modulo, spuntare «Traffico simulato — scenario ipotetico», usare l’area intorno al centro oppure caricare una configurazione salvata, quindi Riprendi. Restano seed, preset, strade reali, chiusure ipotetiche, pausa/reset e limiti già verificati. La nuova voce riusa lo stesso modulo e gli stessi dati, senza una seconda implementazione.
- **Terremoti osservati:** spuntare il livello; selezionare INGV per l’Italia o USGS per altre aree, periodo 1/7/30 giorni e magnitudo minima, quindi Carica area visibile. Il default M≥0 comprende eventi piccoli; è disponibile M≥−1. Cerchi arancioni proporzionali alla magnitudo, origine UTC, profondità, località e autore della soluzione. Non sono previsioni sismiche né aree di danno. La finestra osservata resta esplicita e indipendente dalla timeline meteorologica.
- **Rete alta tensione:** spuntare il livello e scegliere area locale intorno al centro (raggio 1 km, API OSM diretta) oppure area visibile (Overpass, fonte attualmente problematica). Filtri ≥35/132/220/380 kV, linee a tensione sconosciuta distinte, cavi interrati/posa sconosciuta, sottostazioni e sostegni. «Inquadra dati acquisiti» centra l’estratto. Il livello segnala quando la vista supera la copertura acquisita. Attivarlo disabilita le linee aeree del catalogo territoriale generale nel Monitoraggio, evitando una duplicazione iniziale.

**Limite concreto dell’alta tensione:** nell’estratto verificato dell’Aquila sono presenti 53 oggetti OSM (18 tralicci, 31 pali, una `power=line`, tre `power=minor_line`), tutti privi di `voltage`. Nessuno è presentato come AT verificata. La modalità regionale Overpass non ha completato l’acquisizione. Il livello dedicato e i filtri funzionano, ma un inventario AT locale completo e qualificato resta **BLOCKED**. Quote, freccia dei cavi, stato operativo e autorizzazione al volo non sono deducibili dai dati disponibili.

## Architettura e provenienza

Il termine «plugin» identifica qui moduli applicativi indipendenti, con un ciclo di visibilità e propri controlli/livelli. Non è stato aggiunto un caricatore di codice di terzi. Il traffico continua a usare `Traffic` e `trafficLayer`; i nuovi adattatori di consultazione usano `ObservedLayers` e `observedLayer`. HTTP e acquisizioni vengono eseguiti nella VM; Leaflet disegna nel browser. Nessun import dei nuovi adattatori nei worker fisici o nel solver. FIRE e FLOOD restano gli unici simulatori fisici integrati; AR-EXT-01 e separazione dati/modelli/decisioni preservati.

Le acquisizioni hanno ID indipendenti per richiesta: due schede non si sostituiscono reciprocamente il risultato. Cache persistente, una acquisizione attiva per tipo, risposte ≤8 MiB, cache ≤32 MiB per tipo, quote giornaliere 24 sismiche/8 elettriche e almeno 5 secondi fra nuove richieste. Cache sismica a finestre di 10 minuti, elettrica giornaliera. Massimo 1000 eventi sismici con avviso di limite; massimo 5000 oggetti elettrici, oltre il quale la risposta è rifiutata senza mostrare un inventario troncato. Nessun polling automatico del fornitore; la pagina interroga solo il job locale durante l’acquisizione esplicita.

Le richieste INGV sono ammesse nell’estensione documentata 6–19E,35–48N. Fuori viene richiesto USGS; non si interpreta un catalogo italiano vuoto come copertura mondiale. Anche USGS non garantisce piccoli eventi completi ovunque. I dati possono essere rivisti. Il formato testuale non fornisce qui incertezze complete né uno stato di revisione affidabile: non vengono inventati. I filtri di tensione usano volt OSM, anche valori separati da punto e virgola, senza inferire il voltaggio dalla forma della linea. Sottostazioni in relazioni OSM non acquisite: mancanza dichiarata.

Fonti gratuite e documentazione verificate:

- [INGV ISIDe](https://data.ingv.it/dataset/09), ISIDe Working Group (2007), DOI10.13127/iside: catalogo italiano, soluzioni automatiche e revisioni. [API ufficiali INGV](https://github.com/INGV/openapi), [politica di licenza del portale](https://data.ingv.it/docs/note-legali.html): attribuzione e CC BY4.0 salvo diversa indicazione. Attribuzione conservata, nessuna pubblicazione degli snapshot locali in GitHub.
- [USGS FDSN Event API](https://earthquake.usgs.gov/fdsnws/event/1/), [diritti d’uso USGS](https://www.usgs.gov/faqs/are-usgs-reportspublications-copyrighted): dati USGS di pubblico dominio, attribuzione al fornitore della soluzione conservata; non estendere la licenza automaticamente a contenuti terzi.
- [OpenStreetMap](https://www.openstreetmap.org/copyright), ODbL; [semantica power=line](https://wiki.openstreetmap.org/wiki/Tag:power=line) e [voltage](https://wiki.openstreetmap.org/wiki/Key:voltage). Modalità locale `api.openstreetmap.org/api/0.6/map`; modalità estesa Overpass. Nessuna garanzia di completezza o stato operativo.

## Esiti verificati

| Attività | Esito | Evidenza |
|---|---|---|
| INGV reale in Abruzzo/zone vicine | PASS |95 eventi tra16/10 13:20UTC e23/10 13:20UTC, M0,2–2,3,34 eventi sotto M1; nessuna riga scartata |
| INGV nella vista browser più ampia | PASS |156 eventi, finestra successiva13:30UTC, legenda e metadati visibili |
| USGS fuori Italia | PASS |84 eventi nella prova California, ultime24ore; query Abruzzo0eventi, distinta dal successo INGV |
| Inventario elettrico OSM locale | PASS tecnico |53 oggetti reali, 0 tensioni dichiarate; nella vista browser locale34 oggetti, 3 linee nel filtro iniziale |
| Acquisizione elettrica regionale | FAIL della fonte / BLOCKED copertura |timeout Overpass, prove alternative HTTP406/502/504; area più densa API OSM HTTP400. Esiti conservati, nessuna rete inventata |
| Filtri, cache, errori, input ostili, richieste distinte | PASS |78 test Python VM, inclusi10 nuovi;18 check JS sui filtri di visualizzazione |
| Coesistenza dei moduli | PASS |traffico38veicoli su1221archi, sismi e rete elettrica attivi insieme al meteo; pausa e disattivazione traffico verificate |
| Layout | PASS |1280×720 mappa1280×664;375×812 e768×1024 senza overflow; accesso al livello elettrico sul telefono |
| Integrità | PASS |311 file scientifici/workspace invariati e95job identici, nessuna simulazione avviata |
| Rete AT certificata, danni/intensità sismica | BLOCKED |fonti/attributi mancanti; non derivati dalla sola mappa |
| Nuova fisica, benchmark completo UI/Safari, nuovo carico combinato400veicoli | NOT RUN |limiti e gate scientifici precedenti invariati |

Le prove negative includono un primo controllo Node eseguito per errore in modalità CommonJS, poi ripetuto correttamente in modalità modulo; un primo selettore browser prematuro corretto dopo aver letto il DOM; le acquisizioni Overpass non riuscite sono conservate nel run.

## Prestazioni e comandi

Le nuove geometrie sono statiche e disegnate su Canvas, senza un nuovo ciclo animato. Il traffico riusa il limite400veicoli e il modello precedente. In una prova correlata del traffico con38veicoli e gli altri due livelli attivi: ultimi300campioni, p95 del solo disegno veicoli0,30ms, intervallo33,5ms. Non è una misura di FPS dell’intera dashboard, né del caso massimo5000oggetti/400veicoli.

Trenta letture locali sequenziali per ciascun risultato già acquisito: sismi95eventi/42.665byte p50~0,63ms,p95~0,88ms; rete53oggetti/44.441byte p50~0,61ms,p95~2,33ms. Misura nel guest, calda e correlata, non include rete esterna, rendering o simulazioni; nessun confronto con hardware precedente. Cache consultazione dopo le prove: rete~11,6MB (inclusi XML OSM grezzi), sismi~0,28MB.

Comandi principali nella VM, da `~/hazardia-runtime/app`:

```sh
PYTHONPATH=src:tests/unit:tests/web ../core-env/bin/python -m unittest test_observed_layers test_traffic test_recent_imagery test_consultation_cache test_radar_service test_map_navigation test_maps test_regional_satellite test_osm_tiles test_map_weather test_bootstrap test_fire_workspace test_fire_cases
```

Check client di sviluppo: `node tests/web/observed-layer-model.test.mjs`. API: POST `/api/monitoring/{earthquakes|power}/prepare`, poi GET `/api/monitoring/{earthquakes|power}?request=<id>`. Solo host loopback e richieste same-origin di ricerca. Nessuna installazione, servizio commerciale, cambio risorse o dispatch.

Evidenza grezza e snapshot con SHA256 in `experiments/runs/modules-power-quakes-20261023/` sul Mac e `~/hazardia-runtime/runs/modules-power-quakes-20261023/` nella VM. Estratto pubblicabile: `reports/modules-power-quakes/verification.json`; immagini locali nella stessa cartella report. Passo successivo per la rete: fonte AT con voltaggi e copertura verificati, o ripristino del servizio Overpass e nuova verifica regionale; non confondere un livello funzionante con un inventario certificato completo.
