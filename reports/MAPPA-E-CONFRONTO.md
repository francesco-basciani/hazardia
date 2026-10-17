# Mappa e confronto visuale

Run `map-workbench-20261017`, base privata `2761f5c3a30d4bbd46f3ce3050df03e0030ce982`, reviewer Codex self-check. Incremento di UI entro il piano originale (SPEC§8,FR-FIRE-WORKSPACE-01,AR-EXT-01; M3/M7). Identità HAZARDIA generica preservata, intervento concreto sul modulo di simulazione già esistente. Nessuna nuova architettura o dipendenza.

## Riferimento e modifica

La pagina pubblica [Technosylva Wildfire Operations](https://technosylva.com/products/wildfire-operations/) e l'immagine indicata dall'utente suggeriscono la lettura cartografica di livelli e il confronto tramite separatore. Riferimento consultato il17ottobre2026: sezione “Choose your view”, immagini prima/dopo. L'ispirazione riguarda l'interazione; le caratteristiche commerciali e scientifiche dichiarate da quel produttore non sono risultati di HAZARDIA.

Nella stessa sezione **Simulazioni e risorse**:

- mappa centrale, strumenti cartografici sul bordo, pannello **Scenari e livelli** richiudibile; creazione di scenari e selezione della configurazione da modificare restano immediatamente accessibili;
- **Sovrapposizione** mostra gli scenari spuntati con colori distinti; **Separatore** mostra due risultati selezionabili, con la stessa ora simulata, separati da una maniglia trascinabile;
- opacità dei risultati regolabile nel pannello livelli; timeline e comandi riuniti sotto la mappa;
- icone SVG locali coerenti per inneschi e categorie, editor della geometria sulla mappa, mantenimento di drag/drop, vertici, play/pausa/rewind, più scenari e salvataggio nella VM;
- componenti, spaziatura, gerarchia dei pulsanti e schede della piattaforma riordinati; opzioni secondarie e istruzioni spostate nel pannello contestuale.

Come provarlo: scegli **Separatore**, seleziona gli scenari Sinistra/Destra, porta la timeline su un'ora calcolata e trascina la maniglia. Tastiera: frecce a passi2%, Shift+freccia10%, Home/End0/100%. La vista a ora0 non inventa un frame. Un risultato mancante o una bozza modificata hanno indicazione esplicita; i risultati precedenti restano distinguibili.

## Integrità dei risultati

Il confronto usa gli stessi PNG georiferiti e verificati già prodotti dai job reali nella VM. `raster-comparison.js` è un helper esclusivamente visivo: il taglio segue le coordinate di schermo delle immagini Leaflet anche durante pan, zoom e resize. L'opacità è una proprietà visuale. La modalità separatore conserva la colorazione nativa; la sovrapposizione distingue i livelli cromaticamente mantenendo la trasparenza del raster. Nessuna area o probabilità viene ricalcolata o ridotta per ottenere un effetto estetico. Le geometrie editabili appartengono allo **scenario da modificare**; i risultati visualizzati appartengono ai livelli o alla coppia selezionata.

Tutti i servizi e gli asset continuano a provenire dalla stessa VM. Distribuzione di5file statici, nessun riavvio, installazione, sostituzione di modelli o nuova simulazione. Restano i limiti già registrati su fuel reale, moisture e calibrazione, logistica/efficacia, scala e validazione. Il confronto grafico non qualifica la fisica.

## Verifiche

Raw locale: `experiments/runs/map-workbench-20261017/`; riepilogo pubblico `reports/workspace/map-workbench-verification.json`.

| Verifica | Esito | Evidenza |
|---|---|---|
| URL dei frame identici ai prodotti nativi | PASS | browser-delivery; confronto con serie dei job |
| Taglio0/50/100%, mouse, tastiera, pan/zoom/resize | PASS | browser-delivery; errore osservato del bordo inferiore a0.01pixel nelle misure campionate |
| Opacità e ripristino dei livelli sovrapposti | PASS | browser-delivery |
| Nessun frame inventato a0h o per scenario non calcolato | PASS | browser-delivery, caso negativo con risposta workspace intercettata nel browser |
| Responsive375/721/1440/1920 | PASS | Nessun overflow orizzontale della pagina, mappa in vista prima di800px nello scenario verificato |
| Accessibilità automatica | PASS |8scansioni axe pagina/componente del nuovo confronto,0violazioni; altre6nella regressione interattiva |
| Touch su375px | PASS |5controlli in touch-delivery, gesto reale emulato via Chrome DevTools; maniglia al75%, pannello apribile/chiudibile |
| Workflow precedente | PASS |29controlli in interaction-regression-v2: drag/drop, aree/vertici, tempo eventi, più scenari, timeline, persistenza |
| Conservazione configurazioni/job | PASS | Nuovo confronto non scrive workspace e non crea job; regressione modifica fixture e la ripristina |
| Hash VM e sorgenti/modelli | PASS | runtime-verification.json nel raw |
| Primo adattamento harness al pannello chiuso | FAIL | interaction-regression: attesa di un elemento nascosto; preservato e corretto con attesa inizializzazione/apertura esplicita |
| Nuovi run fisici, benchmark p95/soak, user study | NOT RUN | Modifica di visualizzazione; nessuna conclusione di efficacia/usabilità misurata |
| Safari/Android/dispositivi fisici | NOT RUN | Il touch verificato è emulazione Chrome |
| Gate scientifici completi M5–M7 | BLOCKED | Invariati |

Il nuovo confronto conta46controlli browser,5touch e29del workflow preesistente:80asserzioni, incluse14scansioni axe. La verifica automatica e la revisione degli screenshot non dimostrano da sole che l'interfaccia raggiunga il livello estetico o l'usabilità di un prodotto commerciale.

Riproduzione, dalla root con runtime VM già acceso e una workspace di test con almeno due risultati completati:

```sh
HAZARDIA_PLAYWRIGHT_PATH=/percorso/playwright \
HAZARDIA_BROWSER_EXECUTABLE=/percorso/chrome \
HAZARDIA_AXE_PATH=/percorso/axe.min.js \
node tests/browser/map-workbench.cjs /cartella/evidenze

HAZARDIA_PLAYWRIGHT_PATH=/percorso/playwright \
HAZARDIA_BROWSER_EXECUTABLE=/percorso/chrome \
node tests/browser/map-touch.cjs /cartella/evidenze-touch
```

`tests/browser/fire-sandbox.cjs` resta la regressione del workflow e richiede una fixture isolata senza altri client che modifichino la workspace durante la prova. Il confronto visuale non espone frame di job incompleti, non riparte da checkpoint e non introduce streaming del simulatore.
