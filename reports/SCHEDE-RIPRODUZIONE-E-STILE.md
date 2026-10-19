# Schede, riproduzione Safari e cornici — 19 ottobre 2026

Run `tab-playback-20261019`, base `2f9f7808df292b203b9e278bf81bb4638936f9bd` + modifiche; commit finale in Git/PUBLICATION.json. Reviewer: stesso agente Codex. Diagnosi esplorativa successiva alla segnalazione, nessun nuovo esperimento fisico.

## Risultato osservato

La VM serve più browser contemporaneamente. Il server è `ThreadingHTTPServer`; la riproduzione dei risultati ha un cursore locale alla scheda. Il worker dei calcoli fisici è invece unico e i nuovi job sono accodati. Due client HTTP concorrenti nella VM hanno ricevuto i PNG richiesti con checksum corretti in 0,02475 s complessivi: prova funzionale, non benchmark di carico né prova di due simulazioni fisiche simultanee.

Due schede IAB sullo stesso caso sono rimaste indipendenti: prima 10→10,981475 h in riproduzione, seconda ferma a10 h; reload seconda ancora10 h. Non esiste un cursore della VM occupato da Codex.

**Safari controllato direttamente:** la scheda reale non era nel caso `optimized-physical-fonte-vetica-20261019`, ma nel workspace principale, con parametri URL legacy `a`/`b`. Questi non sostituiscono un workspace già salvato. Il nominale effettivo era `job-00a07daae47d42318502b8bc5b074114`, non il vecchio job citato nel parametro `a`. Primo controllo erroneamente indirizzato ai job nell'URL: erano storici da3h; corretto interrogando `/api/fire-workspace` e gli ID effettivi. Non si attribuisce quindi quel risultato storico al caso visualizzato.

In Safari il tempo è avanzato da2,822832 a11,334 e16,829h, con meteo variabile e stato «fronti esauriti». L'audit degli output effettivi conferma:

| Scenario nel workspace | Ultima variazione della superficie | Primo campione con zero fronti | Area media finale |
|---|---:|---:|---:|
| Senza interventi |5,25h|5,25h|1,53ha|
| Scenario 1 |4,25h|4,25h|1,215ha|
| Scenario 3 |0,25h|0,25h|0,09ha|

Tutti hanno288campioni fino72h e2realizzazioni;864NPZ verificati perSHA. È un risultato del modello su quegli input, non un blocco del lettore né prova che la previsione sia accurata. Non è stata isolata la causa fisica dell'esaurimento né calibrata l'inizializzazione.

Aperto poi **lo stesso caso ottimizzato anche in Safari**: ingresso0h, Riproduci0→21,06825→25,7775h; a25,75h aree376,50/376,41ha e meteo sincronizzato. Nessun arresto a3h osservato in questa prova. Il fronte non viene artificialmente esteso per rendere più evidente l'animazione. I limiti del piano (indice prudenziale8→8 e beneficio medio finale−1,094%) restano quelli dei report precedenti.

## Correzioni

- Una nuova navigazione allo studio parte da0h, anche se la prova salvata aveva `initial_hour=72` o la nuova scheda eredita una copia della sessione. Reload e cronologia conservano il tempo della stessa scheda. Il recupero di un calcolo attivo con punto di ripresa valido resta preservato.
- Comando **Inizio** per tornare a0 senza ricalcolare. Unico Riproduci condiviso da incendio e meteo.
- Errori inattesi del ciclo asincrono/animazione riportano il lettore in pausa con messaggio visibile. Nessun errore del genere riprodotto in Safari; non viene presentato come causa accertata della segnalazione.
- Cornici neutre grigio azzurro, intestazioni bianche, nessuna ombra verde. La selezione resta distinta, senza cambiare i colori scientifici degli scenari.

## Registro delle prove

| Attività | Esito | Evidenza |
|---|---|---|
| Due richieste HTTP concorrenti, checksum PNG | PASS | `reports/tab-playback/verification.json` |
| Indipendenza cursori e reload scheda IAB | PASS | `reports/tab-playback/ui-verification.json` |
| Nuova navigazione0h, reload/history e recupero batch | PASS | `node tests/browser/studio-view-state.mjs`,8assert; ingresso Safari0 e reload16,829 |
| Ritorno Inizio0h Safari | PASS | verifica AX nativa, riepilogo UI |
| Riproduzione Safari oltre3h e crescita nel caso ottimizzato | PASS | osservazioni native0→25,7775h, superficie campionata e meteo |
| Audit workspace effettivo72h/288frame | PASS | `reports/tab-playback/safari-workspace.json` |
| Cornici e layout ai viewport esterni375/768/1440 | PASS | larghezze iframe355/556/1188, nessun overflow, comandi alti44px; riepilogo UI |
| Regressioni stati fronte e superficie campionata | PASS | `node tests/browser/fire-comparison-status.mjs`,20assert |
| Sintassi modulo principale | PASS | `node --input-type=module --check < src/hazardia/web/static/fire-studio.js` |
| Primo tentativo reload con navigation type dell'iframe | FAIL corretto | azzerava al reload del parent; ora legge navigation type del parent, reload10h verificato |
| Primo harness layout su scheda inattiva / locator IAB | FAIL harness | campioni ripetuti701px scartati; misure rifatte sulla scheda attiva. Locator click fallito, verifica UI proseguita tramite AX nativo |
| Input artificiale di eccezione nel lettore | NOT RUN | gestione aggiunta, nessun errore reale osservato |
| Nuova fisica, calibrazione, ablation esaurimento fronti, p95/FPS/soak/axe | NOT RUN | fuori da questa diagnosi |
| Qualificazione scientifica/operativa M5–M7 | BLOCKED invariato | efficacia, logistica, skill e inventari incompleti |

Nessuna nuova dipendenza, installazione, cambio risorse, restart backend o job fisico. Runtime nella VM esistente; browser sul Mac. Configurazioni utente non modificate: sole selezioni, tempi e inquadrature client. Dati grezzi locali in `experiments/runs/tab-playback-20261019`; screenshot pubblicamente esclusi dal packaging. Il test Chrome ha verificato solo caricamento0h, non viene contato come prova di riproduzione. Safari `setValue` del cursore nativo non ha generato l'evento input: tentativo non contato come PASS seek.

Prossimo incremento scientifico invariato: qualificare input/interventi e feedback fisico del piano secondo M0–M7, senza dedurre efficacia dall'animazione o dall'esaurimento di due sole realizzazioni.
