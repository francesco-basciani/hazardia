# Verifica del piano e della piattaforma HAZARDIA

16 ottobre2026. Run `plan-audit-20261016T054141Z`. Sorgente esaminato `d0f9f34d5b0ae0f2ca01349e21b3e21f31c5b44a`. Revisore: Codex, autocontrollo; nessuna revisione scientifica esterna. [Matrice strutturata](plan-audit/coverage.json). Questo audit non modifica requisiti, soglie o modelli e non avvia nuove implementazioni.

## Risposta alla domanda

**Il piano originale è ancora previsto, ma non è stato interamente realizzato né verificato. La piattaforma è un prototipo di ricerca utilizzabile: il rilascio completo resta BLOCKED.** Esistono funzioni reali e prove ripetibili; altre sono contratti o laboratori con dati sintetici, altre mancano. Nessun requisito aperto viene considerato implicitamente completato perché la dashboard si apre o i test software passano.

PASS nelle tabelle significa soltanto il perimetro espressamente verificato. BLOCKED significa che l'accettazione completa dipende da funzionalità/dati/prove mancanti; non indica automaticamente un ostacolo esterno o bisogno di permesso. NOT RUN significa prova/incremento non eseguito. FAIL indica criterio misurato non soddisfatto. Nessuna percentuale globale di completamento è dedotta da questi numeri eterogenei.

## Come è stato controllato

Letti requisiti/architettura, M0–M7 e dipendenze, ledger e protocollo/evidenze; ispezionati ingest, eventi, decisioni, rolling, adattamento, API/UI, test e report effettivi. Nuovo piano di audit fissato prima dei controlli runtime in `experiments/runs/plan-audit-20261016T054141Z/plan.json`, con hash degli otto documenti. Accesso SSH in sola lettura, GET health/catalog/jobs; regressioni in un prefisso indipendente della stessa VM. Nessuna nuova simulazione, fault injection, modifica di note/casi utente o test browser interattivo durante questo audit.

**Nuove prove PASS:** dashboard8080 RUNNING,7scenari a catalogo, nessun job QUEUED/RUNNING al controllo;85test nella VM (38unitari+19dominio+14decisione+14web). Output raw in `experiments/runs/plan-audit-20261016T054141Z/guest-regressions.json`; identità/sourcehash in `runtime-inspection.json`. Comandi guest: `../core-env/bin/python -m unittest discover -s tests/UNITA -v`, con UNITA=`unit`, `domain`, `decision`, `web`, dalla app del prefisso ricostruito.

Runtime originale attivo commit589cb5f; prefisso ricostruito6c44c4b. Il secondo ha tutti i file `src/` uguali al sorgente locale analizzato; nell'originale differisce soltanto `src/hazardia/jobs.py`, per il supporto del prefisso GRASS privato aggiunto al bootstrap. Non confondere pubblicazione con aggiornamento automatico del servizio: UI attiva conservata, nessun restart/deploy durante audit. Le85regressioni nuove appartengono al prefisso ricostruito, non sono una nuova campagna browser o storico-fisica.

## Requisiti funzionali, inclusi quelli presenti solo in parte

