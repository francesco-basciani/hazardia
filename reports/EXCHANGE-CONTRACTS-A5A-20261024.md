# A5a — confine generico di scambio e adapter compatibili

24 ottobre 2026 · run `exchange-contracts-20261024` · baseline privata `a146c3c`, pubblica `1bd2171`. L’utente autorizza i punti 1/2: indipendenza dai domini e contratti di interoperabilità, preservando i componenti esistenti. Reviewer: Codex self-check. Questo incremento copre prodotti grigliati e compatibilità, non riscrive l’intero framework o il manoscritto.

## Implementazione

PASS tecnico: nuovo kernel `hazardia.exchange` senza enum di hazard, contratti prodotto/requisito versionati con identificativi di dominio/quantità opachi. Controlla unità, riferimento spaziale, griglia, asse, finestra temporale, disponibilità/cutoff/freshness, origine/qualifica, incertezza e obblighi di calibrazione/licenza. Risultati COMPATIBLE/INCOMPATIBLE/UNKNOWN; nessuna conversione, interpolazione o esecuzione implicita. Hash e contenimento dei percorsi verificati soltanto quando è fornita la root; il risultato lo dichiara. Compatibilità dei metadati distinta da validità fisica e autorità operativa, sempre false.

`hazardia.contracts` è ora una facciata compatibile; i validator/migration legacy sono collocati in `adapters/legacy_contracts.py`. AST dei sette corpi funzione identici alla baseline, cambia solo la risoluzione della stessa cartella schemi. I vecchi nomi/firme/versioni restano disponibili; nuovi nomi espongono il kernel generico. Schemi legacy congelati: nessun allargamento permissivo degli enum negli ingressi storici.

L’adapter `legacy_exchange.py` contiene tutta l’interpretazione FIRE/FLOOD del nuovo confine. La pipeline aggiunge `exchange-product.json` a esecuzioni nuove dopo guard pre/post e comandi nativi invariati; JobStore ne conserva l’hash senza modifica al manifest schema. Licenza aggregata/calibrazione restano UNKNOWN; la disponibilità è esplicitamente fornita dalle nuove esecuzioni, sconosciuta per esportazioni storiche prive di prova. Dati, serie temporali, scenari e originali non vengono riscritti. Il nuovo formato descrive il prodotto finale, non ancora tutti i frame.

## Esiti verificabili

| Attività | Esito | Prova |
|---|---|---|
| Dominio/quantità non predefiniti, unità anche negative, nessuna mutazione | PASS | Fixture sintetica di temperatura, non nuova fonte/modello; kernel senza nomi FIRE/FLOOD o import scientifici |
| Unità/CRS/griglie/supporto/origine/qualifica errati, dati futuri/scaduti | PASS | Rifiuto esplicito senza conversioni, massimi/cumulati non riutilizzati per finestre diverse |
| Unknown licenza/calibrazione/datum/disponibilità/membri | PASS | UNKNOWN quando il consumatore lo richiede; N/A solo se esplicitamente ammesso, ispezione CLI elenca gli ignoti |
| Integrità, path escape, NaN, duplicati, campi ignoti e schemi locali | PASS | SHA/path, JSON finito e limiti, rifiuto ref esterni/ciclici senza rete |
| Regressioni VM | PASS | 231unit + 47web + 60decision + 19domain = 357test, 19 nuovi; 11suiteJS |
| Legacy adapter/facciata | PASS | Funzioni AST equivalenti, vecchi errori/alias invariati, viste non distruttive, sidecar esclusivo, errore metadata classificato dopo comandi nativi |
| PROPAGATOR 600s | PASS | JobStore reale isolato; array probability/fire/arrival e raster identici; anche nuova prova dopo facciata/risoluzione locale |
| PROPAGATOR72h/2risorse | PASS | JobStore reale, prodotti finali e tutti i frame identici; dati meteo/azioni congelati |
| HMC→REFlEx6h | PASS esecuzione/validator | JobStore SUCCEEDED, portate/bridge HMC identici, nuova busta verificata |
| REFlEx replay esatto | **FAIL** | 80celle con scarti≤7,4505806e-9m, maschera e massimo uguali; variabilità preesistente, nessuna tolleranza o RNG modificati |
| Pubblicazione nuovo documento | PASS | Tre job nativi con sidecar, SHA nel manifest, metadati equivalenti a vista del raw; unità errate INCOMPATIBLE/licenza necessaria ignota UNKNOWN |
| Wheel offline + CLI da wheel estratto | PASS | Nuovi moduli/schemi inclusi; hash verificati su prodotto reale; nessuna installazione/download |
| Conservazione | PASS | 311file/95job/145enginehash invariati, servizioRUNNING; 28file legacy schema/worker/decision/API invariati |
| Migrazione scenari, ingresso job generico, composizione automatica, nuovi hazard | NOT RUN | Non implementati, nessuna abilitazione nominale |
| NuovaVM/browserinterattivo/qualificazione scientifica | NOT RUN / BLOCKED | VM/browser NOT RUN; gateM5–M7 BLOCKED invariati |

