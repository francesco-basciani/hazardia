# Fonte Vetica — prova prospettica ispirata alla notizia

Run `fonte-vetica-20261018`, base `c26d70dc786efb7d915142534c90a075755ed284` con modifiche dichiarate per il caricamento separato delle prove. Commit consegna in Git/PUBLICATION.json. Reviewer Codex self-check; nessuna validazione indipendente.

## Aprire la prova

Nella dashboard locale: [Fonte Vetica · prova prospettica](http://127.0.0.1:8080/?view=results&case=fonte-vetica-20261018). Stessa sezione Simulazioni e risorse e stessa scheda browser. Il collegamento è disponibile anche in **Come creare e confrontare gli scenari → Prove salvate**. Si apre a+24ore, con3finestre native confrontabili; la timeline permette inizio/play/pausa e fino a72ore. **Torna ai miei scenari** riapre il workspace abituale. Aggiunte/modifiche della prova sono conservate in una workspace revisionata distinta nella VM, senza sostituire gli scenari esistenti. Il collegamento è locale, non un servizio pubblico.

## Cosa sappiamo della notizia

La pagina [MarsicaLive indicata dall’utente](https://marsicalive.it/campo-imperatore-brucia-fonte-vetica-vigili-del-fuoco-e-volontari-al-lavoro-nella-notte/) riporta un incendio a Fonte Vetica e interventi di vigili del fuoco/volontari, con vegetazione erbacea secca prossima ad aree boscate. Il campo datePublished del primo NewsArticle indica18/10/2026 ore11:08:03+02. L’immagine è dichiarata d’archivio, quindi non è osservazione utilizzabile per validare il perimetro. La cronaca [NewsTown del18ottobre](https://news-town.it/2026/10/18/cronaca/incendio-a-fonte-vetica-vigili-del-fuoco-sul-posto-per-le-operazioni-di-spegnimento/) colloca l’inizio nel pomeriggio del17. Nessuna di queste fonti fornisce punto/ora esatti, perimetro georiferito, inventario completo o posizionamento/tempi delle squadre. Il riferimento al2017 nella cronaca non va confuso con l’evento2026.

L’articolo è stato acquisito realmente nella VM:156761byte, SHA256 `b95b7897dc77c76de5b84ef42034ad9a81d8f74d05c17fb23181794fd0b3d672`. Il tool web non apriva direttamente la pagina; fetch HTTPS guest riuscito e schema/testo letti. HTML originale mantenuto solo nel raw locale, senza redistribuire articolo o fotografia. Non è una fonte operativa ufficiale.

## Ipotesi fissate prima del calcolo

Il [riferimento cartografico dell’Ente Parco](https://www.gransassolagapark.it/pdf/FonteVetica-Eng.pdf) colloca Fonte Vetica a42°25′31,78″N /13°44′29,22″E, ossia42.42549444444444,13.74145. Questo punto della località è usato come **innesco rappresentativo ipotetico**, non come posizione del rogo accertata. Protocollo registrato nella VM prima dei job; criterio: se il punto fosse non combustibile, fermarsi senza spostarlo silenziosamente. Il punto è risultato eseguibile senza spostamenti.

Tre casi condividono innesco, terreno, meteo congelato, orologio, seme1729,2realizzazioni e durata72h:

1. Senza interventi.
2. Una squadra generica con rimozione ideale del combustibile in un’area di circa100×100m centrata sull’innesco, attiva da0min.
3. Stessa squadra/area, attiva da60min.

Categoria, area e tempi sono inventati per la prova, non desunti dalle operazioni riportate. Rimozione istantanea e completa del fuel non equivale a una squadra capace di realizzarla: niente efficacia, durata del lavoro, acqua, strade, sicurezza o autorità operativa qualificata. Il caso immediato è un controllo limite che intercetta il combustibile all’innesco, non una strategia dimostrata praticabile.

Inizio **18/10/2026 alle12:00UTC (14:00Roma)**; termine21/10 alle12:00UTC. È una prova futura ispirata alla notizia: non ricostruisce il17ottobre e non prevede l’incendio già in corso, del quale manca lo stato iniziale. Input GLO30/WorldCover2021, vento distribuito e moisture hFFMC1977 con FFMC iniziale85 assunto, come ADR-0014. Campo reale `map-weather-c8a8114d6aa219ff5ac51474`, riusato con verifica di copertura del nuovo dominio; non viene inventata una nuova acquisizione. Terreno `e97be42ecdae76e0a67e32ae3869c23edda7de8516287df69686b0a4cd21e684`. Spec riproducibile [examples/fonte-vetica-20261018.json](../examples/fonte-vetica-20261018.json).

## Risultati tecnici osservati

| Scenario | Job | Stato | Frame | Area media finale simulata ha | Realizzazioni con fronte a72h |
|---|---|---|---:|---:|---:|
| Senza interventi | job-9007a1fc063749dba5bed8b55f8e05a6 | PASS/SUCCEEDED |288|2766,195|2|
| Intervento ideale immediato | job-7ebc9b72a7054bdba6d7df5de3b1683c | PASS/SUCCEEDED |288|0,09|0|
| Intervento ideale dopo1h | job-7e29200923e649acbba9e6274c6cb051 | PASS/SUCCEEDED |288|1486,17|1|

Queste aree sono controfattuali non calibrati, **non ettari del rogo reale né una stima dell’efficacia dei soccorsi**. Non viene scelta o adattata l’umidità per aumentare la propagazione. PASS identità di terreno/meteo/seme/inneschi, stessa evoluzione prima dell’intervento ritardato, celle fuel realmente modificate e prodotti nativi finali diversi. Verificati indipendentemente15asset,864frame e864PNG per SHA;145pin motori invariati. Due realizzazioni e un seme su un singolo caso non dimostrano skill, significatività o generalizzazione. Specie, stato stagionale dell’erba, moisture iniziale e risoluzione meteorologica in montagna restano minacce alla validità; la disponibilità di un DEM non elimina il bias DSM né qualifica i combustibili.

PASS21test webVM (3dedicati alle prove separate),19controlli browser del caso e30regressioni del percorso generico;6axe senza violazioni a375/768/1440. Provati caricamento dei3risultati e relativi meteo congelati, modifiche della sola copia, persistenza/reload e ripristino, rifiuto di case sconosciuto/traversal/vuoto senza fallback al workspace principale. Workspace principale rev59 invariato. Il test ripristina solo la prova, non tocca gli scenari dell’utente. Caricamento di una prova e sue modifiche non avviano automaticamente altri job. I nuovi calcoli riacquisiscono la previsione di base quando necessario, senza ereditare in modo nascosto il forcing_id della vecchia esecuzione.

VM unica invariata4vCPU/8GiB/19GiB, almeno7.622.447.104byte liberi al checkpoint. Nessuna installazione, costo, dispatch o servizio esposto; sorgenti gratuite con gli stessi limiti. Nuovi benchmark FPS/p95/soak e nuova installazione da zero NOT RUN. Nessun FAIL tecnico nei run nativi/finali di questa prova; accesso web iniziale alla pagina FAIL, recupero HTTPS nella VM PASS. Il dato mancante rimane mancante, non una bassa criticità.

**BLOCKED:** ricostruzione/validazione dell’evento vero finché mancano innesco/perimetri/cronologia e osservazioni utilizzabili; qualificazione fuel/moisture/soppressione/logistica e fullM5–M7 invariati. Nessuna H1–H3 o conclusione scientifica anticipata. La prova è un caso pilota preregistrato di integrazione e confronto; l’intervento immediato era deliberatamente favorevole per geometria e tempo, quindi non è un confronto di politiche operative.

## Riprodurre nella VM

Con runtime e servizio della [guida](../docs/INSTALLAZIONE.md) avviati, da app:

```sh
PYTHONPATH=src ../core-env/bin/python scripts/prepare_fire_case.py \
  --runtime "$HOME/hazardia-runtime" \
  --spec examples/fonte-vetica-20261018.json
```

Lo script genera una nuova partenza futura, preregistra la spec, esegue i3job e registra la prova solo quando tutti sono completati, con inizio e meteo comuni. Non sovrascrive una prova già registrata: usare un nuovo ID nella spec per un nuovo snapshot. I dati live saranno diversi, quindi questo percorso non è un replay esatto del run20261018. Per registrare risultati già conservati aggiungere `--from-run /percorso/run`: questa modalità è stata realmente eseguita qui e verifica identità del risultato nell’archivio attivo e hash degli asset. Il percorso completo di acquisizione/simulazione è stato eseguito con il probe preregistrato, conservato nel raw; nuova ricostruzione su un’altra VM NOT RUN.

Definizione runtime in `web-assets/fire-cases/`, bozze separate in `web-state/fire-case-workspaces/`, modelli e cache nei percorsi usuali. `/api/fire-cases` elenca le prove; `/api/fire-workspace?case=<id>` indirizza solo quella copia. Il catalogo non crea workspace; il primo accesso esplicito inizializza la copia. Raw: `experiments/runs/fonte-vetica-20261018` e omonimo nella VM, con protocollo, input, risultati, registrazione/audit/script, test/screenshot. [Sommario verificato](fonte-vetica/verification.json). Fotografia, HTML della notizia, raster e stato utente non pubblicati.
