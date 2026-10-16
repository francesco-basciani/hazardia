# Open-Meteo reale nella mappa e nei nuovi run CIMA

16ottobre2026. Run `openmeteo-20261016T060251Z`; reviewer Codex self-check. [ADR-0010](ADR-0010-openmeteo-forecast.md), [verifiche misurate](weather/verification.json). Runtime unico nella VM UTM Ubuntu22.04ARM64. I simulatori sono gli stessi approvati, nessuna nuova installazione o servizio a pagamento.

## Cosa puoi provare

1. Apri http://127.0.0.1:8080/ . Attiva **Meteo**: marker puntuale sull’Aquila e pannello **Previsioni reali · Open-Meteo**. Scegli un’ora nei prossimi giorni per leggere temperatura, vento/direzione, umidità, pioggia, pressione e radiazione.
2. Premi **Simula con queste previsioni**: si apre la sezione decisioni, con il nuovo calcolo CIMA e la fonteFORECAST già selezionata. Scegli ora futura e modello, poi **Avvia simulazione**. Incendio10/30/60min; alluvione6h. Non sono supportati giorni generali da questo builder: il laboratorio incendio72h resta distinto.
3. Consulta il nuovo risultato nel selettore di ciascun pericolo. È marcato **METEO REALE**, con condizioni di ignizione/combustibile/umidità/soil/Q0 ancora ipotetiche. I vecchi casi sono **STORICO**; il meteo corrente non li modifica. I risultati restano legati allo snapshot accettato e non si ricalcolano automaticamente dopo una nuova acquisizione.

Previsioni per un punto, non un raster meteorologico dell’intero Abruzzo né sensori osservati. Coordinate richieste42.350,13.380; griglia restituita42.375,13.375, quota621m. Ortofoto2018–2019 e Sentinel2024 restano sfondi datati. Il replay allerte è ancora sintetico e separato.

## Fonte reale e gratuità

Acquisizione VM effettiva **16ottobre2026 alle08:07:25ora Roma/Berlino** (`2026-10-16T06:07:25.320904Z`), DWD ICON-EU via Open-Meteo. Risposta 5464B, SHA256`3772e6d2a363b7de18914f1ab484893107b02380178e3fa7206ab0d415c8adaa`;96record grezzi,95intervalli normalizzati,4giorni richiesti e selezioneUI di almeno72ore disponibili al primo controllo. Il provider non fornisce nell’endpoint standard l’istante d’inizializzazione del run: emissioneUNKNOWN esplicita, non inventata dalla dataHTTP o dal tempo di calcolo.

