# Monitoraggio — pioggia oraria per zona

Run `monitor-zone-series-20261021`, 21 ottobre2026. Primo incremento della
baseline funzionale MyDewetra, non dichiarazione di parità completa.
Revisore Codex self-check. Base f7da679, documentazione preesistente dirty.

## Cosa cambia

In Monitoraggio → Pioggia e allerte, selezionare una zona dal menu o dalla mappa.
La zona ha un contorno più spesso; il pannello mostra un grafico delle successive
48ore, il massimo orario medio con data/ora e una tabella dei valori. Accumuli,
legenda e copertura sono richiudibili. I motivi dell'allerta DPC sono consultabili
separatamente. Le date sono in ora di Roma; ogni barra è la quantità prevista
nell'ora indicata, non una misura istantanea o osservata.

Le serie provengono dalla stessa griglia congelata e dalla stessa quadratura
spaziale delle cumulate esistenti. Non sono stati aggiunti nuovi dati o soglie.
Una zona non interamente coperta, un'ora mancante o una geometria della fonte
non qualificata produce dato mancante, rappresentato con tratteggio. Una
copertura incompleta non diventa una previsione di zero precipitazioni.
Le medie areali non stimano il vero massimo locale, la pioggia può includere
equivalente d'acqua della neve e nessuna classe quantitativa è un'allerta idraulica.

La richiesta HTTP accetta `field_id` oltre ad `at`: identifica lo snapshot
effettivamente mostrato dalla scheda. Il servizio legge l'archivio con controllo
di integrità, identità e TTL; rifiuta campi scaduti, futuri, non trovati o ID non
validi. Il browser verifica che la risposta corrisponda allo snapshot richiesto.
I client precedenti che inviano soltanto `at` restano compatibili. Questa modifica
evita che il calcolo zonale prenda implicitamente l'ultimo campo globale scelto
da un'altra scheda; non sostituisce l'intero meccanismo di scelta del meteo per
viewport. Il cambio di griglia può cambiare medie e coperture e rimane dichiarato.

## Prove effettuate

| ID | Verifica | Esito |
|---|---|---|
| MS-01 | 23test nella VM: cumulate, serie variabile, buchi, fine orizzonte, geometrie invalide, TTL e richiesta esplicita del campo | PASS |
| MS-02 | 14controlli Node del modello/markup, 18regressioni del rendering meteo | PASS |
| MS-03 | Snapshot reale `map-weather-5c7b71c5afc7a8793df80b46`, ora13UTC21ottobre:187zone,83complete;1496controlli numerici | PASS |
| MS-04 | Cumulate preesistenti identiche al codice precedente; identità degli intervalli comuni avanzando1h sullo stesso snapshot | PASS |
| MS-05 | HTTP su VM con field_id congelato: risposta FRESH, ID corrispondente e48record | PASS |
| MS-06 | UI reale1280×720:48barre, tabella48ore, dettaglio, impostazioni richiudibili,48ore mancanti su zona non qualificata, controllo errori JavaScript | PASS nello scope osservato |
| MS-07 | 145hash motori,90job e2file protetti workspace/casi invariati | PASS |
| MS-08 | Nuovi radar/pluviometri, soglie locali, validazione impatti | NOT RUN / qualificazione BLOCKED |
| MS-09 | Benchmarkp95≥30, Safari, dispositivi fisici, nuovi run fisici | NOT RUN |

La singola valutazione completa nella VM richiede1,718s nel pilot: non è un p95
o una misura di scalabilità. I risultati completi, i checksum dei9file consegnati
e le informazioni di ambiente sono nel sommario `monitor-zone-series/verification.json`.
Il nuovo schema dei risultati ha una chiave cache differente; non altera gli
archivi precedenti. Archivio pioggia al controllo finale40.061.247byte, con i
limiti di ammissione esistenti; ulteriore crescita può produrre CACHE_FULL,
non eliminazione silenziosa delle evidenze.

## Problemi riscontrati e conservati

- Node16 host interpreta i file.js come CommonJS: primo harness fallito,
  corretto usando l'import data-URI già impiegato dai test del repository.
- Il nuovo test della lettura esplicita ha rilevato una fixture con timestamp
  `+00:00` anziché il formato contrattuale `Z`: rifiuto corretto, fixture corretta.
  Log negativo e successivo23PASS conservati separatamente.
- Una selezione automatizzata basata su etichetta con quantità variabile è
  fallita durante un aggiornamento: la verifica usa ora l'ID stabile della zona.
- L'iniziale pannello troppo prolisso nascondeva il grafico: impostazioni e
  motivazioni sono richiudibili, senza perdere i dettagli disponibili.
- Le immagini satellitari regionali risultano non disponibili per il limite
  cumulativo locale64MiB: endpoint restituisce DOWNLOAD_LIMIT, contatore
  65.017.285byte più riserva di ammissione. Il riavvio del servizio svuota la
  cache RAM delle immagini, non il contatore. Nessun limite è stato aumentato.
  Aggiunto avviso visibile per sfondi incompleti; cartografia OSM provata come
  alternativa. La cache satellitare persistente e la sua politica restano da
  valutare separatamente, inclusi diritti e budget.

I due riavvii locali per il servizio non hanno recuperato o cancellato job attivi
(`interrupted jobs explicitly classified []`). PID finale707049. Nessuna
installazione, modifica del modello, nuova simulazione fisica, azione reale o
deployment pubblico. Le normali richieste cartografiche/meteo del browser
continuano a usare i budget esistenti; i calcoli zonali leggono le cache.

## Riproducibilità

Nella VM, da `/home/hazardia/hazardia-runtime/app`:

```sh
PYTHONPATH=src:tests/unit PROJ_LIB=/usr/share/proj /home/hazardia/m0/reflex-env/bin/python -m unittest test_rain_assessment test_rain_service test_attention_zones -v
```

Sul client di sviluppo:

```sh
node tests/browser/rain-series.mjs
node tests/browser/rain-clarity.mjs
```

Raw nel run omonimo in `experiments/runs/` e nella VM in `runs/`; preregistrazione,
input congelati e audit numerico conservati. La correzione field_id e le
rifiniture UI sono successive ai rilievi del pilot: non valutazione held-out.

Restano aperti rete osservativa, radar, soglie locali qualificate e rischio
d'impatto. La baseline MB-01…08 e i gate scientifici M5–M7 non sono chiusi da
questo incremento. Prossimo lavoro: disponibilità/diritti e contratto della
prima fonte osservativa, poi controllo delle finestre e delle soglie con dati
osservati separati dalle previsioni, senza inventare validazione operativa.
