# Scenari indipendenti, modifica nel tempo e ottimizzazione

Run `scenario-workflow-20261018`, 18 ottobre2026. Parent privato `b1b38977160715890e0664c69feb85d7000e7c5a` più modifiche documentate; SHA consegna nel Git/PUBLICATION.json. Reviewer: Codex self-check. SPEC/AGENTS aggiornati alla nuova richiesta: gli inneschi diventano **locali allo scenario**, superando la precedente scelta degli inneschi comuni. Architettura multi-hazard AR-EXT-01 invariata; incremento esecutivo FIRE dentro M3/M5/M6/M7, senza nuovo simulatore.

## Uso nella dashboard

1. In **Simulazioni e risorse → Incendio**, crea uno scenario vuoto oppure usa quello corrente. Trascina uno o più inneschi sulla sua mappa. Anche il primo e un unico scenario possono contenere squadre.
2. Trascina le squadre sulla mappa destinataria. In **Strumenti e confronto → Elementi dello scenario**, seleziona la squadra: categoria, dimensione, linea/area e minuto di attivazione sono modificabili. **Attiva all’ora selezionata** usa il tempo della timeline. Puoi spostare icone/vertici o rimuovere elementi. Su touch: scegli il tipo e tocca la mappa.
3. **Duplica** copia esplicitamente gli input, che poi sono indipendenti. **Crea scenario** lascia inneschi e risorse vuoti. Confronta le mappe desiderate con **Scenari e livelli**. A parità di inneschi, confronti l’effetto degli interventi; inneschi o meteo diversi sono segnalati.
4. **Avvia simulazione** prepara gli input e attende il vero calcolo. La timeline riproduce i risultati fisici e il meteo relativo alla stessa validità. Pausa e cursore permettono di tornare indietro. Dopo una modifica, **Aggiorna e riprendi** ricalcola e riparte dall’ora selezionata. Il risultato precedente è marcato come superato. **Annulla calcolo** interrompe le richieste pendenti e la coda del confronto.
5. **Scenario ottimizzato** apre inventario e priorità. Puoi importare le squadre correnti, dichiarare disponibilità/attivazioni e modificare i pesi. Dopo conferma delle ipotesi, il solver produce una proposta verificata; se manca, viene calcolato un riferimento senza squadre con gli inneschi selezionati. **Calcola scenario ottimizzato e riferimento** esegue una coppia nativa su input congelati e poi valuta entrambi gli esiti. Gli scenari manuali restano disponibili.

Il ricalcolo è completo: non è un checkpoint o un motore che riceve modifiche mentre integra. Il replay mantiene i campioni fisici esistenti di15minuti, senza inventare perimetri intermedi. Il nuovo forecast usa un inizio futuro valido e può aggiornare il contesto dell’intero confronto; il replay ottimizzato usa invece gli input congelati del riferimento, senza presentarli come una previsione appena acquisita. La fonte aggiornata di consultazione non cambia retroattivamente i risultati.

## Prova fisica eseguita

Protocollo fissato prima dei run in `experiments/runs/scenario-workflow-20261018/protocol.json`, con successiva registrazione della prova IAB prima del suo replay in `ui-protocol.json`. Tutti i calcoli nella VM UTM Linux ARM64:4vCPU,8GiB RAM,19GiB disco; core/geo/fire/decision in ambienti separati esistenti. Nessuna installazione o download di nuovi dataset;6,8GiB liberi al termine,145pin motori invariati. Un riavvio ordinario del backend prima dei nuovi job, senza job attivi. Mac usato per editing, browser QA e copia delle evidenze.

Il riferimento è il risultato FonteVetica `job-2065f1b44e7f422ab7098d9d3cfc8f04`: innesco ipotetico, terreno/vegetazione reali già acquisiti,72ore dal18/10 ore13:00UTC, seme1729,2realizzazioni. Meteo distribuito congelato, umidità del combustibile HFFMC_1977 con inizializzazione sperimentale; non ricostruzione dell’incendio osservato. Weather SHA256 `099b1b2180e445d28750042b9aaf92378d5080cd6600be4090b09887dc6abcfd`.

