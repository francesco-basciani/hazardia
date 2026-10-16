# M0 — Dal terreno artificiale al territorio reale

15 ottobre 2026. **Incremento M0 eseguito; gate complessivo ancora BLOCKED. M1 non avviata.**

Abbiamo acquisito terreno e immagini satellitari reali di una piccola area della Lunigiana e prodotto una mappa REFlEx sovrapposta al satellite. Le portate sono ipotetiche: questa è una verifica tecnica georeferenziata, non una previsione né la ricostruzione di un'alluvione. Il codice ufficiale ha mostrato un difetto su due tratti; una copia sperimentale con due modifiche circoscritte supera i controlli eseguiti. Il Mac non richiede più risorse per questo incremento.

![Satellite reale e scenario ipotetico](m0-real-terrain/satellite-e-scenario.png)

Run `experiments/runs/m0-real-terrain-20261015T142405Z/` (RUN), predecessore `m0-linux-rng-20261015T124458Z` immutato. Responsabile e revisore dei controlli: Codex / Research Recorder; lettori separati guest/Mac; revisione idrologica umana **pendente**. Git SHA/dirty null: la directory non è un repository Git. Identità tramite hash dei documenti, dati, sorgenti ufficiali e patch. Quadro precedente in [M0-continuation.md](M0-continuation.md).

## Cosa è reale, cosa è ipotetico

| Elemento | Origine e significato |
|---|---|
| Territorio | Rettangolo WGS84 [9.90,44.30,9.99,44.42], Lunigiana/area Caprio. Scelto prima dei risultati; non ancora verificato come bacino completo. |
| Elevazione | Copernicus GLO-30 pubblico, tile `Copernicus_DSM_COG_10_N44_00_E009_00_DEM`, distribuzione AWS2021. DSM: comprende edifici/vegetazione, non DTM del terreno nudo. Datum verticale EGM2008. |
| Satellite | Sentinel-2 L2A `S2B_32TNQ_20240711_1_L2A`, acquisizione **11 luglio2024 10:18:34.254UTC**. Sfondo storico, non osservazione della piena né immagine in tempo reale. |
| Pioggia e portate | Nessuna pioggia reale e nessun idrogramma HMC su questo territorio. Qpeak ipotetica =1m³/s per km² di area drenata; Q0=0 soltanto come assunzione sintetica. |
| Mappa blu | Output effettivo REFlEx, con due patch sperimentali esplicite. Profondità massima dello scenario, non tempi di arrivo o evoluzione temporale della piena. |
| Risorse/interventi | Assenti: nessuna decisione o azione operativa. |

