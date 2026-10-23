# Monitoraggio, moduli e audit tecnico — 23 ottobre 2026

Run `monitor-audit-20261023`; base privata `2927927d70e7df6029d74214539fef1a8db200dc` + modifiche elencate nel commit di consegna. Reviewer: Codex self-check. Esecuzione servizio/acquisizioni/test Python nella VM UTM Linux, 6vCPU/16GiB/disco19GiB. Test dei moduli JavaScript lato client con Node sul Mac di sviluppo; controllo UI nel browser integrato, non Safari. Nessuna nuova simulazione fisica o modifica al manoscritto.

## Risultato della correzione

- PASS: Monitoraggio non contiene più «Scenari e simulazioni» o «Traffico simulato» fra i livelli; risultati storici simulati disattivati in questa vista. Gli interruttori Incendi/Alluvioni filtrano il monitoraggio territoriale, non caricano scenari di esempio.
- PASS: traffico disponibile nello stesso sito, in **Simulazioni e risorse → Tipo di simulazione → Traffico stradale simulato**. Mappa e parametri a destra, attivazione inizialmente disabilitata. Il modulo riusa rete, configurazione, seed e motore esistenti. Non introduce congestione/evacuazione né modifica tempi delle risorse o ottimizzatore. Cambiando sezione l’animazione viene sospesa.
- PASS: **Meteo e osservazioni** apre i parametri a destra. Nove scelte indipendenti, incluso il vento; nessuna serie duplicata a sinistra. Pioggia e nuvole combinabili, preset dedicato e legende distinte. Il velo nuvoloso combinato è attenuato per conservare la leggibilità della pioggia; le celle asciutte non diventano pioggia.
- PASS: pulsante terremoti ora abilita il livello prima di acquisire; prima poteva acquisire e lasciare il livello spento. Catalogo automatico INGV nel rettangolo italiano supportato, USGS altrove, scelta manuale conservata. Nessun risultato, errore e caricamento distinti. Filtro M≥0 iniziale, anche magnitudo inferiori selezionabili; elenco degli ultimi20 eventi con data/luogo.

## Inventario verificato

| Componente | Esito e prova di questa sessione | Limite |
|---|---|---|
| Meteo distribuito | PASS: API FRESH,95 campioni orari, T/UR/vento/pioggia/probabilità/nuvole/raffiche/pressione/radiazione; UI con6600 pixel pioggia e13280 nuvole nello stesso raster | Campionamento/interpolazione non aumenta la risoluzione del modello; dati reali previsti, non sensori |
| Vento regionale fine legacy | BLOCKED: `WEATHER_CACHE_FULL`, snapshot STALE | Campo globale della vista FRESH utilizzato; avviso nel pannello e stop ai tentativi inutili. Archivio scientifico conservato. Richiede archiviazione verificata/compressione senza perdita prima di riprendere questo affinamento opzionale |
| Radar osservato | PASS: acquisizione Radar-DPC SRI23/10,14:25UTC; raster1km, valid_fraction0,4920 circa; prova futura OUTSIDE_VALIDITY | Nessuna osservazione nel futuro, mancanti tratteggiati, non sostituiti con asciutto; non assimilato nel rischio o nei simulatori |
| Pluviometri | PASS: MeteoHub4078 stazioni nel payload,3979 fresche nella risposta verificata | Copertura per stazione, non tutta la mappa; non assimilazione automatica |
| Zone e criticità | PASS tecnico: prodotti reali EFFIS e bollettino DPC consultabili; stato PARTIAL conservato | Valutazione d’impatto locale non qualificata; radar/pluviometri separati. Rettificata la vecchia dicitura che li dichiarava entrambi non collegati |
| Terremoti | PASS:156 eventi INGV nell’area visualizzata; richiesta locale stretta/24h/M≥4 restituisce READY con0eventi; area INGV non supportata rifiutata | Piccoli eventi secondo rilevabilità della rete, nessuna previsione/danno/intensità. Un tentativo ravvicinato è stato correttamente limitato a5s; non contato come catalogo vuoto |
| Sfondi cartografici | PASS tecnico: servizi OSM/satellite/ortofoto rispondono, satellite visibile nella UI; test cache/coda/cancellazione | Nessuna garanzia di disponibilità upstream o copertura delle ortofoto fuori area. Nessun nuovo benchmark immagini completo in questa sessione |
| Immagini recenti | PASS regressione adapter e catalogo già integrato; NOT RUN nuova acquisizione live in questa sessione | Quicklook separati dallo sfondo; copertura e nuvolosità dell’acquisizione, non raster scientifico |
| Territorio/OSM e rete elettrica | PASS regressione filtri/attributi/geom. e catalogo esistente; NOT RUN nuova acquisizione elettrica estesa | Timeout/quote dei precedenti tentativi restano limiti reali; nessuna copertura AT completa/certificata, tensione mancante sconosciuta, nessuna certificazione di volabilità |
| Traffico | PASS rete salvata1221segmenti,38veicoli default;400 con preset intenso, pausa/ripresa; seed/restrizioni/chiusure/missing nei test | Simulazione visuale ipotetica indipendente, non traffico osservato |
| Risorse/scenari/decisioni | PASS regressioni e apertura studio FIRE con due risultati salvati;303 test Python complessivi;311file/95job invariati e pin motori verificati | NOT RUN nuovi job PROPAGATOR/HMC/REFlEx, nuove prove fisiche e nuovi benchmark decisionali. Non equivale a ricalibrazione o qualificazione M5–M7 |
| Hotspot/perimetri/idrometri/popolazione qualificata | BLOCKED come prima: MAP_KEY FIRMS assente, dataset/perimetri/connessioni non acquisiti o non qualificati | Nessun controllo vuoto e nessuna falsa disponibilità |
| Safari/monitor enorme/carico completo | NOT RUN in questa sessione | Prove browser integrate1280×720 e375×812, documento senza overflow; pannelli interni scorrevoli |

