# M2 — Dati territoriali, eventi e conseguenze

**PASS tecnico, 15 ottobre 2026**, run `m2-domain-20261015T190836Z`. Autorizzazione: «Ok andiamo avanti», dopo consegna M1 e indicazione M2 come prossimo passo. M3 non avviata. Reviewer Codex self-check, nessuna revisione scientifica esterna. Tutte le esecuzioni nella VM Linux esistente4vCPU/8GiB/19GiB; nessuna installazione, acquisizione remota o servizio nuovo.

Ora le mappe di M1 hanno un livello condiviso per territorio, osservazioni/eventi, meteo, punti esposti, strade, risorse e interventi. Questo prepara gli input del futuro motore decisionale; non sceglie interventi e non autorizza operazioni.

| Incremento | Esito | Esecuzione osservata |
|---|---|---|
| M2.1 profili/versioni | PASS | Abruzzo/L'Aquila e Senegal sintetico, CRS/fusi diversi, stesso codice di snapshot/eventi; versioni0.4.0, precedenti immutate |
| M2.2 associazione/qualità | PASS | Duplicati rimossi, conflitti conservati, casi ambigui non fusi; dati futuri/scaduti/parziali esclusi; replay indipendente dall'ordine |
| M2.3 ensemble | PASS (contratto) | Membri/unita/tempi/pesi verificati, forecast sintetico distinto da ERA5 reale normalizzato come reanalisi; nessuna previsione storica inventata |
| M2.4 effetti | PASS (semantica) | Entrambi i raster CIMA reali riletti; esposizione sintetica30→25 con5evacuati, SHA del raster identico; effetti fisici/ignoti non supportati respinti |
| M2.5 esposizione/accessibilità/risorse | PASS (input) | Fuori griglia/NoData/popolazione ignota non sicuri per default; risorse incomplete respinte, strada chiusa/carico/turno/scadenza/autonomia controllati |
| M2.6 replay/negativi | PASS |19test M2,33regressioni M1,5verifiche d'integrazione; CLIvalidate/events/window eseguita |
| Estensione M2 di AT-EXT-03 | PASS limitato | Normalizzazione meteo e snapshot/eventi separati dai simulatori; codice M1 immutato. Decision-core replacement M3 NOT RUN |
| Modelli empirici locali/risorse reali | BLOCKED | Nessuna calibrazione/efficacia dimostrata o inventario operativo qualificato |
| Solver, dashboard, allerte,60s/p95,H1–H3 | NOT RUN | M3–M7 restano future milestone |

## Implementazione e utilizzo

`src/hazardia/domain/`: contracts/state/events/consequences/geo e CLI. `profiles/research/`: due profili dichiarati di ricerca; dati demografici/stradali/risorse/detezioni dei test sono **sintetici**, non ricavati da Sentinel. Coordinate dei punti di esposizione di integrazione selezionate intenzionalmente in tre celle positive di ciascun raster M1 per verificare il caso positivo; non campionamento di popolazione reale. La reanalisi e i raster fisici sono quelli reali e immutati di M1.

Esempi nella VM, dalla directory `/home/hazardia/hazardia-runtime/app`:

```sh
../core-env/bin/python -m hazardia.domain validate profiles/research/abruzzo.json
../core-env/bin/python -m unittest discover -s tests/domain -v
../core-env/bin/python -m unittest discover -s tests/unit -v
# Dati/eventi/index già preparati nel run, senza riscrivere quelli finalizzati:
../core-env/bin/python -m hazardia.domain events --profile profiles/research/abruzzo.json --records ../runs/m2-domain-20261015T190836Z/verified-replay/abruzzo-observations.json --as-of 2024-07-13T13:00:00Z --output /tmp/NUOVO-event-snapshot.json
../core-env/bin/python -m hazardia.domain window --index ../runs/m2-domain-20261015T190836Z/verified-replay/spatial.sqlite --bbox 13.37 42.34 13.38 42.35 --as-of 2024-07-13T13:00:00Z --limit 100
```

Usare un output nuovo: creazione esclusiva, nessuna sovrascrittura degli esperimenti. Le prove geospaziali usano `PROJ_LIB=/usr/share/proj PYTHONPATH=src:. /home/hazardia/m0/reflex-env/bin/python tests/integration/verify_m2.py --run NUOVA_DIRECTORY` dopo averla creata/preregistrata; core/CLI nell'ambiente core-env. Comandi effettivi completi in `experiments/runs/<run_id>/m2-*.json` sul Mac, con UTC/stdout/stderr/esito. Non è necessario rieseguire i simulatori per M2: riuso in sola lettura dei prodotti M1, tutti gli artefatti di quel run e145file motori verificati invariati.