Inventario dichiarato: squadra a terra subito, elicottero dopo1440minuti, Canadair indisponibile con arrivo ipotetico30minuti. Il solver HiGHS con verificatore indipendente esclude il Canadair e seleziona due aree da300×300m. Il beneficio ideale tiene ora conto delle celle raggiunte prima dell’attivazione nella baseline. Disponibilità/autonomia per l’intero orizzonte sono **ipotesi**, non turni o voli realmente sostenibili.

La sorgente priorità di questa prova è l’edificato ESA WorldCover2021,27geometrie, SHA `fdc62efd2c7fce9e2812b9f2d7d7057edd5e1f23334794d4576c2383469dc71c`. OSM aveva restituito500 nello snapshot geografico precedente: destinazione d’uso, ospedali/scuole e popolazione sono mancanti, non inferiti dall’edificato. I pesi dichiarati sono sanità5, istruzione3, soccorso3, residenziale2, località2; solo categorie disponibili partecipano al calcolo. Indice fisico: somma pesata della probabilità media/massima sulle geometrie cartografate con buffer sperimentali75m per punti e100m per poligoni, blend0,5; area finale rompe i pareggi.

| Risultato nativo a72h | Riferimento | Proposta |
| --- | ---: | ---: |
| Superficie media bruciata |2552,85ha|2477,925ha|
| Indice sulle priorità |3,5847222209|2,2327381000|
| Celle combustibile modificate |0|100 a0s,100 a86400s|
| Aggiornamenti orari distribuiti consumati |72|72|

Prima coppia API: `ideal-native-162da690d6c74defa8bdaa9dd346a0cf`, job A `job-03fd5fabea1a443d903e6c2ddd015d8e`, B `job-fb8c2519a7484c0e9652837490a1e7a9`. Decisione `decision-d72b397ace354a93a3a2ae99a7cae63e`.

Seconda coppia avviata nella scheda IAB esistente: decisione `decision-b3b5220fc2c740b8a3939a45279a2f74` (1,535s osservati, non p95), confronto `ideal-native-bd9cb31bee314a62b8b6be21a2f62a23`, A `job-487cb86fa6774e2a97ab123fe0948fc9`, B `job-521538ef71204f27a7d67ef7cdbf10a4`. Stessi risultati: replay con stesso seme/input, **non repliche statistiche indipendenti**. La dashboard mostra il verdetto dalla valutazione dei prodotti nativi, non dal solo beneficio del solver.

Audit VM PASS sulle quattro nuove esecuzioni:20asset,2376artefatti manifestati incluse1152matrici temporali e1152PNG; riferimento identico ai288array originali in entrambe le coppie.11411celle di probabilità finale differiscono fra A e B. Valutazione rifiuta output alterati, terreno/forzanti o seme diversi, piano non corrispondente alla proposta e riferimento con squadre. Il caso utente passa da rev17 a20 aggiungendo solo la coppia; i primi tre scenari sono identici. Workspace principale rev65 identico prima/dopo. Evidenze JSON pubblicabili in `reports/scenario-workflow/`; raw completo locale nel run.

## Verifiche e risultati negativi

PASS12test VM:7validazione/solver e5valutazione indipendente. PASS114controlli browser finali:23authoring,22ricalcolo,22clock,28playback e19confronto ottimizzato;12esecuzioni axe senza violazioni a375/768/1440. Coprono primo scenario con squadre, inneschi locali e trascinabili, duplicazione indipendente, estensione350m e tempi, rewind/edit/remove, ripresa all’ora scelta, preparazione riferimento esplicita, errore di preparazione senza autoplay, meteo congelato alla stessa validità, PNG lenti/mancanti, selezione di due mappe conservando cinque configurazioni, layout del pannello e salvataggio isolato.

