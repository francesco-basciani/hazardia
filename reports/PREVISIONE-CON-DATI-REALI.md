# Previsione condizionale con dati reali e inizializzazione antecedente

Run `forecast-case-20261018`,18ottobre2026, base `b5422c85b16fa958d93eb2c3352c34bc3d6a6af3`+dirty; SHA finale Git/PUBLICATION.json. Reviewer Codex self-check. La scelta utente è **previsione con dati reali su innesco ipotetico**. Non ricostruzione o validazione dell’incendio del17ottobre; AR-EXT-01 e piano M0–M7 invariati.

## Provare nella dashboard

[Apri previsione](http://127.0.0.1:8080/?view=results&case=forecast-fonte-vetica-20261018), in Simulazioni e risorse e nella stessa scheda. Due mappe sincronizzate: riferimento senza interventi e Canadair nativo lungo linea prefissata a+1h. Caso separato dal workspace principale e dal precedente FonteVetica; niente sostituzione dei propri scenari. La vista di consegna è a+24h in pausa: **Riproduci** avanza incendio e meteo insieme; cursore torna indietro. Modificare le risorse richiede ricalcolo fisico, mantenendo gli input congelati e poi riprendendo dall’ora scelta. Si possono aggiungere scenari vuoti/copie esplicite e usare il percorso ottimizzato esistente, i cui proxy rimangono ideali.

Nelle impostazioni avanzate **Previsioni orarie e parametri del modello** sono selezionabili inizializzazione dai7giorni precedenti e2/4/8realizzazioni. La storia168h richiede FORECAST e hFFMC; non viene applicata alla modalità manuale/storica. Cambiare quei parametri invalida il vecchio risultato e passa a nuova preparazione; modifiche delle sole risorse conservano esattamente il profilo del genitore. I casi precedenti mantengono2realizzazioni/resetFFMC85 e i propri dati originali.

## Dati e protocollo prima dei risultati

Spec [examples/forecast-fonte-vetica-20261018.json](../examples/forecast-fonte-vetica-20261018.json), preregistrata dal preparatore nella VM prima dei job. Punto della località FonteVetica42,4254944444/13,74145 è ipotetico e invariato dal riferimento geografico precedente; non è l’innesco osservato del rogo. Linea Canadair fissata prima degli esiti a lat42,4282,lon13,737–13,746, attivazione60min. Nessun riposizionamento in base ai risultati. Selezionati8membri, seme1729 e72h come pilot entro il contratto esistente, non come numerosità scientificamente sufficiente. Nessun effetto garantito.

Inizio **18/10 ore18UTC,20:00Roma**, termine **21/10 ore18UTC,20:00Roma**. Previsione Open-Meteo/DWD ICON Global reale acquisita prima dei job, un unico snapshot distribuito congelato `map-weather-e8017a84e00f0bef7e3e2dc1`. Nuovo modulo antecedente acquisisce168ore necessarie su81nodi, stesse coordinate della previsione, dati recenti archiviati e tratto previsto fino all’inizio futuro: non osservazioni di stazione. Storia grezza747038byte, entro1MiB, ricevuta/hash conservati. Le precipitazioni provider riferite all’ora terminante sono allineate all’intervallo corretto; nessuna pioggia successiva all’innesco usata per inizializzare.

DEM reale GLO30 e copertura WorldCover2021 riclassificata, terreno congelato `e97be42ecdae76e0a67e32ae3869c23edda7de8516287df69686b0a4cd21e684`,30m/1024², stessi asset del dominio già verificato. Non aumentata la risoluzione fisica in base al dettaglio satellitare. Specie, carico/stato stagionale e curing dell’erba restano non qualificati; bosco generico non diventa automaticamente conifera o combustibile osservato2026.

## Percorso fisico verificato

Nuovo contratto interno `distributed/2`, mantenendo envelope FIRE0.4.0 e leggibilità di `distributed/1`. Il geo-worker proietta/interpola i campi atmosferici su ogni cella, fa evolvere l’estimatore hFFMC1977 già presente per168h e salva `initial_moisture` nel medesimo asset arrays con SHA. FFMC85 è il prior assunto all’inizio del warm-up, non un valore misurato all’innesco. La griglia iniziale effettiva è16,80267334–18,91386414%. Il worker PROPAGATOR carica quella griglia, verifica forma/finite/range e applica poi il meteo spaziale orario per72h. Audit: range del primo evento nativo uguale all’array preparato. Una nota generica ereditata nei manifesti descrive ancora FFMC85 assunto; contratto2, asset e ulteriore assunzione168h documentano precisamente la nuova inizializzazione, senza riscrivere manifesti conclusi.

La stima rimane hFFMC1977 indipendente già in HAZARDIA, **non RISICO**, non moisture misurata e non una validazione ecologica. Vento10m e meteorologia globale~11km non diventano misure locali o flussi risolti fra edifici. Otto realizzazioni stocastiche dello stesso forecast non sono un ensemble di otto previsioni meteo indipendenti.

Acquisizione condivisa con budget meteo esistente:48tentativi/giorno,81equivalenti per campo, intervallo65s, cache64MiB, risposta max1MiB. Cache storia separata dal campo mostrato sulla mappa, riuso solo griglia esatta/finestra completa e hash/normalizzazione verificati. Attesa limitata150s in preparatore isolato; cancellazione controllata ogni secondo. Geo staging max240s, supervisor nativo900s invariato, preparatore seriale e4slot esistenti. Fonti/gap/quote/cache incoerente bloccano il nuovo calcolo con motivo; non sostituiscono la storia con combustibile secco. Risultati precedenti restano disponibili; il profilo precedente è una scelta esplicita dell’utente. Nessuna richiesta per quadro di animazione e nessun piano a pagamento.

## Risultati osservati, inclusi negativi

| Caso | Job | Frame | Area media finale ha | Realizzazioni con eventi di fronte ancora in coda a72h |
|---|---|---:|---:|---:|
| Senza interventi | job-ebe51c3a0c4b4832bda1ab3f117e6ec6 |288|1229,20875|4/8|
| Canadair nativo a+1h | job-6ef11525dfe94014906dd353cc1bc202 |288|1271,655|4/8|

PASS stesso terreno, meteo, griglia iniziale, orologio e opzioni. Tre campioni prima dell’intervento identici bit per bit;81celle ricevono l’azione sull’umidità a3600s;19960celle di probabilità finale differenti. PASS10asset/1188artefatti, inclusi576array e576PNG per SHA;145pin upstream invariati. Probabilità coerenti con passi1/8; nessuna interpolazione fisica dei prodotti. La riproduzione grafica usa la dissolvenza già qualificata.

**FAIL ipotesi di riduzione della superficie per questo Canadair:** area finale maggiore di42,44625ha. Non significa che un Canadair reale peggiori gli incendi: una sola coppia,8realizzazioni e traiettorie/RNG che divergono dopo azioni non consentono conclusioni causali operative. Non corretto il risultato per ottenere un beneficio. Non confronto ablation con i vecchi casi: previsione, partenza, inizializzazione e campionamento sono cambiati insieme. Area cumulativamente raggiunta non è area di fiamme attive. Nessuna durata artificiale: in questa coppia il motore conserva fronti anche a72h.

## Verifiche e risorse

PASS124testVM inclusi9dedicati a storia completa, causalità, variazione spaziale, cache/quote/missing/rate-limit/parametri. PASS5preflight su input reali senza nuovi job: mismatch ensemble/history rifiutati, ora mancante rifiutata, replay sole risorse conserva8membri/168h; staging storico conserva8membri senza avviare nuovi job. PASS37controlli browser (14profilo e23authoring), includono6axe a375/768/1440 senza violazioni. Scritture e POST di calcolo dei test UI isolati; i due job dichiarati sopra sono esecuzioni native effettive. PASS controllo IAB di due finestre, play24→42h circa, pausa/seek a24h e meteo alla stessa validità; nessuna modifica agli input. Main preservata dal preparatore e dai test; precedente caso rev20 preservato.

VM unica4vCPU/8GiB/19GiB,6,4GiB liberi. Esecuzioni native136,47s e125,20s, coda0,18/0,31s, RSS campionato gruppo2,80/2,83GB (byte decimali, circa2,61/2,63GiB). Sono due misure, non p95. Nessuna installazione, nuovi engine, privilegi, aumento risorse o deployment; due riavvii backend a coda/preparazioni vuote, zero job interrotti. Compilazione Numba e librerie già presenti.

FAIL intermedi conservati: due attese harness UI anticipavano inizializzazione/PNG; un negativo rimuoveva un’ora fuori dalla finestra richiesta e veniva correttamente accettato, corretto l’oracolo scegliendo una delle168ore effettivamente richieste. La revisione ha inoltre rilevato che il vecchio staging storico ignorava il nuovo selettore8membri: propagazione del parametro corretta e verificata preparando2richieste storiche senza avviare job. Nessun fallimento nativo della coppia. Non sovrascritte evidenze.

## Riprodurre

Nella VM con servizio avviato: `PYTHONPATH=src ../core-env/bin/python scripts/prepare_fire_case.py --runtime "$HOME/hazardia-runtime" --spec examples/forecast-fonte-vetica-20261018.json`. Il comando avvia realmente due nuovi job e rifiuta sovrascritture: per una nuova acquisizione scegliere un nuovo ID nella spec. La data futura è fissata al prossimo orario+2h e viene registrata prima dei run; il meteo cambia, quindi non è replay esatto dello snapshot precedente. Per modificare solo risorse nel caso esistente, il normale player usa `/api/firelab/branch` con gli input congelati.

Test: `PYTHONPATH=src PROJ_LIB=/usr/share/proj <geo-python> -m unittest discover -s tests/unit -v`; audit `PYTHONPATH=src <geo-python> tests/native/fire_forecast_case_audit.py <runtime> forecast-fonte-vetica-20261018`. Browser: env Playwright/Chrome/axe e `node tests/browser/forecast-profile.cjs <directory-nuova>`; authoring usa anche HAZARDIA_FIELD_FIXTURE, come nei run precedenti. Nessun scientific runtime necessario sul Mac. Raw privati `experiments/runs/forecast-case-20261018` e run VM `forecast-fonte-vetica-20261018-20261018T163630Z`; sorgente/fixture ipotetico e sintesi redistribuibile `reports/forecast-case/verification.json`.

PASS previsione condizionale eseguibile e confrontabile con dati reali. BLOCKED realismo operativo completo, calibrazione fuel/moisture/soppressione/logistica, skill/held-out e gate completiM5–M7. NOT RUN nuovo weather ensemble, calibrazione osservazionale, ottimizzazione nativa di questo specifico caso, benchmark30/p95/soak/device fisici/secondaVM. Prossimo incremento scientifico: caratterizzazione della varianza/efficacia su geometrie e semi preregistrati, qualificazione fuel locali e priorità/logistica; nessun nuovo hazard o operazione reale autorizzato implicitamente.
