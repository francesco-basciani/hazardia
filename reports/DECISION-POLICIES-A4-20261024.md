# A4 — policy decisionali separate, comportamento conservato

24 ottobre 2026 · run `decision-policies-20261024` · baseline privata `9841d29`, pubblica `41ca275` · autorizzazione dell’utente «Procedi!» dopo A3. Reviewer: Codex self-check. Incremento della migrazione approvata, nessun manoscritto modificato.

## Implementazione e confini

PASS tecnico: `decision/policies.py` definisce due policy locali immutabili, collegate ai contratti già esistenti: esposizione sintetica in persone (0.5.0) e assegnazione ideale antincendio in punti di priorità (0.6.0). Sono estratti header, categorie, skill/equipment/effect dichiarati, esclusività del target e comportamento del controller su riserva/risultato vuoto/fallback. Il modello MILP, l’aritmetica degli obiettivi, i vincoli, il fallback e gli algoritmi non cambiano. Nessuna policy dinamica o nuovo hazard; nessuna formulazione universale.

`problem.validate` mantiene firma e messaggi/errori; l’assembler HiGHS usa costanti della policy ma mantiene le proprie espressioni e predicati. Il controller mantiene solver pluggable, budget, riserva 0,1s/2s, watchdog e fallback verificato. I valori pubblici `fire_ideal.POLICY` e `CATEGORIES` restano uguali. Nessuna modifica a payload legacy, unità, risorse/scenari o endpoint.

Il verificatore e la funzione losses sono byte-per-byte invariati; nessun import delle policy o riuso dei predicati di ammissibilità/righe del solver. La validazione dell’input resta condivisa come prima; le regole dirette e il calcolo delle perdite restano indipendenti. Un fault controllato alla skill della policy solver viene respinto dal checker. La separazione non rende operativi i mezzi, non autorizza velivoli e non trasforma il proxy di copertura in efficacia fisica.

## Esiti eseguiti nella VM

| Attività | Esito | Riscontro |
|---|---|---|
| Due policy esplicite, immutabilità, unità distinte, header/versioni ignoti rifiutati | PASS | 9 nuovi test in `tests.decision.test_policies` |
| Import policy senza dipendenze del solver/geo/JSON Schema | PASS | processo nuovo e subprocess HiGHS puliti, nessuna installazione |
| Equivalenza dei validator | PASS | 122 confronti accettazione/eccezioni/messaggi con implementazione pre-A4 |
| Matrici/modelli HiGHS | PASS | Sei LP serializzati identici tra vecchio e nuovo worker, incluse due istanze archiviate; stesse assegnazioni, verifiche e losses |
| Controller | PASS | Otto flussi old/new identici salvo ID/timestamp/elapsed: enumerazione, safety UNKNOWN, zero risorse e solver assente per entrambe le policy |
| Regressioni | PASS | 212 unit + 47 web + 60 decision + 19 domain = 338 test; 11 suite JS |
| Pilot deadline | PASS nel carico fissato | 30 richieste per policy, 60 totali, stessi risultati della baseline; tutte entro 60 s, risposta finale serializzata inclusa |
| Conservazione | PASS | 311 file scientifici, 95 job e 145 file dei motori invariati; servizio RUNNING; 12 file di confine invariati inclusi verifier/watchdog/rolling/CIMA/API/JobStore |
| Nuovi replay fisici CIMA / browser interattivo / VM da zero / migrazione schema A5 | NOT RUN | Worker e dispatch CIMA immutati, nessuna necessità concreta di migrazione dimostrata |
| Gate scientifici completi M5–M7 | BLOCKED invariati | Nessuna nuova accuratezza fisica/logistica/interventi qualificata |

I sei casi sono FIRE, FLOOD e JOINT sintetici, policy ideale sintetica, problema 0.5 archiviato e problema ideale 0.6 archiviato dalla dashboard. Gli input di ciascuna coppia sono copiati e fissati prima dell’esecuzione; confronto di modello e solver reale HiGHS nell’ambiente decision-env, validazione nel core-env. Nessun provider live, dispatch reale o modifica al DB applicativo.

Il fallback resta disponibile nella policy ideale quando il solver manca; nell’esposizione il codice precedente restituiva DEPENDENCY_UNAVAILABLE e continua a farlo. Con safety UNKNOWN non vengono introdotte assegnazioni non verificate. Zero risorse conserva i diversi stati storici: selezione vuota verificata 0.5 vs NO_ADMISSIBLE_ACTION 0.6. Non è una nuova estensione della graceful degradation a domini non implementati.

## Prestazioni del pilot e validità

VM esistente 6vCPU/16GiB, 30 ripetizioni sequenziali per ciascuno di due piccoli problemi archiviati, budget esplicitamente fissato a60s e copie con hash. Esposizione: p50 0,12337s, p95 0,17503s, massimo0,17786s. Ideale: p50 0,12121s, p95 0,12390s, massimo0,12397s. Il chiamante misura da prima del watchdog fino al ritorno dopo scrittura della risposta; i processi controller/solver sono nuovi a ogni richiesta, cache OS non svuotate. Tutte60selezioni/perdite coincidono con la baseline confrontata.

Questo è un pilot software su carico fissato, non un benchmark di scalabilità, coda HTTP, carico concorrente o confronto statistico di velocità con A3. Ordine dei workload fisso, misure correlate, una sola VM e nessuna valutazione di usabilità/qualificazione fisica. Non viene chiuso il gate generale dei60s né rilassato alcun P0.

## Problemi e correzioni preservati

Il primo tentativo di audit in decision-env fallisce per JSON Schema: la nuova policy importava indirettamente il validator del core e l’ambiente solver non lo contiene. Dipendenza rimossa usando soltanto HazardError e controlli leggeri; aggiunto test in processo nuovo che vieta jsonschema/highspy/numpy/geo nel solo modulo policy. Il driver dell’audit è stato separato: core-env per validator/controller, subprocess decision-env per worker HiGHS vecchio/nuovo, senza aggiungere pacchetti o mescolare gli ambienti. Le prove finali girano negli ambienti previsti e passano. Il log fallito non è sovrascritto.

L’uguaglianza esatta REFlEx rimane il FAIL già documentato in A2/A3: non ripetuto o reinterpretato in questo incremento, nessuna modifica a RNG o tolleranze.

## Riproduzione e migrazione

Guida `docs/DECISION-POLICIES.md`; script `tests/integration/verify_decision_policies.py` e `benchmark_decision_policies.py`. Evidenze pubblicabili `reports/decision-policies/{verification,differential,deadline-pilot,preservation,source-boundaries,client-tests}.json`. Raw host `experiments/runs/decision-policies-20261024`, VM `runs/decision-policies-20261024/{differential-2,differential-final,deadline-pilot}`; baseline Python estratte dal commit precedente, checksum nel protocollo scritto prima delle prove. Mai eseguire baseline Python non attendibili.

A4 completato tecnicamente. A5 schemi/workspace e A6 nuovi domini/MDE restano NOT RUN/DEFER: richiedono un bisogno concreto e compatibilità verificabile, non una rinomina generale dei dati. Le basi A2/A3/A4 sono implementate mantenendo i percorsi esistenti; nessuna conclusione di piena universalità del framework. Rollback tramite revert/redeploy A3, senza toccare archivi o workspace. Il checkpoint stabile rimane invariato.