Le prove native usano un nuovo JobStore per caso in `runs/exchange-contracts-20261024-native`, separato da quello della dashboard; non sostituiscono il DB o workspace dell’utente. Le fixture byte sintetiche dei test unitari non sono prove CIMA. Raw/archive e output numerici restano collegati da SHA; il kernel non interpreta le celle né certifica le fonti.

## Prestazioni

Pilot30ripetizioni per ciascuno dei tre prodotti nativi congelati, stesso processo caldo e VM6vCPU/16GiB, attività di background non eliminata, cache non svuotate. Dimensioni dei documenti:5094B FIRE,4239B FLOOD,6118B studio. Esportazione legacy con validazione/hash: p95 2,276ms/1,715ms/27,257ms rispettivamente. Compatibilità con hash: p95 1,343ms/1,133ms/8,283ms. RSS massimo dell’intero processo circa38,8MB, non incremento di memoria attribuibile alla sola funzione. Nessun claim FPS, p95 del framework o nuovo gate di deadline chiuso; dati completi in benchmark.json. Nessun aumento risorse necessario/dimostrato.

## Risultati negativi e validità

Un primo test di scansione source legge quattro file AppleDouble `._*.py` generati dal tar macOS: rimossi solo quei file temporanei dopo verifica della firma, trasferimenti successivi con COPYFILE_DISABLE=1 o git archive. Nessuna modifica alle regole del test per ignorare sorgenti illeggibili.

Deduplicando gli schemi con riferimenti locali, jsonschema3.2 della VM fallisce nel risolvere frammenti sotto ID URN (nessuna connessione remota riuscita). Correzione esplicita: espansione limitata alle definizioni locali, rifiuto di riferimenti esterni/mancanti/ciclici e prova offline. Suite e dati nativi rivalidati, nessuna libreria installata o rete richiesta. Log iniziali conservati separatamente.

L’uguaglianza esatta REFlEx rimane FAIL; l’inizializzazione casuale upstream era già documentata. L’assenza di differenze nelle maschere non prova equivalenza fisica o calibrazione. UNKNOWN può essere accettato soltanto dove il consumer dichiara di non richiederlo: un metadata match non equivale a autorizzazione o compatibilità fisica di due modelli. Il nuovo formato non esprime ancora tutte le geometrie/procedure/serie, e gli ingressi dei job/decisioni restano i percorsi legacy recensiti.

## Riproduzione e prossimi confini

Guida `docs/EXCHANGE-CONTRACTS.md`; script `tests/integration/verify_exchange_runtime.py` e `benchmark_exchange.py`. Artefatti redistribuibili `reports/exchange-contracts/{verification,native,facade-native,benchmark,preservation,source-boundaries,client-tests}.json`; raw host `experiments/runs/exchange-contracts-20261024`; VM `runs/exchange-contracts-20261024-{native,facade,benchmark-final,wheel}`. Protocolli con input/runtime/source SHA e ipotesi scritti prima delle esecuzioni, output esclusivi.

A5a completato nel perimetro dichiarato: nucleo di scambio indipendente dai domini e integrazione con i due adapter. Non tutta l’ammissione/esecuzione della piattaforma è già generica. Ingressi generici per modelli approvati e composizione con binding semantici sono incrementi successivi; gli enum legacy rimangono negli adapter/schemi storici per non alterare gli archivi. Migrazione completa di workspace e nuovi modelli richiedono bisogno concreto e prove dedicate. Rollback sorgente/deploy A4, senza cancellare sidecar/risultati storici; tag stabile invariato.
