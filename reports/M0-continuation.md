# M0 — Proseguimento Linux UTM, catena flood e ripetibilità

**Checkpoint storico: lo stato più recente e la prova su satellite reale sono in [M0-real-terrain.md](M0-real-terrain.md).**
15 ottobre 2026. **Esito corrente del gate M0: BLOCKED per qualificazione fisica e chiusura dei contratti; M1 NOT RUN / non autorizzata.** La fattibilità tecnica dei tre motori e del passaggio dati HMC→REFlEx è ora dimostrata su fixture sintetiche. Non è una validazione del framework, dei modelli su eventi reali o dell'efficacia degli interventi.

Questo checkpoint aggiorna il [primo assessment](M0-feasibility.md), senza cancellarne fallimenti o limitazioni. Responsabile: Codex / Research Recorder; verifiche con lettori separati nel guest e sul Mac, revisore umano esterno pendente. Run: `experiments/runs/m0-linux-rng-20261015T124458Z/` (RUN). Predecessore immutato: `m0-audit-20261015T122006Z`. Git ancora assente: SHA/dirty null, hash dei documenti e sorgenti espliciti. Manifest/checksum finali in RUN.

## Risultati e loro significato

| ID | Esito | Prova effettiva |
|---|---|---|
| M0-VM-01 | PASS | Linux ARM64 in UTM, 4 vCPU, 8192 MiB RAM, disco 19 GiB; boot, SSH localhost, compilazione/esecuzioni, arresto verificato |
| M0-BUDGET-02 | PASS | Download stimato conservativamente <1.5 GiB inclusa riserva metadata, limite 5 GiB; disco guest circa 5.24 GB usati, capacità virtuale 19 GiB; nessun costo/servizio commerciale |
| M0-RNG-02 | PASS limitato | Seed nei worker paralleli Numba: 9 output identici per seed/OS, 3 processi, due seed; probabilità/fire/arrival uguali anche Mac↔Linux |
| M0-RNG-01 / controllo seriale Mac | FAIL conservato | Seed seriale, con/senza priming, produce 9 output diversi su 9 per seed; sul Linux provato il metodo seriale invece si ripete |
| M0-HMC-BUILD | PASS | Compilazione upstream senza modifiche, ELF aarch64, GFortran 11.4 / NetCDF |
| M0-HMC-RUN | PASS standalone sintetico | Sei passi orari, sei mappe NetCDF, idrogrammi positivi; controllo asciutto ha idrogrammi ASCII 0 e residui raster <4×10⁻⁷ m³/s |
| M0-REFLEX-04 | PASS standalone | Step4 su HAND analitico; poi intera pipeline reale step0–4 su DEM sintetico con tre tratti |
| M0-COUPLE-IO | PASS tecnico | Griglia/reticolo derivati condivisi, tre sezioni HMC associate ai reach 2/4/6; scarto coordinate 0; portate reali HMC → CSV → REFlEx → GeoTIFF |
| M0-COUPLE-PHYS | BLOCKED | Volume triangolare, Q0, tconc, nominale area celle, stabilità e calibrazione non ancora qualificati idrologicamente |
| M0-PERF-PILOT | PASS misurazione esplorativa | Tempi/RSS su esecuzioni piccole, timeout reali conservati; nessun p95 o target 60 s verificato |
| M0-DATA-RIGHTS | BLOCKED per dati reali | Catalogo ufficiale hmc-datasets trovato, file Git LFS, licenza non dichiarata; dati reali non acquisiti/usati |
| G-01 | NOT RUN | Inventario contratti presente nell'ADR; freeze completo ed esempi validi/invalidi eseguibili non prodotti come implementazione del framework |
| FR/QR del prodotto, M1–M7 | NOT RUN | Nessun adapter/framework, solver, UI, sistema di allerta o dispatch implementato |

## VM, limiti e stato finale