| ID | Esito di accettazione | Cosa esiste e cosa resta | Riferimento |
|---|---|---|---|
| FR-01 — Profili territoriali e validazione | PASS | Contratti e due fixture; configuratore geografico completo in UI assente. | [contracts.py](../src/hazardia/domain/contracts.py) |
| FR-02 — Acquisizione/cache satellitare sostituibile | PASS | STAC e snapshot reali; non monitoraggio satellitare continuo. | [providers.py](../src/hazardia/ingest/providers.py) |
| FR-03 — Associazione/tracciamento eventi | BLOCKED | Deduplica, conflitto e ambiguità testati; confronto con baseline semplici richiesto dalla SPEC non dimostrato. | [events.py](../src/hazardia/domain/events.py) |
| FR-04 — Fusione conservativa | PASS | Fixture con correlazione/conflitto; confidenza non calibrata, nessuna skill osservativa dichiarata. | [test_domain.py](../tests/domain/test_domain.py) |
| FR-05 — Salute fonti/sensori | BLOCKED | Controlli stale/coverage e fault sintetici; manca catena automatica di salute delle fonti reali. | [control.py](../src/hazardia/adaptation/control.py) |
| FR-06 — Meteo storico/previsioni/ensemble | BLOCKED | ERA5 reale e acquisizione MET separate; manca forzante forecast completa, coerente con nuovi modelli ed ensemble. | [M7-validation.md](../reports/M7-validation.md) |
| FR-07 — Esecuzione simulatori reali | PASS | PROPAGATOR e HMC→REFlEx eseguiti; scenari non calibrati, patch REFlEx dichiarata. | [PUBBLICAZIONE-GITHUB.md](../reports/PUBBLICAZIONE-GITHUB.md) |
| FR-08 — Separazione fisica e conseguenze | PASS | Evacuazione impact-only; laboratorio fisico incendio distinto; azioni non supportate rifiutate. | [consequences.py](../src/hazardia/domain/consequences.py) |
| FR-09 — Esposizione/vulnerabilità/accessibilità | PASS | Rappresentazione e provenienza testate con dati sintetici; mancano censimenti e rete stradale operativa verificata. | [consequences.py](../src/hazardia/domain/consequences.py) |
| FR-10 — Risorse e vincoli | PASS | Contratti/verificatore e negativi testati; unità e soglie di ricerca, non inventario reale. | [verifier.py](../src/hazardia/decision/verifier.py) |
| FR-11 — Proprietà/trasferimenti/riserve | PASS | Due regioni sintetiche e autorizzazioni; nessuna autorità giuridica reale certificata. | [M4-joint.md](../reports/M4-joint.md) |
| FR-12 — Solver sostituibile, robustezza, rolling | PASS | HiGHS e enumerazione di riferimento, checker separato, expected/worst e continuità; obiettivi/effetti sintetici. | [controller.py](../src/hazardia/decision/controller.py) |
| FR-13 — Alternative candidate e stati negativi | BLOCKED | Stati negativi presenti; un optimum e baseline, manca portfolio di strategie distinte/frontiera. | [controller.py](../src/hazardia/decision/controller.py) |
| FR-14 — Deadline sperimentale60s | PASS | Due campagne n30 su piccolo fixture; non garantisce nuovi run fisici entro60s né qualsiasi carico. | [M5-adaptive.md](../reports/M5-adaptive.md) |
| FR-15 — Sei capacità e transizioni | PASS | Regole e recupero con evidenze sintetiche; monitor reale distinto e incompleto. | [control.py](../src/hazardia/adaptation/control.py) |
| FR-16 — Ottimizzare conservazione capacità | BLOCKED | Fallback e fault testati; manca ottimizzazione generale delle capacità prioritarie e confronto sperimentale completo. | [M6-degradation.md](../reports/M6-degradation.md) |
| FR-17 — Allerte predittive georiferite reali | BLOCKED | Lifecycle su replay scritto a mano; manca watcher reale di impatti, lead time/falsi allarmi osservati e review window qualificata. | [alerts.py](../src/hazardia/adaptation/alerts.py) |
| FR-18 — Tutti i workflow UI previsti | BLOCKED | Mappe, confronto, job, revisione e laboratorio presenti; builder territorio/fonti/eventi/ensemble e confronto completo strategie non coperti. PASS del vecchio slice non vale per requisito intero. | [server.py](../src/hazardia/web/server.py) |
| FR-19 — Manifest, traccia ed export | PASS | Provenienza e pacchetto/hash verificati; non equivale a campagna scientifica completata. | [PUBBLICAZIONE-GITHUB.md](../reports/PUBBLICAZIONE-GITHUB.md) |
| FR-20 — Preposizionamento valutato | PASS | Stessi vincoli indipendenti su modello sintetico120/480s; efficacia sul campo non provata. | [M6-degradation.md](../reports/M6-degradation.md) |
| FR-21 — Worker isolati e risultati parziali | PASS | Crash reale del solo job alluvione e FIRE conservato; cancellazione/retry testati storicamente, non ripetuti durante audit. | [M6-degradation.md](../reports/M6-degradation.md) |
| FR-22 — Una VM, locale e senza servizi a pagamento | PASS | Runtime attivo e ricostruito nella stessa VM; dipendenze separate, Mac client. Portabilità nuova macchina non provata. | [ADR-0002-single-linux-runtime.md](../reports/ADR-0002-single-linux-runtime.md) |
| FR-23 — P1: collaborazione/notifiche/interoperabilità | NOT RUN | Differito esplicitamente; confronto con prodotti commerciali non autorizza dispatch o collaborazione operativa. | [SPEC.md](../SPEC.md) |
| FR-24 — Responsive e accessibilità di base | PASS | 375/768/1440 e tastiera/axe; incompletes conservati, nessuna certificazione WCAG. | [UI-CONTROL-ROOM.md](../reports/UI-CONTROL-ROOM.md) |
| FR-25 — Job lunghi e UI interattiva | PASS | Job reale, pan/cancel/retry verificati nel pilot; acquisizione e previsione live complete ancora mancanti. | [M3-dashboard.md](../reports/M3-dashboard.md) |
| FR-26 — Confronto completo/scala/delta/export | BLOCKED | Coppie sincronizzate e export presenti; workflow generale multi-day/flood e carichi grandi non qualificati,100kFAIL. | [M7-validation.md](../reports/M7-validation.md) |
| FR-27 — Cache/windowing/concorrenza | PASS | Controlli di limiti e navigazione senza nuovi run sul fixture; non capacità illimitata del browser. | [MAPPE-DETTAGLIO.md](../reports/MAPPE-DETTAGLIO.md) |
| FR-28 — Osservabilità/errori | PASS | Metriche job/API/browser nei run, stati errore; non una piattaforma di telemetria continua per ogni carico. | [M3-dashboard.md](../reports/M3-dashboard.md) |

