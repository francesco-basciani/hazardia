# M5 — Decisioni limitate nel tempo, continuità e allerte

15ottobre2026. **PASS tecnico sui casi controllati; qualificazione meteorologica/anticipatoria reale BLOCKED.** Run `m5-adaptive-20261015T195150Z`; integrazione UI nel run `m6-degradation-20261015T200034Z`. Reviewer Codex self-check; nessuna revisione scientifica esterna. Non equivale al completamento di ogni P0 di M5.

## Decisione e deadline

Il supervisore esterno comprende attesa dalla presa in carico, processo solver, verificatore e pubblicazione. Il solver HiGHS è un sottoprocesso isolato; il watchdog può terminare l'intero gruppo, inclusi discendenti. I risultati tardivi non vengono promossi a piani validati. Sono conservati problema, configurazione/codice, solver raw, verificatore e risposta. La coda HTTP è limitata a4 richieste e2worker; i modelli fisici hanno una coda separata e un worker.

Benchmark preregistrato:4risorse/2hazard/2scenari/2regioni,1slot,seed1729+i,30esecuzioni native nuove, budget60s, stesso contesto genuino CIMA, effetto sintetico. Nearest-rank p95. Prima campagna source8d8081a:30/30 `VALIDATED_FOR_SIMULATION`,p50 .738789s,p95 .870891s,max .902334s. Dopo correzione del margine di chiusura, campagna `perf-second` sourcee5ec104:30/30 utili e30/30 entrodeadline,p50 .714691s,p95 .820538s,max .828716s. Tutti i tempi raw e denominatori in `deadline-benchmark.json`. Il tempo misurato esternamente include il ritorno dalla funzione e la serializzazione. Non sono30eventi fisici indipendenti e non è un SLA certificato.

Il test forzato da0,8s ha registrato un FAIL storico: .800246s. Correzione e1f748e: riserva di chiusura fino a1s o metà dei budget brevi, tempo residuo ricalcolato dopo lo spawn. Il test mantiene il limite originario; non è stato allentato. I test successivi comprendono arresto del discendente e coda già scaduta senza avvio di worker. Il tempo interno `elapsed_s` è registrato prima dell'ultima scrittura; il benchmark esterno è il riferimento end-to-end. Un OS general purpose non fornisce una prova formale di hard real-time.

`perf-second/cpu-rss.log` contiene `/usr/bin/time -v` per l'intera suite seriale e suoi discendenti (30benchmark+ricalcoli/confronti); non è la RAM simultanea dell'intera VM né un percentile RAM per richiesta. Ambiente versionato nel dossier M7. Le simulazioni fisiche nuove non sono comprese nel budget decisionale.

## Continuità e allerte

`decision/rolling.py` verifica il piano precedente, conserva impegni ancora attivi, sottrae benefici già conseguiti dall'esposizione residua, registra consumi e rinvia opzioni alternative. Il progresso è un modello **sintetico lineare** dichiarato. La prova con missioni da2slot conserva gli impegni nel secondo ricalcolo; la UI permette di avanzare10minuti, con controlli di validità dei prodotti invariati. Non simula automaticamente la soppressione fisica dell'incendio o il prosciugamento dell'alluvione.

`adaptation/alerts.py` applica il contratto forecast con issued/available/valid time; deduplica, rifiuta identità mutate, revisioni arretrate, scadenza e effetto ignoto. Stati OPEN/ACKNOWLEDGED/UPDATED/RESOLVED/EXPIRED; presa visione senza autorità operativa. L'API/UI conserva eventi immutabili del replay, controlla la revisione concorrente e invalida proposte calcolate prima di un cambiamento del contesto.

Forecast di prova: emissioni12:00/12:15/12:30Z, validità13:00–14:00Z del13luglio2024, esposizione45→50→20, soglia35. Anticipo iniziale3600s. Due esiti di verità creati a mano includono un falso allarme; la frazione .5 descrive questi due casi, **non** una misura di skill meteorologica. Il comando di riavvio crea un nuovo ciclo esplicito, senza fingere una nuova emissione reale.

Confronto media-only vs worst-only: su questo input le assegnazioni coincidono. Nessun vantaggio della robustezza osservato; il test verifica la coerenza dei due obiettivi, non H2. Le probabilità/effetti dei casi sono sintetici. Statica vs rolling è illustrata dal registro di progressi; non è un confronto causale indipendente sul campo.

## Limiti e ripetizione

M5.1/2/3 e lifecycle software PASS nel perimetro dei test. Forecast reale coerente con nuove esecuzioni CIMA, falsi allarmi su osservazioni indipendenti, baseline sperimentali complete e sensibilità statistica restano BLOCKED/NOT RUN. ERA5 del2024 acquisita nel2026 è reanalisi, non previsione emessa in anticipo. Non viene riclassificata per soddisfare il gate.

Nella VM, dalla cartella app, usa un nuovo percorso vuoto:

```sh
../core-env/bin/python -m unittest discover -s tests/decision -v
/usr/bin/time -v ../core-env/bin/python tests/integration/verify_m5.py \
  --runtime /home/hazardia/hazardia-runtime --run /tmp/NUOVO-m5-run
```

Riproduce i meccanismi sul catalogo disponibile; per confronto esatto ripristinare i riferimenti del run congelato. Comandi originari, errori import-path e tutti i risultati sono conservati in `experiments/runs/m5-adaptive-20261015T195150Z/` e nella copia guest. Non sovrascrivere i risultati precedenti.
