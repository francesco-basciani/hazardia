# A3 — collegamento compatibile del catalogo ai worker

24 ottobre 2026 · run `domain-dispatch-20261024` · baseline privata `16955bd` (A2), tag stabile `stable-2026-10-24-pre-domain-evolution` conservato. Autorizzazione esplicita: «procedi». Reviewer: Codex self-check. Nessuna modifica al manoscritto o ai motori scientifici.

## Cambiamento implementato

PASS tecnico: `adapters/dispatch.py` collega il catalogo validato ai due worker esistenti, attraverso una tabella locale approvata. Il catalogo non fornisce nomi eseguibili: modulo, interprete e comando prodotto provengono solo dalla tabella/codice recensiti. Non ci sono import dinamici, shell, servizi nuovi o nuove dipendenze. I riferimenti dichiarativi restano metadati.

`adapters/pipeline.py` delega la selezione al nuovo collegamento, mantenendo i controlli SHA degli engine prima e dopo il lavoro. Gli stessi comandi e ambienti raggiungono PROPAGATOR e HMC→REFlEx. Restano invariati guard della patch sperimentale FLOOD, errore di hazard sconosciuto, worker scientifici, prodotti, schema delle richieste, JobStore, API, workspaces, solver/verifier e adattamento. La descrizione deve corrispondere alle revisioni nel runtime congelato: divergenza, catalogo mancante/corrotto o binding non approvato producono errore classificato prima del worker, mai fallback silenzioso.

Ogni nuova esecuzione scrive esclusivamente `adapter-binding.json`, con snapshot dei metadati, ID/versione/digest, liste di comandi e hash request/runtime. JobStore lo include già nel manifest degli artefatti; nessuna modifica al suo schema. È un binding al momento dell’esecuzione, non un freeze del descriptor all’accettazione. Gli input/runtime continuano a essere congelati alla submit come prima; codice/catalogo distribuiti restano quelli disponibili quando il processo viene avviato. Retry esplicito crea un nuovo job, senza alterare la ricevuta precedente.

La qualificazione rimane `UNQUALIFIED_RESEARCH`, l’autorità operativa non è concessa. Il lookup non implementa composizione universale, nuove policy o nuovi hazard. La UI non cambia in questo incremento: livelli a sinistra, parametri a destra, orario monitorato e IT/EN sono preservati.

## Esiti e prove

| Attività | Esito | Evidenza |
|---|---|---|
| Comandi/ambiente equivalenti al selettore precedente | PASS | Test differenziali su FIRE 0.2/0.3/0.4 e FLOOD 0.2/0.3, percorsi con spazi, nessuna mutazione degli input |
| Hash prima/dopo, guard FLOOD e hazard sconosciuto | PASS | Fault mirati: zero worker se hash iniziale errato; errore dopo prodotto se sorgente varia; codici e messaggi legacy identici |
| Catalogo mancante/corrotto, digest/revisione/binding non approvati | PASS | Errore classificato; nessun avvio worker o fallback; errore PACKAGE_RUNTIME attraversa il supervisore come job inutilizzabile |
| Timeout/cancellazione dopo lookup reale | PASS | Pipeline e JobStore reali con interprete **sintetico** dormiente; discendenti terminati, ricevuta conservata nel manifest; retry su ID nuovo |
| Regressioni VM | PASS | 212 unit + 47 web + 51 decision + 19 domain = 329 test, 11 nuovi per A3 |
| Regressioni client | PASS | 11 suite JS, nessuna modifica frontend; interazione manuale browser NOT RUN in A3 |
| PROPAGATOR legacy 600 s | PASS | Probabilità, fuoco, arrivo e raster identici al job archiviato; ricevuta verificata; singola esecuzione ~5,52 s |
| PROPAGATOR studio 72 h con 2 risorse | PASS | Output/raster finali e 288 frame esattamente identici al job archiviato; ricevuta verificata; singola esecuzione ~32,41 s |
| HMC→REFlEx nativi 6 h | PASS esecuzione e validator | Portate/bridge identici; ricevuta verificata; singola esecuzione ~45,57 s |
| Confronto raster REFlEx esatto | **FAIL** | 105 celle differenti, massimo scarto assoluto 7,4505806e-9 m; maschera, griglia e massimo coincidono |
| Conservazione | PASS | 311 file scientifici, 95 job e 145 file engine invariati; dei 14 file runtime confrontati cambia solo pipeline intenzionalmente; servizio RUNNING |
| A4 policy / A5 schemi-workspace / nuova VM | NOT RUN | Incrementi successivi; nessuna migrazione implicita |
| Qualificazione fisica/operativa M5–M7 | BLOCKED invariato | Le prove tecniche non qualificano accuratezza o efficacia degli interventi |