## Qualità e performance

| ID | Esito | Perimetro / mancanza |
|---|---|---|
| QR-01 | PASS | Checker/UNKNOWN/autorità, nel modello di ricerca |
| QR-02 | PASS | Deadline n30, workload piccolo fissato; non hard real-time |
| QR-03 | PASS | Crash reale isolato, prove storiche conservate |
| QR-04 | BLOCKED | Replay FIRE esatto; FLOOD197celle differiscono max1.49e-8m, causa/tolleranza statistica e installazione OS indipendente non risolte |
| QR-05 | PASS | CRS/unità/tempi/provenienza e negativi |
| QR-06 | PASS | Confronti controllati e mismatch; evacuazione non cambia raster |
| QR-07 | PASS | Localhost/protezioni di ricerca; push sorgenti ora autorizzato; sicurezza deployment condiviso NOT RUN |
| QR-08 | BLOCKED | Due profili contrattuali; workflow fisico/decisionale Senegal completo NOT RUN |
| QR-09 | PASS | Identità job/decisioni, transizioni, errori e hash |
| QR-10 | PASS | Lifecycle/lead time/falsi allarmi sul replay sintetico controllato; skill su osservazioni indipendenti NOT RUN e FR-17/M5 BLOCKED |
| QR-11 | PASS | Budget interazione su piccolo fixture, evidence storica n30; non100k |
| QR-12 | PASS | API warm e3cold display; completamento ortofoto online escluso dal segnale iniziale |
| QR-13 | PASS | Job reale lungo/cancel/retry/UI sul pilot |
| QR-14 | FAIL | 100kdisplay senza campioneFPS valido/heap1.316GB;30min vecchia UI PASS, nuova UI soak NOT RUN |

## Richieste aggiuntive confermate

| ID | Esito | Verifica |
|---|---|---|
| AR-EXT-01 | PASS | Sette possibilità conservate nei confini/versioni; AT-EXT M1/M2/M3 controllati, non prova di sostituibilità fisica universale. |
| FR-MAP-01 | PASS | Ortofoto Abruzzo20cm nominali e Sentinel10m, coordinate/ricerca/scala; strade/POI locali, confini/quartieri ufficiali/catasto non coperti integralmente. |
| FR-MAP-02 | BLOCKED | Coppia nativa incendio con fascia ideale PASS; confronto fisico alluvione e azioni generali integrati nel decision engine NOT RUN. |
| FR-HORIZON-01 | BLOCKED | Laboratorio incendio72h reale PASS; jobUI10/30/60min, solver1–12slot e alluvione massima6h: durata generale di giorni NOT RUN. |
| FR-UI-REF-01 | BLOCKED | Restyling/strumenti cartografici salvati PASS; parità funzionale Tactical Analyst/Geospace NOT RUN, editor fisico libero e feeds mancanti. |
| FR-FLOOD-ACTIONS-01 | NOT RUN | Laminazione/invasi, argini e pompaggio richiesti tutti; nessuna delle tre integrazioni fisiche verificata. |
| FR-REPRO-GH-01 | PASS | Sorgenti/script/guide pubblicati, clone191hash PASS; nuovo prefisso nella stessa VM PASS, bootOS nuovo NOT RUN. |