FAIL conservati: prima decisione `decision-d3772f53c1a6410eb5e77047fb66a2d5`, NameError su arrival non caricata; corretto il caricamento dall’output nativo prima del retry. Harness authoring iniziali aspettavano500ms contro debounce600ms: corretti attendendo il salvataggio osservabile. Harness playback lasciava `previous_job_id` in una fixture dichiarata senza risultati: corretta la fixture, non la logica del prodotto. Prova visuale IAB ha rivelato bottoni dell’inventario con la larghezza44px ereditata dai pulsanti di chiusura: corretto il layout e aggiunto controllo di non sovrapposizione. FAIL axe a pannello aperto per tabella vuota scrollabile non focalizzabile: aggiunti regione nominata e tabindex. Un tentativo SSH con connessione interrotta è conservato, retry sequenziale PASS. Nessun risultato negativo cancellato o trasformato in evidenza positiva.

## Limiti e prossimo incremento

PASS tecnico del workflow, non chiusura scientifica M5–M7. BLOCKED: efficacia differenziata e logistica dei mezzi, qualificazione fuel/moisture, calibrazione e validazione osservata, completezza delle priorità. Tutte le categorie applicano la stessa rimozione ideale del combustibile; non sono simulate scariche/rifornimenti/viaggi/turni reali. L’obiettivo migliore è **fra le due simulazioni valutate**, non un ottimo fisico globale né una policy operativa certificata. Il proxy additivo può divergere dal risultato fisico; se vince il riferimento, il sistema lo dichiara. Il vincitore della coppia non è automaticamente il migliore di ogni scenario manuale arbitrario.

NOT RUN: checkpoint/streaming del solver, nuova efficacia per categoria, ensemble ampio/held-out, nuovo benchmark30/p95, FPS/soak, dispositivi fisici, nuova idrologia o secondo hardware. Nuovo acquisto/cloud/deployment/dispatch: NOT RUN. Prossimo incremento scientifico del piano originale: qualificazione degli interventi e input, logistica verificabile e confronto su ensemble/priorità osservate; conservare la distinzione fra proposta ideale e verifica fisica.

## Comandi riproducibili

Nella VM, da `hazardia-runtime/app`, con PYTHONPATH=src e PROJ_LIB=/usr/share/proj:

```sh
/home/hazardia/hazardia-runtime/core-env/bin/python -m unittest discover -s tests/decision -p test_fire_ideal.py -v
/home/hazardia/m0/reflex-env/bin/python -m unittest discover -s tests/decision -p test_fire_evaluation.py -v
/home/hazardia/m0/fire-env/bin/python tests/native/fire_ideal_audit.py --runtime /home/hazardia/hazardia-runtime --comparison ideal-native-bd9cb31bee314a62b8b6be21a2f62a23 --out /tmp/ideal-audit.json
```

API reale: POST `/api/fire-ideal` con job baseline/fleet/weights/robust/assumptions_confirmed; GET `/api/decisions/<id>`; POST `/api/fire-ideal/replay` con decision_id; attendere entrambi GET `/api/firelab/<job>` SUCCEEDED; POST `/api/fire-ideal/evaluate` con comparison_id; GET decision terminale COMPARISON_EVALUATED. Richieste locali JSON con header `X-Hazardia-Research:1`. Non usare questi ID su una VM nuova: occorre prima ricreare i dati/riferimenti con bootstrap e procedure documentate.

Browser QA: Node con Playwright/Chrome esistenti, `node tests/browser/<suite>.cjs <nuova-cartella-output>`; impostare HAZARDIA_PLAYWRIGHT_PATH, HAZARDIA_BROWSER_EXECUTABLE e HAZARDIA_AXE_PATH verso gli strumenti locali. Authoring usa anche HAZARDIA_FIELD_FIXTURE, snapshot meteo dichiarato; queste fixture verificano il trasporto/UI e non contano come fisica nativa. Il test optimized-scenario richiede la coppia completata; non avvia modelli né sostituisce configurazioni reali.
