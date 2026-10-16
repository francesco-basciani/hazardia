# M0 — Esecuzione unificata nella VM Linux

15 ottobre2026. **Collocazione applicata e verificata: PASS per le prove M0.** Incendi, alluvioni, preparazione dei dati, controlli numerici e produzione della figura sono stati eseguiti nella stessa VM `HAZARDIA-M0-ARM64`. Il Mac ha trasferito file/comandi e visualizza risultati: nessun calcolo scientifico nativo Mac è necessario per questa pipeline.

Decisione richiesta esplicitamente dall'utente: [ADR-0002](ADR-0002-single-linux-runtime.md). La scelta vale anche per i futuri backend, scheduler, solver e build/servizio della dashboard, **ancora NOT RUN / M1 non autorizzata**. M0 complessiva resta BLOCKED per i prerequisiti scientifici/contrattuali già documentati.

Run: `experiments/runs/m0-unified-vm-20261015T150415Z/` (RUN). Esecuzione guest: `/home/hazardia/m0/m0-unified-vm-20261015T150415Z/` (GUEST). Git SHA/dirty null: directory host non Git; documenti, input, sorgenti, patch e output identificati mediante SHA256. Ricercatore/revisore: Codex, con lettori separati dei prodotti nel guest e controlli di trasferimento sul Mac; revisione umana esterna pendente.

## Componenti nella stessa macchina

| Componente | Collocazione / esito verificato |
|---|---|
| Accesso alle fonti | VM: catalogo pubblico HTTP200, due letture HTTP206 da16KiB di DEM e Sentinel; byte identici ai payload fissati. PASS. |
| Cache dati | VM: copia integrale dei tre asset originali, hash verificati. Si riusa la cache già acquisita, senza dichiarare falsamente un nuovo download integrale dalla VM. PASS. |
| Preprocessing | VM: ritaglio DSM, area ellissoidale delle celle, riproiezione UTM, immagine satellite e classificazione SCL.140725celle, come nel pilot. PASS. |
| PROPAGATOR | VM, `~/m0/fire-env`, Python3.12.15. Sei nuove esecuzioni, due seed, tre repliche, un thread/spottingoff. Array probabilità/fire/arrival ripetibili per seed e identici alle precedenti prove Linux; i seed producono risultati distinti. PASS limitato alla fixture64². |
| HMC | VM, binario ARM già compilato. Nuova directory statica/forcing e output/state/restart inizialmente vuoti; sei prodotti gridded65², m³/s, finiti/nonnegativi e fine normale. PASS sintetico. |
| REFlEx | VM, ambiente flood Python3.10.12. Pipeline0–4 effettivamente ripetuta con la copia sperimentale che include le due correzioni già dichiarate;69HAND validi,69ottimizzatori finiti, mappa433×325. PASS tecnico. |
| Validatori numerici | VM: NumPy/rasterio/netCDF4 leggono i prodotti e controllano dati e hash. PASS. |
| Rendering satellite/allagamento | VM: Pillow9.0.1 e font Linux DejaVuSans, senza font/librerie Mac. PNG generato nel guest e soltanto copiato sul Mac per mostrarlo. PASS. |
| Backend, solver, dashboard HAZARDIA | Previsti nella medesima VM; non costruiti né avviati. NOT RUN. |

Gli ambienti Python separati restano **dentro la stessa VM**: servono a evitare conflitti di dipendenze fra fire e flood. Il contenimento dei guasti rimane basato su processi/ambienti separati, non sulla divisione tra Mac e Linux.

La figura generata nella VM è disponibile in [satellite-e-scenario-vm.png](m0-unified-vm/satellite-e-scenario-vm.png). Dati e limitazioni sono quelli del [pilot sul territorio reale](M0-real-terrain.md), comprese le attribuzioni: elevazione/immagine reali, portate ipotetiche, nessuna piena osservata o previsione validata. Nessuna nuova calibrazione/skill dedotta dal cambio di collocazione.

