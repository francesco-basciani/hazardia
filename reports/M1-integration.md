# M1 — Ingestione e simulazioni separate in Abruzzo

**Esito tecnico: PASS, 15 ottobre 2026.** Run `m1-abruzzo-20261015T161041Z`. M1.1–M1.5 implementate ed eseguite; M2–M7 **NOT RUN**, non avviate. Reviewer: Codex self-check; controllo del contenuto separato dal codice dei simulatori, nessuna revisione scientifica esterna. Non è una certificazione fisica o operativa.

In parole semplici: ora HAZARDIA acquisisce dati reali, prepara gli input, avvia uno dei due modelli CIMA, controlla i file prodotti e registra successo oppure errore. Entrambi i percorsi girano **nella stessa VM Linux**, attraverso codice applicativo e CLI. Prima erano esperimenti di fattibilità separati. La dashboard e il motore che propone interventi appartengono alle milestone successive.

## Cosa è stato eseguito

| Attività | Esito | Evidenza |
|---|---|---|
| M1.1 acquisizione/cache/preparazione | PASS | `ingestion-result.json`, `preparation-result.json`, ricevute SHA-256, input e fonti nel run |
| M1.2 incendio PROPAGATOR | PASS | `job-7f7c35a549494a118219cd98bcf70093`: probabilità e primo tempo di arrivo, GeoTIFF64×64, EPSG32633,30m |
| M1.3 HMC→REFlEx | PASS | `job-78cd5d14b5234865b715bd8f090c0caf`: sei griglie HMC,26tratti/HAND validi, profondità GeoTIFF145×145, EPSG4326,1arcsec |
| M1.4 supervisore persistente/manifest/CLI | PASS | FIFO SQLite,4in attesa/1attivo perstore, processi isolati, timeout/cancellazione/retry esplicito, errori classificati |
| M1.5 verifiche | PASS | `unit-final.log`:33test; `integration-validation.json`:6verifiche sui prodotti reali |
| AT-EXT-02/03/05 fase M1 | PASS | Contratti/prodotti veri, provider pubblico/snapshot controllato, audit import e processi VM |
| AT-EXT-04 fase di review M1 | PASS | ADR-0005: responsabilità, input/prodotto versionati e metadati modello; nessun AI/Twin/agent runtime |
| AT-EXT-01 e fasi decision-core/M2/M3 | NOT RUN | Core decisionale, fusion e consumer futuro non implementati |
| Accuratezza storica, calibrazione locale | BLOCKED | Mancano bacino completo qualificato, parametri/combustibile validati e osservazioni di confronto |
| Forecast/ensemble, decisione60s, p95, UI, graceful degradation | NOT RUN | Future milestone; nessuna inferenza dai test di M1 |

Le righe PASS si riferiscono a questa piccola integrazione tecnica. I requisiti di prodotto completi in CHECKLIST restano aperti dove comprendono funzionalità future.

## Dati, territorio e assunzioni

Area preregistrata presso L'Aquila: bbox[13.36,42.33,13.40,42.37], fuso Europe/Rome, lavoro EPSG32633. È una AOI parziale, **non un bacino idrologico completo**. La regione Abruzzo è scelta dall'utente, non in base all'aspetto dei risultati.

- Copernicus DSM `Copernicus_DSM_COG_10_N42_00_E013_00_DEM`:42,952,996B, SHA-256 `ce66eaaa51ec82ab45533544cd49be663deb9bfd2f0a42ccd9a64a1a10a83a79`. Modello della superficie, non DTM del terreno nudo.
- Sentinel-2 `S2A_33TUG_20240713_0_L2A`, acquisito2024-07-13T10:09:10.545Z:TCI340,218,184B, SHA`78dbd5110d34933d194c7e764d9ed7ada505555eeeb2af42f8b0fc61495b7366`; SCL3,139,811B. Sul ritaglio: copertura1.0, frazione cloud/shadow/cirrus0.0 secondo SCL, non verità osservativa indipendente.
- ERA5 storico tramite Open-Meteo:24ore/7variabili, unità/timestamp verificati. Reanalisi ottenuta nel2026 per il2024, `issued_at=null`, prima disponibilità effettivamente vista registrata. **Non è una previsione emessa nel2024**.
- Incendio:600s,2realizzazioni, seed1729, un thread, spotting disattivo; innesco[32,32], combustibile uniforme legacy5 e umidità10% sintetici, vento reale ERA5 convertito m/s→km/h. Quattro celle coinvolte; nessuna ricostruzione di un incendio osservato.
- Alluvione:6ore, passo HMC1s, pioggia sintetica[10,30,30,10,0,0,0]mm; suolo/default e roughness non calibrati. Q0zero è un riferimento sintetico esplicito, non il primo campione HMC né una stima di bankfull. Etichetta upstream Q100/TR100 senza significato di ricorrenza attribuito. Profondità massima, nessuna previsione dei tempi di allagamento.