## Scenari d’uso originali

| Scenario | Esito | Perimetro |
|---|---|---|
| SC-01 | BLOCKED | Contratti/ingest presenti; configurazione geografica e builder UI completi assenti. |
| SC-02 | PASS | Tutti i tre motori reali, input dichiarati non calibrati. |
| SC-03 | BLOCKED | Evacuazione e fascia ideale; confronto ground/aerial/mixed e alluvioni fisiche non completo. |
| SC-04 | PASS | Due aree/due hazard/risorsa condivisa sintetica, checker indipendente. |
| SC-05 | BLOCKED | Solo replay sintetico, non catena predittiva reale. |
| SC-06 | BLOCKED | Fault/preservazione sicura provati; ottimizzazione generale e fonti reali mancanti. |
| SC-07 | BLOCKED | Osservazioni CEMS acquisite; hindcast corrispondenti/scoring indipendente non eseguiti. |
| SC-08 | BLOCKED | Profili Italy/Senegal testati; workflow completo senza modifiche core non eseguito. |
| SC-09 | PASS | Revisione modellata append-only; nessun dispatch reale. |

## Milestone e rispetto delle dipendenze

| Milestone | Evidenza realizzata | Accettazione residua |
|---|---|---|
| M0 | PASS fattibilità: installazione, mini-run reali, ponte tecnico, fonti/licenze/stack/benchmark | Non era una certificazione della fisica; problemi originali conservati |
| M1 | PASS tecnico su fixture: acquisizione, adattatori, job e prodotti georiferiti | Generalità, calibrazione e dati storici non seguono dal PASS tecnico |
| M2 | PASS tecnico su contratti, due profili, fusione e conseguenze | Baseline evento FR-03 non dimostrata, dati territoriali reali completi non integrati |
| M3 | PASS dello slice decisionale/UI piccolo | FR-18/26 completi BLOCKED; portfolio, workflow UI generali e azioni fisiche non completi |
| M4 | PASS del fixture congiunto autorizzazioni/riserva/no-overbook | Regioni e risorse sintetiche; non verifica di governance reale o efficacia |
| M5 | PASS meccanismi robust/rolling/lifecycle e n30 deadline | BLOCKED forecast reale coerente, impatti/allerte osservate, baseline e sensibilità principali |
| M6 | PASS regole/fault/crash/recupero sintetico/preposizionamento | BLOCKED funzione generale conservazione capacità, salute fonti reale e confronti completi |
| M7 | PASS pilot tecnico, acquisizione osservazioni e pacchetto sorgenti | BLOCKED hindcast fire/flood, seconda geografia end-to-end, installazioneOS indipendente, ablation/main study e100kdisplay |

**La sequenza di costruzione dei componenti è riconoscibile, ma non tutte le dipendenze di chiusura sono state soddisfatte.** M5–M7 sono state esplorate sotto autorizzazione continua mentre i gate completi precedenti restavano aperti. Sono incrementi tecnici provvisori: non dimostrano che il piano sia stato completato in ordine con tutti i criteri PASS. L'autorizzazione a procedere non elimina un criterio di accettazione. Non cambiamo retroattivamente il piano per far coincidere la consegna con il target.

## Architettura: cosa è preservato

