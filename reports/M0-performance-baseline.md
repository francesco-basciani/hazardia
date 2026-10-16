# M0 — Ambiente e protocollo di riferimento delle performance

15 ottobre 2026. **M0-PERF PASS per inventario e definizione del protocollo; misure di framework/UI NOT RUN.** Evidenza: `experiments/runs/m0-audit-20261015T122006Z/host-and-git.json`, `manifest.json`; dettagli esecuzioni fire in `M0-feasibility.md`. Revisore automatico artefatti: `verify-evidence.py`; review umana pendente. Git assente (SHA/dirty null), sostituto documentale esplicito `baseline.json`, non equivalente a commit.

## Host congelato per il pilot

MacBook Pro Mac16,8 / M4 Pro ARM64, 14 CPU core, 48 GiB RAM, GPU 20 core Metal 4, macOS 27.0.1 (26A434), Chrome 155.0.8059.79, display 3024×1964. Venv Python 3.12.2, Numba 0.62.1, SciPy 1.18.1, NumPy 2.3.5, llvmlite 0.45.1, rasterio 1.4.3. Freeze completo archiviato. Circa 56 GiB disco libero iniziale. UTM 4.6.4 presente; guest/limiti Linux non verificati. Nessun container runtime nel PATH. Test WebGL, browser automatico, scheduler, GPU compute: NOT RUN.

Questo è il riferimento **osservato**, non una promessa che il sistema possa elaborare qualunque bacino. Registrare nuovamente OS/browser/CPU/RAM e stato cache a ogni campagna: aggiornamenti software invalidano il confronto automatico.

## Fixture e carichi preregistrati per pilot futuri

Solo S-fire-smoke è materializzata/eseguita. Le altre righe definiscono il carico da generare/congelare in milestone autorizzate: nessun dataset o tempo fittizio.

| Fixture | Raster per scenario | Feature vettoriali | Eventi / risorse / regioni / scenari meteo / slot | Stato |
|---|---|---:|---|---|
| S-fire-smoke | 64×64, 20 m, 2 realizzazioni, orizzonte fisico 600 s | 0 | 1 fire / 0 / 1 sintetica / 1 / n.a. | PASS esecuzione core; RNG esatto FAIL |
| S-benchmark | 256×256, 2 prodotti comparabili | 1000 | 2 hazard / 20 / 2 / 5 / 12 | NOT RUN |
| M-benchmark | 1024×1024, 2 prodotti comparabili | 10000 | 10 / 100 / 2 / 10 / 24 | NOT RUN |
| L-stress | 2048×2048, 2 prodotti, rendering a tiles/LOD | 100000 | 50 / 500 / 4 / 30 / 48 | NOT RUN |

S-fire ha due fixture di input identiche e tre prodotti reali, ma **non una coppia di interventi matched con RNG controllato**. Servono successivamente no-action e alternativa con uguali input, condizioni, seed policy, CRS, tempi e scale. Non usare la coppia stocastica corrente come beneficio di una strategia.

Il carico decisionale S è candidato per il pilot 60 s; non si afferma che soddisfi il target. Carichi M/L cercano il punto di cedimento. Taglie sintetiche esplicite, con due profili territoriali Italia/Senegal-like in M2 e bacino reale separato quando acquisito. Manifest dovrà fissare tutti gli input, seed e versioni prima dei run. Ogni variazione di taglia diventa nuova configurazione, non sostituzione retroattiva dei fallimenti.

Job costoso: esecuzione fisica genuina, durata osservata >30 s auspicata per prova interazione/cancel; selezionare dopo sizing M1 aumentando griglia/realizzazioni o usando preprocessing REFlEx. Non simulare il carico con uno sleep e chiamarlo prova fisica. Il mini fire M0 non dimostra tale requisito; FR-25/QR-13 NOT RUN.

## Budget e raccolta

Budgets SPEC invariati: ack UI p95 ≤200 ms, mappe target ≥30 fps; read API warm p95 ≤500 ms; dashboard utile ≤3 s in tre navigazioni cold a backend avviato; viewport 375/768/1440 CSS px; sessione stabilità 30 minuti. Deadline decisionale: ogni richiesta accettata termina entro 60 s con proposta verificata o stato classificato; ≥30 ripetizioni per configurazione, p50/p95/worst, frazione utile e timeout/errori separati. Timeout non è successo decisionale.

Metodo percentile da fissare prima della campagna: nearest-rank `sorted_latency[ceil(.95*n)-1]`; riportare anche tutti i valori raw e numerosità. Nessun p95 da tre smoke run. Per qualità decisionale, numerosità e potenza/precisione definite dopo pilot separato dai casi held-out.

