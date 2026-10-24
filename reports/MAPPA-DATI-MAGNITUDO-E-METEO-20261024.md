# Mappa: magnitudo, precipitazioni, nuvole e audit dati —24ottobre2026

Run `map-data-semantics-20261024`; base76a55bd+dirty, reviewerCodexself-check. Servizio, fonti, cache e calcoli geospaziali nella VM esistente; test dei moduli JavaScript sul client di sviluppo, verifica visiva nel browser integrato. Nessuna modifica ai simulatori, ai parametri fisici o all’ottimizzatore.

## Simboli e variabili

**PASS — terremoti.** Raggio sullo schermo `3 + 2 × max(0,min(9,M))` pixel, sempre visibile; colori: M<1 ciano,1–<2 verde,2–<3 giallo,3–<4 arancio,4–<5 rosso,≥5 viola. Legenda di sei cerchi di dimensioni e colori diversi nel pannello e classi nella legenda della mappa. Un’unica funzione fornisce lo stile reale e i campioni. Questo è un simbolo cartografico: non misura area di danno, intensità avvertita o energia. Catalogo reale verificato215eventi, M0,2–2,9: le classi maggiori sono definite ma non vengono inventati eventi per riempirle.

**PASS — precipitazioni.** Scelte alternative esplicite: nessuna, quantità prevista in mm nella prossima ora, probabilità in%. La probabilità usa il campo ensemble reale `rain_probability`, non è dedotta dai mm o dalle nuvole. Ha una propria sovrapposizione graduata, legenda e indicatori%; <5% trasparente, non sinonimo di impossibilità di pioggia. La transizione dell’opacità è continua alla soglia. Nel modulo simulazioni le stesse alternative usano il renderer condiviso; snapshot storici senza probabilità restano n/d, senza inventarla.

**PASS — nuvole.** Checkbox indipendente dalle precipitazioni. Velo bianco/grigio neutro, trasparenza modulata dalla copertura nuvolosa prevista%; colori pioggia/probabilità separati. In combinazione il velo viene attenuato per leggere entrambi. È una rappresentazione del modello, non una foto satellitare né una ricostruzione delle singole nubi a risoluzione stradale. La griglia visuale viene interpolata: non aumenta la risoluzione meteorologica. Nessuna nuvola viene interpretata automaticamente come precipitazione. Le immagini satellitari osservate restano un livello diverso.

## Audit dei dati effettivi

| Livello/componente | Esito | Evidenza e limiti |
|---|---|---|
| Meteo della vista | PASS | FRESH,95record orari, tutte le10componenti scalari/vettoriali presenti: T/UR/nuvole/pioggia/probabilità/raffiche/pressione/radiazione/u/v; snapshot `map-weather-c39eb05c0c283d8c7482e2ae`, copertura39,2–44,5N/9,8–17,1E. Campioni circa74×75km alla scala della vista, modello nativo~11km; non confondere queste due risoluzioni |
| Meteo puntuale | PASS | Endpoint FRESH; fonte reale, punto L’Aquila, non copertura distribuita |
| Vento regionale fine | BLOCKED | STALE, `WEATHER_CACHE_FULL`. Il vento globale della vista è FRESH e disponibile. Nessuno snapshot cancellato né quota aumentata per nascondere il limite |
| EFFIS | PASS | Prodotti FRESH24/25ottobre; FWI/DC previsionali. Non eventi incendio osservati, non rischio d’impatto qualificato |
| DPC | PASS tecnico / copertura parziale | Bollettino del24ottobre valido; prodotto23ottobre scaduto conservato come tale. Il servizio resta PARTIAL, non interamente nominale |
| Accumuli per zona | PASS | Calcolo reale SUCCEEDED/FRESH per24ottobre09UTC sullo stesso campo meteo,187geometrie DPC;77zone hanno finestra24h completa nel campo acquisito, altre incomplete/fuori copertura. Bollettino ufficiale AVAILABLE per l’ora iniziale. Quantità di pioggia non trasformata in un’allerta idraulica HAZARDIA non validata |
| Radar osservato | PASS | Radar-DPC SRI24ottobre08:40UTC, nominale1km, mosaico valido49,288%, pioggia positiva1,7% del mosaico. PNG osservato e maschera mancanti scaricabili. Nessuna previsione radar futura |
| Pluviometri | PASS dopo aggiornamento | Inizialmente STALE/0stazioni fresche: refresh reale24ottobre09:03:29UTC →4039stazioni nel payload,3976fresche, errore assente. Le restanti non diventano misure attuali. Fonte MeteoHub/ItaliaMeteo |
| Terremoti | PASS | INGV,215eventi nell’area visualizzata, finestra17ottobre09UTC–24ottobre09UTC, acquisizione24ottobre09:04:03UTC. Cataloghi rivedibili, piccoli eventi secondo rilevabilità, nessuna previsione sismica |
| Sentinel recente | PASS | Nuova ricerca reale:23ottobre10:00:41UTC, nuvolosità tile54,35%;21ottobre10:00:41UTC,99,46%. Due JPEG accessibili, SHA coerenti. Quicklook separati dallo sfondo, non raster analitici georettificati |
| Rete elettrica | PASS locale, BLOCKED completezza/certificazione | Estratto OSM24ottobre09:03:11UTC,192oggetti,187senza tensione. Tre linee dichiarate150kV, una sottostazione150kV e una132kV. Area13,43795–13,46208E/41,87285–41,89081N, non intera regione. Quote, frecce, stato operativo e clearance volo assenti. Estratto storico aggiuntivo201oggetti con una linea150kV verificato; non spacciato per aggiornamento corrente |
| Strade/traffico ipotetico | PASS | Configurazione salvata,1221segmenti diretti OSM disponibili; XML sorgente SHA verificato. Non flussi osservati, code o tempi di evacuazione |
| Sfondi | PASS tecnico | OSM, EOX Sentinelcloudless e ortofoto rispondono; cache e download ammessi. Date degli sfondi distinte dalle immagini recenti. Non garantisce disponibilità upstream futura o ortofoto fuori Abruzzo |
| Territorio/esposizione esistente | PASS disponibilità tecnica / qualità parziale | Cataloghi OSM/GeoNames/WorldCover già integrati, con proprie date e coperture. Inventario elettrico e sorgenti hanno hash verificati. NOT RUN nuovo download di ogni categoria OSM o nuova stima di popolazione; strutture cartografate non implicano occupazione/capacità sanitaria disponibile |
| Scenari e risorse | PASS preservazione / NOT RUN nuovi job | Nove prodotti nel catalogo, casi salvati e95job invariati; sono risultati datati, non eventi osservati di oggi.311file e pin motori verificati. Nessuna nuova propagazione o ottimizzazione avviata per un controllo grafico |
| Hotspot satellitari live | BLOCKED | MAP_KEY FIRMS assente; assenza di dati non significa assenza di incendi |
| Perimetri incendio osservati locali, idrometri, popolazione/vulnerabilità qualificate | BLOCKED | Dati/connessioni o qualificazione ancora mancanti; non sostituiti con simulazioni o geometrie arbitrarie |
| Traffico osservato e chiusure verificate, fulmini/webcam/air-quality/mezzi aerei reali | NOT RUN / non integrati | Nessun controllo nominale introdotto senza dati; traffico visuale e risorse ipotetiche restano distinti |

