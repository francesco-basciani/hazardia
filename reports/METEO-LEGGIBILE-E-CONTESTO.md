# Meteo leggibile e contesto geografico

Run `weather-readable-20261017`; parent privato `5ac5105db1a58f8bf302f9c6e9f40a6d3abf15fe`, worktree modificato durante le prove. SHA finale nella consegna Git/PUBLICATION.json e nel raw locale `source-final.txt`. Reviewer: Codex self-check. Ambito FR-WX-VIEW-01, FR-26/27 e QR-11: presentazione, senza cambiare le forzanti dei job. Runtime/acquisizione sempre nella VM Linux esistente; host solo sviluppo, browser e copia evidenze.

## Modifica

Monitoraggio e finestre degli scenari condividono un renderer di consultazione. Temperatura e umidità relativa (UR) compaiono insieme in indicatori distribuiti, selezionabili anche raffiche, nubi, pressione e radiazione. Layout adattivo alla finestra, massimo32indicatori per mappa; valori campionati bilinearmente nel campo reale, non misure locali né statistiche per zona amministrativa. Ogni indicatore conserva coordinate, ora, variabili e valori numerici ispezionabili. Campi mancanti: `n/d`; fuori copertura nessun indicatore inventato. Non si aumenta la risoluzione atmosferica aggiungendo indicatori.

La pioggia ha una superficie distinta, opaca al57% circa, con il43% di trasparenza (alpha145/255), con cinque classi:0,1–1 /1–2,5 /2,5–5 /5–10 /≥10mm nell'ora successiva. Sotto0,1mm trasparente. Legenda esterna alla mappa, indipendente dalle altre variabili; colori di intensità prevista, non codici di allerta. Campioni su celle schermo12px, interpolati: non sono perimetri di allagamento e non diventano più accurati con lo zoom. Mostrando soltanto la pioggia sono disponibili anche indicatori numerici della precipitazione; con altre variabili la pioggia resta nel colore e nel riepilogo per ridurre il rumore.

Vento più contrastato, tratto2px, scie e amplificazione visuale `max(22,48/speed)` pixel/(m/s)/s per velocità≥0,1m/s, zero sotto soglia. Direzione dei vettori conservata; velocità visiva non fisica. Massimo420particelle per mappa, pausa/reduced motion con frecce statiche. Non è una visualizzazione di traiettorie atmosferiche. Nessuna modifica ai valori del vento o alla loro assunzione nei simulatori.

Confini regionali Istat Italia2026 e nomi geografici GeoNames/OSM abilitati anche sulle mappe dello studio. Controlli nel gruppo Cartografia; confini generalizzati, utili per contesto e non per determinare appartenenza legale a scala stradale. Nomi locali con controllo delle collisioni e un massimo50per mappa; copertura disponibile parziale e dichiarata, non mondiale. Il renderer è generico e non attribuisce ad altri territori nomi mancanti. Pane dei valori sopra i confini, sotto nomi e icone operative, con pointer-events:none per preservare drag/drop. Fetch cartografici condivisi fra finestre; pulizia dei layer/listener quando una finestra viene rimossa. Disattivata l'animazione di zoom dello studio per mantenere il centro esatto simultaneo fra finestre di dimensioni diverse.

## Fonte e ripetibilità

Snapshot reale usato nella suite principale: `map-weather-99474a77fdeb485292b99430`, acquisito `2026-10-17T18:06:54.716478Z`, DWD ICON Global via Open-Meteo,81nodi, dominio `[[41.9,12.3],[42.8,14.4]]`. Copia in `experiments/runs/weather-readable-20261017/release-final/weather-used.json`. Griglia del modello circa11km; campionamento della vista0,11°×0,26°. Emissione del modello non disponibile dal provider. Snapshot congelato nelle richieste del browser QA per una verifica numerica coerente; i tentativi di refresh di questa suite sono intercettati e dichiarati, non chiamate aggiuntive al provider. UI effettiva usa il servizio VM normale.

Restano cache TTL3h,81località/richiesta,48tentativi/giorno (massimo3888località equivalenti/giorno), rate limit e budget backend già esistenti. Stato osservato prima/dopo:8/48tentativi, nessun aumento per questa consegna. Nessuna nuova installazione o acquisizione massiva, nessun servizio commerciale.

