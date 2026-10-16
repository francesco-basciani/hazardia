# ADR-0010 — Meteo reale Open-Meteo, cache locale e simulazioni condizionali

16ottobre2026. Decisione: autorizzazione esplicita utente a usare Open-Meteo nel piano gratuito, con mappa e nuove simulazioni nella stessa VM. Normativa: FR-06/07/17/22, FR-MONITOR-01, QR-04/05/06/07/09. Non si sostituiscono PROPAGATOR/HMC/REFlEx né si dichiarano qualificati eventi futuri.

## Fonte, limiti e alternative

[API ufficiale](https://open-meteo.com/en/docs), [condizioni](https://open-meteo.com/en/terms) consultate16ottobre2026: API gratuita non commerciale con limiti10.000/giorno,5.000/ora,600/minuto e300.000/mese; i termini richiedono meno delle soglie. Non è API illimitata, nessun account o endpoint a pagamento. Dati CC BY4.0 con attribuzione. Progetto di ricerca, nessun nuovo uso commerciale autorizzato.

Scelto un punto L’Aquila42.35N13.38E e DWD ICON-EU esplicito per evitare una miscela di modelli non identificata;7variabili orarie per4giorni, nessun ensemble. Sono previsioni puntuali, non una forzante distribuita o un sensore osservato. Le coordinate griglia restituite si conservano accanto al punto richiesto. MET Norway resta alternativa valutata, ma la precedente acquisizione non aveva tutte le variabili necessarie; nessun fallback che inventi i mancanti. ERA5 continua ad essere la fonte distinta degli esempi retrospettivi.

Cache condivisa nel backend VM: nessuna chiamata diretta del browser al provider, lock locale e prenotazione SQLite tra istanze/processi, almeno1800s tra tentativi, massimo48tentativi al giornoUTC, payload256KiB, budget JSON16MiB, nessun retry immediato anche in errore. Un refresh di scheda legge la stessa cache. A budget esaurito o rete guasta conservare dati datati con stato esplicito; simulazioni nuove solo con snapshot FRESH eID corrispondente. Il budget è conservativo per questa singola query piccola; non si generalizza arbitrariamente a multi-punto/ensemble/variabili extra che possono cambiare il conteggio equivalente delle API.

## Versionamento e tempi

Schema richiesta/weather0.3.0 aggiunge modo RESEARCH_FORECAST e prova raw weather_raw. I vecchi0.2.0 restano retrospettivi e i forecast0.2 richiedono issued_at valido; non sono migrati o riscritti. Il provider non espone nell’endpoint standard l’inizializzazione dello specifico run: `issued_at=null`, `issued_at_status=UNKNOWN_PROVIDER`; acquisizione e prima disponibilità osservata sono campi separati. Non rinominare generationtime_ms o la dataHTTP come emissione modello. Nessuna pretesa di conoscere la disponibilità prima della prima acquisizione.

La documentazione descrive pioggia come somma dell’ora precedente e radiazione come media dell’ora precedente: la normalizzazione a inizio intervallo t usa i valori del record grezzo t+1h per questi due campi, mantenendo vento/temperatura/umidità/pressione all’istante t. Ultima riga senza successiva esclusa. Nessuna interpolazione/zero-fill di variabili mancanti. I nuovi run partono da oreUTC future complete e richiedono copertura integrale; lo storico2024 non è sovrascritto con meteo2026.

## Consumo nei modelli

PROPAGATOR: m/s→km/h, vento previsto all’inizio mantenuto costante per10/30/60min, direzione FROM; umidità del combustibile e combustibile/innesco restano ipotetici, non trasformati dall’umidità dell’aria.

HMC: precipitazione prevista invariata, temperatura/vento/umidità/radiazione/pressione nei file di forcing; pressione del contratto hPa→kPa richiesti dal lettore nativo. Il vecchio adapter passava hPa e HMC li clampava al default101.3kPa, poi correggeva daDEM: errore di mapping individuato con log reale e corretto senza cambiare upstream. I vecchi artefatti sono preservati, non dichiarati rigenerati identici. Soil/cold-start/Q0, evapotraspirazione esterna di ricerca, neve/bilancio energetico disabilitati restano assunzioni; questa non è una previsione idraulica certificata, né una validazione del forcing distribuito. Precipitazione totale trattata nel modello di ricerca senza calibrazione nivale: nessuna capacità validata su neve.

REFlEx: conservare la sua soglia originale minimum_volume_included1m³ e arrotondamento del volume triangolare. Una tabella ottimizzatori vuota può essere un esito nativo valido solo se nessun reach supera la soglia e il raster nativo contiene celle valide tutte zero. Se c’è runoff eleggibile, NaN, raster vuoto/nonzero incoerente, resta INVALID_OUTPUT. Non aggiungere pioggia, alzare Q o produrre una sagoma artificiale per mostrare un’alluvione. Il primo run rifiutato resta prova negativa; una verifica corretta del caso asciutto non stabilisce sicurezza sul territorio.

## Interfaccia e sicurezza

Livello Meteo distinto da Incendi/Alluvioni; un marker puntuale e selezione oraria su più giorni, unità/data/fonte/cache. Pulsante Simula con queste previsioni apre il builder, senza avviare job automaticamente. Conferma tramite Avvia simulazione; job isolati con stessi limiti/cancel/retry e manifest. Risultati etichettati METEO REALE e sempre non calibrati; vecchi casi STORICO. Il confronto congiunto usa prodotti con stesso hash meteo e almeno10min di finestra comune; i layer liberamente sovrapposti del monitoraggio non diventano causalmente confrontabili. Allerte sintetiche restano nel laboratorio; nessun watcher di allerta reale o dispatch introdotto.

## Verifica ed esternalità

Esiti eseguiti e versioni finali in reports/METEO-REALE.md/CHECKLIST e run openmeteo-20261016T060251Z. Dati/risposte grezze, richieste, schema, codice, seed, campioni e output devono rimanere referenziati perhash. Prove software/tecniche non valgono H1–H3, efficacia, calibrazione idrologica o indipendenza dei dati. Nuove acquisizioni soggette ai limiti esistenti5GiB/19GiB/8GiB/4vCPU. Nessun modello aggiuntivo, chiave privata, spesa, servizio pubblico o decisione operativa.
