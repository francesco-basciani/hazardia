# HAZARDIA — M0 Feasibility Assessment (initial checkpoint)

**Checkpoint storico: lo stato più recente e la prova su satellite reale sono in [M0-real-terrain.md](M0-real-terrain.md).**
**Current-state update:** see [M0-continuation.md](M0-continuation.md). The following is the preserved initial assessment; later real Linux/coupling/RNG results supersede its availability assumptions without erasing its failed runs.

Data: 15 ottobre 2026. **Gate M0: BLOCKED, non completato. M1 non autorizzata.**

Responsabile: Codex, anche Research Recorder. Controllo degli artefatti con script separato; revisione umana/indipendente esterna ancora pendente. Autorizzazione: messaggio dell'utente del 15 ottobre, limitato a M0. Nessun componente del framework implementato, servizio avviato, push, deployment o costo sostenuto.

## Esito e confini dell'evidenza

Il Mac esegue realmente il core upstream PROPAGATOR in Python ARM64 e salva raster GeoTIFF leggibili. Non è ancora verificata l'integrazione HAZARDIA. HMC e REFlEx non hanno prodotto simulazioni locali: mancano toolchain, runtime Linux verificato e un dominio completo di prova. HMC→REFlEx è una trasformazione plausibile da verificare, non un accoppiamento plug-and-play né una catena dimostrata. Non è stata dimostrata impossibilità: non si sostituiscono i modelli.

Il pilot ha anche un risultato negativo: tre output con seed dichiarato identico differiscono. Non si può ancora promettere replay bitwise o attribuire differenze tra interventi senza controllare la variabilità stocastica. I test dei 60 s e della dashboard sono NOT RUN.

Evidenza locale: `experiments/runs/m0-audit-20261015T122006Z/` (di seguito RUN). `manifest.json` e `checksums.sha256` indicizzano file e hash; `baseline.json` conserva identità e hash degli otto documenti prima delle modifiche. Git SHA e dirty state sono **null / non applicabili**: la directory non è un repository. Nessun commit fittizio. Le copie upstream sono parziali, identificate con commit e verificate contro i blob GitHub; non sono cloni completi o distribuzioni HAZARDIA.

## Registro sintetico M0

| ID / attività | Esito | Osservazione / prova |
|---|---|---|
| M0.1 documenti, dipendenze M0–M7, directory e host | PASS | Otto documenti letti integralmente; `baseline.json`, `host-and-git.json`; Git assente, struttura solo pianificatoria |
| M0.2 repository, licenze, dipendenze CIMA | PASS | `sources/*/repository.json`, licenze e tree; 110 file upstream verificati senza differenze |
| M0.3 esecuzione reale fire nativa minima | PASS | Tre run a 600 s simulati, array e GeoTIFF; verifica separata in `reports/m0-evidence-verification.json` |
| M0-FIRE-120 ipotesi propagazione entro 120 s | FAIL | Solo cella di innesco; `diagnostic-execution.json`; non cancellato dopo pilot successivo |
| M0-RNG-01 ripetibilità esatta del metodo seed provato | FAIL | Tre hash diversi con seed 1729 / un thread; non prova che un altro controllo RNG sia impossibile |
| M0.4 HMC standalone | BLOCKED | `hmc-preflight.json`: gfortran e runner Linux assenti dal PATH; dominio/forcing mancanti |
| M0.4 REFlEx standalone | BLOCKED | `reflex-dependency-probe.json`: `ModuleNotFoundError: geopandas`; mancano anche GRASS/GDAL esterni e input |
| M0.5 accoppiamento reale HMC→REFlEx | BLOCKED | Semantica analizzata nel codice; nessun idrogramma HMC o raster REFlEx prodotto |
| M0.6 catalogo dati e politica cache | PASS | Inventario sotto; è verifica documentale, non ingestione/test di tutti i servizi |
| M0.6 credenziali, download e validazione dataset storici | NOT RUN | Nessuna registrazione, credenziale o scena satellitare scaricata; nessun ground truth selezionato |
| M0.7 Python diretto e nuovo processo macOS | PASS | Entrambi eseguono il core; tempi esplorativi sotto; non isolamento OS e non equivalenza stocastica |
| M0.7 Linux ARM/x86 e confronto Mac/Linux | BLOCKED | UTM presente, nessun guest utilizzabile verificato; bootstrap/download da autorizzare |
| M0.8 valutazione stack e ADR | PASS | `reports/ADR-0001-M0-candidate-stack.md`; scelte provvisorie, non implementazione o sostituzione |
| G-01 contratti completi eseguibili, esempi validi/invalidi | NOT RUN | Inventario semantico in ADR; freeze e test di tutti i confini ancora necessari al gate M0/M1 |
| M0.9 recorder, report e go/no-go | PASS | Questo report, ledger e manifest; decisione no-go verso M1 finché prerequisiti aperti |
| M0.10 / M0-PERF baseline e piano benchmark | PASS | `reports/M0-performance-baseline.md`; misure UI, API, 60 s e stress NOT RUN |