## Risultati e limiti

Il nuovo output REFlEx contiene3502celle positive, profondità massima0.7803145051m; SHA256 `10e4e6cd9221838c5e9b711a1a52145caef7d409f5f0e56c20542176e16704d0`. Massimo residuo relativo dei69ottimizzatori3.586×10⁻⁷. Non si assume identità binaria fra nuovi GeoTIFF e il run precedente: ambiente GDAL diverso per la preparazione e inizializzazione casuale dell'ottimizzatore restano registrati. Nessun requisito di ripetibilità universale REFlEx dichiarato.

Gli entry point e le configurazioni sono stati controllati per escludere `/Users/`, `/System/Library/`, `.m0-venv` e volumi host: nessun riferimento presente. Nessuna cartella condivisa host è necessaria. Gli asset sono residenti nel filesystem guest. I comandi SSH sul Mac sono controllo/trasporto, non una dipendenza scientifica del runtime.

Originali CIMA invariati:125file controllati. La copia REFlEx `reflex-src-compat/` conserva identità e diff delle due modifiche: bordo di lavoro HAND di una cella e fusione vincolata ai bounds/res della griglia base. Il precedente FAIL del codice ufficiale non viene riscritto; il presente PASS riguarda tale copia sperimentale e questa fixture.

## Riproduzione e provenienza

Nel guest sono presenti `prepare-terrain.py`, `fire-probe.py`, `render-preview.py`, `settings-vm.json`, cache originali, prodotti, log e copia REFlEx. Dipendenze già installate: **nessuna nuova installazione**, nessun pacchetto scientifico host richiesto. Freeze separati `fire-freeze.txt` e `flood-freeze.txt`.

Sequenza effettiva e comandi integrali sono nei record RUN:

1. `vm-preflight.json`: verifica input, fonte HTTP e preprocessing nel guest.
2. `vm-reflex-steps01.json`, `vm-reflex-steps234.json`: pipeline reale REFlEx.
3. `vm-fire-and-hmc.json`: esecuzioni nuove di entrambi i motori.
4. `vm-validate-fire-hmc.json`, `vm-validate-and-render.json`: letture/controlli numerici e rendering nel guest.
5. `vm-source-access.json`, `vm-archive.json`: accesso diretto ai dati e archivio guest.

Ogni record contiene lo script shell effettivamente eseguito e il suo esito; log numerici e configurazioni sono in GUEST. Per ripetere usare nuove directory/run_id e correggere tutti i riferimenti alle destinazioni, senza sovrascrivere gli esperimenti archiviati. Le prove native Mac precedenti restano controlli storici di portabilità, non istruzioni di deployment.

Archivio guest SHA256 `d6594c2ea837bc67349586a393100ab55a8df9c77e064f968c46dee29371fb28`,10,591,147byte.646file verificati per hash; per evitare duplicazioni l'archivio di trasporto omette i tre asset sorgente grandi, già conservati e hashati sul Mac e **interamente presenti nella VM**. Il controllo di trasporto sul Mac esegue soltanto SHA256 dei file, non calcoli sui raster.

## Budget e stato

VM invariata:4vCPU,8GiBRAM,19GiBdisco; filesystem usato circa5.64GB. Riutilizzo dei dati già scaricati, circa51KB di corpi HTTP nuovi dal guest. La contabilità cumulativa conservativa resta sotto2GiB su5GiB includendo anche il trasferimento locale della cache come margine. Nessun servizio pubblico, costo, push, installazione globale o dipendenza da un secondo computer.

VM lasciata accesa per ispezione. Tutto il futuro runtime deve rispettare ADR-0002; un browser sul Mac può agire da client grafico. **M1 e i servizi del framework non sono stati avviati.** Restano BLOCKED qualificazione idrologica e input/diritti idrologici reali; G-01 completo NOT RUN.