## Prove e misure

Integrazione a commit `f165d7e`:5PASS/0FAIL, due profili con identico workflow, boundary reanalisi/forecast, entrambi i prodotti reali, lettura indicizzata, integrità M1/motori. Ultimo guard CRS e19test a `dfe1b20`:19PASS, entrambi i profili nuovamente accettati; sole differenze dopo l'integrazione sono il rifiuto di CRS metrici non supportati e il relativo test. Regressioni M1:33PASS a `9a4bef0`; diff codice M1 rispetto a fb33a31 vuoto, non modificati simulazione/job/ingest/contratti precedenti. SHA completi e freeze nel manifest.

Misura singola su10.000punti sintetici: costruzione/validazione indice24.7154s; query100record6.492ms; serializzazione1.798ms; payload51.796B; SQLite7.090.176B; massimo RSS del processo103.923.712B (include import e integrazione). La costruzione è un'operazione offline: il costo di validazione è visibile e va profilato su carichi futuri. Query confrontata con selezione completa e risultato uguale; limite1..1000 e filtro esatto dopo candidati RTree. Nessun claim p95, speedup, tempo UI o scalabilità generale.

Fallimenti conservati: prima suite15PASS/1FAIL per uguaglianza floating-point119.99999999999999 vs120s, corretto il test con tolleranza; prima integrazione4PASS/1FAIL per collisione fra nome del modulo `resource` e factory del test, corretto alias del misuratore. Nuova prova `verified-replay/` con piano e hash dell'integrazione fallita; nessun file precedente sovrascritto. Primo warning PROJ registrato, successive esecuzioni impostano PROJ_LIB al percorso già installato.

## Limiti e prossimo incremento

ADR-0006 specifica versioni e alternative. Snapshot temporali sono file di dati, non un Digital Twin o nuovo servizio. Associazione è una regola conservativa di ricerca con anchor/time-window, non un detector o una fusione probabilistica calibrata. Profilo Senegal solo portabilità dei contratti; nessuna simulazione/calibrazione locale. WGS84 UTM è il sottoinsieme metrico supportato: altri CRS vengono respinti. Effetti fisici, efficacia evacuazione, vulnerabilità e danno non qualificati. I controlli input di accessibilità non costituiscono un piano sicuro o autorizzato.

Prossimo incremento: **M3**, solver iniziale pluggable, verificatore indipendente, due percorsi decisionali singolo-hazard e prima dashboard locale con mappe reali. M3 richiede nuova autorizzazione. Il futuro framework conserva rolling horizon, ottimizzazione robusta,60s sperimentali e graceful degradation; nessuno anticipato o sostituito in M2. RQ/H1–H3 senza nuovi risultati scientifici conclusivi.


## Chiusura e integrità

PASS:122artefatti trasportati e verificati singolarmente, archivio1.600.843B SHA`0d49c6e1a04092441d06f9f14ee3c50a64c183fd7999f80f3c52575f74975014`; manifest guest`5f619a68ffdbba6efaf6933b91a340c4e47e7b54bad879cb8cbd82c504c16398`. Manifest host supplementare congela8record di comando/controllo. [Verifica trasporto](m2-domain/transfer-verification.json), [integrazione](m2-domain/integration.json), [metriche](m2-domain/spatial-metrics.json), [budget](m2-domain/budget.json). Bound conservativo2.438.028.097B/5GiB alle19:18:26Z, usato FS6.240.157.696B/libero13.327.613.952B. Include upload locali; nessun nuovo payload scientifico da Internet. Mac solo controllo/copia/hash/display; copia completa degli esperimenti in experiments/runs/<run_id>/evidence/.

Nel controllo di normalizzazione ERA5, il nuovo record di test M2 dichiara intervallo orario con estremo esclusivo a mezzanotte (ultimo campione23:00+3600s), mentre il legacy M1 conserva23:59:59. È una conversione esplicita del nuovo contratto, non modifica del vecchio file né una nuova osservazione. Metadati target del test dichiarati; origine e versione/bytes M1 restano risolvibili attraverso il manifest parent.
