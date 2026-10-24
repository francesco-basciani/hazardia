# Domain packages A2 — 24 ottobre 2026

Run `domain-packages-20261024`, baseline privata `1b7b03a`, checkpoint precedente `stable-2026-10-24-pre-domain-evolution`; reviewer Codex self-check. Autorizzazione dell’utente: procedere preservando PROPAGATOR e tutte le funzioni esistenti. Incremento A2 del progetto Stage 1, nessun manoscritto modificato.

## Implementazione

PASS: catalogo locale opt-in in sola lettura, due descrittori FIRE/FLOOD, schema rigido versionato, digest, identità, allowlist riferimenti e lookup. Nessuna nuova dipendenza, rete, installazione, worker o controllo UI. Gli upstream sono identificati dai commit già fissati nel runtime, non da versioni inventate. I descrittori sono inclusi nella distribuzione wheel. Semantica/limiti e riferimenti ai contratti esistenti espliciti, non un motore universale di composizione. Guida: `docs/DOMAIN-PACKAGES.md`.

Il percorso effettivo di esecuzione non è modificato: JobStore, API, dispatch, validator, worker, workspaces, policy/verifier e adattamento restano identici. Verificati 14 file di queste responsabilità rispetto al checkpoint stabile. Catalogo assente/non valido non blocca il framework: non è importato da questi percorsi. Riferimenti sempre metadati, mai import/esecuzione dinamica. Stato runtime/dati NOT_ASSESSED, ricerca non qualificata e nessuna autorizzazione operativa.

## Verifiche eseguite nella VM

| Verifica | Esito | Evidenza |
|---|---|---|
| Discovery valida FIRE/FLOOD, copie indipendenti, bounds, digest/versioni/duplicati/ref ignoti rifiutati | PASS | 11 test nuovi `tests.unit.test_package_catalog` |
| Assenza rete/scritture/subprocess/import scientifici durante discovery | PASS | audit hook in processo Python dedicato |
| Regressioni unit/web/decision/domain | PASS | 201 + 47 + 51 + 19 = 318 test; discovery separata per suite |
| Client IT/EN, meteo, playback, simboli, contesto aereo e pioggia | PASS | 11 suite JS, `client-tests.json` |
| Wheel offline e discovery da wheel estratto in cwd isolata | PASS | nessun download/install, package IDs verificati |
| PROPAGATOR legacy 600 s, stessi input/seme | PASS | array probability/fire/arrival e raster esattamente uguali; ~5,39 s singola esecuzione |
| PROPAGATOR studio 72 h, 2 risorse, stesso input/seme | PASS | array/raster finali e 288 frame di probabilità esattamente uguali; ~32,51 s singola esecuzione |
| HMC→REFlEx 6 h: esecuzione nativa, validator e portate HMC | PASS | catena reale completata in ~45,02 s; portate/bridge identici |
| REFlEx: confronto esatto raster archiviato | **FAIL** | 144/21025 celle con differenze fino a 4,1909516e-9 m; maschera, celle positive e massimo uguali |
| Conservazione dati e motori | PASS | 311 file, 95 job e 145 file motori invariati; servizio RUNNING |
| Nuovo dispatch A3, migrazioni schema, nuovi domini, nuova installazione VM, qualificazione fisica | NOT RUN / BLOCKED | A3 e nuova VM NOT RUN; qualificazione scientifica M5–M7 BLOCKED invariata |

La prova studio verifica la conservazione delle azioni e del meteo congelati, non dimostra efficacia reale dei due mezzi. Non sono state riacquisite previsioni diverse per un confronto chiamato identico.

## Risultato negativo REFlEx e diagnosi

Il requisito di uguaglianza esatta era fissato nel protocollo prima dell’esecuzione: il relativo FAIL resta immutato. Le statistiche massime e le 1220 celle positive coincidono; la griglia e il bridge delle portate coincidono. Il sorgente upstream già fissato contiene `h_first_attempt = r_min + rand(1) * (r_max - r_min)` prima di L-BFGS-B (`lib/reflex_tools_flooding.py`, riga 67), coerente con una variabilità numerica da inizializzazione casuale. Non è una prova causale isolata né una tolleranza d’equivalenza preregistrata. Nessun seed aggiunto silenziosamente, nessuna patch al simulatore o al raster. Il catalogo non entra nel processo scientifico e tutti i file runtime controllati sono identici al checkpoint. Non attribuiamo al nuovo catalogo questa variabilità, ma neppure dichiariamo riproducibilità bit-a-bit per REFlEx.

Altri esiti negativi conservati: comando di discovery aggregato dalla radice `tests` ha prodotto cinque errori di import tra fixture esistenti; eseguiti i comandi documentati per singola suite, tutti PASS. Estensione iniziale dello script di verifica con errore di indentazione prima del calcolo; corretta e nuova esecuzione studio conclusa. Nessuna modifica applicativa per aggirare i test.

## Prestazioni e limiti

Microbenchmark nella VM 6 vCPU/16 GiB, 30 campioni per serie: processo Python nuovo con catalogo p50 40,90 ms, p95 45,29 ms; interprete+JSON di riferimento p50 8,97 ms, p95 9,72 ms; discovery ripetuta nello stesso processo p50 0,59 ms, p95 0,93 ms. OS page cache non svuotata. Misura circoscritta, nessun claim FPS, RSS o p95 end-to-end del framework. Il catalogo è opt-in e non aggiunge lavoro al servizio o al ciclo dei simulatori. Deadline decisionale 60 s e gate P0 non modificati.

## Tracciabilità e prossimo incremento

Artefatti redistribuibili: `reports/domain-packages/{verification,preservation,native-replay,studio-replay,native-diagnosis,benchmark,client-tests}.json`. Raw host `experiments/runs/domain-packages-20261024/`; VM `runs/domain-packages-20261024-native`, `-studio`, `-packaging`. Protocollo native salvato prima dei processi con input/runtime hash e ipotesi; nuova versione del verifier include il proprio digest. Nessuna sovrascrittura di run esistenti. Benchmark riproducibile con `tests/integration/benchmark_package_catalog.py`; test nel guest, Mac solo sviluppo/display e copia evidenze.

A2 completato tecnicamente nel perimetro dichiarato. A3 resta da implementare: lookup di esecuzione compatibile per i due adapter attuali con confronto di comandi/errori e conservazione dei guard degli hash, della patch FLOOD e dell’isolamento. Non richiede rinominare scenari o cambiare la fisica. La ricerca sulla ripetibilità REFlEx è separata, con protocollo dedicato prima di qualsiasi nuova tolleranza o modifica RNG.
