# Simulazioni e risorse: innesco e squadre

Run: `fire-workspace-20261017`, base privata `592e911328a4095a2330ef8ad52b3cb1cee77419`, reviewer Codex self-check. Incremento UI autorizzato dall'utente. Backend e fisica nella stessa VM; nessuna installazione o nuova acquisizione dati.

## Flusso consegnato

Apri **Simulazioni e risorse → Incendio · innesco e squadre**. Scegli innesco e durata. Nella parte **Posiziona le squadre** scegli categoria e minuti dall'innesco, lunghezza e orientamento della linea ipotetica. Premi **Posiziona squadra sulla mappa B**, poi fai un solo clic sulla mappa B: compare un indicatore numerato e una linea blu centrata nel punto scelto. Si possono cambiare categoria/tempo, spostare o rimuovere le unità. **Esegui i due scenari** avvia i job esistenti: A senza interventi, B con le unità. Modificare la bozza non modifica risultati già calcolati: occorre rieseguire.

Il precedente studio è ora un componente incorporato nella sezione principale: documento same-origin per isolare CSS e ID Leaflet, altezza adattiva e messaggi controllati per origine e finestra sorgente. Nessuna nuova scheda. I vecchi link migrano alla dashboard conservando i due job. L'altro pannello della stessa sezione conserva il laboratorio di evacuazione con allocazione risorse. Le bozze sopravvivono al cambio di sezione, non a un ricaricamento completo; i job completati restano riapribili.

La CSP consente `frame-ancestors 'self'` esclusivamente per `/fire-studio.html`; dashboard/API conservano `frame-ancestors 'none'`. Script esterni e incorporamento da altri siti restano esclusi. Il componente non richiede nuove dipendenze.

## Verifiche

Evidenza locale immutabile: `experiments/runs/fire-workspace-20261017/` (non redistribuita con lo snapshot pubblico). `plan.json` precede le modifiche; `runtime.json` contiene hash delle 7 sorgenti distribuite e header osservati.

- PASS: ripristino del confronto nativo precedente; navigazione integrata, aggiunta con un clic, modifica categoria/tempo, spostamento, annullamento, conservazione della bozza fra sezioni, laboratorio evacuazione conservato.
- PASS: corpo POST intercettato prima dell'accodamento, categoria/tempo/2 estremi e contratto nativo invariati. Nessun nuovo risultato fisico dedotto da questa intercettazione.
- PASS: responsive 375/724/1440px senza overflow orizzontale, scansioni axe su componente e pagina principale, nessun errore JS nel flusso verificato. Risultati finali in `final/verification.json` e `final/axe*.json`.
- PASS: 14 regressioni web eseguite nel core-env della VM (`web-tests.log`); hash runtime e CSP per 3 route.
- FAIL conservati: primo tentativo di redirect inline rifiutato dalla CSP; componente inizialmente bloccato da frame-ancestors none. Risolti con modulo esterno e eccezione same-origin limitata alla singola route. Errore del primo harness axe (iniezione inline vietata) corretto servendo lo script di sola verifica da una route intercettata dal browser: nessuna modifica CSP per i test. Primo ridimensionamento manteneva spazio vuoto dopo il passaggio da mobile a desktop; corretto misurando l'altezza del body.
- NOT RUN: nuove simulazioni native, nuovo benchmark prestazionale, studio di usabilità con utenti; questo incremento cambia configurazione e collocazione della UI. Le prove native precedenti restano quelle del report INNESCO-SQUADRE-E-DEGRADAZIONE.
- BLOCKED invariati: qualificazione efficacia delle categorie, vegetazione reale, accoppiamento T/RH/pioggia→umidità combustibile, validazione storica e gate completi M5–M7. Lunghezza/orientamento non sono prestazioni certificate del mezzo.

Riproduzione (Node/Playwright e Chrome già disponibili; runtime VM acceso e coppia precedente qualificata come fixture UI):

```sh
HAZARDIA_PLAYWRIGHT_PATH=/percorso/node_modules/playwright \
HAZARDIA_BROWSER_EXECUTABLE=/percorso/chrome \
HAZARDIA_AXE_PATH=/percorso/axe.min.js \
node tests/browser/fire-workspace.cjs /cartella/evidenze /percorso/accepted.json
```

`accepted.json` deve contenere `{"jobs":{"A":"job-…","B":"job-…"}}` riferiti a una coppia fisica completata, con almeno una risorsa B. Il test non esegue nuovi job e salva il payload intercettato. Gli script storici `fire-studio*.cjs` sono allineati alla modalità incorporata; la ripetizione nativa completa di quegli script resta NOT RUN per questo incremento.
