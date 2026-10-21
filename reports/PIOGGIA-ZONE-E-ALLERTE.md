# Monitoraggio: precipitazioni per zona e allerte ufficiali

Incremento `rain-zones-20261021`, 21 ottobre 2026. Reviewer: Codex, self-check. Fonte base privata `6348e530e5959407551ea0e6dea2b6bb75d41780` con modifiche mirate; modifiche documentali/paper preesistenti preservate. Non è chiusura del gate scientifico M5–M7.

## Comportamento disponibile

Nel Monitoraggio, **Pioggia e allerte** apre un pannello sulla mappa. Gli accumuli delle prossime 1/3/6/12/24/48 ore sono calcolati nella VM sulle geometrie ufficiali DPC, usando il campo meteorologico realmente acquisito per la vista. Blu/viola esprimono solo quantità; i bordi gialli/arancioni/rossi riportano il bollettino ufficiale valido all'ora iniziale scelta. Nessun livello idraulico è dedotto da una soglia universale di millimetri. Una quantità ICON bassa non annulla un'allerta DPC: fonti e valutazioni sono indipendenti.

Si può scegliere una zona, leggerne motivi, media areale, estremi dei campioni, copertura e intervalli mancanti; il selettore ordina gli accumuli disponibili, non il rischio umano. La barra meteo governa anche l'ora dell'analisi per zona; le transizioni grafiche al minuto non inventano nuove valutazioni idrauliche. Quando questa vista è aperta, le altre campiture meteo/EFFIS/DPC sono temporaneamente nascoste per evitare colori sovrapposti; si ripristinano chiudendola. Nessun risultato fisico, innesco, risorsa o ottimizzazione è modificato.

## Metodo e limiti

Il campo esistente ha 81 nodi di consultazione e risoluzione variabile con l'inquadratura. Si intersecano le celle con i poligoni e si interpola bilinearmente sul centroide di ciascuna intersezione; media pesata con aree EPSG:6933. Min/max sono **estremi dei campioni**, non veri estremi di tutta la zona. Questa quadratura non sostituisce griglie meteorologiche native, radar o pluviometri. Il passo effettivo del campo e lo snapshot sono esposti. La media può nascondere rovesci locali.

Si sommano solo intervalli orari completi, con corretta semantica normalizzata dell'ora successiva. Probabilità di precipitazione e quantità non vengono confuse. `precipitation` Open-Meteo include pioggia, rovesci e neve in equivalente d'acqua: non è necessariamente pioggia liquida disponibile per deflusso. I valori delle 24 ore precedenti, quando coperti, sono previsioni dello stesso snapshot, non osservazioni o saturazione del suolo.

Geometrie invalide, zona non integralmente coperta o ore mancanti producono UNAVAILABLE, non zero. La classificazione idraulica HAZARDIA rimane **NOT_EVALUABLE**: soglie locali attuali, suolo/saturazione, osservazioni e modello d'impatto non sono qualificati. Le soglie preliminari Abruzzo2014 consultate non sono state attivate come regole correnti o trasferite ad altre regioni. Fonte delle geometrie e validità del bollettino sono separate: si possono riusare confini datati senza prolungare un'allerta scaduta. Nessun algoritmo privato di Allarmeteo è assunto o riprodotto.

## Risultati verificati

| Verifica | Esito | Evidenza |
|---|---|---|
| Totali completi, pioggia/probabilità distinte, intervalli mancanti, geometrie invalide/parziali, integrità archivi, bollettino scaduto o emesso nel futuro, deduplicazione | PASS | 25 test VM, `tests.log`; inclusa equivalenza dei valori riusando il piano spaziale |
| Esecuzioni con fonti reali nella VM | PASS | `timing-after-storage-fix.json`, `delivery-hour-0.json`, `delivery-hour-1.json` |
| Geometrie ufficiali | PASS integrazione | 187 zone nel prodotto acquisito; 44 con intervallo24h e copertura completi nel campo congelato del pilot, non 187 stime garantite |
| Collegamento con bollettino DPC | PASS | Revisione `ba96e9a25d5a2390a46de8f76d627059876aa29d`; bollettino emesso20/10 alle15:21 Roma, prodotto21/10 valido fino22/10 alle00:00 Roma |
| Esempio Aterno | PASS consultazione | Alle09UTC21/10:1,210mm medi nelle successive24h; alle10UTC:1,132mm. DPC gialla per idrogeologico/temporali, nessuna allerta idraulica nel testo. Non è una nuova allerta calcolata da HAZARDIA |
| Nessun nuovo job fisico / nessuna scrittura dei casi | PASS nel checkpoint | 90 directory job, confronto stato API e workspace in `final-api-audit.json`; test UI su scheda separata |
| Recupero cache ufficiale piena | PASS | Compressione lossless272287586→94676706byte;106hash raw identici;67,98s in processo separato, archivio originale logicamente conservato. Aggiornamento fonti riuscito, errore CACHE_FULL rimosso |
| Classificazione autonoma di rischio idraulico, equal-rainfall/different-catchment qualificato, calibrazione/skill | BLOCKED | Prerequisiti territoriali/impatti ancora non qualificati; fullM5–M7 invariati |
| Benchmark p95≥30run, carico prolungato, Safari e smartphone | NOT RUN | Il pilot non li sostituisce |

