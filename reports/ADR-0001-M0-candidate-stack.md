# ADR-0001 — Scelte candidate dopo il primo assessment M0

Data: 2026-10-15. Stato: **PROPOSTA CONDIZIONATA**, non autorizza M1, porting sostanziale o sostituzione dei simulatori. Evidenza RUN `m0-audit-20261015T122006Z`, report fattibilità e performance. L'architettura normativa di SPEC rimane invariata.

## Decisione e alternative

| Confine | Candidato iniziale | Alternativa e motivazione | Evidenza / limiti |
|---|---|---|---|
| Core e metadati | Python 3.12, JSON Schema versionato / Pydantic per API future | Core interamente TypeScript/Java o microservizi aumenterebbe i ponti con gli strumenti scientifici | Python ARM64 eseguito; librerie contract/API non installate; schema test NOT RUN |
| Fire | API upstream dentro **worker di processo** con manifest e file I/O, non nel server UI | Embedded nel backend riduce startup ma condivide guasti/RAM; container Linux più riproducibile ma non disponibile | Core diretto e nuovo processo PASS; seed equality FAIL; confronto Linux BLOCKED |
| Flood | HMC e REFlEx separati in Linux, bridge esplicito tracciato | Nativo macOS richiede toolchain/geospatial legacy; x86 guest emulato alternativa a Linux ARM | Nessuna catena eseguita; richiede scelta runtime, dati e validazione idrologica |
| Solver | HiGHS MIP via interfaccia sostituibile per assegnamenti e loss/CVaR lineari su scenari precalcolati | OR-Tools CP-SAT utile per scheduling discreto; richiede scaling intero; non tratta una loss fisica nonlineare come lineare | [HiGHS](https://highs.dev/) MIT e OR-Tools Apache-2.0 da metadata ufficiali; installazione e solve NOT RUN. Nessun solver scelto definitivamente prima del pilot |
| Backend | API locale FastAPI candidata, supervisor job distinto | Flask/Django possibili; framework non sostituisce timeout/process supervision | MIT metadata; non installato. API deve bindare loopback; auth per futuro sharing |
| Dashboard | React/TypeScript, MapLibre GL JS, tiles/asset locali | Leaflet più semplice per piccoli layer (BSD-2); OpenLayers candidato per esigenze raster/CRS da verificare | React MIT; MapLibre testo BSD e avvisi bundled: metadata GitHub NOASSERTION richiede testo completo, archiviato; GPU browser NOT RUN |
| Persistence | file raw hashati + JSON + GeoTIFF/COG + indice SQLite se necessario | PostGIS quando concorrenza/query lo giustificano, non obbligo iniziale | GIS roundtrip rasterio PASS; COG, GeoParquet, DB e web tiling NOT RUN |
| Linux | UTM già presente; guest ARM primo candidato tecnico, x86 fallback da valutare | Lima/Podman gratuiti candidati, non installati; no dipendenza obbligatoria da Docker Desktop/commercial cloud | Hardware hypervisor disponibile; nessun guest verificato; download grande da approvare |

Licenze candidate in `stack-license-metadata.json`; testo MapLibre e Miniforge archiviati perché l'identificatore API è NOASSERTION. Non sono SBOM completa, verifica legale della distribuzione o lock di versioni future. Tutte le versioni frontend/solver saranno fissate prima delle installazioni in milestone autorizzata. Node 16 attuale non scelto come baseline di build moderna.

Nessuna architettura alternativa sostituisce la catena CIMA. Qualora questa non fosse realizzabile: stop, evidenza e decisione utente, come SPEC §5. La VM contiene dipendenze del simulatore ma non equivale a validazione scientifica.

## Decision engine e degradation: responsabilità conservate

Il job manager prepara prodotti validi fuori dal percorso decisionale, conserva snapshot immutabili, limiti di concorrenza, bounded queue, timeout/cancel dell'albero processi, retry dichiarati e stato prodotto parziale/non utilizzabile. Il decision engine consuma problem snapshot e loss scenari con unità normalizzate e gradi d'evidenza. Un solver non può attribuire efficacia a UNKNOWN_EFFECT. Il verifier indipendente ripete tutti i vincoli hard e impedisce l'approvabilità se UNKNOWN; l'interfaccia solver mantiene distinti feasible, proof of infeasibility, timeout senza prova, input invalido e dependency unavailable.

Un supervisor indipendente deve scadenzare monotonicamente i 60 s includendo coda dopo accettazione, solver, verifier e risposta. Si riserva tempo a verifica/serializzazione nel pilot, senza assumere che un time limit del solver da solo garantisca il contratto API. Per robust loss MIP valutare expected + CVaR/max con linearizzazione solo di funzioni giustificate; euristica e warm-start possono proporre candidati ma non eludere il verifier. Risolvere con dati incompleti non è graceful degradation: si misura vettore delle sei capability e loss decisionale, con TTL e recupero solo da evidenza fresca. No dispatch.

## Inventario contratti per freeze M0/M1 (NOT RUN)

Versione proposta `0.1.0`, non ancora schema accettato. Tutti i record: schema_version, id, provenance, unità esplicite, tempi ISO UTC con fuso originale, CRS/datum, checksum/URI e semantica null/UNKNOWN. Cambi incompatibili richiedono ADR/migrazione. Non introdurre sinonimi incoerenti fra status pubblici e interni: mappatura esplicita da testare.

| Confine SPEC §7.1 | Esempio valido da congelare | Esempio negativo necessario |
|---|---|---|
| TerritoryProfile | AOI+CRS+timezone+giurisdizioni+calibration refs | CRS mancante, timezone invalido, calibrazione ignota non default Italia |
| Satellite observation | sensed/available/ingested, footprint, risoluzione, diritti | duplicato, copertura parziale/conflict non confidenza moltiplicata |
| Weather | issue ≤ available, valid, membro/grid/unità | issue-time assente, forecast scaduto, unità non convertibile |
| Sim input/output | job/version/grid/weather/hash, field unit, validAt | griglia o tempi discordanti, no-data fuori contratto, output parziale |
| Resource capability | tipo/qualifica/turno/autonomia/authority | ignoto campo hard, doppio booking, trasferimento non autorizzato |
| Intervention | PHYSICAL_EFFECT/IMPACT_ONLY, effect model/evidence | UNKNOWN_EFFECT con beneficio dichiarato, soccorso flood modifica portata |
| Decision request/response | snapshot+budget+candidate/verifier/termination | timeout→infeasible senza prova, candidate post deadline validato |
| Authorization | proposta+version+attore+scope+decisione+timestamp | permesso scaduto, attore non proprietario, dispatch esterno |
| Experiment manifest | run_id+hash+env+seed+command+code identity | hash rotto, SHA inventato, overwrite di un risultato |

Freeze completo, roundtrip ed esecuzione dei negativi NON effettuati; G-01 NOT RUN, non mascherato da questa tabella. Il manifest M0 espone onestamente l'assenza Git; non autorizza ad accettare tale assenza in futuri test di release. Nessuna libreria o componente di dominio implementato per aggirare il divieto di avviare il framework.

## Conseguenze e riesame

Costi principali: ambiente flood legacy e statiche/calibrazione, bridge fisico, RNG/replay, rendering/tile pipeline e timeout supervision. Ipotesi da riesaminare dopo standalone flood e pilot solver, poi prima di M1 con utente. Non allentare obiettivi UI/performance, non convertire pesi sintetici in policy operative, non confondere source availability con ground truth. Dashboard resta responsive per design da verificare in M3, non garanzia ottenuta dall'adozione di React.


## Evidence update — authorized UTM continuation, 2026-10-15

Run `m0-linux-rng-20261015T124458Z` supersedes the earlier environment-availability assumptions. Linux ARM64 in existing UTM successfully runs unmodified HMC and REFlEx0–4; an x86 guest is no longer a prerequisite for the demonstrated configurations. Retain separate flood environment (Python3.10/GRASS7.8.7) and fire environment (Python3.12/Numba0.62.1), bridged by versioned files. This preserves the baseline architecture, with no core/model substitution.

Candidate fire replay policy: one-thread process + explicit worker-context RNG helper version, tested on Mac/Linux; multi-thread/spotting/large-fixture behavior not established. Do not rely on a Python/serial seed alone. Candidate flood runner must detect HMC STOP/errors despite exit0 and kill nonadvancing adaptive0s integration; supported fixed1s config succeeds on the tested shared grid. REFlEx multiprocessing branch succeeds where serial branch fails. Physical qualification of peak/base/tconc remains BLOCKED; not an approved operational bridge or final solver/UI choice. G-01 implementation/tests remain NOT RUN. No M1 authorization inferred.

## M0 real-terrain evidence amendment — 2026-10-15
Original model source pins remain unchanged. Run `m0-real-terrain-20261015T142405Z` demonstrates a candidate two-line REFlEx compatibility procedure in an isolated experimental copy: a one-cell HAND workgrid halo and explicit authoritative bounds/resolution in serial raster merge. Original real-terrain quality FAIL retained, patched69reach technical checks pass, physical qualification pending. Not an architecture replacement or adoption of a maintained fork. Any eventual adapter must preserve source/patch identity and validate nonempty perreach products, not only process exit/file presence. The real DSM/Sentinel pilot also establishes a local georeferenced image path without paid basemap service; it does not implement the planned UI or ingestion connector. Full G-01 contract freeze remains NOT RUN.

## Runtime placement superseded by ADR-0002 — 2026-10-15
The user explicitly requires all execution components inside one Linux VM. Earlier per-engine native Mac/Linux options are historical alternatives only. Retain separate Python environments and isolated worker processes within that single VM. Future core/backend/jobs/solver/dashboard build and service must use this placement, with Mac as control/display client. No M1 authorization inferred.
