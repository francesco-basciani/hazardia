# Pausa/ripresa e controlli sulla mappa — 20 ottobre 2026

Run `overlay-resume-20261020`, base `a0dd31d2e9214e3d93d67362634ffaf0e22a9b04` + modifiche, reviewer Codex self-check. Commit finale in Git/PUBLICATION.json. Correzione software/UX, nessun nuovo esperimento scientifico o job fisico.

## Difetto riprodotto e corretto

**FAIL prima della modifica:** dopo una pausa e due passi indietro sui risultati già caricati, il lettore si è fermato a37h con messaggio `renderTimeline(...).then is not a function` (`reports/overlay-resume/pre-fix.json`). Il rendering ritorna una Promise se deve caricare immagini; con i fotogrammi in cache ritorna invece un booleano. La continuazione del player presupponeva sempre una Promise. Le precedenti prove di riproduzione su fotogrammi ancora da caricare non esercitavano questo percorso: non bastavano a dimostrare una ripresa corretta a cache calda.

La continuazione ora normalizza il risultato con `Promise.resolve(renderTimeline())`: nessuna modifica al simulatore, alle forzanti o ai prodotti. Il controllo sullo stato attivo resta presente, così una continuazione già avviata non riattiva una riproduzione messa in pausa. Quando esiste un punto intermedio, il pulsante in pausa indica **Riprendi**; a inizio/fine orizzonte indica Riproduci. I pulsanti per ricalcolare scenari modificati restano distinti nel comportamento.

**PASS dopo la modifica, IAB:** pausa14,96155h; ritorno14,5h su cache; ripresa28,352975h ancora attiva, pausa28,382375h; seconda ripresa34,4066h ancora attiva. Nessun errore osservato. **PASS Safari nativo:** ingresso6,25h; riproduzione/pausa22,78h; ritorno22,5h; ripresa e pausa40,852h senza l'errore. Non sono nuovi risultati fisici: sono replay dei prodotti congelati del caso ottimizzato.

`node tests/browser/playback-resume.mjs`: **PASS38assert** sui veri handler play/pause estratti dal modulo, dipendenze controllate, rendering sincrono/asincrono, quattro pause/riprese per percorso e callback cancellate. Controllo negativo con la chiamata precedente: riproduce l'errore e l'arresto al campione. Harness di contratto del player, non emulazione del motore né prova di rete reale.

## Mappa e pannelli

Il tipo di simulazione è in un menu compatto nella stessa fascia di Piano/Confronto. La mappa comincia subito sotto quella fascia. Gestione scenari, palette, selezione e inquadrature sono nel pannello flottante **Scenari e risorse**; si chiude anche con Escape o clic esterno. Le opzioni interne si espandono dentro il pannello, con limite d'altezza e scroll. Nome/stato della mappa e indicazione Prova ipotetica sono piccoli elementi sovrapposti. Unica timeline nella parte bassa della mappa nominale, condivisa con le altre finestre e il meteo. Il nominale e l'ordine delle alternative non cambiano.

Riferimento Geospace riesaminato con browser, `https://wildfire.geospace.es/operational-map`: mappa e pannello di stato sovrapposto osservati; non dichiarata parità funzionale. Lettura web inizialmente non disponibile, fallback browser riuscito; nessun codice o asset copiato.

**PASS6record** DOM corroborati da screenshot (confronto e piano):

| Viewport | Inizio mappa, entrambe le viste | Larghezza×altezza | Overflow orizzontale |
|---|---:|---:|---|
|1440×1000|110px|1414×800px|assente|
|768×1000|163px|742×680px|assente|
|375×900|163px|365×680px|assente|

Confronto con la consegna precedente alla stessa larghezza1440:336→110px,226px recuperati sopra la mappa. Tablet421→163px; telefono419/467→163px. La misura riguarda la geometria dell'interfaccia, non la precisione o le prestazioni del modello. Timeline dentro la mappa in tutti i record. Palette mobile aperta con cinque categorie, nessuna unità inserita. Screenshot in `experiments/runs/overlay-resume-20261020`, riepilogo pubblicabile `reports/overlay-resume/verification.json`.

## Verifiche, negativi e limiti

- **PASS:**38assert player+20stato fronte/superficie+8stato schede,66totali; sintassi moduli fire-studio/ui-layout e `git diff --check`.
- **PASS:** due riprese IAB, ripresa a cache calda Safari; sei layout; menu mobile e chiusura con Escape; indicazione ricerca preservata.
- **PASS:** workspace principale revision119 e hash invariati;90directory job, nessun calcolo QA, installazione, restart backend o ampliamento risorse. Runtime nella VM esistente.
- **FAIL iniziali corretti:** menu interno poteva uscire a sinistra, ora espande nel drawer; legenda meteo Leaflet sopra i comandi, corretta isolando lo stacking della mappa e alzando il drawer sopra i controlli Leaflet, entro il contesto della mappa e sotto l'header.
- **FAIL harness, misure scartate:** handle di schede riassegnati ma funzioni di misura ancora legate alla vecchia scheda; utilizzati handle stabili e URL QA distinto. Coordinate di una misura fuori schermo non usate per azioni successive; ripresa verifica tramite AX e screenshot. Un timeout di navigazione recuperato sulla stessa scheda, health/JS200 verificati: non dedotto un difetto del backend da quel timeout.
- **BLOCKED solo ultimo refresh Safari:** Mac bloccato durante l'ultima chiamata UI; le prove Safari precedenti erano terminate. Non tentato alcuno sblocco o cambio di impostazioni. La consegna dei file nella VM non dipende dal refresh del client.
- **NOT RUN:** nuovo p95/FPS/soak/axe, drag/drop completo delle squadre, perdita rete pilotata, ricalcolo di scenari modificati dopo questa correzione, ulteriori prove Safari dopo il blocco del Mac, nuovi esperimenti fisici o validazione di efficacia.
- **BLOCKED invariati:** calibrazione, logistica/efficacia e gate scientifici M5–M7. Il piano ideale precedente conserva il criterio prudenziale8→8 e beneficio medio finale−1,094%; nessuna nuova efficacia dedotta dal player corretto.

Prossimo incremento scientifico invariato: qualificazione input/interventi e feedback fisico dell'ottimizzatore secondo il piano originale.
