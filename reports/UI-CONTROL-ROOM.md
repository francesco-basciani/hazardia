# Interfaccia HAZARDIA: confronto con i riferimenti e revisione

Data: 16 ottobre 2026. Run: `ui-controlroom-20261016`. Revisore: Codex, autocontrollo tecnico. Runtime: stessa VM UTM Linux; Mac per sviluppo, browser e copia delle evidenze.

## Cosa cambia per chi la usa

La mappa è la vista iniziale. La navigazione separa **Mappa**, **Risultati**, **Dati e fonti** e **Guida**. Su telefono e nei pannelli stretti i comandi dello scenario si aprono dal pulsante «Scenario e interventi», lasciando spazio alla mappa. Configurazione avanzata, provenienza scientifica e prove di guasto sono chiuse inizialmente.

1. Scegli incendio o alluvione; cerca una località o coordinate. Lo sfondo predefinito resta l’ortofoto regionale dettagliata, con Sentinel offline come alternativa esplicita.
2. In «Livelli e sfondo» regola l’intensità del colore, mostra/nascondi risultati e gruppi del test, cambia sfondo e nomi geografici.
3. Usa «Misura distanza», «Disegna area» o «Aggiungi nota». Puoi cliccare sulla mappa oppure inserire coordinate per lavorare da tastiera. Termina per salvare nella VM; Esc annulla una bozza. I contorni che si incrociano vengono rifiutati nel disegno UI. Le misure non sono percorsi stradali né rilievi catastali: distanza geodetica fra vertici, area planimetrica locale approssimata.
4. Apri «Note, coordinate e viste salvate» per salvare/richiamare l’inquadratura ed esportare l’archivio. «Esporta GeoJSON» esporta annotazioni con coordinate longitudine/latitudine, esplicitamente prive di effetto sui simulatori.
5. Apri «Prova un’evacuazione», imposta unità e accessibilità, quindi «Confronta evacuazione». Si affiancano A/B; in «Risultati» trovi persone ipotetiche esposte, assegnazioni e verifica dei vincoli. Il pericolo fisico resta uguale.
6. «Casi salvati» conserva nome, riferimento al risultato fisico e impostazioni del singolo pericolo. Ripristinare un caso richiede un nuovo calcolo del piano; non riutilizza una decisione vecchia. Il salvataggio congiunto a due pericoli non è supportato e viene spiegato esplicitamente.
7. «Incendio su 1–3 giorni» apre i raster orari nativi già verificati, con/senza fascia tagliafuoco ideale. Il controllo senza intervento conserva uguaglianza esatta A/B. Non è un editor libero di interventi fisici.

I testi chiariscono differenze tra fotografia, simulazione, persone inventate e vincoli verificati. Una guida spiega le parole principali. Questo è un miglioramento tecnico dell’interfaccia; la sua comprensibilità per utenti esterni non è ancora misurata.

## Cosa abbiamo potuto verificare dei riferimenti

