# Meteo su tutta la vista — 16 ottobre 2026

Nella sezione **Meteo sulla mappa** il vento riempie l’area visibile ai livelli di zoom8–20. **Colore trasparente sulla mappa** seleziona temperatura o precipitazione, mantenendo il vento; nessun colore equivale al solo vento. Meteo spegne tutti i livelli. Il clic sul territorio/cella incendio apre i valori previsti per quel punto, con orario e modello. I dettagli del punto L’Aquila e i nuovi job restano separati.

Dati reali acquisiti nellaVM: `map-weather-57e2891971ca12d18b2204d1`, prima disponibilità `2026-10-16T13:17:40.170084Z`, raw325228B, SHA256`57e2891971ca12d18b2204d17e32ce8a6a0978f4aaa144ccc25175c76b13e0d0`.81punti,95ore valide dopo l’allineamento della precipitazione. Contesto effettivo39,6–44,9N /8,7–19E per la geometria del browser usata. Risoluzione del prodotto globale0,1°/~11km; campionamento della panoramica0,6625°×1,2875° per questo contesto. Vento nell’Abruzzo riusa il campo ICON-EU più fitto quando fresco e temporalmente compatibile. Non è una previsione distribuita di bacino già collegata ai simulatori.

| Verifica | Esito | Evidenza |
|---|---|---|
| Software nellaVM | PASS |70unit+19domain+14decision+14web=117; unit.log/regression.log |
| Copertura/zoom/UI | PASS |31controlli finali: copertura100% ai13zoom, trasparenza, campi distinti, ispezione, responsive375/768/1440, nessun nuovo job |
| Vento/controlli precedenti | PASS |28controlli, reduced-motion, pausa, campi temporali, nessuna chiamata browser al provider |
| Accessibilità automatica | PASS |6scansioni axe0violazioni, incompleti conservati |
| Trasformazioni sul dato reale | PASS |972confronti su3ore e4componenti; max arrotondamento4.985881065855402e-05; non accuratezza del forecast |
| Motori | PASS |145SHA invariati; nessuna nuova esecuzione fisica |
| Distribuzione locale | PASS |9file sorgenti/script verificati identici VM;834JSON precedenti immutati esclusi2contatori cartografici; archivio raw copiato e hash verificato |
| Senegal/altre geografie reali, antimeridiano, studio storico/30min/carichi elevati | NOT RUN |Test sintetici dei bounds includono Senegal; non sono validazione geografica o operativa |

Run `viewport-weather-20261016T1320Z`, piano preventivo e hash iniziali in plan.json; source base95dc0c9 più overlay identificato dai9hash finali. Manifest sintetico reports/weather/viewport-verification.json; raw/log/browser nei percorsi del run. Comandi principali: unittest discover nei4gruppi nellaVM; scripts/verify_map_weather.py --runtime /home/hazardia/hazardia-runtime --output …/native-verification.json; tests/browser/viewport-weather.cjs e regional-wind.cjs sul servizio locale. BrowserChrome155 sul Mac, server/acquisizione/preprocessing nellaVMUbuntuARM64. Nessuna installazione o variazione4vCPU/8GiB/disco19GiB. Upper bound conservativo download3705762115/5368709120B, includendo nuovamente tutti i contatori/raw meteo attuali per evitare sottostima; spazio libero9265893376B.

Negativi conservati: prima verifica HTTP immediatamente dopo riavvio non riuscita (curl56), servizio poi verificato; ispezione dopo zoom rapidi inizialmente FAIL perché clic sulle celle del layer incendio non aggiornava l’inspector. Aggiunto handler alla cella; verifiche finali PASS. Non cancellate le cartelle browser-inspection/final/inspect-diagnostic/inspect-fix e i probe. Il confronto con quadro precedente è tecnico, non studio di usabilità. Gate scientificiM5–M7 restanoBLOCKED.

Cache/quota/fruizione globale e minacce alla validità: ADR-0012. Le forzanti fisiche continuano a usare il contratto puntuale qualificato separatamente. Reviewer: Codex self-check.