I dati CIMA di esempio con diritti non risolti non sono stati impiegati. Licenze Copernicus conservate e condizioni Open-Meteo archiviate; attribuzioni e trasformazioni in [ATTRIBUTION.md](m1-abruzzo/ATTRIBUTION.md). L'accesso gratuito Open-Meteo è per uso non commerciale; [licenze](https://open-meteo.com/en/licence) e [condizioni](https://open-meteo.com/en/terms) verificate il15/10/2026. Nessun servizio a pagamento o contatto esterno.

## Ambiente e versioni

UTM `HAZARDIA-M0-ARM64`, Ubuntu22.04.5, kernel5.15.0-198-generic/aarch64,4vCPU/8GiB RAM/disco19GiB. Stessa macchina per acquisizione, preprocessing, modelli, test e rendering. Mac: scrittura/controllo/trasporto SHA/display, nessuna nuova elaborazione scientifica nativa.

Core Python3.10.12/jsonschema3.2.0; ambiente incendi Python3.12.15/NumPy2.3.5/Numba0.62.1/llvmlite0.45.1; geoscienza Python3.10.12/NumPy1.21.5/rasterio1.2.10/GDAL3.4.1/GRASS7.8.7. Freeze completi per ambiente nei manifest/runtime-v2.json. Installazione locale editable del package0.1.0 verificata nel core-env; build tools pip24.0/setuptools69.5.1/wheel0.43.0, tre wheel circa3MB. Nessuna installazione privilegiata/globale. Installazione indipendente su nuova macchina NOT RUN (M7).

Motori originali pin: PROPAGATOR48b45078093692aa8dcca98f51849a5fbcd981a5; HMCe6e95ecbc794431c4e6d09a81b3292704f3cca42; REFlEx0dd5aa9803f7c163a4f6c3b42d9f69bce88a53bd. Fonti/binario/copia compatibilità:145file SHA verificati; originali CIMA non alterati. REFlEx usa la dichiarata copia sperimentale con due modifiche HAND-halo/bounded-merge già esaminate in M0; patch SHA`61dea2c4a8b5de6d003c5bc1a2d32e5a0d0ca7c963f9199e099036afedd1a82e`. Non è upstream immutato.

Codice: Git locale main, nessun remote configurato/push. Fire finale a86c96b3, flood finale a03adad0; verifiche a6efd8fe, rendering compatibile a7dc308f e attribuzioni incorporate a858a223. SHA completi, dirty=false e hash sorgenti nei singoli record. Contratti M0 congelati0.1.0, richieste/prodotti M1/observation0.2.0, manifest0.3.0; migrazioni esplicite in ADR-0005. Nessuna pubblicazione di software o dataset.

## Comandi riproducibili

Root VM `/home/hazardia/hazardia-runtime`; run in `runs/m1-abruzzo-20261015T161041Z`, snapshot/cache/prepared lì; job in `jobs/job-*`. I comandi esatti di acquisizione, installazione, configurazione, preparazione, esecuzione e controllo, con stdout/stderr/esito/UTC, sono in `experiments/runs/m1-abruzzo-20261015T161041Z/m1-*.json` sul Mac. Nessuna chiave privata inclusa nell'archivio.

