# Verifica fisica del meteo e delle squadre

Run `fire-coupling-20261018`, parent `96c9959924de024543a161aa60ec62402cb10f26` + modifiche; SHA finale nel manifest Git/PUBLICATION. Reviewer Codex self-check. Ambito FR-FIRE-WORKSPACE/FORCING, FR-26/28, gate scientifici M5–M7 invariati.

## Causa osservata nella prova utente

La workspace Fonte Vetica era alla revisione5. Due squadre erano state spostate di circa1km dalle geometrie iniziali; le nuove coordinate erano in `input.resources`, mentre `submitted_input` e i piani dei tre risultati contenevano ancora le posizioni originarie. Riproduci mostrava i vecchi PNG mentre le icone rappresentavano le nuove bozze. Non era evidenza che le squadre fossero ignorate dal simulatore: i nuovi input non erano stati calcolati. L’avviso precedente nel pannello non rendeva evidente questa incongruenza.

Ora qualsiasi modifica sospende la riproduzione. L’unico comando diventa **Calcola e riproduci**: esegue prima l’intero gruppo con inizio e snapshot comuni, poi avvia i nuovi risultati soltanto se coerenti. Un avviso accanto alle mappe e lo stato di ciascuna finestra identificano risultati precedenti/non aggiornati. Nessun ricalcolo a ogni movimento del mouse, nessuna propagazione disegnata o riduzione inventata. Le altre richieste restano classificate indipendentemente in caso di errore; il confronto incompleto non parte automaticamente.

Il controllo aggiuntivo verifica la geometria/tempi delle risorse, inneschi, durata, inizio, fonte meteo, seme e moisture effettivamente presenti nel piano del risultato. L’ultima richiesta salvata non prova che il suo calcolo sia riuscito. Questo protegge anche il reload dopo un errore, quando lo stato transitorio di fallimento non è presente nella workspace serializzata. L’ispettore mostra inoltre il numero di celle effettivamente modificate all’istante dell’intervento: totale del gruppo a quell’istante, non conteggio esclusivo di ogni singola squadra.

## Cosa entra effettivamente in PROPAGATOR

Il worker crea72 condizioni orarie native per un run72h. Campi u/v reali sono interpolati sulla griglia fisica e trasformati in velocità/direzione tenendo conto della convergenza cartografica. La stima hFFMC1977 aggiorna l’umidità del combustibile usando temperatura, umidità relativa, vento e pioggia dell’ora precedente; la pioggia non viene anticipata. In modalità manuale questo estimatore non è usato. Nubi, pressione e radiazione visualizzabili non costituiscono altrettanti ingressi fisici consumati da questo worker.

Le aree/linee richieste diventano maschere sulla griglia reale; al tempo indicato il worker invia a PROPAGATOR `vegetation_changes` con combustibile non vegetato nelle celle coinvolte. È la rimozione ideale richiesta dall’utente, non una simulazione qualificata di equipaggi, acqua, turni, viaggi o lanci di velivoli. Tutte le categorie condividono attualmente questo effetto ideale. Umidità del combustibile stimata, classificazione fuel e capacità operative restano non calibrate.

## Esperimento nativo controllato

Protocollo nella VM prima dei run, SHA `51aed6956ffc9f8f230d3081e87bc88d8287e657f1a0c3d2aa6c592269b6e607`. Quattro esecuzioni72h/288campioni, stesso terreno/innesco, seme1729,2realizzazioni,1thread. Copia immutabile delle risorse della revisione5. Il confronto è offline sullo snapshot originale, non una nuova previsione operativa; non aggira la policy di freschezza delle richieste web.

| Condizione | Area finale simulata ha | Celle fuel modificate | Celle di probabilità diverse dal replay |
|---|---:|---:|---:|
| Replay senza interventi |2766,195|0|0|
| Prima area nelle nuove coordinate utente, da0min |2832,615|20|14781|
| Seconda area nelle nuove coordinate utente, da60min |2827,350|16|15814|
| Override vento ipotetico da+1h, nessuna squadra |3685,770|0|25225|

**PASS**replay identico elemento per elemento per tutti i288array rispetto al risultato originale. **PASS**entrambe le nuove geometrie consumate,20/16celle; tutte raggiunte dalla probabilità positiva del riferimento a72h. **PASS**vento modificato cambia gli array prodotti dal motore. L’override inverte la provenienza e imposta un vento uniforme di almeno3m/s: cambia anche l’eterogeneità e, attraverso il modello, l’umidità; non è un isolamento del solo effetto della direzione. Durate osservate53,33/42,08/39,95/48,42s: singole misure, non p95.

