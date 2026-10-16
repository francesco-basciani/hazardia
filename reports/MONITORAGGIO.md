# Monitoraggio al centro della dashboard

16ottobre2026. Run `monitor-first-20261016T054705Z`. Sorgente verificato e applicato `1b7ccf9d8e8558cddc94e3127470a2a8920ffbd5`. Reviewer Codex self-check.

Apri http://127.0.0.1:8080/ : la prima sezione è **Monitoraggio**. La mappa occupa il centro; attiva Incendi, Alluvioni o Mostra tutti. Il pannello del territorio permette di scegliere un risultato per hazard, leggere data e legenda, cambiare sfondo/trasparenza, cercare luoghi o coordinate. Su telefono il pannello si trova sotto la mappa. Sono risultati simulati di ricerca, non eventi attuali. Sovrapporre due casi non li rende una previsione congiunta; incendio a fine simulazione, alluvione come massimo6h.

**Decisioni e confronto** contiene configurazione risorse/evacuazione, mappe affiancate, risultati, job e confronto fisico incendio1–3giorni. Tornare al Monitoraggio conserva il piano già calcolato se non cambiano input o contesto. Il laboratorio di guasti/allerte sintetici resta sotto Dati e fonti, esplicitamente distinto dal monitoraggio reale non ancora integrato.

Verifiche nuove:85test guest PASS;44browser PASS,12axe scans con0violazioni e incompletes conservati,375/768/1440 e tastiera;35feedback filtro p95=17ms. Due vere richieste solver/verificatore FIRE/FLOOD nel prefisso di collaudo; nessun nuovo job CIMA dalla mappa. Report [verification.json](monitoring/verification.json). Test ripetibile `tests/browser/monitoring.cjs`, con HAZARDIA_BASE_URL e QA runtime documentati nella guida d’installazione. Raw browser-first/ e guest-tests.json nel run.

Deploy nella VM: prima nessun job attivo e checkout tracciato pulito, fast-forward e restart dei soli processi posseduti; 810file JSON di stato preesistenti rehashati e invariati. Asset statici identificati perhash nella verifica. Modelli/dati e hardware invariati. Download conservativo 3467423994B/5368709120B, nessun nuovo servizio/costo/deployment pubblico.

Correzione durante preparazione: sfondo Sentinel collocato in pane190 sotto i tile ortofoto, così la foto locale non copre il dettaglio online; collaudo finale sul codice corretto. Nessun FAIL di test finale. Nuova stabilità30min e100kstress NOT RUN; vecchio QR-14FAIL e fullgate scientifici BLOCKED rimangono. Nessuna nuova simulazione fisica, qualificazione storica, popolazione reale o sensori live introdotti.