Comandi ripetibili dalla root:

```sh
ssh -i .m0-runtime/ssh-key -p22227 -o UserKnownHostsFile=.m0-runtime/known_hosts hazardia@127.0.0.1 'cd /home/hazardia/hazardia-runtime/app && PYTHONPATH=src ../core-env/bin/python -m unittest tests.unit.test_map_weather -v'
node tests/browser/weather-readable.cjs QA_OUTPUT_DIRECTORY
node tests/browser/clean-authoring.cjs QA_REGRESSION_DIRECTORY
```

Per browser QA impostare HAZARDIA_PLAYWRIGHT_PATH, HAZARDIA_BROWSER_EXECUTABLE e HAZARDIA_AXE_PATH, come nei report browser precedenti; Node del runtime Codex e Chrome sul Mac di riferimento. Tutti i servizi/API restano nella VM. Log, snapshot, screenshot375/768/1440, report axe e configurazioni nel raw del run. Le fixture negative/palette sono dichiarate SOFTWARE TEST e non sono dati sperimentali di meteo reale.

## Esiti osservati

- PASS10test VM del servizio meteo: unità, allineamento orario, vettori, griglia e campi aggiuntivi/missing.
- PASS47controlli browser dedicati: valori combinati e corrispondenza con cache reale, nomi/confini configurabili, densità limitata, tre finestre, zoom8–20, vento visibile, colori/soglie della pioggia e trasparenza asciutta, sorgente mancante, una variabile mancante esplicita e fuori dominio senza estrapolazione, interazione Monitoraggio.
- PASS33regressioni authoring: inneschi comuni, squadre indipendenti, nessun intervento implicito, finestre e centri sincronizzati, invio dei soli elementi scelti (endpoint positivo intercettato; non un nuovo run fisico), workspace reale preservato. Tutti gli80controlli PASS;6controlli axe senza violazioni alle tre larghezze. Screenshot e assenza errori JS verificati.
- PASS piccolo profilo di30toggle umidità, tre mappe, Chrome headless1440px: p50 16,60ms, p95 17,70ms, massimo141,70ms click→requestAnimationFrame. Precedente esecuzione34controlli, prima di aggiungere i13controlli zoom: p95 33,60ms, massimo35,20ms; conservata con le altre prove preliminari. Regressione separata30toggle radiazione: p95 31,30ms. Sono workload locali di presentazione, non p95 del simulatore, né verifica completa di QR-11–14.
- FAIL intermedi conservati: vecchio riordino UI cercava una label rimossa (eccezione, corretto spostamento del nuovo gruppo); locator QA non univoco con tre legende (harness corretto); regressione rilevava centri diversi durante zoom animato (corretta camera simultanea senza animazione). Screenshot iniziali mostravano confini sopra gli indicatori e legenda sovrapposta: ordine dei pane corretto e legenda pioggia spostata nei controlli. Prove finali dopo correzione.
- NOT RUN nuove esecuzioni PROPAGATOR/HMC/REFlEx, skill fisica, studio con utenti, dispositivi mobili fisici, stress/soak30min e visualizzazione di precipitazione non nulla osservata in campo. La palette pioggia è verificata su gradiente software dichiarato0→12mm e caso asciutto, senza far piovere artificialmente nella dashboard reale.
- BLOCKED invariati: qualificazione fuel/umidità combustibile/efficacia e logistica, fullM5–M7. Nomi fuori copertura e meteo oltre il dominio/ora disponibili rimangono dati mancanti; nessuna validazione operativa dal restyling.

Prossimo incremento eseguibile: continuare la qualificazione degli input fisici e la validazione degli interventi già prevista dal piano. Questi indicatori di consultazione non risolvono il coupling di temperatura/pioggia/UR con il combustibile.

Ambiente browser verificato: Apple M4 Pro,48GiB RAM; macOS27.0.1 build26A434; Chrome155.0.8059.84, Node24.19.0. VM Linux5.15.0-198-generic aarch64, Python3.10.12; disco19GiB,11GiB usati,7,5GiB disponibili al controllo. `viewport-weather.cjs` delega alla suite corrente: non è una seconda esecuzione indipendente.