L'utente ha autorizzato esplicitamente questa VM entro 5 GiB di download, 20 GiB disco, 8 GiB RAM, 4 vCPU. Creata **HAZARDIA-M0-ARM64**, UUID `6706102A-6B83-4DE2-8475-D8D8E067BE41`, UTM 4.6.4 / QEMU 9.1, hypervisor ARM, Ubuntu 22.04.5 LTS / kernel 5.15.0-198-generic. Ubuntu Jammy offre [GRASS 7.8.7](https://packages.ubuntu.com/jammy/grass), compatibile con la major prevista dal repository REFlEx.

Immagine [Ubuntu ufficiale del 04/10/2026](https://cloud-images.ubuntu.com/jammy/20261004/), `jammy-server-cloudimg-arm64.img`: 700778496 byte; SHA-256 `86e13258765945ad792dac75fac7f02f4db9fa73a4a535ffa472266e7041fa19`, uguale a SHA256SUMS ottenuto via HTTPS dalla stessa origine. Firma GPG non verificata indipendentemente. Cloud-init NoCloud con chiave SSH locale dedicata; nessuna password o chiave privata nel report/evidence bundle. Runtime e chiave sotto `.m0-runtime/`, esclusi da Git.

Creazione tramite API [UTM](https://docs.getutm.app/scripting/scripting/) e configurazione tramite interfaccia UTM per il resize: `guest size` è ignorato quando si importa l'immagine. Disco iniziale circa 2.2 GiB, poi espanso a **19 GiB**, `20401094656` byte, con growpart/resize2fs nel guest. RAM configurata 8192 MiB; `nproc=4`; MemTotal guest 8314118144 byte (memoria riservata al kernel esclusa). No VM x86 emulata necessaria per le prove riuscite.

Rete emulata NAT; unico forwarding `127.0.0.1:22227 → guest:22`; nessuna cartella host condivisa, servizio pubblico o deployment. Gli update automatici apt e il refresh snap del guest sono stati fermati per limitare traffico e variazioni dell'ambiente sperimentale; questa è una VM di ricerca isolata, non una configurazione operativa. Nessuna modifica privilegiata/globale del Mac.

Contabilità: immagine host 700778496 byte + tar HMC 6085568 byte + contatori RX guest finali 747515493 byte (includono traffico locale, quindi conservativi per download Internet), più riserva di **100 MiB** per metadata host, prove fallite e traffico iniziale prima del reboot. Totale conservativo circa **1.453 GiB**, sotto 5 GiB. La riserva è un margine contabile esplicito, non una misura sperimentale del traffico. Capacità guest 19 GiB, filesystem circa 5.24 GB usati; picchi RAM aggregati dell'intera VM non profilati. Guest spento con shutdown: SSH restituisce 255 per chiusura della connessione, ma `utmctl status` verifica `stopped` e lsof non trova listener sulla porta. VM conservata per replay, non eliminata/sospesa su disco.

Evidenze: `image-download.json`, `image-verification.json`, `create-vm*-result.json`, `configure-network-result.json`, `guest-inventory.json`, `guest-sources-and-budget.json`, `archive-final.json`, `guest-shutdown.json`, `vm-final-state.json`. Tentativo iniziale di accedere direttamente alla cartella container UTM negato da macOS; nessun permesso aggirato. Resize effettuato tramite l'app.

## Versioni e sorgenti

Commit CIMA invariati rispetto al primo assessment:

- PROPAGATOR `48b45078093692aa8dcca98f51849a5fbcd981a5`.
- HMC `e6e95ecbc794431c4e6d09a81b3292704f3cca42` (builder 3.4.3; il template namelist dichiara 3.4.0, stampato nel banner: il banner non sostituisce il commit).
- REFlEx `0dd5aa9803f7c163a4f6c3b42d9f69bce88a53bd`, step0/1/3/4 dichiarano 2.1.0, step2 2.0.4.

Tutti EUPL-1.2; non modificati. HMC completo scaricato senza storia Git, 72 file verificati contro blob ufficiali; 125 file originali complessivi nel guest verificati SHA-256 contro gli snapshot host, nessuna differenza. L'errore di etichetta `commit` nel primo `hmc-full-source-integrity.json` è corretto da un nuovo record `*-correction.json`, senza riscrivere l'originale: il pinned_repository_commit era già corretto.

GRASS add-ons [OSGeo/grass-addons](https://github.com/OSGeo/grass-addons), branch grass7, commit `b77e72b0da59510826c5063e701ed9fbba60380b`; archivio SHA-256 `9086730da7d6bb05ae2236dcaf8fcf146ef0335e8d06e855329e15268f40c8d8`. Compilati da sorgente locale pinned r.stream.basins, r.stream.order, r.stream.distance, r.accumulate. GRASS/GPL e tutte le dipendenze mantengono licenze proprie; non viene approvata alcuna redistribuzione.

Ambiente flood: Python 3.10, GDAL 3.4.1, GRASS 7.8.7, NumPy 1.21.5, SciPy 1.8.0, pandas 1.3.5, geopandas 0.10.2, rasterio 1.2.10, xarray 0.16.1, Numba 0.55.1, rioxarray 0.9.1, pysheds 0.3.3, richdem 0.3.4 compilato ARM64, grass-session 0.5 e dipendenze datashader/xrspatial. È una ricostruzione documentata, **non** la riproduzione invariata del vecchio lock Linux x86/Python3.7. Freeze e pacchetti apt completi archiviati.

Ambiente fire Linux separato: CPython 3.12.15 da [python-build-standalone](https://github.com/astral-sh/python-build-standalone), release 20261013, tar 29242161 byte, digest API verificato `9467a99bacc7d90b64b02de7fa9ecfc99b72905e64e74f7ff6b460ad95cfed5a`. Stessi Numba 0.62.1, NumPy 2.3.5, llvmlite 0.45.1, SciPy 1.18.1 del Mac (Python 3.12.2). Nessun Python di sistema sostituito. Il backend TBB del guest è risultato troppo vecchio per Numba 0.62: warning conservato, nessuna pretesa di aver usato TBB.

## PROPAGATOR: ipotesi RNG e risultati

Prerecord `rng-plan.json`; fixture 64×64, 20 m, fuel5, DEM piatto, 2 realizzazioni, 600 s fisici, vento 10 km/h / 90°, moisture0.1, spotting off. Due seed 1729/1730, tre ripetizioni per seed e modalità, tre processi per OS: **108 esecuzioni misurate complessive** (54 Mac, 54 Linux), oltre al priming. Non sono 108 trial indipendenti di qualità fisica o un benchmark 60 s.

Confrontati: seed seriale; priming del modello e seed seriale; priming e seed nel contesto parallelo con `njit(parallel=True)` / `prange`. Il helper inizializza lo stato e consuma un valore uniforme per worker; questa parte fa parte del protocollo, quindi la sequenza non è promessa identica a un ipotetico seed API upstream. NUMBA/OMP/BLAS thread=1.

| Metodo | Mac: output distinti per seed, n=9 | Linux: output distinti per seed, n=9 |
|---|---:|---:|
| Seed seriale | 9 — FAIL ripetizione esatta | 1 — PASS nel contesto provato |
| Priming + seed seriale | 9 — FAIL | 1 — PASS |
| Priming + seed worker | 1 — PASS | 1 — PASS |

I due seed producono output differenti fra loro. Nel terzo metodo i byte degli array **probabilità, fire e arrival** coincidono anche fra Mac e Linux per entrambi i seed. Validazione sul Mac di ogni file `.npz`, bounds, forma, propagazione e checksum in `rng-artifact-validation.json`; nessun codice upstream modificato.

Il risultato è coerente con lo stato RNG per thread documentato da [Numba](https://numba.readthedocs.io/en/stable/reference/numpysupported.html), ma non attribuisce causalità universale a un solo dettaglio del backend. Non generalizzare a più thread, spotting, griglie differenti, altri pacchetti/CPU o tolleranze di skill. Configurazione candidata per replay iniziale: worker dedicato a un thread e helper esplicito versionato; multi-thread e ripetibilità statistica ancora NOT RUN. Il FAIL originario resta valido per il metodo precedente, non cancellato dal nuovo PASS.

## HMC: esecuzioni reali, controllo e fallimenti

Compilazione nel guest, senza sorgenti patchate:

```sh
NETCDF_DIR=/usr bash hmc-src/configure.sh hmc-src /usr "$HOME/m0/hmc-bin" true
```

Binario ELF aarch64 SHA-256 `d8a59e52d9f19deebbdebabd5d1cd4cca75d0452ae900b36d878896a056c71e5` archiviato con licenza. Test iniziale: bacino sintetico 9×9, 49 celle attive, DEM/flow keypad/soil statici dichiarati, 6 passi da un'ora, pioggia 10/30/30/10/0/0 mm, risorse/interventi assenti. Configurazione e generatori completi nel run e in `guest-final/artifact-final/` (GUEST).

Tentativi conservati:

1. Attributo NetCDF scritto `NODATA_value` anziché `nodata_value`: STOP, **exit 0**, nessun risultato completo — FAIL.
2. Attributo corretto, output point NetCDF: errore “Attempting netcdf-4 operation on netcdf-3 file”, STOP **exit 0**, prodotto parziale — FAIL.
3. Output point ASCII supportato e output grid NetCDF: sei passi, `SIMULATION END`, sei raster di portata finiti/nonnegativi m³/s — PASS standalone.

Picco gridded 180.75862 m³/s; massimo idrogramma sezioni ASCII 151.50 m³/s. Le rappresentazioni non sono automaticamente equivalenti (campo gridded vs sezioni/aggregazione); la prova di ponte successiva usa esplicitamente il campo gridded. Controllo con stessa configurazione e pioggia zero: ASCII 0.00, massimi raster nell'ordine 10⁻⁷–10⁻⁸ m³/s. Nessuna skill idrologica o calibrazione dedotta da questo controllo.

Warnings su mappe opzionali/default, pressioni costanti, aggiornamenti neve assenti con modulo spento ed ET al limite temporale sono archiviati. L'input è sintetico e intenzionalmente minimo: non rappresenta un bacino pronto per previsioni. Stato funzionalità FR-07 HAZARDIA rimane NOT RUN.

## REFlEx: da HAND preparato alla pipeline effettiva

Prima prova 33×33, 10 m, EPSG:32632, HAND analitico in centimetri, un reach con Q100=12, Q0=1 m³/s, tconc=3600 s. Il ramo seriale restituisce quattro valori a tre colonne pandas e fallisce (`ValueError: Must have equal len keys and value`). Con configurazione multiprocesso upstream, due processi, termina: 165 celle positive, profondità massima 0.42370656 m, volume raster circa 3031.15845 m³ contro V_cut 3031.15847, residuo circa 6.8×10⁻⁵ m³. Questo primo PASS riguarda solo step4 su input preparati.

Poi vera pipeline step0–4: DEM sintetico 65×65, EPSG:4326, passo0.0001°, due valli a Y e tre reach 2/4/6; GRASS, richdem, pysheds, Pfafstetter, maschere, tconc e HAND realmente eseguiti. D8, soglia reticolo100 celle, no coastal expansion, due processi, un thread ciascuno. Profilo di volume piccolo esplicito: filtro0.1 m³, bound profondità0.0001 m; non sono soglie operative.

Corner case conservati: valle a singolo ramo fallisce r.stream.order con soglie100 e1000; sorgente add-on gestisce max_trib solo2…5 nella tabella vettoriale, non0. L'ipotesi iniziale “troppi tributari” è stata smentita dall'ispezione (un solo ID): nessuna diagnosi precedente viene presentata come confermata. Fixture a Y supera il caso. Manual activation ereditata dal template Magra richiedeva manual_ce anche con coastal disabled: nuovo file di configurazione la disattiva, senza patch del motore.

Output completo con Q sintetica0.03 m³/s: tre HAND e raster65×65, 80 celle positive, massimo0.01766856 m. Residui ottimizzatore sotto1% del V_cut (e sotto0.01 m³ per V_cut≤1) nel controllo a posteriori; questa tolleranza non è preregistrata come criterio di calibrazione scientifica. GDAL riporta warning di color table/precisione, GeoPandas su buffer geografico, pysheds su nodata: log conservati. La verifica dei pixel validi passa, non prova assenza di ogni errore numerico.

Il primo lettore HAND escludeva nodata con `a != nodata`: con nodata=NaN il test fallisce. Record originale FAIL conservato; nuovo controllo usa la mask GDAL/rasterio, verifica rispettivamente3969/840/930 pixel validi finiti e nonnegativi. Correzione del verificatore esplicita in `hand-verification-v2.json`, riconfermata sul Mac in `host-raster-validation.json`.

## Catena HMC→REFlEx e limite della fisica

La prova finale usa effettivamente DEM condizionato, D8 e reticolo prodotti da REFlEx come statiche per HMC sullo stesso geogrid65×65. Conversione D8 GRASS NE/N/NW/W/SW/S/SE/E → HMC9/8/7/4/1/2/3/6. Una sezione per reach al pixel attivo di massima accumulazione. Campi HMC NetCDF riassociati tramite Longitude/Latitude, scarto massimo osservato0°. Timestamps sintetici coerenti, sei snapshot; m³/s espliciti.

Due tentativi con passo adattivo terminati dal watchdog a120 s (exit124), senza prodotti completi. Coarsening del forcing uniforme65×65→3×3 non risolve. Diagnosi gdb e stdout unbuffered mostrano SubFlow e `IntegrationStep 0 [s]`: l'ipotesi iniziale sul costo regridding non è sostenuta. Configurazione supportata `iFlagVarDtPhysConv=0`, `iDtPhysConv=1` completa i sei passi; sorgenti inalterate. Non è uno studio di convergenza/stabilità o una correzione upstream del caso adattivo: la fixture che si blocca è conservata.

Per ogni reach: Q0=primo campione, Q100=massimo gridded HMC; tconc realmente derivato da REFlEx. **“100” è soltanto l'etichetta sintetica richiesta dall'interfaccia upstream, non un tempo di ritorno stimato.** CSV, hash input, match e assunzioni in GUEST `reflex-chain-v3/coupling-manifest.json`. Output in directory separata `flood-hmc`: 80 celle positive, profondità massima0.03981196 m, tutti i pixel validi finiti/nonnegativi. Residuo massimo dei tre ottimizzatori circa1.25×10⁻⁵ m³. Questi numeri non misurano accuratezza rispetto a un evento reale.

| Reach | Picco HMC m³/s | Volume triangolare pre-rounding m³ | Integrale trapezoidale dei 6 snapshot m³ |
|---|---:|---:|---:|
| 2 | 0.346893 | 858.2811 | 3886.2153 |
| 4 | 0.111204 | 163.8479 | 1269.0024 |
| 6 | 0.116327 | 173.3451 | 1327.1681 |

Sono quantità diverse: i campioni orari non descrivono tutto il tail; REFlEx riduce ancora il volume con il tempo di transito. Non si promette conservazione del volume dell'idrogramma, né si sommano reach annidati come bacini indipendenti. Il bridge è tecnicamente eseguibile, ma Q0/forma temporale, scelta tconc, bilancio, rugosità, griglia geografica con area nominale100 m², datum e calibrazione richiedono verifica idrologica. Nessuna previsione di arrivo temporale o effetto di soccorso sulla portata inventato. **M0-COUPLE-IO PASS; M0-COUPLE-PHYS BLOCKED.**

## Performance osservata e minacce alla validità

Un probe aggiuntivo con `resource.getrusage(RUSAGE_CHILDREN)` in wrapper separati misura:

| Probe n=1 | Wall clock | Max RSS riportato Linux |
|---|---:|---:|
| HMC9×9, sei passi | 0.1143 s | 20148 KiB |
| REFlEx step4, tre reach65×65 | 1.3982 s | 199744 KiB |

RSS è la misura del figlio riportata dal sistema, **non** il picco aggregato contemporaneo dell'albero processi o dell'host. HMC65×65 con dt fisso completa in pochi secondi dai timestamp grezzi; due configurazioni adattive falliscono a120 s. Nessun confronto di speedup, p95, carico reale o rispetto della deadline decisionale60 s. UI/API non esistono; benchmark prodotto e scaling restano NOT RUN.

Le fixture sono state raffinate durante il pilot: non sono casi held-out e non dimostrano validità fisica. I dati negativi rimangono nel bundle. Nessuna evidenza a sostegno di H1–H3; i risultati informano invece prerequisiti di portabilità, replay e isolamento: i codici uscita possono mentire, dt adattivo può non avanzare, i worker richiedono watchdog esterno e prodotti validati.

## Dati reali e diritti

Trovato repository ufficiale [c-hydro/hmc-datasets](https://github.com/c-hydro/hmc-datasets), commit `8fa82282089df8cbbf827067e22970a7ee5ca440`, domini Italy_Vda / Africa_AF2400 / Bolivia_Chapare, oggetti Git LFS. La licenza non è dichiarata nei metadata/file consultati. Sono stati letti solo catalogo, README e puntatore LFS (non i payload reali); nessun diritto dedotto automaticamente dalla licenza del modello. [hmc-training-local](https://github.com/c-hydro/hmc-training-local) spiega che i dati sono consegnati separatamente da CIMA ed esclusi dal versionamento.

Questa è una disponibilità candidata, non un dataset autorizzato/calibrato. Scelta caso storico italiano, dati satellite/meteo contemporanei, rilascio/licenze e ground truth restano da risolvere. Nessun contatto a CIMA o altri inviato, nessuna registrazione o spesa. La matrice fonti del primo report resta applicabile.

## Riproduzione e artefatti

L'archivio `guest-final.tar.gz`, SHA-256 `86c36d6133ac6fd525bc8f95fb4c88c4b6db4d701a0b2ea95cf4279697da9d25`, è estratto in RUN `guest-final/artifact-final/`: 501 file verificati uno a uno con hash guest, oltre ai record/script host. Contiene log negativi, input/config, output NetCDF/GeoTIFF, binario HMC, freeze, coupling manifest e stack. I source files sono pinned e controllati separatamente. Non è un bundle pubblicabile/offline completo di dipendenze, né prova G-03 del futuro framework.

Replay locale della verifica già eseguibile (VM spenta):

```sh
RUN=experiments/runs/m0-linux-rng-20261015T124458Z
.m0-venv/bin/python "$RUN/verify-rng-files.py" "$RUN"
```

Per ripetere i modelli, avviare soltanto la VM HAZARDIA-M0-ARM64 già configurata e usare i comandi esatti archiviati nei JSON del run; `m0ctl.py` registra script, UTC, exit, output, elapsed e contatori RX. Ogni replay deve scrivere in nuova directory/run_id, non sovrascrivere le evidenze. I comandi di creazione/installazione non vanno rieseguiti alla cieca su una VM esistente. La chiave locale rimane in `.m0-runtime/ssh-key`; non esportarla. Nessun framework da lanciare.

## Decisione al gate e prossimo incremento

Non servono altri download grandi o modifiche hardware per dimostrare l'esecuzione tecnica: i tre motori sono partiti realmente su questo Mac/VM ARM. Non si dichiara M0 conclusa PASS né si avvia M1: restano qualificazione del bridge fisico, diritti/input reali e contratti completi.

Il prossimo incremento M0 è concreto: fissare il significato idrologico dell'interfaccia peak/base/tconc e un dominio con diritti espliciti; preregistrare verifica di bilancio, stabilità del passo e skill; completare il freeze dei contratti al confine M0/M1 senza sostituire i modelli. L'opzione conservativa è mantenere il bridge attuale come **ricerca su scenari geomorfologici**, escludendo per ora equivalenza con idrogrammi completi, tempi di arrivo e calibrazione operativa. Se si richiede conservazione dell'idrogramma/propagazione temporale, occorre una decisione esplicita su eventuale estensione del modello: non è stata implementata.

Autorizzazione ancora limitata a M0 e al budget VM già approvato. Nessuna nuova autorizzazione viene presunta per M1, push, pubblicazione, contatti o deployment. Per la chiusura scientifica serve revisione idrologica umana; nessuna “certificazione” ricavata da queste prove.
