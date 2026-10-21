# Monitoraggio: prima integrazione di pioggia osservata

Run `observed-rain-20261021`, iniziato 21 ottobre 2026 UTC e terminato 22 ottobre ora italiana. Parent `44bc591c434457de24f60cae46c8aa71b8302c0a` + modifiche focalizzate; commit di consegna nella cronologia Git/PUBLICATION.json. Reviewer: Codex, self-check. Documentazione del paper già modificata da un altro lavoro preservata e non inclusa nel commit.

## Risultato visibile

Ricaricare la dashboard, aprire **Monitoraggio → Pioggia e allerte → Mostra le misure delle stazioni**. I cerchi rappresentano singoli pluviometri: quantità misurata nell’ora precedente il timestamp, nome/codice, rete, intervallo Roma/UTC, età, controllo della fonte e licenza. Il menu «Esamina stazione» consente l’accesso anche senza cliccare un piccolo punto. Punti diradati su celle di 36 px, precedenza agli accumuli maggiori, massimo 350: conteggio mostrato/totale esplicito. Nessuna interpolazione areale delle osservazioni.

Previsioni Open-Meteo/ICON per zona e bollettini ufficiali DPC rimangono distinti. Il cursore futuro non genera osservazioni: compare «osservazioni non ancora disponibili». Dei dati già acquisiti si mostrano soltanto quelli con termine non successivo all’ora scelta e nelle due ore precedenti. Non è un archivio storico completo: lo snapshot contiene l’ultima misura restituita per sensore, non tutte le misure passate. Misure oltre 90 minuti: tratteggio/stato vecchio; acquisizione oltre 90 minuti: cache scaduta. L’assenza di sensori o dati non diventa zero pioggia.

## Fonti e decisione di integrazione

