# Terremoti: apertura e visibilità —24ottobre2026

Run `quake-opening-20261024`, basebac2794+dirty, reviewerCodexself-check. La pagina utente mostrava livello disattivato dopo il solo clic sulla voce. Premendo esplicitamente Mostra e aggiorna eventi, INGV ha restituito216eventi nella vista corrente; non è stato riprodotto un guasto della fonte.

Correzione limitata all’interfaccia: al primo accesso a Terremoti osservati, attivare e acquisire automaticamente tramite gli handler esistenti. Nessuna acquisizione all’avvio della pagina prima dell’apertura. Se l’utente disabilita il livello, riaprire il pannello non deve riabilitarlo. Mostra e aggiorna eventi rimane disponibile per cambiare periodo, magnitudo o area. Fonte/filtri/quote e validità invariati; nessuna conversione dei cataloghi vuoti in errori o viceversa.

PASS nella pagina effettiva del browser integrato: assenza di acquisizione prima dell’apertura; primo clic→READY/216eventi/checkboxattivo; disabilitazione→chiusura→riapertura lascia spento; riattivazione riusa dati acquisiti. INGV,17ottobre08:40UTC→24ottobre08:40UTC, area10.67322/39.85072/16.22681/43.85037; magnitudo≥0, acquisizione24ottobre08:47:16UTC. Eventi osservati rivedibili, nessuna previsione o completezza garantita per piccoli eventi.

Evidenza: reports/quake-opening/verification.json e screenshot locale delivery.png; preregistrazione privata experiments/runs/quake-opening-20261024. NOT RUN Safari, nuovi job fisici o nuova validazione scientifica: modifica reversibile di attivazione UI, non del backend o dei simulatori.