Non tutto il framework dispone quindi di un feed attuale o di dati qualificati. La verifica distingue dati reali disponibili, cache datate, dati mancanti e simulazioni. I limiti scientifici/operativi M5–M7 restano BLOCKED.

## Verifiche e ripetibilità

PASS17suiteJavaScript, incluse magnitudo finite/null/boundary, colori per classe, raggio monotono, composizione pioggia/probabilità/nuvole, zero e missing, timer comune, cache/code di immagini e traffico. Comandi principali:

```sh
node tests/web/observed-layer-model.test.mjs
node tests/browser/cloud-probability.mjs
node tests/browser/weather-render-plan.mjs
```

PASSbrowser effettivo: probabilità+nuvole produce7412pixel probabilità/15621nuvole/0pioggia; quantità+nuvole1549pioggia/15621nuvole/0probabilità; solo nuvole15621/0/0. Stesso snapshot e orario, nessuna conversione fra variabili. Legenda sismi: diametri6/10/14/18/22/26px per i campioni M0/1/2/3/4/5. Nessun erroreconsole. Mobile375×812, pannello destro350×531px e nessun overflow del documento. Il primo controllo mobile troppo ravvicinato al resize ha osservato il pannello chiuso; ripetuto dopo l’assestamento della media query, pannello visibile correttamente. NOT RUN Safari/caricoend-to-end.

PASS5controlli d’integrità:2JPEG Sentinel/SHA,2PNG radar osservato/mancanti, XML stradale/SHA. Snapshot osservati elettrici/sismici salvati confrontati con gli hash sorgente. PASS311file/95job/pinCIMA invariati dopo acquisizioni e calcoli; nessuna sostituzione fisica o nuova dipendenza. Limiti/quote restano invariati.

Raw privati: `experiments/runs/map-data-semantics-20261024/` e run omonimo nel guest, preregistrazione e script audit. GETsu14servizi esistenti, acquisizioni bounded Sentinel/radar/pluviometri, rete stradale da cache, valutazione accumuli su fonti già presenti. Estratto pubblico `reports/map-data-semantics/verification.json`. Screenshot locali `quakes.png`, `probability-clouds.png`, `clouds-only.png`, `delivery.png`, `mobile.png`.

Riproduzione con probabilità+nuvole+vento e sismi: conclusa automaticamente al termine dell’orizzonte27ottobre22UTC;120campioni correlati conservati, p95lavoro per frame10,7ms. Non è il frame-rate totale né un benchmark operativo. Nessun riavvio forzato: il pulsante a fine orizzonte torna Riproduci.

PASS studio integrato sul caso salvato optimized-physical-fonte-vetica-20261019: attivando probabilità e nuvole, i due risultati congelati18ottobre mostrano esplicitamente DATI MANCANTI NELLO SNAPSHOT per la probabilità, mentre la nuvolosità è presente(1% al centro). Nessuna probabilità inventata o nuovo calcolo fisico; tabQA temporanea chiusa.
