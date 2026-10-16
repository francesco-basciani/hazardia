# Mappe più dettagliate e contesto geografico

La dashboard locale ora offre **ortofoto aeree regionali a 20 cm/pixel dichiarati**, zoom fino a 20 e mappe espandibili. Si distinguono edifici, piazze e strade. La precedente base Sentinel-2 a 10 m resta selezionabile per l’uso offline nell’area ritagliata dell’Aquila.

Per provarla: aprire http://127.0.0.1:8080/, scegliere **Ortofoto Abruzzo**, cercare `L'Aquila` o coordinate come `42.34892, 13.397967`, premere **Vai** e **Mappe più grandi**. Un clic sulla mappa apre la scheda del punto. **Centra area** torna ai risultati fisici. Ricerca e ispezione non avviano simulazioni.

## Cosa viene mostrato

- Coordinate WGS84 del puntatore, del centro e del punto selezionato; zoom, nord e scala metrica.
- Località dell’Abruzzo dal repertorio GeoNames; quartieri, strade e punti di interesse da uno snapshot OpenStreetMap del centro dell’Aquila.
- Località e quartiere/frazione più vicini, strada nominata più vicina e punto di interesse più vicino, con distanza approssimata e collegamento al record sorgente. Indirizzi solo dove presenti nella fonte.
- Fonte, data e limiti del dato; stato di caricamento/errore delle immagini e passaggio manuale a Sentinel offline.

**Non sono ancora presenti confini amministrativi ufficiali, particelle catastali, quota interrogabile o una copertura stradale completa dell’Abruzzo.** Il nome più vicino è un riferimento geografico, non determina il comune o il quartiere di appartenenza. Le strade visualizzate non certificano percorribilità o sicurezza e non modificano i vincoli sintetici del decision engine.

## Fonti e condizioni