- **Adottata:** [ItaliaMeteo, catalogo delle osservazioni](https://dati.agenziaitaliameteo.it/dataset/osservazioni-idro-meteo-stazioni-al-suolo), [mappa pubblica MeteoHub](https://meteohub.agenziaitaliameteo.it/app/maps/observations). Il catalogo attribuisce le osservazioni con licenza CC BY; i dettagli per rete sono acquisiti da `GET /api/datasets?licenceSpecs=true`. Si accettano soltanto dataset pubblici del gruppo `CCBY_COMPLIANT`, con CC BY 4.0 e attribuzione esplicite. Reti regionali e rete amatoriale MeteoNetwork sono identificate separatamente.
- **Accesso:** stesso GET anonimo della mappa pubblica, senza credenziali, tramite `/api/observations`. La [guida](https://meteohub.agenziaitaliameteo.it/ui/user-guide) esclude la pioggia dai comandi di esportazione della mappa; nessun POST di esportazione o servizio autenticato è stato usato. Il normale GET di visualizzazione restituisce la pioggia. Codice pubblico del frontend letto come documentazione, mai eseguito. L’endpoint può cambiare: schema/unità/licenza inattesi bloccano l’aggiornamento.
- **Semantica verificata nel frontend pubblico e nel payload:** `product:B13011;timerange:1,0,3600;level:1,0,0,0`, `last=true`, `reliabilityCheck=true`. Unità `KG/M**2`, equivalente a mm di acqua; accumulo nell’ora precedente, anche neve equivalente. Timestamp senza offset interpretato UTC come nel frontend della fonte. Si accettano soltanto valori finiti non negativi e `rel=1`; quest’ultimo non è una validazione scientifica. Sentinel/trace negativi non diventano zero. Nessuna somma di contatori cumulativi. Il parametro `bounding_box` della prima prova non ha ristretto la risposta: il connettore acquisisce esplicitamente il prodotto nazionale limitato a 2 MiB e filtra i punti nell’inquadratura solo per la visualizzazione, senza moltiplicare le richieste.
- **Non adottata per il monitoraggio corrente:** [portale idrografico regionale](https://protezionecivile.regione.abruzzo.it/dati-della-rete-regionale-in-telemisura-online-il-nuovo-portale/), che dichiara 15 giorni di ritardo per l’accesso pubblico. Gli accessi fiduciari richiedono login. AgroAmbiente Abruzzo espone un catalogo pubblico, ma i diritti di riuso delle misure non sono stati risolti: nessuna integrazione di quei dati. NOAA/DWD valutate come alternative, non acquisite in questo run.

## Acquisizione e ripetibilità

Tutto il backend, acquisizione e replay eseguiti nella VM Linux aarch64, kernel 5.15.0-198-generic, Python 3.10.12; 4 vCPU/8 GiB, disco VM 19 GiB. Nessuna installazione, sudo, servizio a pagamento o deployment pubblico. Mac impiegato per sviluppo, browser e copia delle evidenze.

Snapshot reale acquisito `2026-10-21T21:58:10.636014Z`, ID `observed-1244e935ebf10d23dfe5b9cd`:

- SHA-256 dati `1244e935ebf10d23dfe5b9cd369c6b6107f0e0ce1caec65d8e127cd4214b3da9`.
- SHA-256 catalogo/licenze `6be3e371e55b3439a05df9807c04992c55e7389383dd16edb94f7c215a6432c3`.
- 4.068 stazioni normalizzate. Nel bbox lon 13–14,9 / lat 41,6–43: 115, di cui 37 MeteoNetwork, 37 Lazio, 21 Marche, 16 Molise, 4 Umbria. **È un riquadro geografico, non il conteggio amministrativo dell’Abruzzo.** Non è presente una rete regionale Abruzzo dedicata nel catalogo osservato. Copertura del sensore, proprietà della rete e copertura di una regione sono concetti distinti.
- Esempio verificato anche nella UI: `abr133`, 0,3 mm tra 20:00 e 21:00 UTC (22–23 Roma), rete MeteoNetwork. Non viene attribuito un nome di località inventato al codice.

Stato persistente: `web-state/observed-rain/`, raw gzip immutabili e ricevute con hash, catalogo originale gzip, ultimo prodotto normalizzato. Richiesta HTTP di lettura senza acquisizione; refresh asincrono, una richiesta condivisa/ora al massimo e catalogo ogni 24 h. Limiti persistenti: 2 MiB/risposta, 64 MiB cumulativi riservati anche sui fallimenti, 64 snapshot. Il superamento blocca nuovi download conservando dati e orari precedenti; non azzerare contatori o cancellare evidenze automaticamente. Il refresh ripetuto dal browser riusa la cache, senza richiamare la fonte durante pan/zoom. Primo aggiornamento runtime: 827.440 byte, catalogo incluso. Discovery iniziale separata, 7.511.816 byte conservati nei file `.raw`, entro il limite di lettura di 20 MiB; un singolo JS pubblico completo da 4,08 MB autorizzato dal protocollo emendato prima del download, dopo troncamento della lettura iniziale a 2 MiB.

Comandi nella VM, dalla directory dell’app:

```sh
PYTHONPATH=src:tests/unit ../core-env/bin/python -m unittest test_observed_rain test_rain_service test_rain_assessment test_attention_zones -v
PYTHONPATH=src ../core-env/bin/python scripts/verify_observed_rain.py /home/hazardia/hazardia-runtime
```

API locali: `POST /api/monitoring/observed-rain/refresh` con `{}` e intestazione `X-Hazardia-Research: 1`; `GET /api/monitoring/observed-rain`. Nessun URL di fonte, prodotto, licenza o orario arbitrario ammesso nel POST. Le risposte raggruppano i metadati comuni nel dizionario `data.networks`; ogni punto lo riferisce tramite `properties.network`. Lo snapshot scientifico mantiene gli attributi completi.

## Esiti e limiti

| Verifica | Esito | Evidenza |
|---|---|---|
| Acquisizione pubblica reale e attribuzioni CC BY 4.0 | PASS | raw/ricevute nel run, verifica hash del catalogo e delle osservazioni |
| Replay normalizzazione esatto dello snapshot congelato | PASS | `reports/observed-rain/verification.json` |
| 36 test VM, inclusi 13 osservazioni e regressioni pioggia/zone | PASS | `tests-compact.log`; unità, qualità, licenza, coordinate, tempo, trace, cache, quota e deduplicazione |
| 14 controlli Node della serie oraria esistente | PASS | comando `node tests/browser/rain-series.mjs`, output conservato nella sessione |
| UI reale: punti, quantità/intervallo/fonte/licenza, selezione accessibile, legenda unica, toggle e ora futura | PASS | `reports/observed-rain/ui.json`, screenshot |
| API calda, 30 letture snapshot nazionale dopo compattazione | PASS | p50 152,8 ms, p95 233,2 ms, max 471,2 ms; soglia QR-12 p95≤500 ms, non benchmark dell’intera piattaforma |
| 145 file motori, 8 file workspace/casi, 90 job preesistenti | PASS | hash e conteggi preservati; riavvii a coda inattiva, nessun job interrotto |
| Nuova qualifica di soglie locali, rischio idraulico e skill allerta | BLOCKED | mancano soglie locali qualificate, suolo/bacino e validazione; nessuna allerta derivata solo dai mm |
| Misure regionali Abruzzo complete/ufficiali correnti | BLOCKED | catalogo senza rete regionale dedicata; ritardo/accesso/diritti delle alternative |
| Assimilazione delle nuove misure nei simulatori | NOT RUN | questa integrazione riguarda Monitoraggio; nessun run PROPAGATOR/HMC né skill nuova |
| Nuovi test di dispositivi fisici, FPS/p95 interazioni, soak e copertura mondiale | NOT RUN | verifica UI desktop IAB 1280×720; nessuna equivalenza a piena chiusura QR-11–14 |

Fallimenti conservati: primo GET privo del gruppo licenza → HTTP 400; prima lettura JS troncata a 2 MiB; primo test con timestamp artificiale fuori dal range datetime → errore del test, corretto a tempo corrente; prima UI con import della legenda privo del medesimo suffisso di versione → doppia legenda, corretta; una verifica HTTP ha superato 3 s e una richiesta browser è scaduta durante un rallentamento (load VM 4,20, causa non provata). Una serie successiva prima della compattazione ha dato p95 556,9 ms: **FAIL QR-12**, sebbene il controllo di replay di quel vecchio script riportasse PASS. Conservato `verification-before-compact.json`; il PASS del replay non deve essere interpretato come PASS prestazionale. Compattazione dei metadati ripetuti e cache in memoria dell’ultimo file → nuova serie riportata sopra. Nessun risultato negativo cancellato né target rilassato.

M5–M7 completi e rilascio scientifico restano BLOCKED. Nessuna inferenza di efficacia operativa, rischio validato o novità scientifica. Prossimo incremento: qualificare e confrontare osservazioni/previsioni su intervalli e coperture comparabili, con dati territoriali/idrologici e soglie locali documentate, prima di aggiungere indicatori automatici di rischio.