I [dati Copernicus DEM](https://registry.opendata.aws/copernicus-dem/) e [Sentinel-2 COG](https://registry.opendata.aws/sentinel-2-l2a-cogs/) sono stati acquisiti dai mirror pubblici senza account/pagamenti; i diritti sono verificati separatamente dai codici CIMA. Licenze primarie archiviate in RUN `sources/dem-license.pdf` e `sources/sentinel-legal-notice.pdf`: [licenza DEM](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/DEM/resources/license/License-COPDEM-30.pdf), [legal notice Sentinel](https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice). Attribuzioni complete in [ATTRIBUTION.md](m0-real-terrain/ATTRIBUTION.md). Questo risolve l'accesso al terreno/sfondo del pilot, **non** la licenza dei dataset idrologici CIMA, ancora non accertata.

Scelta satellite preregistrata: giugno–agosto2024, copertura AOI intera, minimo cloud cover di scena, poi timestamp/ID. Dei37 risultati il prescelto ha cloud cover0.110879% sull'intera scena; sull'AOI le classi SCL3/8/9/10 sono assenti e la copertura valida è100%. È un controllo della classificazione fornita, non una garanzia indipendente di assenza nubi o una selezione di evento storico. Scene/data/ETag/HTTP/hash in RUN `sources/`, `commands/`; immagini complete conservate e versionate con checksum.

## Esecuzioni e verifiche

| ID | Esito | Risultato / evidenza RUN |
|---|---|---|
| REAL-RIGHTS | PASS per questi due prodotti | Licenze/provenienza e payload reali; `sources/`, `selection-verification.json` |
| REAL-GRID | PASS tecnico |433×325 =140725celle valide, elevazioni118.674–1813.068m; GeoTIFF WGS84 e derivato UTM32N30m; `terrain-verification.json` |
| REAL-AREA | PASS misurazione | Area ellissoidale media683.51745m², range682.82685–684.20755; assumere900m² sovrastimerebbe l'area del31.67%. Configurato `res_km=0.026144166741208372`; errore massimo della media costante circa0.101%. Controllo indipendente pyproj.Geod al centro concorde entro1.9×10⁻⁷ relativo. |
| REAL-REFLEX-BASE | FAIL qualità completa | Codice originale step0–4 termina e genera un raster, ma HAND14/32 hanno zero pixel validi e relativi ottimizzatori hanno velocità non finita/residuo100%. `real-output-validation.json` nel guest. |
| REAL-HAND-DIAG | PASS diagnosi circoscritta | Entrambi i tratti hanno un solo pixel di reticolo, 35/37celle dal bordo AOI. Bersagli presenti nel ritaglio; stesso pysheds sul dominio intero produce HAND. Un bordo di lavoro1cella ripristina dati. `empty-hand-crop-probe.json`, `empty-hand-halo-probe.json`. Non attribuito erroneamente al confine dell'AOI. |
| REAL-HALO-MERGE | FAIL tentativi conservati | HAND con halo prodotti; merge originale tenta434×327 contro433×325. Ritaglio degli input ai bounds non basta:434×326 per allineamento numerico. Log `step4-halo*.stdout`. |
| REAL-REFLEX-COMPAT | PASS configurazione sperimentale | Halo + merge esplicitamente vincolato a bounds/res della griglia base.69HAND non vuoti, finiti/nonnegativi;69righe ottimizzatore finite; raster finale433×325. `halo-output-validation-v2.json`, patch e comandi. |
| REAL-HAND-REGRESSION | PASS confronto | Nessun pixel precedentemente valido perso; differenza sui pixel comuni **0cm**;7032pixel validi aggiuntivi entro le estensioni precedenti. Non prova validità fisica dei nuovi pixel. |
| REAL-MAP | PASS output/visualizzazione |3502celle positive, profondità massima0.7803145051m. SHA256 `6a6fe903e885de6b6a64b891a1d4b1b7bf66edbaea004c6ea3ee947aa6dfa258`. Residuo relativo ottimizzatore massimo5.20×10⁻⁷, assoluto0.000803m³: misura di adattamento al volume imposto, non accuratezza rispetto a osservazioni. |
| HMC-DT | PASS esecuzione/sensibilità | Tre nuovi run sintetici65² con dt4/2/1s, sei prodotti ciascuno, fine normale e portate finite/nonnegative. `dt-validation.json`. |
| BRIDGE-SEMANTICS | PASS analisi; qualificazione BLOCKED | Audit sorgenti e letteratura; Q0 richiede significato idrologico corretto. `interface-audit.json`. |
| REAL-INTEGRITY | PASS |1126file guest verificati;125sorgenti originali invariati;987artefatti del run precedente invariati. `transfer-validation.json`, `host-verification.json`, `parent-integrity.json`. |
| G-01 completo / HMC reale / skill / UI / decision60s | NOT RUN | Nessuno schema completo o adapter del framework, calibrazione su evento, dashboard o benchmark del prodotto implementato. |

I file menzionati solo col nome sono sotto RUN oppure RUN `guest/m0-real-terrain-20261015T142405Z/` (GUEST). Tutti i tentativi negativi restano leggibili; il PASS della copia sperimentale non riscrive il FAIL upstream.

## Correzione sperimentale: due righe, limiti espliciti

Sorgente REFlEx ufficiale fermo a `0dd5aa9803f7c163a4f6c3b42d9f69bce88a53bd`. Solo la copia GUEST `reflex-src-halo/` differisce:

1. `lib/reflex_tools_basins.py`: `grid.clip_to(basin_mask_raster, pad=(1,1,1,1))` aggiunge un bordo numerico di lavoro per HAND.
2. `reflex_step4_flood_mapping.py`: nel ramo seriale di fusione, `rasterio.merge` riceve `bounds=src_grid.bounds, res=src_grid.res`, mantenendo l'output nel dominio autorevole.

Diff EUPL e hash in GUEST `halo-compatibility.patch`, `halo-patch-identity.json`, `merge-patch-identity.json`, `halo-procedure-context.json`. Step0–2 ufficiali, step3 dalla copia con halo, step4 finale dalla copia con merge vincolato. Parametri, reticolo, DSM e portate restano quelli dichiarati prima della prova; nessun tratto rimosso, profondità inventata o algoritmo fisico sostituito. Correzione candidata, non release ufficiale né patch approvata upstream. Il ramo parallelo di fusione non è stato corretto/testato: impostazione merging multiprocessing=false.

## Chiarimento sul collegamento HMC–REFlEx

La [pubblicazione primaria](https://doi.org/10.1111/jfr3.13034), §§2.3/2.5/2.6.2, chiarisce che Q0 è un riferimento di portata a piene rive, non genericamente il primo campione HMC. Il volume triangolare e quello di transito sono quantità distinte dall'integrale dell'intero evento: la sola disuguaglianza non dimostra una violazione di conservazione. È documentato un precedente Continuum→REFlEx, che sostiene la fattibilità concettuale ma non valida il nostro caso.

Conseguenza per HAZARDIA: la precedente interfaccia sintetica rimane una prova tecnica; il suo Q0 iniziale non diventa una stima idrologica giustificata. Prima di usare conseguenze nelle decisioni occorrono scelta del riferimento Q0, intervallo/temporalità delle portate, corrispondenza dei tratti e calibrazione. Proposta semantica in RUN `interface-audit.json`: unità m³/s e secondi, campo di massima profondità/estensione, tempi delle fonti separati da finestra dello scenario, nessun tempo di ritorno senza analisi di frequenza, nessuna mappa di arrivo derivata dalla massima estensione. È una proposta M0 parziale; G-01 completo resta NOT RUN.

Accesso alla pagina Wiley tramite strumento web riuscito; archiviazione diretta PDF/HTML fallita con403 e, sul diverso host istituzionale, certificato scaduto. Controlli TLS non aggirati; log negativi conservati in RUN `commands/`. Nessun testo integrale della pubblicazione dichiarato archiviato.

## Sensibilità del passo HMC

Stesso terreno artificiale e forcing del precedente ponte, nuove directory output/state/restart vuote. Parametro `iDtPhysConv` intero nel sorgente: i prospettati passi0.5/0.25s non sono stati eseguiti; emendamento preregistrato a4/2/1s. Tutte e tre le esecuzioni completano sei passi orari.

| dt | Picco gridded m³/s | Wall time esplorativo |
|---|---:|---:|
|4s|0.34559667|5.21s|
|2s|0.34606668|10.33s|
|1s|0.34689280|19.29s|

Differenza L2 relativa dei campi:4→2s0.6611%,2→1s0.3326%; picco2→1s0.2381%. Questi sono risultati di sensibilità su una fixture, non una stima dell'errore vero o una certificazione di convergenza. Tempi n=1, attività concorrenti con REFlEx: non benchmark p95/scaling/60s, non confrontabili causalmente con i probe precedenti. Il problema adattivo dt0 resta irrisolto.

## Riproduzione, errori degli strumenti e budget

Verifica offline sul Mac, dalla radice HAZARDIA:

```sh
.m0-venv/bin/python experiments/runs/m0-real-terrain-20261015T142405Z/verify-host.py
```

Questo controlla i raster già archiviati e non riesegue i modelli; se il record esiste ne confronta il contenuto senza sovrascriverlo. Procedura di creazione dati in `prepare-terrain.py`, figura in `render-preview.py`, comandi guest esatti nei JSON di `m0ctl.py` (`script`), tutte le configurazioni e output nel bundle guest. Per nuove esecuzioni usare nuovo run_id e nuove directory/configurazioni: non lanciare alla cieca script con destinazioni di questo run. Dipendenze congelate in GUEST `flood-env-freeze.txt`; nessuna installazione aggiuntiva. Figura statica con rasterio/NumPy e Pillow12.3 già disponibile nel runtime dell'app; non è codice UI del framework.

Errori del recorder conservati: primo lettore scipyNetCDF3 usato su outputNetCDF4, sostituito dal lettore netCDF4; percentuali su due HAND vuoti generavanoNaN nel diagnostico, chiarite da `empty-hand-diagnosis-v2.json`; controlli preliminari della patch fermati da assertion conteggio e percorso temporaneo senzaT100; prima figura respinta per sentinella NoData fuori copertura durante reproiezione, corretta con sorgente mascherata e mask di copertura. Questi fallimenti non sono limiti hardware. Nessun esito precedente cancellato.

Archivio guest11,672,198byte, SHA256 `b698ae5afc56fc262c6224f15689cdf08754252a10764674030acf15bce86ac7`,1126file verificati sul Mac. Download HTTP nuovi220,800,553byte; totale cumulativo conservativo circa**1.66GiB su5GiB**, inclusa riserva precedente. Disco guest circa5.36GB usati su19GiB; configurazione invariata8GiB/4vCPU. VM **accesa** e conservata per ispezione; SSH solo localhost. Nessun costo, servizio pubblico, push o installazione globale del Mac. `budget-final.json` esplicita stima, contatori e limiti del metering.

## Cosa manca e prossimo incremento

- **BLOCKED:** qualificazione idrologica del ponte e delle portate reali; nessun Q0 a piene rive, suoli calibrati, forcing reale/gauge o ground truth acquisito per questo dominio.
- **BLOCKED:** licenza dei dataset CIMA già individuati; risolta soltanto disponibilità DEM/satellite del pilot.
- **NOT RUN:** delimitazione/verifica di un bacino completo e reticolo indipendente, validazione storica, robustezza della patch su altre geografie, ripetibilità REFlEx con inizializzazione ottimizzatore controllata, freeze completo dei contratti G-01.

Prossimo incremento M0: usare questa fixture per consolidare il caso di regressione del bordo, verificare un bacino completo e cercare DTM/portate/precipitazioni con diritti espliciti; formalizzare Q0 e i contratti mancanti. La patch resta candidata di ricerca, da riesaminare prima dell'eventuale integrazione. L'accettazione scientifica/operativa richiede revisione idrologica; non serve aumentare risorse per i controlli svolti. **Nessuna autorizzazione a M1 viene presunta.**