| Livello | Metodo/tool locale gratuito candidato | Confini e misure | Stato |
|---|---|---|---|
| Ingestion | `time.perf_counter`, resource/getrusage, byte/file/hash, HTTP timings | cold source fetch vs warm validated cache; parsing/CRS/serializzazione separati | NOT RUN |
| Simulatore | monotonic watchdog esterno, `/usr/bin/time -l` macOS / `-v` Linux, campionamento processo/albero | queue, import/JIT, runtime, peak RSS, CPU, disco, output; cancellazione/kill e cleanup | Solo `perf_counter` e self-RSS mini fire eseguiti |
| Solver/verifier | trace monotonic per correlation ID + timeout supervisor | acceptance→queue→solver→verifier→serialization; utile/timeout/infeasible/error distinti | NOT RUN |
| API | client locale Python/strumento HTTP gratuito, log server | ≥30 read warm per route, cold cache separata, payload bytes | NOT RUN |
| Browser | Chrome DevTools trace/PerformanceObserver, requestAnimationFrame; Playwright e axe da valutare/installare quando autorizzato | ≥30 azioni per tipo, ack e completion separati, fps/frame gaps; keyboard/contrast e 3 viewport | NOT RUN |
| Stress/resilienza | metriche processo/albero e browser ogni 5 s, log cancellazioni e fault | sessione 30 min; RSS, heap, GPU se misurabile, file descriptors, code, latenza e cache size | NOT RUN |

Cold: nuovo contesto browser/cache HTTP vuota, backend già avviato; cold dati e JIT riportati separatamente. Warm: identico snapshot e asset già in cache, ma controlli di freshness attivi. Fissare alimentazione, thermal/power mode, scala display, zoom 100%, viewport CSS, concorrenza e workload estraneo; tali condizioni non sono state congelate nel pilot attuale e ne limitano la comparabilità.

Proposta sizing iniziale da testare (non soglie di sicurezza o target già raggiunti): un job simulatore pesante alla volta; massimo 4 thread nel worker; separare riserva per UI e sistema, iniziale massimo memoria guest 8 GiB/4 vCPU; coda finita e backpressure prima dell'accettazione. Su macOS puro i limiti devono essere verificati, non solo dichiarati. Nessuna di queste quote è implementata.

QR-14 non ha ancora soglia quantitativa RAM approvata: prima del test congelare limite della cache e budget processo in base al sizing, registrando il trend e crescita a parità di cache. Non equiparare “grafico memoria apparentemente piatto” a limite dimostrato. Nessun target SPEC viene allentato qui.

## Esiti pubblicabili ora

Solo inventario e mini-run della versione upstream su fixture sintetica. Modello circa 2.74 s prima chiamata in processo, 0.000248 s seconda, nuovo processo circa 4.97 s totale; cache JIT già scaldata e output diversi. Dati esplorativi, nessuna conclusione su 60 s, UI, casi reali, vantaggio processo/embedded o miglioramento RQ1–RQ3. Tutti i test di prodotto QR-11…QR-14, G-04/G-05 e M7-PERF rimangono NOT RUN.


## Authorized Linux continuation — updated 15 October 2026

See `M0-continuation.md`, run `m0-linux-rng-20261015T124458Z`. Actual UTM Ubuntu22.04.5ARM64 reference:4vCPU/8192MiB/19GiB; genuine HMC and REFlEx0–4 and shared-grid technical bridge execute. Linux child-process probes n=1: HMC9²/six hours0.114257s/maxRSS20148KiB; REFlEx three reach65² step41.398232s/maxRSS199744KiB. These are not aggregate process-tree/VM peak or p95. Two HMC adaptive-dt0 configurations failed at120s; fixed1s succeeds. This is evidence for watchdog/resource isolation needs, not proof a future scheduler passes.

PROPAGATOR repetition checked on both OSs with pinned scientific dependencies and Python3.12.2vs3.12.15. Worker-context seed at1thread yields identical probability/fire/arrival bytes on tested fixture; serial Mac controls fail. n=108 across different modes/seeds/platforms is not a homogeneous30run performance configuration. Full UI/API/decision60s/performance requirements remain NOT RUN. New VM/image/freeze/config/raw traces captured; no target relaxed. Physical validity/calibration and real-case scaling remain unverified.

## M0 real-terrain sizing checkpoint — 2026-10-15
Run `m0-real-terrain-20261015T142405Z`. Real DSM433×325/69reaches; SentinelTCI full182710294bytes, DEM35799772bytes, SCL1237935bytes. Actual REFlEx step0–4 and two-line experimental compatibility procedure executed inside unchanged4vCPU/8GiB/19GiBVM; guestFS~5.36GB used, cumulativeconservative downloads1.66GiB/5GiB. No aggregatepeakmemory measurement, scalingdistribution, interactiveUI or60sdecision benchmark. HMC fixed-dt4/2/1s synthetic65² sensitivity wall5.21/10.33/19.29s (n=1each, overlapping otherjobs) is not a controlled performancecomparison. Static figure reprojection/render is not dashboard responsiveness evidence. See `reports/M0-real-terrain.md` and rawlogs for exact scope/negatives.

## User-confirmed compute topology — 2026-10-15
ADR-0002 requires all compute on the existing4vCPU/8GiB Linux VM, including fire and flood. Run `m0-unified-vm-20261015T150415Z` verifies data preparation, all three simulators, numerical checks and image rendering within that VM. The Mac is a hypervisor/control/display client. Main timing/scaling benchmarks must pin VM resource limits and distinguish client rendering from VM compute. This replay is not an end-to-end product performance benchmark or p95 claim; no resource limit increased.
