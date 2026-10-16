# ADR-0004 — Estensibilità architetturale prima di M1

Data: 2026-10-15. **Stato: decisione confermata dall'utente; allineamento documentale completato. Verifica eseguibile dell'estensibilità NOT RUN. M1 non autorizzata.** Fonte: richiesta utente «HAZARDIA — Architectural Extensibility Requirement (Before M1)», conservata con checksum nel record `reports/doc-extensibility-20261015T154021Z/`. Nessun nuovo esperimento scientifico.

## Decisione e motivazione

Preservare la compatibilità architetturale con una futura piattaforma predittiva multidominio basata su Digital Twin, modelli fisici e AI e agenti specializzati, senza implementarli adesso. Si tratta di un vincolo sul disaccoppiamento del lavoro già pianificato. Non modifica l'ordine M1.1–M1.5, i simulatori approvati, i requisiti di qualità/sicurezza, la collocazione nell'unica VM Linux o le condizioni di autorizzazione.

I sette punti concettuali sono descritti in SPEC `AR-EXT-01`: ObservationProvider, TerritorialStateProvider, PredictionModel, ModelEvaluation, ModelRegistry, AgentOrchestrator, DomainDecisionPolicy. Non sono classi, servizi o nuove dipendenze da creare. In M1 si concretizza soltanto quanto necessario ai connettori, adapter e manifest esistenti; valutazione, policy e orchestrazione restano nelle milestone che già ne richiedono le responsabilità.

Acquisizione/normalizzazione, stato territoriale, previsione fisica, impatti, decisioni/allocazione, adattamento e visualizzazione comunicano attraverso contratti espliciti versionabili. Nessun import dei dettagli interni CIMA nel core decisionale, nessuna sorgente o geografia fissata nel solver. Un futuro Digital Twin fornisce stato/provenienza, senza sostituire il decision engine; agenti e modelli futuri restano soggetti al verifier indipendente, alle validità temporali e all'autorizzazione umana. Un nuovo modello non è automaticamente qualificato perché rispetta lo schema.

Alternative considerate: costruire subito gerarchie astratte/registry/servizi agentici sarebbe sviluppo prematuro e fuori scope; ignorare le estensioni fino al termine potrebbe consolidare dipendenze evitabili. Si sceglie la separazione già coerente con SPEC, con verifiche concrete differite ai componenti effettivamente esistenti.

## Riesame delle assunzioni correnti

| Assunzione letta | Esito del riesame documentale | Trattamento |
|---|---|---|
| SPEC core hazard-neutral, worker isolati e connettori sostituibili | PASS: compatibile sulla carta | Conservare contratti ai confini; verificare i veri adapter in M1. |
| Flusso descrive PROPAGATOR e HMC→REFlEx | PASS: scelta della V1, non vincolo universale | Mantenerli reali e approvati; non sostituire un simulatore fisico senza autorizzazione. |
| Schemi M0 0.1.0: FIRE/FLOOD, un tipo di meteo, griglie allineate, bundle chiuso | PASS con limite esplicito: fixture finiti, non contratto universale | Restano immutabili; eventuali nuovi formati richiedono versione, ADR, migrazione e test. Mai accettare campi/effetti sconosciuti per rendere il formato genericamente permissivo. |
| PLAN colloca decision core in M3 | PASS: dipendenza da rispettare | La sostituzione senza modificare quel core è NOT RUN in M1 e deve essere esercitata in M3, non anticipata costruendo il core in M1. |
| Simulazione fisica distinta da impatti/efficacia | PASS: preservata | Capacità, unità, incertezza, tempi e qualificazione devono essere dichiarati; nessuna equivalenza fisica dedotta dall'interfaccia comune. |
| Runtime unico locale, performance e portabilità | PASS: nessuna nuova dipendenza prevista | Nessun framework Digital Twin/agentico richiesto. Verifica dipendenze/processi in M1 e ai successivi gate; conservare budget UI/decisioni. |

Questi PASS riguardano il riesame e l'allineamento dei documenti, non l'esistenza o l'estensibilità del software.

## Verifica prevista

La matrice con ID `AT-EXT-01…05` è in PLAN e CHECKLIST §N, registro ufficiale. In M1: leggere prodotti reali tramite contratti, cambiare configurazione del provider con fixture controllati, ispezionare dipendenze e avvio nello stesso guest senza runtime aggiuntivi. Non pretendere una dimostrazione del core ancora assente. In M2: controllare stato temporale e normalizzazione. In M3: eseguire una sostituzione controllata di un adapter per lo stesso hazard/prodotto dichiarato, senza cambiare codice del core, con esiti e verifiche registrati. Un adapter di prova può dimostrare il confine software, deve essere etichettato e non può sostituire le prove fisiche CIMA né dimostrare qualità di un altro modello reale.

L'integrazione di un vero modello AI, Digital Twin o agente resta fuori dall'attuale M0–M7 e richiede futura autorizzazione. Non è un nuovo obbligo nascosto di M7. Le possibilità di valutare evoluzione dei modelli ed estensibilità sono future opportunità scientifiche, non nuove RQ confermate o risultati sperimentali.

## Stato e autorizzazione

Documenti allineati: PASS; implementazione/verifiche runtime `AT-EXT-01…05`: NOT RUN. M0 resta BLOCKED per qualificazione e dati idrologici reali; questo vincolo non risolve né aggira il gate. Nessuna interfaccia vuota, installazione, servizio, esecuzione scientifica o modifica agli artefatti congelati. Avviare M1 richiede esplicita autorizzazione utente e riesame dei prerequisiti M0: la richiesta ricevuta dispone di fermarsi dopo l'allineamento se M1 non è già autorizzata.

## Chiarimento confermato dall'utente — 15 ottobre 2026
Concentrarsi esclusivamente sui due domini originali, incendi e alluvioni. I sette punti restano possibilità architetturali future, senza sette linee di sviluppo o nuovi deliverable. Le verifiche di compatibilità si applicano ai confini concreti dei componenti già previsti, nelle rispettive milestone. Nessuna implementazione Digital Twin/AI/agenti/registry o di altri domini richiesta. Questo chiarimento documentale non avvia M1 né cambia gli esiti sperimentali.