PASS nelle righe di analisi non equivale a PASS di FR-01…FR-28 o QR-01…QR-14. Questi restano NOT RUN nel registro ufficiale. M0 resta BLOCKED finché esecuzioni flood, accoppiamento e prerequisiti del gate non sono risolti.

## Ambiente e compatibilità

Inventario misurato in `host-and-git.json`: MacBook Pro Mac16,8, Apple M4 Pro, ARM64, 14 core CPU (10 performance + 4 efficiency), 48 GiB RAM, GPU integrata 20 core / Metal 4; macOS 27.0.1 build 26A434. Display 3024×1964. Hypervisor disponibile (`kern.hv_support: 1`). Questi dati non dimostrano WebGL o accelerazione di un modello: test browser GPU e GPU compute NOT RUN.

Spazio iniziale circa 56 GiB, volume dati al 94%. Python 3.12.2, pip 24.0, Git 2.42.0, Node 16.20.2; clang Xcode disponibile. Chrome 155.0.8059.79, UTM 4.6.4 installati. `docker`, `podman`, `colima`, `limactl`, `gfortran`, `grass`, `gdalinfo`, `conda` non trovati nel PATH. Non si assume che ciò provi l'assenza di ogni installazione fuori PATH o di ogni VM salvata. Nessuna VM è stata avviata/ispezionata.

**Valutazione:** hardware adatto a pilot locali CPU; dimensionamento di bacini e ensemble non ancora noto. Python nativo confermato per il core fire. HMC documenta Linux 64 bit; Fortran/GFortran ≥8, NetCDF4/HDF5/zlib. ARM64 nativo non certificato da questa prova. REFlEx richiede GRASS 7 con r.stream.basin/r.stream.order/r.accumulate e librerie GDAL/PROJ coerenti con i binding Python. Il lock upstream contiene Python 3.7.7, GDAL 2.3.3, NumPy 1.21.6, Numba 0.56.0, pacchetti Linux/MKL; lo script scarica Miniconda Linux x86-64. Questo ambiente non è installabile invariato su macOS ARM.

Possibili runner senza canone: UTM già presente (Linux ARM virtualizzato o x86 emulato), oppure Lima/Podman da installare. VM ARM evita emulazione ma richiede ricostruzione/verifica delle dipendenze REFlEx; x86 preserva meglio la piattaforma storica a costo di emulazione e pacchetti obsoleti. Nessuna opzione è ancora provata. Non eseguire lo script legacy automaticamente: richiede revisione di percorsi, download e ambiente, e usa defaults Anaconda; valutare conda-forge/Miniforge con termini e licenze per pacchetto, senza assumere che qualsiasi canale sia gratuito per ogni contesto.

## Motori: fonti, versioni, diritti

