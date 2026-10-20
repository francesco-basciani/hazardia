# Mappa principale e comandi compatti — 20 ottobre 2026

Run `map-first-20261020`; base `0c00e639bbf962cfc132211c4f1e6391ca6f10a6` + modifiche. Reviewer: Codex self-check; SHA finale in Git/PUBLICATION.json. Correzione di FR-24/26 e priorità alle mappe richiesta dall'utente; nessun cambiamento dei modelli o del piano M0–M7.

## Modifica verificata

Navigazione principale in una barra orizzontale, senza colonna permanente. Nello studio la selezione dello scenario resta visibile; creazione, duplicazione, ottimizzazione e livelli sono nel menu **Scenari**. Inneschi e categorie si aprono da **Aggiungi**, con menu nei bordi anche a375px. La selezione touch di Canadair chiude il menu e propone l'inserimento sulla mappa; il test ha annullato il disegno senza inserire unità. Le tre inquadrature sono nel menu **Vista**. Timeline e stato del risultato restano accanto alla mappa. Note del caso ipotetico sotto le mappe e indicazione Ricerca/Prova ipotetica in alto; ipotesi e limiti non rimossi.

La palette non sottrae una colonna fissa alla mappa. Nel piano, inventario/priorità e riepilogo sono sotto la mappa, con comando Mezzi per raggiungerli. Il Monitoraggio apre senza pannello laterale; **Livelli** lo apre/chiude mantenendo meteo, territorio e opzioni disponibili. Scenari e fisica non vengono alterati da queste scelte grafiche.

## Misure UI

Riepilogo DOM e prove manuali: `reports/map-first/verification.json`; screenshot locali `experiments/runs/map-first-20261020/{desktop,tablet,phone}.png`, esclusi dalla pubblicazione. Misure dopo ritorno all'inizio della pagina, non durante scroll/ancoraggio automatico.

| Vista | Viewport esterno | Larghezza mappa | Inizio mappa dalla sommità | Altezza mappa | Esito |
|---|---:|---:|---:|---:|---|
| Confronto desktop |1440×1000|1412px|336px|720px|PASS|
| Piano desktop |1440×1000|1412px|336px|720px|PASS|
| Confronto tablet |768×1000|740px|421px|520px|PASS|
| Piano tablet |768×1000|740px|421px|520px|PASS|
| Confronto telefono |375×900|363px|419px|520px|PASS|
| Piano telefono |375×900|363px|467px|520px|PASS|

Nessun overflow orizzontale nei sei record. Monitoraggio desktop:1414×715px, inizio236px; telefono365×585px, inizio413px; pannello chiuso. Con Livelli aperto su desktop, mappa1112px e pannello disponibile; chiudendolo riacquista larghezza. Non sono confronti quantitativi prima/dopo su identica configurazione: il riferimento iniziale è lo screenshot dell'utente.

## Registro delle verifiche

- **PASS:** menu Aggiungi,5categorie reali; scelta Canadair e annullamento senza inserimento; menu Scenari con comandi originali; Vista con3inquadrature; passaggio Piano/Confronto; apertura/chiusura pannello del Monitoraggio.
- **PASS:** riproduzione nativa esistente0→13,2999h, pausa, orizzonte72h; nessun nuovo calcolo fisico. Non è una nuova prova di accuratezza.
- **PASS:** `node tests/browser/fire-comparison-status.mjs`20assert e `node tests/browser/studio-view-state.mjs`8assert; sintassi moduli fire-studio/intervention-plan/clean-room, `git diff --check`.
- **PASS:** workspace principale revision119 e hash identici alla consegna precedente;90directory job osservate, nessun nuovo job di QA. Nessun restart backend, installazione, nuova risorsa o spesa; runtime unico nella VM esistente.
- **FAIL iniziale corretto:** altezza basata sul viewport dell'iframe senza massimo causava una retroazione tra autoresize e altezza mappa. Aggiunti limiti720px desktop/520px mobile; rilanciati controlli di geometria e centratura. Non lasciata una mappa infinita per aumentarne artificialmente la quota visibile.
- **FAIL harness:** click Playwright IAB non riusciti; azioni proseguite con accessibilità nativa. `contentDocument` non disponibile nel bridge DOM: misure separate di parent e iframe. Resize conservava l'ancora di scroll: i record intermedi fuori pagina scartati, misure finali dopo ritorno in alto.
- **NOT RUN:** nuova matrice axe, benchmark FPS/p95/soak, drag/drop completo dopo questa riorganizzazione, prove su device fisici e nuova verifica Safari. Non vengono dichiarati PASS da test precedenti.
- **BLOCKED invariato:** calibrazione, efficacia/logistica reali, inventari completi e gate scientifici M5–M7; il beneficio limitato e criterio prudenziale8→8 dei report precedenti non cambiano.

Prossimo incremento scientifico invariato: qualificazione di input/interventi e feedback fisico dell'ottimizzazione secondo il piano originario. Questa modifica riguarda l'impaginazione e la raggiungibilità degli stessi comandi.