Pilot prestazionale su un solo campo: la prima variante riarchiviava tutte le geometrie a ogni ora e misurava5,72/7,29s nel worker; il solo riuso delle intersezioni non bastava. Variante consegnata: geometrie congelate condivise e verificate per hash, risultati orari separati, piano spaziale riusato e gzip livello1. Due worker con piano già disponibile: **0,751/0,594s**, richieste submitHTTP0,613/0,798s, archivi orari364546/363985byte più geometria condivisa. Non sono una misura di FPS, un p95 o un confronto scientifico controllato; la prima preparazione di un nuovo dominio resta distinta.

Runtime: LinuxARM64, Python3.10.12,4vCPU, VM esistente8GiB/19GiB. Un worker pioggia alla volta, timeout40s, capacità condivisa e archivio64MiB; nessuna acquisizione esterna dal nuovo servizio, riusa solo le fonti/cache già autorizzate. Ogni richiesta ha snapshot, hash e riferimenti alle geometrie immutabili; i risultati sono leggibili solo dopo receipt finale. Superamento limiti o sorgenti scadute produce un errore esplicito.

Negativi di verifica conservati: `node --check` iniziale eseguito come CommonJS su modulo ES fallito, corretto con `--input-type=module`; selettore etichetta Sfondo non associato e attesa di visibilità del primo tile Leaflet fuori vista non affidabili, verificati via DOM e screenshot. In QA rilevato disallineamento dell'ora iniziale del pannello quando la barra conservava un'ora precedente: apertura/eventi ora prendono il tempo scelto, non l'ora corrente. Nessuna modifica ai simulatori.

## Comandi di verifica

Nella VM, da `/home/hazardia/hazardia-runtime/app`:

```sh
PYTHONPATH=src:tests/unit PROJ_LIB=/usr/share/proj /home/hazardia/m0/reflex-env/bin/python -m unittest test_rain_assessment test_rain_service test_attention test_attention_zones
```

API locale: `POST /api/monitoring/rain` con `{"at":"2026-10-21T09:00:00Z"}` e header `X-Hazardia-Research:1`; risposta accodata con ID, poi `GET /api/monitoring/rain/<id>`. Il POST richiede un'ora coperta e un campo fresco: la data è un esempio congelato, non un comando da rilanciare fuori validità. Nessuna chiamata ai simulatori. I due endpoint non applicano soglie idrauliche implicite. Per riprodurre un archivio occorrono richiesta/receipt, geometria condivisa identificata dal SHA e ambiente geospaziale della VM; non basta il solo screenshot.

Evidenza privata: `experiments/runs/rain-zones-20261021/`, originale VM `runs/rain-zones-20261021/`. Sintesi pubblicabili senza raster/immagini: `reports/rain-zones/`.

Fonti consultate21/10/2026: [DPC, zone di allerta](https://www.protezionecivile.gov.it/it/approfondimento/rischio-meteo-idro--le-zone-di-allerta/), [repository ufficiale bollettini](https://github.com/pcm-dpc/DPC-Bollettini-Criticita-Idrogeologica-Idraulica), [procedura Abruzzo2014, allegatoF](https://bura.regione.abruzzo.it/sites/bura.regione.abruzzo.it/archivio_bura/2014/Allegati/SPE_62_sistema%20di%20allertam%20_%20ALL%20A.pdf), [Open-Meteo, definizione delle variabili](https://open-meteo.com/en/docs).

Prossimo incremento scientificamente verificabile: acquisire/qualificare soglie territoriali correnti e stato antecedente, poi validare il collegamento a impatti idrologici su casi indipendenti. Il presente PASS è consultazione meteorologica più bollettino ufficiale, non un sistema autonomo di allerta idraulica validato.

QA visuale: apertura/chiusura, scelta zona Aterno, durata6h/24h, avanzamento di un'ora e futuro oltre il bollettino verificati nel browser integrato; dopo correzione, pannello13:00Roma e barra11:00UTC coincidono. Viewport osservati1280×720 e974×1034; quest'ultimo con cartografiaOSM caricata e bordi ufficiali. Una wait di UI dopo+1h è scaduta prima della risposta: rilettura successiva ha mostrato l'ora corretta e nessun errore console. Le verifiche visive non sono certificazione Safari/mobile o benchmarkUI.
