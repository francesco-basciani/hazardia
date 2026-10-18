# Un solo tempo per scenario e meteo

Run `shared-scenario-clock-20261018`, parent `23362ee8b0e4b677b51aeec719ce6cea5573e3df` + modifiche, SHA finale Git/PUBLICATION; reviewer Codex self-check. Requisiti FR-26/27/28 e decisione esplicita utente del18/10/2026, senza modificare il piano M0–M7.

Eliminati dallo studio il player meteo autonomo, il selettore di un’ora meteo indipendente e il comando separato di pausa delle scie. Un solo Riproduci/Pausa/cursore aggiorna risultati e campi meteorologici. Ogni mappa usa l’inizio effettivo del proprio risultato (o della bozza) più il tempo trascorso; la consultazione della previsione aggiornata mantiene quella stessa validità anziché partire dall’ora corrente. I risultati già calcolati mantengono le forzanti consumate: cambiare la fonte visualizzata non ricalcola la fisica. Monitoraggio conserva il suo player previsionale, uno nella propria sezione.

Il renderer risolve le ore intere dal campione originale; fra ore adiacenti interpola solo per visualizzazione, conservando l’etichetta di transizione e la qualifica oraria di pioggia/raffiche/radiazione. Gap, ore oltre copertura e snapshot congelato non disponibile producono missing, senza fallback implicito ad altre ore o a una fonte differente. Il riepilogo puntuale conserva valori orari con indicazione esplicita dell’ora sorgente durante i campioni frazionari; i livelli cartografici interpolati sono visuali, non nuovi input del modello. Nessuna nuova previsione fisica o acquisizione per frame.

**PASS**22controlli dedicati con3risultati nativi Fonte Vetica72h della VM: corrispondenza assoluta a0/1/1,5/24/25/48h; play/pausa congiunti; fonte aggiornata al medesimo istante; interpolazione vettori/scalari; gap controllato nelle sole risposte del browser, missing evidente sulle3mappe, risultato congelato ancora disponibile. +1h corrisponde a18/10/2026 13:00UTC (15:00Roma), +25h a19/10 13:00UTC: entrambi effettivamente presenti nello snapshot reale `map-weather-682140c5c65bd43e19b09023`, senza spostamento all’ora corrente. Fixture numerica separata10→20°C verifica soltanto l’interpolatore, non è fonte meteo dell’esempio.

**PASS**28regressioni playback (PNG nativi, rallentamento1800ms, HTTP503, pausa in caricamento, fine/ripartenza e bozze),30regressioni authoring/monitoraggio con trasporto QA isolato,6axe375/768/1440 senza violazioni e nessun errore JavaScript. Chrome155.0.8059.84 sul Mac come solo client della VM. Test clock con CSP ordinaria; bypassCSP esclusivamente nelle suite che iniettano axe. Workspace reale principale e caso invariati. PASS controllo IAB nella scheda utente: cursore a+1h e tre legende METEO USATO alle15:00Roma rispetto all’inizio14:00; lasciata in pausa, screenshot raw `iab-plus1h.png`. Nessun nuovo run PROPAGATOR, installazione o riavvio del servizio.

**NOT RUN**nuovi benchmark p95/FPS/soak, device fisici, skill o efficacia operativa. **BLOCKED**qualifiche fisiche e gate fullM5–M7, invariati. Questo è un test di sincronizzazione software; i fotogrammi rimangono i campioni originali a15minuti.

Comandi eseguiti con `HAZARDIA_PLAYWRIGHT_PATH`, `HAZARDIA_BROWSER_EXECUTABLE` e per axe `HAZARDIA_AXE_PATH` del runtime client già disponibile:

```sh
node tests/browser/scenario-clock.cjs <output-nuovo>
node tests/browser/fire-playback.cjs <output-nuovo-playback>
HAZARDIA_FIELD_FIXTURE=experiments/runs/dynamic-fire-domain-20261018/field-italy.json node tests/browser/dynamic-fire.cjs <output-nuovo-regressione>
```

Il test dedicato richiede il caso locale Fonte Vetica già registrato; non avvia job o scrive scenari. Risultati/screenshot/log completi nel raw locale; sommario pubblicabile `reports/shared-clock/verification.json`. Prerequisiti e ricreazione del caso in `reports/FONTE-VETICA-20261018.md`.