Le aree finali delle due nuove posizioni sono leggermente maggiori del riferimento: risultato negativo per l’ipotesi che inserire una risorsa garantisca una riduzione. Non viene corretto graficamente. Due sole realizzazioni e un’identica inizializzazione casuale non qualificano un effetto medio né garantiscono identici percorsi di estrazione dei numeri casuali quando cambiano gli eventi del modello. Il controllo limite originario centrato sull’innesco aveva0,09ha, ma non è la posizione ora scelta dall’utente e non prova efficacia operativa.

## Prova web reale e regressioni

La prima prova end-to-end ha completato il riferimento `job-e9843385a7d24a81b101d5a1425227d8`, ma le altre due preparazioni hanno restituito STALE_FORECAST. Il campo originale era stato acquisito alle09:11:54Z; la prima preparazione delle12:10:22Z lo ammetteva entro3h, mentre le successive erano oltreTTL. **FAIL confronto iniziale**, **PASS rifiuto del dato scaduto**: esiti e input conservati, nessuna estensione TTL. Il retry del gruppo usa il campo fresco `map-weather-cb2fb8a37a7e386cca75724d`, disponibile alle12:12:32Z, con inizio comune futuro. Il retry è **PASS** con3job reali72h/288frame ciascuno, tutti iniziati18/10 alle13:00UTC (15:00Roma), stesso campoSHA `b6d5beba751eeaf6f36c9f8cfca1103a1fd25198e85a80fbd7769b1fb2d42065` e stesso terreno. Posizioni e tempi confrontati esattamente con le bozze originali rev5. Baseline `job-2065f1b44e7f422ab7098d9d3cfc8f04`:2552,85ha; prima area `job-d8c90cc03e4947289029b9c07421b606`:2793,06ha/20celle; seconda `job-b4b2d5219aad4177837cfacac47f0af8`:2669,715ha/16celle. Sono gli attuali risultati nel caso; anche qui non si osserva un beneficio affidabile. Conservati i job precedenti; caso rev17, mainrev59 invariata. Verificati nella VM15asset input,864array e864PNG conSHA. Quota9/48; nessun servizio a pagamento, installazione o riavvio. Totale8nuove esecuzioni native (4offline,1primo tentativo,3retry).

**PASS**102controlli browser finali (22workflow,28playback,22clock,30regressioni),9axe senza violazioni a375/768/1440 su Chrome155.0.8059.84;7testVM su moisture/pioggia/RH/vento/missing. Le suite che iniettano axe usano bypassCSP solo nel profiloQA, clock conCSP normale. **PASS**IAB reale: Calcola e riproduci avvia la catena, poi autoplay osservato a+17,25h e pausa a+21,75h; vista finale a+48h con lo stesso meteo sulle3mappe, screenshot `iab-updated-48h.png` nel raw. Sommario `reports/fire-coupling/verification.json`.

Le verifiche browser separano il trasporto QA dalla fisica: risposte controllate servono a verificare payload, coda, attesa e avvio, mai a dichiarare un risultato nativo. I test playback/clock leggono copie isolate dei piani realmente consumati per non confondere le modifiche utente con la fixture. Nessuna modifica alle coordinate dell’utente da QA. Il test iniziale della coda ha trovato un’interruzione degli altri scenari introdotta nella prima patch: corretta preservando gli esiti indipendenti e disabilitando soltanto l’avvio automatico. Ulteriore harness riallineato ai piani effettivi dopo il fallimento reale, senza cancellare i tentativi.

Comandi nella VM:

```sh
PYTHONPATH=src:/home/hazardia/m0/fire-src /home/hazardia/m0/fire-env/bin/python tests/native/fire_coupling.py --runtime /home/hazardia/hazardia-runtime --workspace <snapshot-workspace-privato.json> --run-id <nuovo-id>
PYTHONPATH=src /home/hazardia/m0/reflex-env/bin/python -m unittest discover -s tests/unit -p test_dynamic_fire.py -v
```

Il test nativo richiede tre scenari con baseline al primo posto, usa input nativi locali e crea una directory nuova; non acquisisce dati o modifica workspace. Le due prove utente sono confronti esplorativi: non richiedono una riduzione come criterioPASS. Browser: `tests/browser/fire-recalculate.cjs`, `fire-playback.cjs`, `scenario-clock.cjs`, `dynamic-fire.cjs`, con runtime/axe locali già documentati, output distinti. Raw `experiments/runs/fire-coupling-20261018`; input completi e output array nella VM sotto `runs/fire-coupling-20261018`, non redistribuiti.

**BLOCKED**skill storica, efficacia differenziale/logistica, qualificazione fuel/moisture e fullM5–M7, invariati. **NOT RUN**held-out, ensemble sufficiente per efficacia, nuoviFPS/p95/soak o secondaVM. Non è una previsione validata del rogo reale e non esegue azioni operative.
