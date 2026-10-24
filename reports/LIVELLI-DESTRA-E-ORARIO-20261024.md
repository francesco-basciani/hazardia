# Livelli e orario monitorato — 24 ottobre 2026

## Esito
PASS tecnico UI. Modifiche distribuite nella VM unica; backend, motori, forzanti, contratti e risultati scientifici invariati.

- PASS: lista a sinistra, parametri separati a destra. Desktop 1011×1034 e mobile 375×812 verificati; mobile alterna elenco e parametri, senza overflow orizzontale.
- PASS: nove categorie OSM esistenti elencate individualmente, senza “Altri livelli territoriali”; 19 interruttori e 20 righe, inclusa la consultazione del catalogo. Riusati input e listener esistenti, nessuna nuova acquisizione automatica.
- PASS: ora monitorata con data, secondi, offset UTC e indicazione futura; orologio attuale separato. Il badge segue la timeline condivisa senza cambiarne i dati. Dati temporali assenti restano esplicitamente indisponibili.
- PASS: 11 suite client e sintassi di tutti i moduli JS. Test nuovo: `node tests/browser/monitor-clock.mjs`, incluso cambio dell’ora con due istanti diversi che mostrano entrambi 02:30.
- PASS: conservati 311 file scientifici, 95 righe job e 145 file motori, controllo hash e confronto DB in sola lettura.
- NOT RUN: nuova installazione VM, qualificazione fisica, benchmark prestazionale quantitativo e lifecycle completo della cache avanti/indietro del browser. Nessuna nuova acquisizione o simulazione scientifica richiesta da questo incremento.

## Problemi osservati e correzioni
Il formatter `shortOffset` non funziona sull’ICU del Node 16 disponibile: calcolo esplicito dell’offset dalla timezone e prova DST passano. Su mobile la legenda Leaflet (z-index 1000) copriva il pannello (920), intercettando i clic: pannelli a 1100 e legende inferiori nascoste durante l’apertura mobile; clic su Edifici verificato corretto. Una prima esecuzione dell’audit conservazione aveva un percorso runtime errato; ripetuta sul percorso corretto con PASS. Nessuna scorciatoia basata su ritardi o blocco dei clic mantenuta.

## Tracciabilità
Evidenze: `reports/domain-evolution/{checkpoint,client-tests,preservation,verification}.json`; schermate locali `desktop.png` e `mobile.png` nella stessa cartella. Le schermate non sono incluse nell’export pubblico standard.

Checkpoint remoto precedente alle modifiche: `stable-2026-10-24-pre-domain-evolution`, commit pubblico `4bdd161166724a641e45dca08cb9c514684609bc`; 633 file verificati mediante clone indipendente.

Prompt corretto: `docs/tasks/DOMAIN-AGNOSTIC-EVOLUTION.md`. Audit e design Stage 1: `reports/EVOLUZIONE-DOMINI-DESIGN-20261024.md`. Stage 2 NOT RUN: il prossimo incremento proposto è discovery locale in sola lettura di descrittori FIRE/FLOOD, senza sostituire il dispatch. Il checkpoint indica stabilità del software di ricerca, non efficacia operativa certificata.