[Regione Abruzzo, ortofoto 2018–2019](https://geoportale.regione.abruzzo.it/Cartanet/catalogo/cartografia-di-sfondo-raster/copy_of_ortofoto-regione-abruzzo-2007-a-colori-1): pixel dichiarato 0,20 m, EPSG:32633 nativo; WMS dichiara anche EPSG:3857. [Accesso WMS regionale](https://trasparenza.regione.abruzzo.it/servizi-erogati/carta-servizi/servizi-wms) gratuito, senza autenticazione. Licenza indicata dalla scheda: **Licenza regionale**, download del mosaico non offerto. Implementata consultazione WMS via HTTPS, cache solo RAM; nessuna distribuzione pubblica o archivio delle ortofoto. Non è un’immagine satellitare né un’immagine dell’evento simulato, ed è del 2018–2019.

[OpenStreetMap](https://www.openstreetmap.org/copyright), ODbL 1.0: estrazione una tantum API ufficiale in bbox `[13.375,42.345,13.405,42.36]`, acquisita 2026-10-15T20:51:26Z. Il timestamp è di acquisizione; i tempi di modifica dei singoli elementi restano nel raw. 14 punti di località, 1.143 tratti stradali nominati e 222 POI; non 1.143 strade distinte. Snapshot originale 12.207.956 B. API di editing usata solo in lettura per questa piccola estrazione dopo errori Overpass; la dashboard non interroga nessuna delle due API durante la navigazione. Per ampliare sistematicamente usare estratti territoriali, non richieste ripetute all’API di editing.

[GeoNames](https://www.geonames.org/export/), CC BY 4.0: estratto Italia gratuito, ZIP 4.361.535 B; filtro luoghi abitati, admin1 `01` (Abruzzo), dentro rettangolo di visualizzazione. Duplicati di nome rispetto ai punti OSM esclusi; punti geografici, non poligoni amministrativi. Dati di epoche diverse, senza garanzia di completezza o aggiornamento. Nessun servizio geocoding a pagamento o Nominatim pubblico integrato.

Snapshot combinato **3.834 elementi / 1.025.160 B**, SHA-256 `afcd5c7927eb65d04f47a72148d6ce48eb2d52ae8527bd44132e1038b0379e4e`. I dati OSM e GeoNames mantengono attribuzioni/licenze separate. Dataset e metadati sono nella VM; Mac è sviluppo e client di visualizzazione.

## Ripetibilità e verifiche

Run `map-detail-20261015T204352Z`; baseline `7c23943`, implementazione e UI finale `a7d3eb6` (precedenti `0a85017`, `37c15f8`). Comandi esatti e stdout/stderr nei log JSON sotto `experiments/runs/map-detail-20261015T204352Z`; copie dati in `/home/hazardia/hazardia-runtime/runs/map-detail-20261015T204352Z`. Ambiente invariato: Ubuntu22.04/aarch64, 4 vCPU, 8 GiB RAM, disco19 GiB; Python core3.10. Browser Chrome155 su Mac, nessun servizio scientifico sul Mac.

```text
# VM, dalla directory app
PYTHONPATH=src:. ../core-env/bin/python scripts/build_map_context.py --runtime /home/hazardia/hazardia-runtime --run /home/hazardia/hazardia-runtime/runs/map-detail-20261015T204352Z
PYTHONPATH=src:. ../core-env/bin/python -m unittest tests.unit.test_maps -v
PYTHONPATH=src:. ../core-env/bin/python -m unittest discover -s tests/unit -v
PYTHONPATH=src:. ../core-env/bin/python -m unittest discover -s tests/domain -t . -v
PYTHONPATH=src:. ../core-env/bin/python -m unittest discover -s tests/decision -t . -v
# Mac, solo test del client browser
node tests/browser/map-detail.cjs experiments/runs/map-detail-20261015T204352Z/browser-final
node tests/browser/accessibility.cjs experiments/runs/map-detail-20261015T204352Z/accessibility-final experiments/runs/m3-dashboard-20261015T192310Z/axe.min.js
```

| Verifica | Esito | Evidenza / limite |
|---|---|---|
| WMS effettivo e prima immagine | PASS | Capabilities HTTP200, layer corretto/CRS3857; JPEG reale512², 63.529 B; log imagery-context-probe.json |
| Contesto acquisito e servito dalla VM | PASS | Prima versione context-build/deploy-context-v2/service-data-proof; versione finale final-context-snapshot/final-release-proof con SHA sopra |
| Tile validati, bbox, cache LRU, budget persistente, errori/release slot | PASS | 5 nuovi test unitari, deploy-context-v2.json |
| Regressioni software | PASS | 38unit+19domain+14decision=71; regression-and-integrity.json |
| Motori e riferimenti prodotti invariati | PASS | 145engine hash corrispondono; elenco SHA dei 7prodotti nel log; nessun modello rieseguito per aumentare il dettaglio |
| Funzioni cartografiche/responsive/errore fonte | PASS | 19controlli browser-final/results.json; larghezze375/768/1440, ricerca, coordinate, scala, nomi, degradazione simulata503 e recupero offline |
| Reattività del client | PASS | 30cambi etichette p9516,2ms;31cambi base p9514,2ms;30pan su base offline con nomi p05≈59,99FPS. Non è misura del tempo di download online |
| Accessibilità automatica | PASS | axe4.10.3, zero violazioni ai3formati; rimangono verifiche contrasto/link **incomplete**, conservate nel raw: non attestazione WCAG completa |
| Download metadati/contesto tramite Overpass | FAIL | HTTP500/502/406 e timeout, conservati; funzionalità recuperata con estrazione OSM limitata e GeoNames |
| Prime estrazioni OSM troppo estese | FAIL | API400, limite50.000nodi; riduzione AOI, nessun aggiramento del limite |
| Prima risposta asset JSON | FAIL | Serializzazione bytes difettosa; corretta e endpoint finale HTTP200 con SHA verificato. Cache versionata per aggiornare client già aperti |
| Precisione fisica a20cm / confini ufficiali / dati catastali | NOT RUN | Non prodotti da questo incremento; non dedotti dalla nitidezza dello sfondo |
| Rilascio scientifico completo / skill storica | BLOCKED | Restano i limiti M5/M6/M7 già registrati |
| Nuova stabilità30min e prestazioni streaming online | NOT RUN | Il precedente soak si riferisce al software precedente; nessuna estensione automatica del risultato |

Proxy consultazione: endpoint/layer fissi, tiles256², zoom8–19 nativo e visualizzazione20, max4download contemporanei, ammissione16richieste, timeout8s più attesa slot10s, payload≤1MiB, cacheRAM≤16MiB, limite persistente256MiB di immagini acquisite. Download globale VM resta vincolato a5GiB; nessun cambiamento risorse. Rendering limitato per vista a120località,200tratti stradali e40POI, etichette anticollisione; nessun caricamento di100.000oggetti DOM. Stress100k precedente resta FAIL: non è risolto né riclassificato da questi test.

Le celle di incendio e allagamento restano i risultati nativi dei simulatori. Una fotografia più nitida **non** rende più precise la griglia fisica, la previsione o l’efficacia degli interventi. Nessuna conclusione H1–H3 o validazione operativa deriva da queste verifiche.

Additional screenshot readiness check PASS: `browser-capture-verified/results.json`, all19checks repeated; screenshot waits for all visible256px tiles at full opacity after map expansion. p95label15.8ms/base15.6ms on this repeat; previous browser-final metrics above remain unchanged. Test-script revision archived with final Git commit. Actual screenshot: reports/dashboard-evidence/map-detail/orthophoto-detail.png.

Final context refinement `c190503`/`14457b5`: retain Chieti/Pescara/Teramo capitals at regional zoom, immutable content-addressed snapshot. Final context SHA afcd5c7927eb65d04f47a72148d6ce48eb2d52ae8527bd44132e1038b0379e4e (1,025,160B); earlier c24d snapshot remains in frozen first archive, not retroactively changed. Full cumulative download accounting carries historical upper bound: PASS2,691,375,540B/5,368,709,120B at final-resource-budget checkpoint (raw image+currentRX alone is incomplete); free disk12,676,374,528B. First archive transport PASS17files, SHA bd541f6b108f981b9b7b56d68566feeb32a0cc8eed40da7806a0dd2ee51558a5. Final release UI/transport outcomes below are separate subsequent checks.

Final UI verification PASS on source `c190503`: `browser-release/results.json` all19checks; labels30feedback p9515.6ms, base31feedback p9515.1ms, offline30pans p05≈60FPS. `accessibility-release/axe-results.json`:0violations375/768/1440, raw contrast/link incompletes retained. `final-release-proof.json` verifies final contextSHA and145unchangedenginefiles; current service/data operated solely in VM. Client display test-script hash and screenshot hashes: client-release-manifest.json. Prior measurements/snapshots stay historical; full scientific-release and100kload blockers unchanged.

Final local evidence transport PASS:21files rehashed on Mac (copy inspection only), archiveSHA90d58689998edb38e2667fb4d3c9c9664607f23e79ca992c04755a88e5f5d294; `final-transport-verification.json`. Final runtime budget proof2,708,877,321B/5,368,709,120B, free disk12,670,672,896B; resources unchanged. Native raster byte integrity and Sentinel background independently rehashed against catalog/product manifests: PASS7native rasters, `native-product-byte-integrity.json`; no physical-resolution upgrade claimed.