[Documentazione API](https://open-meteo.com/en/docs) e [condizioni gratuite](https://open-meteo.com/en/terms) consultate16ottobre2026. Attribuzione/CC BY4.0 visibili. Endpoint pubblico non commerciale senza chiave, nessun account/API a pagamento. Cache VM condivisa: minimo30min tra tentativi, massimo48tentativi/giornoUTC,256KiB/risposta e16MiBJSON. Prenotazione persistente SQLite e lock impediscono moltiplicazioni tra schede/processi. Dopo il collaudo: **1sola richiesta al provider** per questo connettore; trasferimento dello snapshot e del contatore al runtime8080 senza nuovo fetch. Le chiamate browser sono solo al backend locale. Limiti interni conservativi per questa query, non una promessa di API illimitata né autorizzazione all’uso commerciale.

Cache scaduta/rete assente: dati precedenti consultabili con etichettaSTALE; nuove simulazioni bloccate finché non c’è uno snapshot fresco e integro conID corrispondente. Dati grezzi, receipt e normalizzazione rehashati/confrontati; mancanze, unità errate e orari incongruenti rifiutati.

## Nuove simulazioni effettive

Scelta fissata prima della prima prova: prima oraUTC futura completa dopo acquisizione, **16ottobre2026 ore09:00Roma**, indipendentemente dalla pioggia prevista o dal risultato;seed1729, incendio60min, alluvione6h. Stessi input ipotetici dichiarati, nessuna pioggia aggiunta per generare una sagoma.

| Prova | Esito | Evidenza |
|---|---|---|
| Primo FIRE nel prefisso di collaudo | PASS | job-70c75dd5bfab46a1ab445375cb478d0b, vento previsto nativo,31celle positive |
| Primo FLOOD nel prefisso di collaudo | FAIL | job-cff1de0ab68e4a59bd14779579bccf60; checker precedente rifiutava tabella ottimizzatori vuota; raster nativo zero già presente, log originali conservati |
| FIRE avviato dal browser sul runtime8080 | PASS | job-0ccb4d49371045b1af281486b40fa49e,09:00–10:00Roma,31celle positive, output probabilità/arrivo effettivi |
| HMC→REFlEx avviato dal browser sul runtime8080 | PASS | job-a91721608c7d49d6889190ec94ee4c77,09:00–15:00Roma,6output HMC,REFlEx0–4 eseguito,nativo21025celle valide tuttezero |
| Lettura indipendente e conversioni | PASS |29asserzioni: contratti,CRS/griglie/hash,raw,vento m/s→km/h,7file di forcing pioggia invariata epressione hPa→kPa,145hash motori immutati |

Nel caso alluvionale i7campioni di pioggia sono0mm. HMC produce solo portate numericamente piccolissime; dopo il calcolo/arrotondamento triangolare nativo, tutti i volumi sono sotto la soglia REFlEx già fissata a1m³. La sua tabella ottimizzatori è vuota e il **raster nativo** è zero: non abbiamo fabbricato una mappa vuota né cambiato la soglia o la pioggia. `mapping_status=NO_INCLUDED_RUNOFF_VOLUME`,step4eseguito=True. Questo significa nessun allagamento mappato nel modello di ricerca/soglia scelti, non assenza garantita di pericolo reale.

## Correzioni e risultati negativi conservati

- Il controllo originale rifiutava ogni tabella vuota. Corretto solo il caso verificabile con0reach eleggibili e raster nativo valido/finito/tuttozero. Se c’è runoff eleggibile, celle mancanti, NaN o profondità incoerente, restaINVALID_OUTPUT. Test positivi/negativi e nuovo run completo, senza sovrascrivere il fallimento.
- Il log HMC ha evidenziato la precedente pressione in hPa fuori dal range nativo kPa, con default interno daDEM. Adapter corretto dividendo per10. I7file del nuovo run contengono i valori previsti in kPa e il warning del default non compare. Correzione post-fallimento dichiarata; vecchi output non riscritti e ripetibilità bitwise su codice corretto non presunta.
- Il primo test di regressione monitor aveva l’anno2024 fisso: FAIL con un nuovo caso2026. Asserzione corretta per date complete reali, non soglia rilassata.
- Revisione visuale ha trovato che il catalogo inizialmente non propagava mode/weather, marcando STORICO un output nativoFORECAST. Builder corretto, cataloghi rigenerati solo da prodotti esistenti, verifica browser aggiunta; i nuovi casi sono oraMETEO REALE. Nessuna fisica rilanciata per correggere un’etichetta.

Le correzioni dopo osservazione sono pilot engineering, non esperimento held-out. Il primo piano è nel run prima dell’acquisizione; il suo generatore ha riusato la chiave source perURL, sovrascrivendo il campoSHA iniziale: piano originale conservato, identità ricostruita da bundle/manifests delle esecuzioni e correzione source-provenance-correction.json, senza dichiarare quel campo preregistrato; i rimedi e la ripetizione corretta sono esplicitamente successivi. Nessuna H1–H3, misura di accuratezza, calibrazione o capacità operativa stabilita.

## Test e runtime finale

**97test software PASS** (50unit,19dominio,14decisione,14web); **70controlli browser PASS** (26meteo+44monitor),18scansioni axe con0violazioni a375/768/1440,raw incompletes conservati. Browser155.0.8059.84. Test meteo includono più schede/refresh senza nuove chiamate esterne, cacheconcorrenza/quota/errore/unità/tempi/corruzione, IDobsoleto e divieto query arbitrarie. Il test della mappa non avvia job; le due nuove richieste fisiche sono state inviate esplicitamente dalla UI e verificate a completamento. Ricostruzioni app/schema normalizzati e metadati: source3788874→5453ac5→acba68e; native corretto da840d7; cache5a06668; attribuzionea25b05b; catalogo19f81da; correzione harnessde0041a. Nessuna equivalenza tra sola versioneGit e prova di tutti i gate.

Backend/scienza/acquisizione nella VM, browser sul Mac. Il riavvio finale controllato preserva813fileJSON di stato preesistenti; primo handover ne preservava810 e aggiungeva solo la cache meteo. Servizio8080 disponibile, server/tunnel temporanei8081 chiusi. Download conservativo finale3640858902B/5368709120B, spazio libero guest9271984128B;4vCPU/8GiB/19GiB invariati. Nessuna installazione privilegiata, spesa, servizio pubblico o azione operativa.

## Ripetere e limiti rimasti

La guida di installazione/bootstrap esistente include il codice standard-library necessario: nessun pacchetto aggiuntivo. Dal servizio locale, GET `/api/weather` legge la cache; POST `/api/weather/refresh` conJSONvuoto e header same-origin avvia un fetch limitato; POST `/api/jobs` accetta `weather_source=FORECAST`, `forecast_id`, `start_at` UTCfuturo, hazard e parametri già limitati. Nuove prove richiedono nuovi percorsi/ID; una futura acquisizione non può riprodurre lo stesso tempo atmosferico, usare lo snapshot immutabile salvato per replay. Test `tests/unit/test_forecast.py`, `tests/browser/weather.cjs`, `tests/browser/monitoring.cjs`. Raw e manifest in `experiments/runs/openmeteo-20261016T060251Z` e nelle directory jobs della VM; hash in verification.json.

NOT RUN/BLOCKED: ensemble meteorologici, forcing distribuito/calibrazione bacino, snow/energybalance qualificati, watcher allerte d’impatto reali, casi storici e skill indipendente, nuovi interventi fisici alluvionali, giorni generali, nuova sessione30min/100kstress e rilascio scientifico completo. FR-06 restaBLOCKED nella sua accettazione integrale; FR-WX-REAL-01 èPASS nel perimetro di previsione puntuale e nuove simulazioni condizionali.


## Livelli meteo attivabili sulla mappa

Run `weather-layers-20261016T063635Z`, codice `b4dc8e5f139ee5dca4aff12ce8887758d1faa49c`. Nella scheda meteo puoi scegliere **vento**, **temperatura** e **pioggia nell’ora**, separatamente. «Meteo» sopra la mappa nasconde tutto mantenendo le scelte; «Centra il punto meteo» inquadra il punto della griglia. L’ora selezionata aggiorna la sovrapposizione. La freccia indica dove soffia il vento; il numero in gradi indica da dove proviene. Il simbolo è ora ancorato al punto effettivo restituito dal modello, invece che alle coordinate richieste.

PASS36controlli browser e6scansioni axe senza violazioni su375/768/1440, comprese viste di confronto, nessun job dai comandi cartografici e nessuna chiamata browser al provider. Dati e servizio restano nella VM; aggiornati solo4file statici, senza riavviare backend o motori. [Verifica](weather/layers-verification.json).

**Copertura:** un punto della griglia vicino all’Aquila. Non è ancora una mappa continua del vento/pioggia sull’Abruzzo. Per quella servono dati distribuiti; non sono stati inventati o ripetuti valori puntuali su tutto il territorio. Nuove simulazioni e nuove prove di stabilità prolungata NOT RUN in questo incremento.