| Motore e fonte ufficiale | Commit osservato | Dipendenze e I/O essenziali | Esito locale |
|---|---|---|---|
| [PROPAGATOR](https://github.com/CIMAFoundation/propagator_sim) | `48b45078093692aa8dcca98f51849a5fbcd981a5` | Python ≥3.11; core Numba 0.62.1, SciPy ≥1.16.1; extra CLI/I/O rasterio, Fiona, pyproj, geopandas, Shapely ecc.; griglie DEM/fuel, boundary meteo, probability/arrival/intensity | Core reale PASS; CLI upstream completa NOT RUN |
| [HMC/Continuum](https://github.com/c-hydro/hmc-dev) | `e6e95ecbc794431c4e6d09a81b3292704f3cca42` | README dichiara 3.4.3, 28/09/2026; Fortran, NetCDF, namelist, statiche idrologiche e forcing; discharge su griglia/sezioni | BLOCKED |
| [REFlEx](https://github.com/c-hydro/reflex) | `0dd5aa9803f7c163a4f6c3b42d9f69bce88a53bd` | Pipeline step0…4, configurazioni 2.0.1/2.1.0; DEM condizionato, flowlines, HAND, CSV portate; GeoTIFF profondità/estensione | BLOCKED |

Tutti e tre hanno file licenza **EUPL-1.2** archiviato in RUN. Il codice aperto consente lo studio/esecuzione locale nelle condizioni della licenza. Redistribuzione, modifiche e comunicazione di opere derivate richiedono mantenimento degli avvisi e rispetto degli obblighi EUPL; il processo separato non risolve automaticamente la compatibilità di licenza di un'opera combinata. Nessuna scelta di licenza del nuovo framework è stata imposta. Licenze di dipendenze/dataset restano distinte e vanno preservate nel bundle di replica; niente pubblicazione autorizzata. Esempi raster upstream: provenienza/licenza specifica dei dati non chiarita separatamente, quindi non usati per conclusioni empiriche né redistribuiti come dataset HAZARDIA.

Le dimensioni API repository indicano circa 7.8 MiB PROPAGATOR, 314 MiB HMC (storia), 151 KiB REFlEx; scaricati solo file selezionati, non la storia HMC. Tree HMC ispezionato contiene configurazioni `.info.txt`, ma non un dataset completo statiche/forcing. REFlEx include launcher Magra con percorsi locali degli autori, non quei dati.

## Esperimento reale PROPAGATOR

Prerecord: `baseline.json`, `fire-prerun.json`, `fire-config.json`, poi `fire-config-600s.json` prima del nuovo pilot. Nessuna modifica al motore upstream. Installazione confinata a `.m0-venv` (circa 347 MiB finali osservati), wheel ARM64 senza privilegi, circa 85 MiB di wheel principali incluso rasterio; nessun aggiornamento del Python/Node di sistema. Lock osservato: `reports/m0-environment-freeze.txt`; URL/hash delle wheel core in `reports/m0-pip-plan.json`. Snapshot delle sorgenti verificato con Git blob SHA-1, artefatti indicizzati SHA-256.

Fixture sintetica, nessun evento reale: DEM piatto 64×64 float32, fuel legacy 5, cella 20 m, innesco (32,32), vento 10 km/h e direzione 90°, moisture 0.1 nelle convenzioni upstream, 2 realizzazioni, spotting disattivo, seed tentato NumPy/Numba 1729, NUMBA/OMP/BLAS thread=1. EPSG:32632 con origine inventata solo per roundtrip geospaziale, non calibrazione geografica.

| Esecuzione 600 s simulati | Celle con probabilità >0 | Somma probabilità (celle attese bruciate) | Tempo nel modello | RSS massimo processo |
|---|---:|---:|---:|---:|
| `pilot600-cold` | 9 | 6.5 | 2.739865 s | 329826304 byte |
| `pilot600-warm`, stesso processo | 6 | 4.5 | 0.000248 s | 329990144 byte |
| `pilot600-child`, nuovo processo | 6 | 3.5 | 2.727641 s | 327401472 byte |

Tempi completi dei due comandi: 5.0530 s (due run nel primo processo), 4.9732 s (un run nel figlio). I nomi `cold/warm` distinguono prima/seconda chiamata nel processo: **non** certificano cache disco fredda, già scaldata da prove precedenti. Import, compilazione JIT e scrittura non hanno tutti gli stessi confini del tempo modello. Il confronto non ha output stocastici uguali e non è un benchmark prestazionale controllato. Tre prove non stimano p95, scalabilità o latenza di scenari reali.

Lo script separato `verify-evidence.py` riapre gli array/GeoTIFF, verifica forma, CRS, uguaglianza raster-array, valori finiti [0,1], innesco=1, propagazione oltre una cella, checksum e sorgenti. PASS sugli artefatti. Gli hash degli array sono tutti diversi: **M0-RNG-01 FAIL** per il metodo tentato, non diagnosi definitiva del RNG upstream parallelo. Necessario pilot dedicato seed/RNG e/o tolleranze statistiche preregistrate, senza trasformare due mappe stocastiche diverse in effetto causale di un intervento.

Risultati negativi conservati: Python urllib di sistema fallisce verifica CA; usato curl con TLS verificato, senza bypass. Il primo harness risolveva il symlink del virtualenv e avviava il Python base senza Numba; corretto nel retry senza alterare i log. Il pilot 120 s non propaga oltre l'innesco; prova diagnostica registra 1.0/1 cella/120 s. Nuovo orizzonte 600 s preregistrato, risultati precedenti restano FAIL.

### Riproduzione locale della prova, senza framework

Dalla radice HAZARDIA, riutilizzando snapshot e ambiente conservati:

```sh
RUN=experiments/runs/m0-audit-20261015T122006Z
NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
PYTHONPATH="$RUN/sources/propagator_sim/src" \
.m0-venv/bin/python "$RUN/fire-smoke-600s.py" "$RUN" replay-new
.m0-venv/bin/python "$RUN/verify-evidence.py" "$RUN"
```

Usare sempre una nuova etichetta per non sovrascrivere output. Timeout esterno originale 180 s, comandi ed exit code nei `*-execution.json`. Il seed non garantisce gli hash originali: la ripetibilità esatta resta FAIL. Per ricreare l'ambiente usare un nuovo venv Python 3.12 e il freeze archiviato; non installare nel Python globale. Le sorgenti sono recuperabili con `curl -fsSL --max-time 30 --max-filesize 1000000 https://raw.githubusercontent.com/<repo>/<commit>/<path>`; path in `sources/*/tree.json`. La verifica richiede i file effettivamente scaricati, non ogni file del tree. La completa reinstallazione da zero in un secondo ambiente è NOT RUN.

## HMC→REFlEx: fattibilità dell'interfaccia

Osservazioni dal codice pinned:

- HMC `HMC_Module_Data_Output_Gridded.f90:511–513` scrive `Discharge`, unità `m^3/s`, metadato griglia `epsg:4326`. Output point contiene `section_discharge`, e possono esistere output ASCII/time series. Grid/time/orientamento vanno letti dai file reali, non dedotti solo da questo literal.
- REFlEx `reflex_step4_flood_mapping.py:158–171` legge CSV indicizzato `stream`, unisce ai reach derivati dal preprocessing e calcola `V0=(Q<rp>−Q0)*tconc/2`, `Q_p_t=Q<rp>−Q0`. `tconc` è in secondi (formule in `lib/reflex_tools_basins.py`). Quindi portata in m³/s → volume in m³ è dimensionalmente coerente sotto l'assunzione triangolare. Il nome `volume_file_path` non significa che accetti direttamente qualsiasi volume/idrogramma.
- `lib/reflex_tools_flooding.py` divide HAND per 100, ottimizza il volume e scrive profondità raster in metri; areacell deriva da `res_km`. Serve verificare vertical datum, scala HAND, nodata, area fisica alle diverse latitudini e configurazioni in coordinate geografiche.

Il ponte deve: mappare sezioni/celle HMC ai reach REFlEx con controllo area drenata e connettività; fissare finestra/issue/valid time, Q0 e criterio picco; validare tconc e approccio volume; evitare doppio conteggio tra reach, valori negativi e valori mancanti; allineare DEM, reticolo, datum e CRS senza interpolare portate come profondità. La colonna `Q100` è un'etichetta di scenario di tempo di ritorno: un picco previsto non acquisisce automaticamente un tempo di ritorno di 100 anni. Questa traduzione richiede una convenzione esplicita e validazione; non si cambia di nascosto l'algoritmo upstream.

REFlEx produce una stima geomorfologica di profondità/estensione, non una simulazione idrodinamica temporale completa. Il tempo di transito interno non giustifica mappe di arrivo temporali operative. Nessun forecast dinamico flood può essere dichiarato verificato ora. Mitigazione fisica, soccorso ed esposizione restano separati: il soccorso non modifica la portata.

**Prova necessaria:** dominio piccolo con statiche/forcing HMC e almeno tre reach identificabili; idrogrammi reali, conversione tracciata e verificata, esecuzione REFlEx step0…4 o statiche precompute con provenienza; audit delle unità, join mancanti, no-data e conservazione/assunzioni sui volumi; confronto con osservazioni indipendenti più avanti. Stato BLOCKED; nessuna dichiarazione di catena impossibile né sostituzione proposta.

## Inventario iniziale dati e accesso locale

Verifica documentale al 15/10/2026. Nessun dataset storico acquisito o calibrato. PASS del catalogo significa analisi delle fonti, non accesso empirico; le righe pendenti non autorizzano download indiscriminati.

| Fonte primaria / ruolo | Accesso, diritti e granularità | Limite / prossimo controllo |
|---|---|---|
| [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/content/academy/data_api/firms_api_use.html), VIIRS/MODIS hotspot/FRP | API MAP_KEY gratuito; [WFS](https://firms.modaps.eosdis.nasa.gov/mapserver/wfs-info/) indica 5000 transazioni/10 min; NRT e archivio distinti | BLOCKED accesso API finché chiave non fornita; diritti/citazione specifica prodotto da archiviare; hotspot non perimetro né intensità dell'intero incendio |
| [Sentinel-1/2 CDSE](https://dataspace.copernicus.eu/terms-and-conditions) | Dati Sentinel gratuiti/full/open secondo legal notice; accesso prodotti può richiedere account/token e quote; SAR per flood, ottico per burn scar/fuel | Download NOT RUN; separare diritti dei dati e del sito; scene pesanti da ritagliare; nuvole/layover/revisit e tempi di produzione |
| [ECMWF Open Data](https://www.ecmwf.int/en/forecasts/datasets/open-data) | Subset IFS/AIFS gratuito, CC-BY-4.0 + [termini ECMWF](https://apps.ecmwf.int/datasets/licences/general/); GRIB, issue/cycle, lead/valid, membri ensemble | Download/decoder NOT RUN; no servizi di delivery a pagamento; archivio rolling non equivale a storico forecast completo; risoluzione non locale |
| [GPM IMERG](https://gpm.nasa.gov/data/imerg) | Osservazione/estimazione precipitazione; prodotti early/late/final e distribuzione NASA; non ensemble forecast | Accesso prodotto e Earthdata/diritti puntuali da congelare; NOT RUN; final non disponibile all'epoca di un replay NRT |
| [Copernicus DEM](https://dataspace.copernicus.eu/) / DTM regionali | Candidato terreno; servono licenza specifica GLO-30/90 o DTM locale, datum verticale e condizionamento | BLOCKED scelta/diritti del prodotto; DEM non risolve strutture idrauliche o calibrazione; non scaricato |
| [GHSL](https://human-settlement.emergency.copernicus.eu/datasets.php) | Candidato popolazione/edificato globale, da fissare release, anno, risoluzione e licenza nel catalogo | Licenza della release e adeguatezza NOT RUN; griglia popolazione non inventario operativo né presenza in tempo reale |
| [OpenStreetMap](https://www.openstreetmap.org/copyright) | Dati ODbL con attribuzione e obblighi su database derivati; snapshot locale estratto per AOI | Download NOT RUN; tiles hanno policy distinta; strade non certificano accessibilità; chiusure ignote = UNKNOWN |
| EFFIS, Copernicus EMS Rapid Mapping/GFM, UNOSAT | Candidati footprint/extent per scoring storico, con prodotto/evento e orari di rilascio da selezionare | NOT RUN verifica puntuale di licenza/API/ground truth; non applicare la licenza di un report a tutti i raster |
| Misure pluviometriche/idrometriche regionali, suoli/fuel/parametri HMC | Necessarie per inizializzazione/calibrazione e confronto | BLOCKED selezione bacino, disponibilità storica, frequenza, dati e diritti; satellite/meteo globali non li sostituiscono automaticamente |
| Inventari risorse e vulnerabilità/interventi | Risorse sintetiche dichiarate per pilot; nessun inventario reale ricevuto | BLOCKED efficacia operativa/threshold esperti; non inventare percentuali di soppressione/soccorso |

Per Italia: scegliere un evento fire e uno flood solo dopo controllo input e osservazioni held-out; Magra è un candidato tecnico dal launcher, non un caso validato/scelto. Senegal resta test sintetico di CRS/fuso/giurisdizione, non calibrazione reale. Niente selezione opportunistica di soli casi riusciti.

Cache proposta: originali immutabili per hash SHA-256; metadata JSON con product/release, licenza/testo attribuzione, checksum, issue/valid/sensed/ingested/availableAt, CRS/datum/unità, AOI, nodata, preprocessing/versione e diritti di redistribuzione. Derivati GeoTIFF/COG, GeoParquet/GeoJSON a volume ridotto, NetCDF/GRIB originali conservati; join con manifest e indice locale, nessun database distribuito iniziale. Cache LRU per derivati rigenerabili, mai eliminare l'unica evidenza raw; limiti disco espliciti dopo benchmark. Per replay usare availableAt/issue time e riservare dati futuri allo scoring. Offline significa replay di cache valida, non dati eternamente freschi.

## Architettura, contratti e performance

L'ADR confronta stack e isolamento. Si conserva l'architettura multi-hazard con core Python candidato, processi simulatori separati, solver sostituibili, safety checker esterno, sei capability, rolling horizon e autorizzazione umana. Nessun requisito ridotto per far passare le prove. L'interfaccia asincrona deve includere queue bounds, stato terminale, TTL dei prodotti, cancellazione dell'albero processi, directory output per run, commit atomico e retry limitati. Un subprocess macOS non è un sandbox di sicurezza o un limite RAM garantito; Linux consente futuri limiti cgroup, da testare.

Il solver non deve richiamare fisica costosa per ogni ramo: valuta conseguenze su prodotti/ensemble versionati e validi; assenza di hard constraint → UNKNOWN. Il watchdog esterno mantiene 60 s da accettazione, includendo coda, verifica e serializzazione. Timeout non è soluzione utile o prova di infeasibilità. Scelta CVaR/max, pesi e soglie operative restano da pilot/esperti; non vengono fissati qui.

Dashboard locale candidata React/TypeScript e MapLibre con asset/basemap locali, alternative Leaflet/OpenLayers. Nessuna UI costruita né misurata. Node 16 esistente è un prerequisito da sostituire con runtime locale supportato dalla versione di build scelta prima di M3; non è stato aggiornato. Profiling, fixture sizes, viewport e budgets invariati nel report performance.

## Ricerca e minacce alla validità

Rilevanza JSS: i fallimenti RNG, ambiente legacy e accoppiamento idrologico sono evidenza di rischi di riproducibilità/interoperabilità, non risultati a favore di H1–H3. Non sono misurate qualità decisionale, graceful degradation, tempi 60 s, skill fisica o usabilità. La prova nativa fire dimostra eseguibilità della versione specifica su questo host, non validità operativa/geografica. Campione piccolo, fixture piatta, seed non controllato, cache JIT scaldata, nessun confronto Linux e nessuna calibrazione limitano qualsiasi generalizzazione.

Revisione iniziale related work in `research/RESEARCH.md`: fonti CIMA e articolo REFlEx; Delft-FEWS e Sahana mostrano già orchestrazione/risorse/mappe. Siti inaccessibili/redirectati restano non verificati. Nessuna rivendicazione di primato o miglioramento scientifico. La ricerca sistematica SE, BibTeX completo e revisione JSS alla submission restano NOT RUN.

## Decisioni richieste e prossimo incremento eseguibile

1. **Runtime flood e budget download/disco:** autorizzare un proseguimento di M0 per una VM Linux in UTM già installato, con tetto proposto di download 5 GiB e disco virtuale massimo 20 GiB, RAM 8 GiB/4 vCPU. Prima ARM64 moderno con toolchain Fortran/NetCDF e feasibility GRASS; se la ricostruzione REFlEx richiede porting, registrare il problema e chiedere decisione prima di cambiare architettura. x86 emulato resta alternativa da confrontare. Le taglie sono budget proposti, non download misurati o garanzia di sufficienza. Con 56 GiB liberi serve conservare margine; niente VM creata/scaricata ora. Il vincolo deriva da AGENTS § “Stop and ask permission” e dall'autorizzazione utente per download grandi/installazioni privilegiate.
2. **Fixture flood:** selezionare un piccolo bacino con statiche, forcing, calibrazione e diritti, possibilmente esempio ufficiale completo. Ricerca pubblica può continuare in M0; contatto con CIMA o altri richiede autorizzazione a inviare messaggi. Nessun contatto inviato.
3. **Ripetibilità fire:** prossimo pilot M0 dedicato al seed upstream, senza patch silenziose né promesse di identità; poi confronto diretto/processo/VM su fixture identiche e tolleranze preregistrate.
4. **Git:** inizializzazione locale e licenza del framework da concordare per una storia riproducibile prima di M1. Nessun push autorizzato o effettuato. Finché manca Git, manifest riporta SHA nullo e hash file; non soddisfa integralmente il gate commit/replay.

Prossimo incremento: completare **M0**, ottenendo i prerequisiti flood e un run minimo standalone per ciascun motore, poi prova del ponte e contratti validi/invalidi. Solo dopo report del gate e nuova autorizzazione dell'utente si potrà avviare M1. Nessun M1 avviato.
