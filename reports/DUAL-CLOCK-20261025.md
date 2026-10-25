# Ora reale e validità dei dati —25 ottobre2026

Run `dual-clock-20261025`, baseline `9d561d854590df5be65c5b57e55b630e328d1888`, reviewer Codex self-check. Modifica UI richiesta: stato VM ultimo elemento a destra; ora reale e ora dei dati distinguibili.

La barra contiene lingua, configurazione e infine connessione VM. Ordine DOM dei controlli visibili e ordine CSS coerenti, anche se i18n inizializza dopo la console; non viene duplicato l’indicatore. Mobile390px conserva testo e spia, senza il precedente taglio a14px.

Il widget accanto alla ricerca ora mostra due campi: Ora reale (HH:mm:ss, aggiornata ogni secondo dall’orologio del dispositivo client) e Dati sulla mappa (data/ora della validità selezionata). Quest’ultimo diventa Previsione sulla mappa quando nel futuro. Non è l’ora di acquisizione del provider né si dichiara che siano ultime osservazioni: i livelli hanno granularità, snapshot e tempi propri nelle legende/fonti. Missing rimane Orario non disponibile anche con ora reale presente. Zona Europe/Rome; offset UTC e data completa nei tooltip, istanti UTC canonici nei due elementi time. Nessuna modifica all’orologio VM, alla timeline o agli input fisici.

PASS suite client `node tests/browser/monitor-clock.mjs`, `monitor-playback.mjs`, `i18n.mjs`: secondi indipendenti, dati fissi/missing, futuro e ora ripetuta DST, compatibilità lingua, playback invariato. Log `experiments/runs/dual-clock-20261025/tests.log`. Esecuzione client Mac; nessun runtime scientifico sul Mac.

PASS browser integrato1011×1034 e390×844; ora reale09:00:36 distinta da previsione10:00 dopo +1h; successivamente09:03:02 distinta dai dati09:00. Mobile indicatore VM52,7px interamente contenuto entro378px su390; nessun overflow orizzontale osservato. IT/EN verificati e italiano ripristinato. Screenshot locali `reports/dual-clock/{delivery,future,mobile}.png`, esclusi dall’export pubblico.

BLOCKED verifica Safari di questo incremento: Mac bloccato, tentativo di reload non eseguito. Nessuna modifica alle altre schede. NOT RUN nuovi replay fisici/benchmark; presentazione soltanto, gate M0–M7 e FAIL REFlEx invariati.
