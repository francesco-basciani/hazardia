# Valutazione risorse VM —23ottobre2026

**Decisione proposta: mantenere per ora4vCPU/8GiB RAM. Pianificare più disco dopo aver recuperato spazio sul Mac. Nessun ridimensionamento eseguito.** Run `vm-sizing-20261023`, basee99966e7ebbca5219e953a8aec3f78dbb9d67921+dirty. Reviewer Codex self-check.

## Misure attuali

| Risorsa | Risultato | Interpretazione |
|---|---|---|
| Mac | Apple M4Pro,14core CPU (10performance+4efficiency),48GiB memoria unificata | Esiste margine hardware per una VM più grande; non è prova che serva aumentarla |
| Memoria Mac | `memory_pressure`:62% libera, fotografia del momento | Nessuna pressione di memoria indicata da questa lettura; non è un profilo a carico massimo |
| Disco Mac | Volume dati926GiB, circa16GiB disponibili,99% occupato secondo `df -h` | È il vincolo da affrontare prima di un ampliamento significativo del disco guest. La capienza virtuale non crea spazio fisico |
| VM attuale |4vCPU,8GiB assegnati,19GiB disco; Linux rileva7,74GiB RAM utilizzabile | Configurazione originale preservata |
| VM a riposo | Circa269MiB usati e7,3GiB disponibili; sei letture `vmstat` con CPU~100%idle; pressureCPU/memoria/I/O avg10/60/300=0 | Nessun segnale attuale di saturazione. `MemAvailable` comprende cache recuperabile: la cache non è memoria esaurita |
| Disco VM | Circa14GiB usati,4,23GiB disponibili,77% occupato | Margine ancora presente; nuovi domini, raster e risultati accumulati potranno consumarlo |
| Backend a riposo | RSS~96MiB, CPU media di vita processo~0,6% | Non è il picco dei simulatori, né un campione di CPU istantanea |

Stima directory guest: jobs1,2GiB; runs1,4GiB; web-state1,9GiB; ambienti/core22MiB e decision83MiB; ambiente M0~1,8GiB. Sono aggregati orientativi `du`, non somma esaustiva del filesystem. Non sono stati eliminati cache, dati o evidenze.

## Prova di consultazione del backend

Comando nella VM:

```sh
~/hazardia-runtime/core-env/bin/python ~/hazardia-runtime/probe-sizing.py
```

Script conservato nel run host come `probe.py`; risultato guest `~/hazardia-runtime/runs/vm-sizing-20261023/results.json`. Richieste soltanto `GET /api/weather/map`: nessun refresh, download esterno richiesto, job o ottimizzazione avviati.

30risposte in cache, fino a4richieste simultanee, tutteHTTP200, circa641kB per risposta. Durata totale0,572s; latenza p5048,7ms e p95252,3ms. CPU guest media28,5% della capacità complessiva, inclusa la sonda; I/O wait0%; almeno7.795.130.368byte disponibili (~7,26GiB); picco RSS del backend111.058.944byte (~106MiB). I95job rimangono82SUCCEEDED/8CANCELLED/5ERROR, nessunoRUNNING/QUEUED.

**È una sonda breve e correlata di consultazione con cache, non30esecuzioni indipendenti, una prova sostenuta o il dimensionamento della fisica.** Non garantisce la stessa latenza durante PROPAGATOR/HMC/REFlEx o con più utenti. Non confronta configurazioni di VM diverse.

## Perché aumentare la VM non risolve automaticamente la mappa

La VM acquisisce dati, serve API ed esegue i modelli. Leaflet, etichette, interpolazioni visuali, vento e traffico vengono disegnati dal browser sul Mac. Nel precedente incremento il solo disegno di400veicoli aveva p95~0,7ms, mentre l’intervallo fra disegni arrivava a p9548,7ms. Questo non identifica da solo una causa, ma non giustifica attribuire tutta la lentezza alle risorse della VM. Aumentare vCPU/RAM non corregge automaticamente lavoro JavaScript, ridisegni, scheduling o rendering grafico del client. La lentezza va correlata ai profili del browser e del backend sullo stesso workload.

## Quando aumenterei le risorse

| Risorsa | Adesso | Opzione successiva, subordinata alle misure |
|---|---|---|
| CPU | Mantenere4vCPU |6vCPU se il carico nativo tiene occupate le4CPU, presenta coda rilevante ed è effettivamente parallelizzabile. Più core non accelerano automaticamente una fase seriale |
| RAM | Mantenere8GiB |12–16GiB se ensemble/domini/concorrenza portano MemAvailable stabilmente vicino all’esaurimento, pressure/OOM o un limite di memoria verificato. Gli~7,3GiB ora disponibili non motivano un aumento immediato |
| Disco |19GiB attuali, con4,23GiB liberi |40GiB come possibile taglia di lavoro per ulteriori dati, dopo aver recuperato un margine adeguato sul Mac; non è una stima della copertura nazionale e non è approvazione all’espansione |

Prima di qualsiasi ampliamento del disco, inventariare cosa si può archiviare o spostare sul Mac mantenendo le evidenze scientifiche. Non assumere che un file sparse consumi tutta la capienza subito, né che questo renda sicuro lavorare con poco spazio fisico residuo. Nessun acquisto o cancellazione proposto come automatico.

Per decidereCPU/RAM occorre congelare una fixture reale rappresentativa: stessi inneschi, terreno/meteo/seed, orizzonte72h, numero di membri/scenari e limiti di concorrenza; misurare albero dei processi, MemAvailable, CPU per core, I/O, coda e latenza API mentre il browser riproduce lo stesso caso. Solo dopo confrontare eventuali6vCPU/12–16GiB, mantenendo distinto il vecchio ambiente di benchmark. Non alterare retroattivamente i risultati ottenuti con4vCPU/8GiB.

## Esiti

- **PASS:** inventario e misure a riposo; sonda consultazione30GET/fino4concurrenti; nessuna saturazione osservata nel perimetro misurato.
- **PASS:** configurazione invariata e95job preservati.
- **NOT RUN:** nuovo benchmark nativo completo, picco aggregato dei simulatori, confronto4vs6vCPU o8vs16GiB, profiling causale del rendering Safari.
- **NOT RUN:** espansione VM, modifica risorse, cancellazione/archiviazione dati, nuovi acquisti.

Gli attuali limiti autorizzati restano4vCPU/8GiB RAM/disco massimo20GiB (attuale19GiB). La richiesta è di valutazione: non è stata interpretata come autorizzazione a superarli. Nessuna nuova conclusione scientifica; gateM5–M7 invariati.
