# Console cartografica a schermo intero —23ottobre2026

Run `map-console-20261023`, base4f6b29d+dirty; richiesta dell’utente: sola barra superiore, mappa nello spazio restante, livelli a sinistra e parametri a destra. ReviewerCodexself-check. Nessuna modifica delle risorse VM o dei simulatori.

## Interazione consegnata

Monitoraggio: la mappa riempie il viewport sotto la barra principale. **Livelli** apre il navigatore sinistro, con sfondo, filtri dei pericoli, categorie e variabili meteo. La scelta di una categoria apre i relativi controlli nel pannello destro; gli oggetti interrogati mostrano lì i propri dettagli. Ricerca geografica sovrapposta in alto, tempo delle previsioni in basso. I pannelli hanno scorrimento interno; nessuna pagina lunga sotto la mappa. **Escape** chiude i pannelli, pulsanti con nome/controllo/focus tastiera; sotto1000px i pannelli si alternano. Dati e fonti/Guida rimangono sezioni informative con contenuto nello spazio dell’applicazione.

Simulazioni: mappe e confronto occupano il viewport dello studio nella stessa finestra principale. A sinistra scenario attivo, strumenti e palette di inneschi/squadre; a destra impostazioni, meteo, parametri del modello, inventario/priorità, elementi e risultati numerici. Il clic su un’unità conserva l’ispettore esistente. Piano d’intervento e Confronto scenari rimangono modalità distinte dei medesimi scenari. La timeline esistente rimane ancorata in basso. Le legende partono chiuse; i dettagli restano accessibili. Non sono state ricreate copie dei controlli o introdotte nuove simulazioni.

**Rotella:** la nuova decisione dell’utente supera il precedente divieto nelle mappe ora contenute nel viewport fisso, Monitoraggio e studio FIRE/finestre dei peer. Sopra la mappa la rotella modifica lo zoom; sopra un pannello scorre quel pannello senza modificare lo zoom. Le pagine storiche autonome non convertite al nuovo layout mantengono la precedente politica; nessun loro esito storico viene riscritto.

Implementazione: `map-console.js/css`, `studio-console.js/css`; riposizionamento dei nodi DOM e dei loro handler esistenti, senza modifica ai contratti backend. Resize dell’iframe vincolato al viewport; ignorate le vecchie richieste di espansione/scorrimento della pagina nel nuovo contenitore. Il passaggio piano/confronto conserva i nuovi contenitori. Observer dello studio limitato ai figli diretti del workspace, non a ogni aggiornamento meteo/mappa. Pannelli senza filtri di blur; overlay meteo evita i pannelli e la ricerca. Nessuna migrazione a Cesium o nuovo engine.

## Verifiche eseguite

| ID | Esito | Evidenza osservata |
|---|---|---|
| UI-C01 | PASS | Desktop1280×720: barra56px, mappa1280×664 da y56 al fondo720; documento1280×720, nessuno scroll verticale/orizzontale |
| UI-C02 | PASS | Monitoraggio375×812: barra113px, mappa375×699; documento375×812; apertura dei parametri nasconde il navigatore sinistro |
| UI-C03 | PASS | Tablet768×1024: barra109px, mappa768×915; documento768×1024; pannello destro350px e sinistro nascosto |
| UI-C04 | PASS | Studio1280×720: due mappe639×654 affiancate, documento1280×720; passaggio Piano d’intervento→mappa unica1280×654 e ritorno al confronto |
| UI-C05 | PASS | Rotella Monitoraggio: scala50km→10km, scrollTop documento0. Rotella sul pannello: scrollTop pannello81px e scala mappa invariata10km |
| UI-C06 | PASS | Rotella studio: nominale zoom12→15; rotella sul peer15→12 e nominale sincronizzato12, documento senza scorrimento. Una prima prova sopra la legenda non modificava lo zoom: comportamento corretto del controllo; ripetuta sulla superficie libera |
| UI-C07 | PASS | Meteo reale ancora leggibile:23/10 14:00Roma, vento2,2m/s, T16°C, UR68,2%, precipitazione0mm nel punto centrale; data/qualificazioni conservate. Non sono nuove osservazioni o forzanti |
| UI-C08 | PASS | Clic su incendio simulato del catalogo apre “Dettagli sulla mappa” a destra, con coordinate, date16/10 e job originali; poi overlay ripristinato allo stato iniziale |
| UI-C09 | PASS | Esecuzione raggiungibile nel pannello destro, pulsante `run` visibile; non premuto. Accesso a impostazioni/ottimizzazione senza invio di job |
| UI-C10 | PASS |68test core/web nella VM;6041checkJS su viewport-weather-state/render-plan/basemap-state nel client di sviluppo; nessuna nuova qualificazione delle fisiche |
| UI-C11 | PASS |311file di workspace/casi con SHA invariati;95job82SUCCEEDED/8CANCELLED/5ERROR, nessun nuovo job. Screenshot e JSON nel run/report |
| UI-CNEG | FAIL iniziale, corretto | Primo CSS dello studio lasciava le card con altezza0 e il contesto territoriale sulla mappa; corretti stretch/altezze e collocazione dei pannelli, poi ripetute misure e controllo visivo. Una prova del renderer con il DOM parziale del test non forniva querySelectorAll; aggiunto accesso opzionale, ripetuti tutti6013check con esito PASS. Prove viewport indirizzate inizialmente alla scheda di test attiva anziché al Monitoraggio: rilevato dalle dimensioni e ripetuto su scheda isolata |
| UI-C12 | NOT RUN |Safari fisico, nuovo audit axe completo, soak e benchmark completoFPS/memoria/carico; il vecchio harness browser dynamic-fire richiede adeguamento dei selettori e delle aspettative della rotella al nuovo flusso |

Comandi: nella VM `PYTHONPATH=src:tests/unit:tests/web ../core-env/bin/python -m unittest test_traffic test_recent_imagery test_consultation_cache test_radar_service test_map_navigation test_maps test_regional_satellite test_osm_tiles test_map_weather test_bootstrap test_fire_workspace test_fire_cases`; client di sviluppo `node tests/browser/viewport-weather-state.mjs`, `node tests/browser/weather-render-plan.mjs`, `node tests/browser/basemap-state.mjs`. Interazioni reali e schermate mediante CUA/IAB; nessun driver esterno avviato per questi test.

Rispetto al precedente Monitoraggio desktop575px, la mappa ha89px verticali in più; nessuna inferenza automatica suFPS o latenza da questa misura geometrica. I controlli riutilizzano i servizi/cache esistenti: non aumentate quote, RAM, vCPU, disco o worker. Missing/licenze/dati bloccati del precedente incremento rimangono tali; nessuna promessa di parità di prodotto con God's Eye View, efficacia antincendio, evacuazione o nuovo risultato scientifico. M5–M7BLOCKED invariati. Fonte grafica di riferimento locale God's Eye View MIT, commit224745bd0aa1050f73bded841ecc467c3ad1ce7c, struttura pannelli/foundation; nessun suo feed extra integrato.

Evidenze: `experiments/runs/map-console-20261023/`, `reports/map-console/verification.json`, screenshot locali `delivery.png`, `mobile-final.png`, `tablet.png`, `studio-final.png`. Le immagini cartografiche restano locali, escluse dalla pubblicazione del codice.