PASS della revisione nei confini concretamente esercitati: incendi/alluvioni, processi isolati, contratti versionati, regole indipendenti dal solver, HiGHS/reference, decisioni separate da rendering e fisica, assenza di dispatch, una VM. I sette punti futuri restano tutti previsti: acquisizione (`ingest`), stato temporale (`domain/state.py`), predizione (`adapters`), valutazione (verificatori e protocollo di ricerca), identità/versione (manifest), futura coordinazione agenti (nessun runtime obbligatorio), policy di dominio (`decision/problem.py` e checker). Le prove M3 di sostituzione sono controllate e finite, non una prova di sostituibilità di qualunque modello. Le versioni correnti ammettono esplicitamente due hazard: nuovi domini richiedono evoluzione di contratto, non si attivano cambiando un nome. Nessun Digital Twin, AI/agent framework, training continuo o terzo dominio è dovuto nella V1 concordata.

Il termine “ibrido” indica oggi vincoli/ottimizzazione più regole/validazione: non esiste un pianificatore AI addestrato. Il solver è separato e sostituibile nel perimetro testato; il generatore di casi della dashboard è ancora specifico del fixture Abruzzo. Portabilità del core e portabilità dell'intera applicazione sono verifiche diverse.

## Disallineamenti documentali corretti da questo audit

1. FR-03: precedente PASS sul solo algoritmo/fixture non dimostrava il confronto con baseline richiesto. Accettazione intera riclassificata BLOCKED, prove passate conservate.
2. FR-18 e FR-26: precedente PASS dello slice piccolo non dimostrava tutti i workflow/confronti e la scala previsti. Accettazione completa BLOCKED; UI implementata e test PASS non cancellati.
3. QR-10: lifecycle su due truth-case inventati non prova qualità delle allerte su replay osservativo. Accettazione completa BLOCKED.
4. MEMORY “Current next action” chiedeva ancora quale intervento alluvionale scegliere: obsoleto, utente ha richiesto tutti e tre. Anche il riferimento HMC “candidate pending compatibility” è superato dall'esecuzione tecnica.
5. Voci aggregate “30min pending”, “replication pending” e “no push” erano anteriori ai checkpoint: aggiornate distinguendo soak storico PASS/nuova UI NOT RUN, ricostruzione stessoOS PASS/nuovoOS NOT RUN, pubblicazione codice PASS/servizio pubblico non avviato.

Queste correzioni aumentano la precisione del registro; non sono nuove funzionalità né cambi di scope approvati tacitamente. SPEC resta invariata e ogni vecchio run conserva l'esito originario.

## Lavoro residuo, nell’ordine utile

1. **Interventi fisici e durata:** completare valutazione/prova invasi-laminazione HMC; valutare componente idraulica per argini/pompaggio, presentando eventuale adozione sostanziale prima di applicarla. Integrare confronti fisici e giorni nel normale builder/job/decisione, preservando il laboratorio72h come evidenza circoscritta.
2. **Fonti, territorio e casi:** forecast/ensemble realmente completi e coerenti, aggiornamenti automatici con salute fonti, esposizione e accessibilità attribuibili, AOI/bacini/eventi e UI di configurazione; scelta e split storici prima dello scoring. Disponibilità/diritti/competenza di dominio possono bloccare specifici punti, non dipendono semplicemente da più RAM.
3. **Decisioni/adattamento:** portfolio di alternative, impatti multiobiettivo con unità esplicite, ottimizzazione delle capacità; baseline per eventi, robustezza, anticipazione e degradazione, con test indipendenti.
4. **Qualità e riproduzione:** correggere scala/rendering grandi carichi, provare orizzonti/carichi M/L supportati, soak nuovaUI, workflow completo Senegal sintetico, boot/installazione su OS nuovo entro risorse autorizzate o con proposta motivata.
5. **Validazione e ricerca:** un hindcast Abruzzo per hazard con osservazioni coerenti, calibrazione/limiti/esperto, main study e ablazioni H1–H3, parametri e campioni fissati prima delle nuove misure; figure/manoscritto solo sulle evidenze reali. Nessun paper o claim scientifico concluso.

Gli incrementi ordinari restano autorizzati. L'audit non richiede di ripetere il permesso per M1 né di rinunciare a requisiti. Installazioni privilegiate, risorse/download oltre i limiti, nuova architettura idraulica sostanziale, spese o operazioni reali richiedono le decisioni già previste. **Aumentare la potenza può aiutare carichi misurati; non crea dati, calibrazione, fisica degli interventi o software mancante.**
