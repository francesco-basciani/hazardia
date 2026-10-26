# Terremoti: attivazione e filtri automatici — 26 ottobre 2026

Richiesta: attivando il livello o scegliendo catalogo/periodo/magnitudo, acquisire e mostrare i dati automaticamente. Eliminare il pulsante manuale e rendere leggibili tutte le date visualizzate.

Implementato nel renderer esistente, senza cambiare gli adattatori scientifici o le quote. Checkbox e apertura del livello avviano l’acquisizione. La soglia M≥X filtra subito mappa, conteggi e lista eventi sui dati disponibili. Un catalogo completo con soglia più bassa viene riutilizzato; abbassando la soglia oltre i dati disponibili parte una nuova acquisizione. Una risposta troncata a1000 eventi non è considerata un insieme completo riutilizzabile per una soglia diversa. Cambio periodo/catalogo e vista fuori copertura avviano acquisizioni automatiche. Richieste distanziate secondo i limiti preesistenti; stato di caricamento/errori esplicito, nessun dato inventato o quota aumentata.

Le risposte di selezioni superate non possono sostituire l’ultima richiesta: revisione locale del filtro, richieste serializzate e recupero automatico dell’ultima selezione. Livello disattivato non richiede nuovi dati. Rimane solo il pulsante geografico “Inquadra dati acquisiti”, che non carica dati. Rete elettrica mantiene il proprio flusso manuale e i filtri esistenti.

Date in pannello, finestre dei cataloghi, elenco e dettagli del terremoto: giorno, mese abbreviato, anno, ore:minuti:secondi e fuso Europe/Rome. Esempio “26 ott 2026, 10:59:35 CET”; formato inglese “26 Oct 2026, 10:59:35 CET”. Distinti CET/CEST nell’ora ripetuta del cambio legale. UTC originali, identificativi e archivi immutati; date non valide/non disponibili → trattino. Cambiando lingua si aggiorna anche il formato delle date.

## Verifiche

Base privata bd818df; run privato `quake-auto-20261026`. Revisione dello stesso autore, non indipendente.

- **PASS reale INGV:** attivazione della sola checkbox → LOADING →193 eventi acquisiti senza pulsante manuale. Selezioni immediate M≥0→M≥3→M≥1:193→0→137 marker nel livello acquisito e lista coerente, acquisizione/snapshot invariati (il conteggio include elementi fuori dall’inquadratura). I numeri valgono per l’area/periodo e l’istante della prova, non sono conteggi nazionali costanti.
- **PASS reale:** cambio rapido 24ore→7giorni termina sul periodo7giorni/M≥1; cambio catalogo esplicitoINGV automatico. Dettagli evento47631792: origine 26 ott 2026, 05:19:36 CET e acquisizione 26 ott 2026, 11:00:50 CET. Le stesse date sono visualizzate in inglese senza modificare UTC.
- **PASS adapter test controllato:** moduloUI reale con risposte sintetiche e clock/timer controllati; attivazione, assenza del bottone, filtro sincrono su mappa/lista, nessuna fetch superflua, risposta obsoleta scartata, ultimo periodo rispettato, livello spento senza rete. Non costituisce prova scientifica o live del provider.
- **PASS modelli di visualizzazione:** filtri magnitudo/non finiti/tipo evento, riuso completo/troncato, composizione INGV/USGS, copertura, freschezza e filtri elettrici preservati.
- **PASS date:** italiano/inglese, secondi, fuso Roma, ora ripetuta CET/CEST, mezzanotte, valori mancanti e inputUTC immutati.
- **PASS i18n:** suite bilingue esistente. **PASS VM:**10 test `test_observed_layers.py`.

Comandi: `node tests/web/quake-auto.test.mjs`, `node tests/web/observed-layer-model.test.mjs`, `node tests/web/observed-layer-time.test.mjs`, `node tests/browser/i18n.mjs`; backend nella VM con `PYTHONPATH=src:tests core-env/bin/python -m unittest discover -s tests/web -p test_observed_layers.py`. Log e proveUI nel run privato; screenshot locali `reports/quake-auto/delivery.png` e `event.png`.

La prima asserzione del vecchio test pretendeva un cache-miss alzando la magnitudo: aggiornata alla nuova semantica con controlli negativi per catalogo troncato/soglia più bassa. Non sono state ridotte soglie di performance o promosse qualifiche dei dati. Nuovo profiling30FPS/Safari, replay fisici e disponibilità continua del provider NOT RUN.