I test sintetici del supervisore non vengono contati come esecuzioni CIMA. I tre replay nativi usano copie degli asset/request/runtime congelati, in directory run nuove; non inviano job al DB della dashboard né acquisiscono nuovi dati. Stesse previsioni/azioni/semi nello studio: il PASS dimostra conservazione del comportamento già esistente, non efficacia reale dei mezzi.

## REFlEx: esito negativo conservato

La verifica richiede uguaglianza esatta e resta FAIL, come già in A2. L’upstream fissato usa inizializzazione casuale prima dell’ottimizzatore della profondità, documentata nel report A2. Il nuovo confronto osserva scarti di miliardesimi di metro con portate/maschera/massimo invariati. Non viene introdotta una tolleranza dopo aver visto i risultati e non si altera RNG, worker o output. Non è una nuova prova causale della sorgente della variabilità né una certificazione di equivalenza fisica.

Altri problemi registrati: un tentativo SSH parallelo termina prima dell’avvio del protocollo; tentativo sequenziale completato. Primo benchmark senza directory repository sul PYTHONPATH fallisce nell’import delle fixture; comando corretto `PYTHONPATH=src:.` completato. Raw dei tentativi separati e conservati.

## Prestazioni

VM esistente 6 vCPU/16 GiB, 30 campioni per serie, selezione FIRE su metadati fissati. Processo nuovo (page cache OS non svuotata): p95 selettore precedente 15,83 ms, nuovo 45,98 ms; nello stesso processo p95 precedente 0,0011 ms, nuovo 0,8586 ms. Queste sono misure del solo percorso di selezione, inclusi avvio/import nel caso cold; non FPS, consumo RSS, p95 della simulazione o deadline decisionale. Il lookup non entra nel thread HTTP o nel solver. Nessuna modifica a risorse VM, worker concorrenti, quote o deadline 60 s. Non è stata dichiarata una nuova soglia prestazionale più permissiva.

## Riproduzione, rollback e confini

Guida corrente `docs/DOMAIN-PACKAGES.md`; verificatore nativo `tests/integration/verify_package_catalog.py`; benchmark `tests/integration/benchmark_dispatch.py`. Evidenze redistribuibili in `reports/domain-dispatch/{verification,audit,native-replay,studio-replay,benchmark,client-tests}.json`. Protocollo e raw host `experiments/runs/domain-dispatch-20261024`; guest `runs/domain-dispatch-20261024-native` e `-studio`. Manifest dei replay con ipotesi, hash source/request/runtime prima del calcolo; nessuna sovrascrittura dei risultati storici.

Rollback: ripristino/redeploy del commit A2, senza eliminare artefatti o ricevute. Il tag stabile non è spostato; nessun interruttore di fallback aggira il catalogo non valido. L’installazione completa su nuova VM e un benchmark generale del framework restano NOT RUN. A4, estrazione delle policy preservando formulazione, unità, solver e verificatore, è il prossimo incremento distinto; nessun gate scientifico è dichiarato chiuso.