```sh
cd /home/hazardia/hazardia-runtime/app
# Installazione già verificata, usando toolchain/deps locali del core-env:
../core-env/bin/python -m pip install --no-deps --no-build-isolation -e .
# Nuove acquisizioni/preparazioni richiedono un NUOVO run_id e plan preregistrato.
# Questi script creano file esclusivamente, non sovrascrivono i risultati vecchi:
PYTHONPATH=src ../core-env/bin/python scripts/acquire_abruzzo.py --root "$NEW_RUN"
PYTHONPATH=src /home/hazardia/m0/reflex-env/bin/python scripts/prepare_abruzzo.py --root "$NEW_RUN"
# Replay dei prepared già presenti: vedi examples/fire e examples/flood.
../core-env/bin/hazardia --runtime-root ../jobs --config ../runtime-v2.json submit --request ../runs/m1-abruzzo-20261015T161041Z/fire-request.json --snapshot-root ../runs/m1-abruzzo-20261015T161041Z
../core-env/bin/hazardia --runtime-root ../jobs --config ../runtime-v2.json work-once
../core-env/bin/python -m unittest discover -s tests/unit -v
PYTHONPATH=src /home/hazardia/m0/reflex-env/bin/python tests/integration/verify_real_run.py --run ../runs/m1-abruzzo-20261015T161041Z --jobs ../jobs --output "$NEW_VALIDATION_FILE"
```

`NEW_RUN`/`NEW_VALIDATION_FILE` sono nuovi percorsi scelti esplicitamente prima dell'esecuzione; il replay non riscrive manifest già finalizzati. L'integrazione di riferimento richiede il controllo arrival salvato chiamando il metodo upstream; comando esatto in `m1-formal-integration.json`. CLI `status/events/cancel/retry/work-once/recover` verificata. Il codice di uscita0 della CLI indica richiesta gestita, **non** che un job sia riuscito: controllare state/error_code/usable_product. Non avviare altri store per aggirare il limite di un simulatore attivo.

## Misure osservate, non benchmark statistico

| Caso riuscito | Coda s | Esecuzione s | CPU user/system s | Picco RSS campionato gruppo | Artefatti prima del manifest |
|---|---:|---:|---:|---:|---:|
| PROPAGATOR |0.013522|28.1862|26.7802 /1.2024|333,737,984B|240,505B|
| HMC→REFlEx completo |0.013424|230.4269|261.1502 /8.9664|1,412,108,288B|20,573,845B|

Il tempo incendi include processo nuovo/JIT. Il picco RSS è un limite inferiore campionato, somma dei processi del gruppo, non RSS unico: può contare pagine condivise; sleep del monitor0.1s più costo di scansione,155/1204campioni, non frequenza garantita10Hz. Artifact bytes non è il picco disco. Nessun p50/p95/30ripetizioni/60s decisionale dichiarato.

Acquisizione iniziale ripresa dopo blocco del cap per-file: non un benchmark end-to-end completamente cold. TCI cold29.8654s / warm verificato SHA0.5490s; SCL3.5541s /0.00462s; ERA5snapshot0.1423s /0.000199s; DEM già ripreso in cache, warm0.08498s (UTC primo fetch disponibile separatamente, non un falso tempo cold). Tutte sei ricevute warm verificate senza nuova rete. Budget rilevato16:46:25Z: bound conservativo2,434,488,075B (~2.27GiB)/5GiB, incluso traffico guest locale; FS usato6,203,097,088B, libero13,364,674,560B, configurazione invariata. Non serve aumentare risorse per M1.

## FAIL conservati e correzioni

| Prova | Esito originale | Causa e seguito |
|---|---|---|
| Bundle Git iniziale | FAIL | Bundle HEAD senza branchmain; esportato il branch, clone riuscito |
| Acquisizione TCI | FAIL | Cap240MiB inferiore al file324MiB; stop prima del body; cap perfile adeguato al budget totale384MiB invariato |
| Prima suite unit | FAIL,22PASS/2FAIL | Accettati gap meteo/durata incoerente; controlli semantici aggiunti, suite finale33PASS |
| Prima installazione build tools | FAIL | pip22 non supporta --report; ambiente core locale aggiornato ai tre wheel, installazione riuscita |
| `job-0134da1475e24da2a88e7fe7dddadb01` | ERROR/INVALID_OUTPUT | Lettore assumeva asse realizzazioni errato; corretto asse2; arrival ora confrontato con metodo upstream |
| `job-db8e1601e3a7464086493102450225a4` | ERROR/INTERNAL_ERROR | Journal SQLite di GRASS rimosso fra elenco e stat; monitor tollera file scratch scomparsi, test regressione PASS |
| `job-bae664bc609d4464b5b5e0e1ac506ad2` | ERROR/GRID_MISMATCH | Differenza numerica ~2.4e-17° nel passo; tolleranza1e-12°, nessun riallineamento nascosto |
| `job-368ef8ba980841fa933aa94607bfb7e9` | ERROR/OPTIMIZER_RESIDUAL | Floor upstream0.1m impone troppo volume; residuo relativo massimo99.2502. Nuovo run preregistrato con minimo1e-6m, soglia1% invariata: massimo2.13e-6 |
| Primo rendering | FAIL | Pillow9.0 senza Image.Resampling; API compatibile Image.NEAREST, rendering VM riuscito |

