# Zoom esplicito e pin di navigazione —25ottobre2026

Run `map-pin-zoom-20261025`, baseline `302c49f6ea8ff9b4b07943a9037f2ce6ee666203`, reviewer Codex self-check. Incremento UI Monitoraggio; nessun nuovo dominio, provider o cambiamento scientifico.

Accanto a +/−/Centra compare il selettore dello zoom corrente, con livelli interi2–20 filtrati ai limiti effettivi della mappa; zoom15 riporta Edifici, richiamando la soglia cartografica già implementata senza attivare automaticamente il layer. Scegliere un livello centra il pin quando presente; senza pin conserva il centro. Centra con pin conserva lo zoom; senza pin mantiene la precedente azione sulle aree disponibili. +/−/rotella continuano ad aggiornare il numero mostrato.

L’ispezione puntuale esistente ora rappresenta un pin distinto, visibile e trascinabile; si può posizionare con l’apposito pulsante e clic sulla mappa, con un clic diretto o dalla ricerca. Un solo pin, sostituito ad ogni nuova scelta; × lo elimina e ripristina il comportamento senza pin. Dragend aggiorna lo stesso riferimento di navigazione. Il pin ha voce esplicativa nella legenda e NON è un innesco, un evento osservato o una risorsa; non viene serializzato nei contratti scientifici o persistito dopo reload.

FAIL esplorativo corretto: una scelta di zoom durante l’animazione della ricerca poteva essere sovrascritta dalla conclusione dell’animazione precedente. Nel Monitoraggio la ricerca e i salti di scala ora sono immediati, zoomAnimation disabilitata come già negli studi; non modifica animazioni meteo, timestep, playback o dati fisici. Ripetuta la sequenza ricerca→Zoom15 nello stesso batch: stato/centro/selettore coerenti.

PASS4suite client pure su Mac: `node tests/browser/{map-navigation,i18n,monitor-clock,layer-menu-model}.mjs`; selezione pin/no-pin, limiti e rifiuto NaN/Infinity/fuori-range, soglia15 e compatibilità i18n/clock. Raw `experiments/runs/map-pin-zoom-20261025/tests.log`.

PASS browser integrato1011×1034: ricerca42.35,13.40→Zoom15; centro[42.35,13.4], zoom15 e un solo marker. Dopo pan tastiera centro[42.34999695373878,13.403427600860597], pin immutato; Centra ripristina esattamente[42.35,13.4] a15. Rimozione produce0marker e nessun pin; pulsante pin+clic mappa produce1marker e termina modalità inserimento. PASS390×844/EN: selezione16 riporta centro al pin[42.349981095582905,13.400015830993654], DOM marker-draggable presente, nessun overflow orizzontale. Italiano e zoom15 ripristinati. Screenshot locali `reports/map-pin-zoom/{delivery,pin15,mobile-en}.png`, esclusi pubblicazione curata.

NOT RUN gesto manuale di trascinamento, Safari nativo, replay fisici e nuovi benchmark; attivazione drag osservata nel DOM non equivale a prova end-to-end del gesto. Non si dichiara copertura OSM completa: acquisizioni e quote territoriali restano quelle esistenti. Nessun nuovo polling, backend, pacchetto, limite scientifico o autorizzazione operativa. Gate M0–M7/FAIL REFlEx invariati.