[Tactical Analyst, pagina ufficiale Technosylva](https://technosylva.com/products/tactical-analyst/) descrive un quadro cartografico condiviso, incidenti e risorse, meteo e simulazioni, aree d’interesse, viste salvate, rapporti e collaborazione. È documentazione commerciale pubblica: non abbiamo avuto accesso al prodotto autenticato o verificato le prestazioni dichiarate.

[Geospace / Envair360](https://wildfire.geospace.es/) è stato ispezionato nel browser. Osservati navigazione per analisi, evoluzione, storico, simulatore, fonti e catalogo; nel simulatore erano presenti punto d’innesco sulla mappa, parametri vento/umidità/pendenza e legenda temporale. Non abbiamo eseguito un confronto scientifico del suo modello. Il tentativo di aprire «Mapa Operacional» ha mostrato un errore del sito: questa parte non è verificata. La lettura tramite estrattore web non era disponibile; il browser ha permesso l’ispezione. Snapshot del simulatore nel run locale, senza interazioni operative o invio di dati del progetto.

## Matrice funzionale: stato HAZARDIA

| Esigenza d’uso | Stato di questo incremento | Limite concreto |
|---|---|---|
| Mappa dettagliata, ricerca, coordinate e riferimenti locali | PASS, funzione esistente conservata e riorganizzata | Ortofoto datate; nomi Abruzzo, strade/POI solo area centrale L’Aquila; nessun confine amministrativo dedotto |
| Livelli, trasparenza e confronto singolo/affiancato | PASS | Griglia nativa invariata; esposizione sintetica |
| Misure, annotazioni e area disegnata | PASS | L’area non attiva una stima censuaria né modifica i motori |
| Viste e casi persistenti, esportazione GeoJSON/archivio/decisione | PASS | Nessun salvataggio congiunto; report cartografico PDF NOT RUN |
| Confronto fisico incendio e riproduzione 1/2/3 giorni | PASS, risultati precedenti riusati e interfaccia ricontrollata | Due realizzazioni, fascia ideale fissata; nessuna efficacia sul campo |
| Avvio arbitrario da punto sulla mappa e parametri meteo liberi | NOT RUN | Restano i controlli del job esistente su griglia e durate 10/30/60 minuti; nessuna falsa interfaccia collegata a un modello diverso |
| Confronto alluvionale con laminazione, argini e pompaggio | NOT RUN | Richiesti tutti dall’utente; HMC invasi da provare, idraulica locale da valutare |
| Dati e provenienza comprensibili | PASS per esposizione delle informazioni | Meteo ERA5 retrospettivo; non un livello di previsione operativa |
| Rilevamenti satellitari live, meteo live, storico eventi validato | NOT RUN in questa UI | Richiedono acquisizione, copertura e verifica temporale/coerenza con le simulazioni |
| Edifici/popolazione censiti, analisi impatto per area | NOT RUN | Non confondere gruppi sintetici con censimento o servizi disponibili |
| Risorse GPS, dispacciamento e collaborazione multiutente | NOT RUN | Nessuna azione reale; sistema locale di ricerca |
| Parità complessiva con i due prodotti | NOT RUN | È un obiettivo di copertura funzionale; nessuna equivalenza dichiarata |

## Implementazione e ripetibilità

Frontend locale senza nuove dipendenze o CDN; Leaflet esistente. `workbench.js` organizza sezioni, livelli, annotazioni e casi; non invia job fisici durante la navigazione. Disegni viola sono annotazioni dell’utente, separati dai prodotti nativi. Il confronto incendio conserva il manifest scientifico precedente.

`GET/POST /api/notebook` usa la stessa VM e le protezioni same-origin/Host della dashboard. Dati validati: massimo 20 casi, 20 viste, 50 annotazioni, 200 vertici per annotazione, 60 kB per contenuto. Revisioni confrontate prima della scrittura impediscono che una scheda sovrascriva cambiamenti di un’altra. Snapshot append-only, scritti atomicamente nella VM sotto `web-state/notebook`; fino a 500 snapshot, poi rifiuto esplicito. Le versioni precedenti restano recuperabili. I campi accettati non includono comandi, dispatch o percorsi di accesso ai file; il testo non viene interpretato come codice. Testo utente conservato come dato e protetto nell’HTML.

Comandi riproducibili nella VM, dalla directory `app`:

```sh
../core-env/bin/python -m unittest discover -s tests/web -v
../core-env/bin/python -m unittest discover -s tests/unit -v
../core-env/bin/python -m unittest discover -s tests/domain -v
../core-env/bin/python -m unittest discover -s tests/decision -v
```

QA browser sul client di visualizzazione, mentre API, archivi e prodotti rimangono nella VM:

```sh
node tests/browser/control-room.cjs experiments/runs/ui-controlroom-20261016/browser-handoff
node tests/browser/physical-fire.cjs experiments/runs/ui-controlroom-20261016/physical-final experiments/runs/m3-dashboard-20261015T192310Z/axe.min.js
```

I percorsi assoluti del runtime Node/Chrome di questo Mac sono fissati negli script di QA già in uso; non sono dipendenze di esecuzione della piattaforma. Chrome e metriche effettive sono registrati nei JSON dei risultati. I controlli di browser usano i prodotti scientifici già esistenti, senza nuove esecuzioni CIMA.

## Esiti e problemi

- PASS: 6 test nuovi di archivio/concorrenza/validazione; 38 unitari preesistenti, 19 di dominio, 14 del decision engine. Totale 77.
- PASS: integrità dei 145 file dei motori e manifest del confronto incendio invariato (`69ddda1244015b7470ca6ed823ccf1aa7011157733c3a4e202bff0600b6fb684`).
- Primo test browser FAIL per errore nel test: URL API relativo senza `baseURL`; nessuna asserzione dell’app eseguita. Secondo/terzo tentativo: aspettativa errata sullo zoom salvato e selettore di navigazione ambiguo, poi corretti. Log originali conservati; non sono risultati scientifici o difetti dei motori.
- FAIL iniziale di accessibilità nella pagina incendio: nuovo sfondo scuro dei pulsanti con testo scuro. Correzione locale del colore del testo; esito del controllo successivo nel registro ufficiale.
- Test automatici e misure della revisione finale: vedere `CHECKLIST.md` e i JSON `browser-handoff/results.json`, `physical-final/results.json` del run, senza sovrascrivere prove precedenti.
- NOT RUN: nuovo soak di 30 minuti, nuova prova con 100k elementi, studio di usabilità con utenti, qualificazione fisica/storica. Il precedente soak e il precedente FAIL a 100k elementi non si trasferiscono automaticamente a questa UI.

## Prossimo incremento

La richiesta «Voglio tutto» del 16 ottobre include laminazione, argini e pompaggio. Non è più pendente la scelta di un solo intervento alluvionale. Occorre esaminare e provare invasi/laminazione HMC con geometrie e configurazione ripetibili; valutare parallelamente, come attività di piano, la componente idraulica necessaria per argini/pompaggio. Qualunque adozione o sostituzione sostanziale di motore resta una decisione architetturale da presentare con evidenze prima di applicarla. La UI non deve introdurre controlli fisici non collegati a prove reali. L’estensione richiesta non autorizza costi, servizi pubblici, operazioni reali o superamento dei limiti della VM.

## Metriche finali della revisione

PASS:54controlli browser principali +18del confronto fisico.15scansioni axe senza violazioni, con verifiche incomplete conservate nei file grezzi. Chrome 155.0.8059.84. Feedback locale p95: hazard-layer 16.2 ms; opacity 3.3 ms; comparison 16.6 ms; navigation 16 ms, su almeno30interazioni per azione. Cadenza RAF al quinto percentile su30pan: 59.993FPS, non misura diretta del compositore GPU. Segnale di visualizzazione utile a browser freddo, backend già avviato: [195.3, 186.2, 207.1]ms, indipendente dall’eventuale completamento dello streaming ortofoto. APIarchivio p95su30letture:69.31ms. Finestra di carico piccola, dati congelati; nessuna generalizzazione a eventi reali, scale maggiori o usabilità dimostrata.

Final evidence transport PASS: 241regularfiles in VM archive, SHA256`ec8c37cd00f5184754771e40c502785dda962dc3df8ebced05a7edc058841fec`; transport-verification.json. Runtime checkpoint2026-10-16T04:47:17.831825+00:00: cumulative conservative download3,301,968,232B/5,368,709,120B; freeguestdisk12,569,681,920B;4vCPU/8GiB/19GiB unchanged. Notebook cleanup guard independently checked against immutable VM snapshots: original content preserved, revision25→29→30. GUI evidence reports/dashboard-evidence/ui-controlroom-20261016/anteprima.png.
