# M7 — Verifica finale e gate della ricerca

15 ottobre 2026, run `m7-verification-20261015T200759Z`. **Dashboard locale disponibile per prove; gate completo M7 BLOCKED.** Reviewer Codex self-check, revisione umana/esterna non eseguita. I blocchi non sono rimossi dall'autorizzazione a procedere e non indicano scarsa potenza del Mac.

## Casi storici effettivamente esaminati

Sono state acquisite nella VM le pagine ufficiali e due archivi vettoriali, con limiti di download/decompressione, SHA-256, HTTP e lettura indipendente Fiona/CRS/bounds/schema:

- **Incendio L'Aquila/Arischia, dal 30 luglio 2020**, [attivazione CEMS EMSR449](https://mapping.emergency.copernicus.eu/activations/EMSR449/). Primo prodotto delineazione, archivio 619.620 B.
- **Alluvione dicembre 2013, Teramo**, [attivazione CEMS EMSR062](https://mapping.emergency.copernicus.eu/activations/EMSR062/). Delineazione Detail01 Teramo, archivio 1.016.121 B. L'attivazione complessiva include altre aree: non tutti i prodotti sono Abruzzo.

Lettura di 21 layer effettivi, inclusi strati di contesto: non vengono contati come 21 osservazioni indipendenti dell'evento. Attribuzione e [condizioni CEMS](https://mapping.emergency.copernicus.eu/terms-and-conditions/) archiviate. Non scaricate o riutilizzate immagini commerciali di terzi. Gli [Annali idrologici ufficiali Abruzzo](https://protezionecivile.regione.abruzzo.it/agenzia-regionale-di-protezione-civile-abruzzo/servizi-e-uffici-dellagenzia/apc001-servizio-prevenzione-dei-rischi-di-protezione-civile-e-pianificazione/ufficio-prevenzione-rischio-idrogeologico-e-idraulico/annali-idrologici/) sono una fonte individuata; la pagina pubblica non dimostra automaticamente licenza, risoluzione suboraria o disponibilità di curve di deflusso complete.

**PASS acquisizione/lettura delle osservazioni; BLOCKED validazione storica dei nostri modelli.** Le simulazioni della dashboard iniziano il 13 luglio 2024, con innesco/fuel/pioggia/Q0 sintetici e piccola AOI dell'Aquila. Non sono hindcast dei due eventi e non possono essere confrontate con questi poligoni per dichiarare accuratezza. Servono finestre e domini corrispondenti, posizione/tempo dell'innesco, combustibile/umidità appropriati, bacino completo/forzanti/condizioni idrauliche, calibrazione e cutoff di osservazione definiti prima dello scoring. Nessuna IoU/RMSE/skill inventata, nessuna selezione di eventi sulla base del risultato ottenuto.

## Previsione corrente reale e confine degli input

Una richiesta HTTPS a **MET Norway Locationforecast compact**, punto di ricerca 42.35 N / 13.38 E, ha restituito HTTP200: 2.817 B compressi / 40.532 B JSON,91 tempi. `updated_at=2026-10-15T19:18:24Z`, disponibilità osservata `2026-10-15T20:16:33.965650Z`, tempi validi 15–25 ottobre 2026. Fonte integra e attribuita: [documentazione](https://api.met.no/weatherapi/locationforecast/2.0/documentation), [licenza CC BY4.0/NLOD2.0](https://api.met.no/doc/License), [regole cache/identificazione](https://api.met.no/doc/TermsOfService). Una sola richiesta, nessun polling prima della scadenza, nessuna chiave o servizio commerciale.

**PASS acquisizione reale, BLOCKED impiego nella catena attuale**: non coincide con i raster del2024; mancano radiazione solare e pressione di superficie (la pressione al livello del mare non è una sostituzione automatica); il punto non è una forzante distribuita calibrata di bacino. `updated_at` resta aggiornamento del prodotto, non è rinominato ciclo di inizializzazione di ogni modello. I valori antecedenti alla disponibilità osservata non diventano automaticamente una previsione fatta in anticipo dal nostro sistema. La documentazione del provider limita la redistribuzione del proprio archivio storico alle regioni nordiche/artiche: non si assume un archivio italiano attraverso questa API. Questo non significa che nessun altro archivio italiano possa esistere.

Il replay allerte della UI resta dichiaratamente sintetico. Non si collegano arbitrariamente dati2026 e risultati2024.

## Regressioni e dimensionamento

66 test finali:33 base,19 dominio,14 decisione/adattamento PASS. Dopo il FAIL storico sul margine del watchdog, ulteriori10 prove di arresto del gruppo con budget0,8s PASS. Tutti i145 hash del runtime motori sono immutati rispetto a `runtime-v2.json`; la compatibilità REFlEx dichiarata rimane quella congelata.

Indice geografico,30 query/size con restituzione limitata a1000 record:

| Record sintetici | Costruzione s | p95 query s |
|---:|---:|---:|
| 100 | .268 | .00231 |
| 1.000 | 2.388 | .03046 |
| 10.000 | 24.951 | .06699 |
| 100.000 | 255.323 | .52223 |

Peak RSS del processo di questa sequenza circa37.760 KiB. Le query con un insieme ampio di candidati e ordinamento hanno un costo visibile: non sono richieste read API misurate direttamente e non vengono assimilate al precedente p95 API. Solver a2eventi/12slot,4/20/100risorse e2/5/10scenari: .804/1.105/1.489s, una esecuzione per taglia, tutte verificate. **Nessun p95 da n=1**. Il contratto rifiuta24slot: l'M/L candidato iniziale da24/48slot non è supportato, anziché essere eseguito senza dichiararlo. I casi fisici M/L completi non sono stati prodotti.

Stress grafico isolato sul browser client, catalogo intercettato solo nel test e geometrie duplicate artificialmente; non sono celle CIMA nuove, non vengono inviate al backend o pubblicate nel catalogo utente:

| Geometrie per mappa | Caricamento ms | p05 FPS /30 movimenti | Heap rilevato | Esito |
|---:|---:|---:|---:|---|
| 1.000 | 204 | ~60 | 18,3 MB | PASS |
| 10.000 | 422 | ~60 | 190,8 MB | PASS |
| 100.000 | 2.162 | Nessun campione di movimento valido | 1,316 GB | FAIL |

Il fallimento non viene trasformato in FPS zero misurati o in PASS. La pipeline attuale usa raster compatti e griglia incendio64², non un input arbitrario da100.000 poligoni. Lo stress rivela un limite per generalizzazioni future: servono rendering per finestre/tiles/LOD preservando dati originali e provenienza. Non viene allentato il target30FPS. QR-14/release su grandi carichi restano bloccati.

## Interfaccia, stabilità, replicazione

I test finali desktop/tablet/telefono e le30 azioni per tipo passano; axe4.10.3 restituisce0violazioni a375/768/1440px, con verifiche di contrasto incompiute sopra raster/native controls esplicitamente conservate. Non è una certificazione WCAG. Sessione rappresentativa di30minuti e copia verificata del supplemento: **vedere checkpoint finale aggiunto dopo l'esecuzione**, nessun PASS anticipato.

La prova in un checkout isolato del sorgente riusa gli ambienti della stessa VM: può verificare il packaging e il replay decisionale; non è una seconda macchina o un'installazione indipendente completa. Nessuna prova scientifica nativa sul Mac è stata aggiunta dopo la decisione single-VM. Portabilità fisica/installa ex novo resta NOT RUN.

## Gate e prossimo incremento

Il risultato consegnabile ora è una dashboard locale di ricerca con modelli reali, confronto di interventi sintetici, vincoli indipendenti, code e prove di errore. Non è il rilascio scientifico completo. Restano:

1. Ricostruire almeno un caso storico corrispondente per ciascun hazard, con dati/diritti/tempi/calibrazione ed esperto di dominio; fissare un protocollo prima della valutazione.
2. Integrare una previsione reale completa e temporalmente coerente con nuove esecuzioni fisiche, senza riempimenti arbitrari; validare gli effetti degli interventi prima di attribuire loro skill reale.
3. Completare strategie alternative, ottimizzazione della conservazione delle capacità e baseline/ablazioni principali; l'attuale confronto di regole/pesi sintetici non dimostra H1–H3.
4. Risolvere il limite grafico dei grandi carichi e verificare installazione/portabilità indipendente prima di dichiarare un research release completo.

Nessuna spesa, aumento risorse, pubblicazione, deployment pubblico, push o operazione reale effettuata. La licenza di redistribuzione del codice HAZARDIA dovrà essere scelta dal titolare prima di una pubblicazione; nessuna licenza pubblica è stata concessa autonomamente.

### Isolated source checkout checkpoint

PASS: a new local checkout from source bundle b0b3fae loaded HAZARDIA from its own `src/`, reran the pinned M5 problem with the existing isolated solver and independently verified the same objective. Both geographic profile contracts validate. The first clone attempt lacked a default HEAD in the main-only bundle and failed before running Python; explicit checkout main corrected it. Export now includes main and HEAD. This packaging failure and its actual commands are retained; it is not a model failure or a fresh-machine installation. Source paths/losses in isolated-replay/results.json; no networking or native physics was needed by the replay, but no OS network namespace isolation was claimed.


## Final30-minute stability checkpoint —2026-10-15
PASS runm7-verification-20261015T200759Z/stability/results.json: measured1800.030s after60sseparatewarmup,120samples,156feedbackpoints p9517.100ms,123map samples p0560FPS, peakclientheap5161124B, GC-normalizedgrowth461064B, DOMgrowth8nodes. NoJavaScript/UIerrors or simulator submissions fromnavigation. Chrome155/MacM4Proclient; allbackend/science staysVM. ExplicitGC only atbaseline/end; rawtrend retained; concurrentQAstress disclosed.44production-sourcefiles/145enginehashesunchanged atcheckpoint. This is bounded smallfixture evidence, not proof of allfutureloads;100kstressFAIL and fullresearchgates remainBLOCKED. Archive/transport classified separately afterexecution.


## Final supplement/health checkpoint —2026-10-15T20:41UTC
PASS local integrity and transport:3275files, expanded213996457B, archive68478162B; manifestSHA965e16421c2f2b099e0d310ccc28b2db160dd6dbd74871c2472a6c48c426e10a, archiveSHAff69a31d9bcdd9631ce35bfa7c3dea9d0746b101f1b8afcd01cc2f0d3a125a02. Frozen source998b934faf8b7519eb567ed6384cd591eac976f6; final documentation commits only append this subsequent verification. VM export/home/hazardia/hazardia-runtime/exports/research-supplement-20261015T203922Z.tar.gz; host experiments/runs/m7-verification-20261015T200759Z/exports/research-supplement-20261015T203922Z.tar.gz. Independently host-copied file sizes/hashes all match. Packagedsourcebundle defaultHEAD clone/replayPASS, same selected IDs/objective51.346, using existing guest environments; not a freshmachine/native-physics reproduction. Earlier main-onlybundle HEADfailure retained and corrected.
FinalhealthPASS: VMserviceRUNNING/loopback,44productionfiles+145enginefiles unchanged,4vCPU/8GiB/19GiB unchanged, conservative cumulative downloadbound2614785687B/5368709120B, freeguestdisk12712792064B. No paid/public/push/real action. Dashboard left available for user http://127.0.0.1:8080/; guide reports/DASHBOARD-GUIDA.md, plainstatus reports/STATO-IN-PAROLE-SEMPLICI.md. Scientificfullgates M5/M6/M7 remainBLOCKED; incomplete software/main-study items remain explicitly listed.
