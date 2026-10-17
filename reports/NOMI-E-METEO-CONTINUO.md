# Nomi geografici e riproduzione continua del meteo

Run `weather-continuity-20261017`; base privata `728fbaa754d7009fbd3142fc67443ea0789b7bd0` + modifiche. SHA della consegna nel commit Git e nel manifest PUBLICATION.json. Reviewer: Codex self-check.

## Risultato

**PASS** località con punto cartografico e testo scuro con alone chiaro; regioni in maiuscolo color sabbia e sottolineatura; numeri meteo a spaziatura fissa, temperatura colorata. Valori senza riquadri, copertura locale dei nomi invariata.

**PASS** replay continuo in Monitoraggio e nelle finestre degli scenari, interpolazione visuale a circa20 aggiornamenti/s su requestAnimationFrame, cursore frazionario, pausa sul punto intermedio e ripresa senza tornare all'ora intera. Le particelle conservano le scie durante il replay; non vengono ricreate a ogni quadro. Fine orizzonte, scheda nascosta e assenza dati interrompono la riproduzione; un buco fra ore non viene interpolato. Nessuna estrapolazione fuori copertura e nessuna sostituzione dei dati mancanti con zero.

La nota sotto il cursore esplicita l'interpolazione. Temperatura/umidità/pressione/nubi e componenti u/v del vento sono interpolate fra due record orari adiacenti della stessa griglia. Interpolare componenti evita la rotazione errata della direzione passando per0°/360°. Pioggia, raffiche e radiazione sono una transizione visuale fra campi riferiti a finestre orarie: **non** sono quantità previste per il minuto intermedio. Nessun record interpolato è inviato ai simulatori. Le previsioni orarie originali, il tempo dei risultati fisici e gli input dei job sono invariati.

## Dati reali verificati nella VM

Snapshot testato `map-weather-99474a77fdeb485292b99430`, DWD ICON Global tramite Open-Meteo, acquisito `2026-10-17T18:06:54.716478Z` (20:06:54 Roma),81 nodi su [[41.9,12.3],[42.8,14.4]], circa11km nativi. Stato API FRESH durante la prova; ora di inizializzazione del modello non fornita dal provider. Sono previsioni, non osservazioni locali.

**PASS** SHA256 del file grezzo del provider conservato nella VM corrisponde alla provenienza dello snapshot: `99474a77fdeb485292b9943095ff1267835ebace33891e376b88b3ac7c4b4e29`. Ricevuta, URL, timestamp e confronto hash in `experiments/runs/weather-continuity-20261017/vm-audit.json`; raw nella VM `~/hazardia-runtime/web-state/map-weather/raw-<sha>.json`. Nessun valore casuale usato per il meteo. Le posizioni delle particelle sono casuali esclusivamente per il rendering.

Quota osservata12/48 acquisizioni giornaliere del campo;81 località/richiesta,3888 equivalenti massimi/giorno, TTL3ore e intervallo minimo65s esistenti. Nessuna chiamata al provider per quadro, nessun nuovo servizio/installazione/riavvio. L'API può acquisire un nuovo campo quando si cambia inquadratura; i test bloccano le acquisizioni e usano lo snapshot reale congelato, senza modificarne date o valori.

## Esecuzione e verifiche

Runtime Ubuntu22.04 ARM64 nella UTM esistente; codice statico servito nella VM. Browser QA Chrome155.0.8059.84 su MacM4Pro48GiB, solo client di visualizzazione; viewport375/768/1440. I test intercettano il workspace con una fixture separata vuota e confrontano prima/dopo lo stato reale.

```sh
# Sul Mac, client QA; dipendenze Playwright/Chrome già disponibili.
HAZARDIA_PLAYWRIGHT_PATH=<playwright-installato> \
HAZARDIA_BROWSER_EXECUTABLE=<Chrome-installato> \
HAZARDIA_AXE_PATH=<axe.min.js> \
node tests/browser/weather-continuity.cjs <nuova-directory-evidenze>
# Regressione: stesse variabili, tests/browser/forecast-map-first.cjs.
```

**PASS35 controlli dedicati +58 regressioni =93**,9 esecuzioni axe senza violazioni rilevate (3 dedicate studio +6 regressioni studio/monitor). Verificati valori numerici rispetto all'interpolazione dei record reali, frame intermedi, assenza salti di un'ora, pausa/ripresa, sincronizzazione, campo mancante, orizzonte, layout/mappe alte, dati mancanti e assenza di nuovi job. Workspace utente preservato, con3 scenari e relative risorse; il test non inserisce esempi nel workspace reale. Verifica diretta anche nella scheda dell'utente: pausa a18/10,08:43 Roma, incendio ancora+0h.

Costo del lavoro UI di ciascun quadro su una mappa:32 campioni, p95 **3,30ms**, massimo3,70ms. Regressione30 toggle nuvole su2 mappe: p9518,10ms, massimo18,10ms. Misure locali del lavoro JavaScript, **non** benchmark FPS/dispositivo mobile o simulatore.

**FAIL conservati e corretti:** `attempt-1` rilevava6 errori di stato: il listener del selettore cancellava la fase prima dell'aggiornamento del renderer; listener interno corretto. `attempt-2`33/33 PASS. Il successivo probe `final` includeva l'inizializzazione asincrona della mappa nel conteggio dei reset; misurazione stabilizzata dopo il caricamento, run definitivo `release`35/35 PASS, contatore reset monitor invariato durante il replay. Nessun artefatto precedente sovrascritto.

**NOT RUN:** nuove simulazioni native, accuratezza delle previsioni, validazione percettiva con utenti, FPS/soak, dispositivi fisici, grande carico. **BLOCKED** fullM5–M7 invariati: combustibili/moisture, efficacia/logistica degli interventi e qualificazione scientifica. La fluidità è una proprietà della visualizzazione, non una validazione meteorologica.

Raw: `experiments/runs/weather-continuity-20261017/{release,regression,attempt-1,attempt-2,final}`, log, verification.json, screenshot, ricevute/hash e source-manifest.json. Pubblicazione solo sorgenti e report; cache grezze/stato utente/media restano locali. Prossimo incremento scientifico invariato secondo PLAN.