Totale7job scientifici:3SUCCEEDED (due fire, un flood),4ERROR conservati. I test di guasti usano processi/test fixture esplicitamente controllati e non sono simulazioni scientifiche aggiuntive. Due esecuzioni fire stesso seed hanno array identici su questa fixture; non sono campioni indipendenti. La ricerca del bound shallow è tuning post-fallimento, non validazione held-out o prova di stabilità dell'ottimizzatore.

## Artefatti e limiti del gate

[Anteprima effettiva su Sentinel-2](m1-abruzzo/abruzzo-satellite-products-attributed.png), [attribuzioni](m1-abruzzo/ATTRIBUTION.md), ADR-0005 e ledger CHECKLIST/EVIDENCE. Archivio locale `experiments/runs/m1-abruzzo-20261015T161041Z/evidence/`; manifest completo include hash di cache originali, prepared, tutti i job anche falliti, runtime/env e test. Le tre grandi TIFF originali restano nella VM: il trasporto locale conserva ricevute/hashes/locator e ritagli, senza duplicare385MB inutilmente. L'archivio completo dei job consente ispezione dei fallimenti; niente chiavi o directory private M0 incluse. SHA e trasporto verificati prima della chiusura del gate.

M1 dimostra orchestrazione reale e controllo degli artefatti; non sostiene H1–H3 del paper. Unica AOI piccola, parametri sintetici, same-author review, due-line patch e configurazione adattata dopo errori, seed/parallelismo limitati, assenza ground truth e reanalisi retrospettiva sono minacce alla validità. Solver robusto/rolling horizon/allerte/graceful degradation/dashboard e casi storici validati restano nelle rispettive milestone.

**Prossimo incremento eseguibile: M2.1–M2.6**, profili territoriali e contratti condivisi, eventi/fusione, ensemble, distinzione effetto fisico/impatto, esposizione/accessibilità e test di replay. Prerequisito tecnico M1 soddisfatto; M2 non avviata e richiede nuova autorizzazione. La prima dashboard interattiva rimane M3. Nessuna azione operativa reale.


## Verifica finale dell'archivio

PASS:1.163artefatti inventariati nella VM;1.160trasportati e verificati uno per uno sul Mac. Tre originali TIFF385MB restano nella cache guest con hash/URL/ricevute; nessuna omissione nascosta. Archivio16.198.427B, SHA-256`b3ddab064315311c970c74219433a4327e31789ac2e7aa30184816f2401263af`; manifest guest SHA`05ad03f4ee45460987cc2cf1a0a45604623eee9ce9c0e1c7f50d5796fd440ae8`. Manifest host supplementare congela23record di comandi/controllo, compreso il comando di freeze; nessun hash auto-referenziale. [Verifica trasporto](m1-abruzzo/transfer-verification.json), [verifica prodotti reali](m1-abruzzo/integration-validation.json), [budget finale](m1-abruzzo/budget-closure.json). Ultimo bound conservativo2.435.051.901B/5GiB alle16:53:12Z; FS usato6.204.862.464B. Nessun processo scientifico in esecuzione; VM disponibile per ispezione.

Seed1730 incluso tra le opzioni della preregistrazione, ma non eseguito nel nuovo pilot M1: NOT RUN; non contato come replica. Il lavoro non estende la prova di ripetibilità oltre le esecuzioni documentate.