**Precisazione temporale radar:** il run conserva sia l’acquisizione14:20UTC sia quella14:25UTC; usare `radar-current.json` per il timestamp esatto dell’ultima prova, non il tempo del cursore meteo futuro. I rapporti di copertura appartengono al mosaico nazionale, non alla sola area visibile.

## Comandi ed evidenze

Nel guest, da `/home/hazardia/hazardia-runtime/app`:

```sh
PYTHONPATH=src:tests/unit:tests/web ../core-env/bin/python -m unittest discover -s tests/unit
PYTHONPATH=src:tests/unit:tests/web ../core-env/bin/python -m unittest discover -s tests/web
PYTHONPATH=src:tests:tests/unit:tests/web ../core-env/bin/python -m unittest discover -s tests/domain
PYTHONPATH=src:tests:tests/unit:tests/web ../core-env/bin/python -m unittest discover -s tests/decision
```

PASS186+47+19+51=303 test. PROJ emette un warning nel core-env: i worker geospaziali hanno ambiente separato e il radar reale ha completato l’esecuzione; nessuna qualificazione scientifica dedotta. `discover tests/integration` trova0test: **NOT RUN**, sono script `verify_m*.py` con argomenti e dataset, non test scoperti da unittest.

Sul client di sviluppo:15 suite `.mjs` in `tests/browser` e `tests/web`, tutte PASS; nuova prova di composizione indipendente nel renderer (6023controlli complessivi della suite). Corretto il runner di `territorial-math.mjs`, che falliva perché Node interpretava il modulo browser come CommonJS; le sette asserzioni restano invariate. Primo fallimento conservato. Node non installato nella VM: non è una dipendenza runtime del servizio, il JS è eseguito dal browser.

Raw privati in `experiments/runs/monitor-audit-20261023/` e percorso omonimo nel guest: preregistrazione, inventoryAPI, risposte, test, negativi, hash e verifiche di preservazione. Estratto pubblico `reports/monitor-audit/verification.json`. Screenshot locali `reports/monitor-audit/{weather,earthquakes,traffic,mobile}.png`.

Traffico400veicoli:300campioni correlati nel browser, p95 disegno0,80ms/intervallo50ms (circa20fps in questa prova); misura circoscritta a disegno/intervallo, non latenza end-to-end né promessa60fps. Modello puro su Mac,30trial/12000segmenti/400veicoli: p95step+positions0,0196ms circa. Non comparare questi tempi con solver o VM come se fossero lo stesso benchmark.

Restano da risolvere esplicitamente: archivio vento fine, fonti assenti/qualificazione, copertura elettrica e validazione scientifica. Nessuno di questi viene trasformato in PASS dalla revisione grafica.
