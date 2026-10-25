# Audit del framework e dei livelli — 25 ottobre 2026

**Esito PARZIALE: non tutti i livelli hanno dati aggiornati e completi.** Corretti problemi reali di caricamento, ridisegno e storage. Nessuna certificazione scientifica o operativa. Base privata182b3c4; riepilogo misurabile in [verification.json](framework-audit/verification.json); prove grezze nella VM e nel run privato `framework-audit-20261025`.

## Protocollo

Soglie fissate prima del benchmark: feedback UI p95≤200ms, API in cache p95≤500ms, prima visualizzazione utile≤3s, obiettivo30 FPS; almeno30 campioni per serie,3 navigazioni, viewport375/768/1440. VM Linux aarch64,6 CPU/16 GiB; browser IAB Chromium155 sul Mac,DPR 2. Rendering sul client. Quote, fonti gratuite e archivi scientifici preservati.

Test sul working tree locale comprendente WII in sviluppo concorrente: i110 test WII non pubblicano o qualificano quel lavoro con questo incremento. Le3 navigazioni ricreano il documento JS ma condividono cache browser/backend caldo: cold-cache completo **NOT RUN**. Feedback evento→due requestAnimationFrame, non misura del compositore. Revisione dello stesso autore, non indipendente. Conteggi riferiti a vista/istante di prova, non completezza nazionale.

## Disponibilità dopo attivazione

| Livello | Esito reale | Fonte e limite |
|---|---|---|
| Vento, temperatura, umidità, pioggia, probabilità, nuvole, raffiche, pressione, radiazione | PASS campo globale:95 ore,9×9 campioni visuali,7.695 valori finiti/variabile,0 mancanti | Open-Meteo/DWD ICON Global+ensemble.25/10 00:00Z→28/10 22:00Z. Campioni interpolati, non risoluzione nativa. Archivio vento regionale fine pieno: aggiornamento fine BLOCKED, fallback globale FRESH dichiarato. |
| Accumuli previsti | Disponibile il calcolo sulle ore del campo | Precipitazione equivalente in acqua, può includere neve. Non è un’allerta o rischio locale qualificato. |
| Radar osservato | PASS: mosaico datato nazionale, circa49% celle valide, pioggia non nulla in parte del mosaico | Radar-DPC SRI, passo5min/griglia nominale1km. Fuori copertura/celle mancanti nessun dato. Overlay rimosso al futuro, non sostituito con osservazioni vecchie. |
| Pluviometri | PASS aggiornamento condiviso:3.995 stazioni,3.936 recenti alla lettura finale; inizialmente STALE durante ritardo orario | MeteoHub/ItaliaMeteo, sole reti CC BY4.0,25/10 10:00Z. Refresh≤1/ora. Misure puntuali provvisorie; vista stretta può avere0 stazioni. |
| Terremoti | PASS:211 acquisiti INGV,193 nella vista ampia,0 nella vista urbana stretta | Ultimi7giorni,M≥0. Cerchi per magnitudo, non raggio di danno. Nessun evento nella vista non equivale a guasto. Nuova acquisizione USGS mondiale NOT RUN. |
| Immagini recenti | PASS:2 anteprime realmente caricate e prima impronta attivata | Sentinel-2/Copernicus,23/10 e21/10,tessera33TUH; nuvole54,35%/99,46%. Anteprime343px, non raster analitici georettificati o cambiamento classificato. |
| Centri abitati | PASS parziale:24 località/aree nella vista urbana | OSM/contesto acquisito; non censimento o confini ufficiali. |
| Sanità e assistenza | PASS parziale:14 oggetti nell’estratto | OSM; capacità/apertura non verificate. |
| Emergenze e soccorso | PASS parziale:47 oggetti | Include idranti/AED; non47 squadre disponibili. |
| Istruzione | PASS parziale:12 oggetti | OSM, inventario parziale. |
| Strade e trasporti | PASS parziale:2.378 disponibili,2.368 nella vista urbana | Include ferrovie. Chiusure reali/percorribilità attuale non certificate. |
| Reti e impianti | PASS parziale:3 oggetti | CategoriaOSM generale, distinta dal livello elettrico dedicato. |
| Edifici | PASS parziale:1.742 disponibili,1.732 nella vista urbana | Visibili da zoom15, nascosti intenzionalmente sotto soglia; indicatore presente. |
| Ambiente e acque | PASS parziale:508 oggetti | Idrografia cartografica, non portata/idrometria osservata. |
| ConfiniOSM / altri oggetti | PASS parziale:8 /4.586 disponibili | Inventario generico, distinto da confini amministrativi. |
| Confini amministrativi | PASS 3 selettori:242 nazioni,20 regioni,110 province nel catalogo | Natural Earth mondiale1:50m; Istat2026 Italia generalizzato. Non province mondiali. |
| Cavi aerei e tralicci | **DEGRADATO**: providerlive timeout; snapshot verificato,3 oggetti acquisiti/1 nel filtro visibile | OSM limitato13.375–13.405E/42.345–42.360N. Snapshot disponibile17/10, osservazioneOSM non datata. Non reteAT completa, tensioni spesso assenti, nessun corridoio di volo certificato. |
| CriticitàDPC/EFFIS | **BLOCKED aggiornamento**: archivio256MiB pieno, snapshotSTALE; consultazione datata disponibile | DPC 187 zone/testi,183 geometrie utilizzabili. Bacino di Levante/Carso,Salento,Iglesiente,Gallura non classificabili. EFFIS 183/187. Grigio/scaduto non significa sicurezza. |
| Incendi/alluvioni dei simulatori | Dipendono da prodotti calcolati, non osservazioni | Replayincendio salvato provato:avvio,pausa+2h43,ripresa+2h45. Nessun nuovo job fisico o validazione dell’efficacia delle squadre in questo audit. |
| Traffico simulato | PASS attivazione:1.221 segmenti diretti,38 e400 veicoli provati | OSM23/10;44vie senza senso dichiarato,14 escluse per restrizioni,2 per accesso. Ipotetico sempre esplicito; nessuna coda/capacità/evacuazione o effetto sui risultati scientifici. Configurazione salvata non sovrascritta. |
| WII opzionale locale |110 testPASS, statoUNQUALIFIED_RESEARCH | Lavoro concorrente, non trasforma origini surrogate in incendi confermati. Nessun crawler/training avviato dall’audit. |

**Non connessi/qualificati:** hotspotFIRMSlive senza chiave, idrometri, popolazione/vulnerabilità/terreno locale qualificati, perimetri osservati correnti integrati nel monitoraggio. I perimetri storiciWII non costituiscono automaticamente un livello operativo live. Non aggiunti controlli vuoti o dati inventati.

## Correzioni

- Primo click sulle immagini recenti avvia ricerca e prima impronta; errori/caricamento anteprime espliciti.
- Query elettrica filtrata invece dell’intero estrattoOSM urbano che superava8MiB. Fallback solo da archivio esistente conSHA verificato, geometrie dipendenti preservate, copertura/data degradate esplicite. Nessuna promozione a input dell’ottimizzatore.
- MonitorOSM: layerLeaflet riutilizzati, bounds memorizzati, popup costruiti all’apertura; cache client 2 contesti/5min. Spostamenti non forzano più nuove copie di contesto; richieste accorpate.
- Ridisegni meteo duplicati per zoom/movimento accorpati al frame; valori/interpolazione scientifica invariati.
- Conteggi reali per categoria; legenda radar consolidata.
- CopieJSON territoriali immutabili condividono inode:114 coppie preesistenti deduplicate conservando ogni nome/contenuto/SHA;957.257.021byte duplicati recuperati. Nuove acquisizioni territoriali sospese sotto2GiB+64MiB; cache consultabile.

## Prestazioni e conformità

| Prova | Misura | Esito |
|---|---|---|
| APIcached |13 endpoint×30 GET validi, HTTP200,p95max101,35ms | PASS latenza, non aggiornamento. Imagery/trafficIDLE dopo riavvio e prima dell’attivazione distinti da errore. |
| Apertura pannelli |30 prove,p95≈18,9ms | PASS campione |
| Zoom14↔15 | Prima497,8ms; intermedio203,6ms; finale196,7ms/max202,8 su30 prove | PASS soglia p95 finale. Snapshot/carico fra fasi non identici; non speedup universale. |
| Prima mappa/meteo |3 documenti, tile≈501ms/meteo≈1.001ms, probe ogni500ms | PASS con cache calda; cold-cache NOT RUN |
| Fluidità30 FPS | Stress vento p95intervallo≈41,7ms; traffico400 veicoli34,2ms, drawp95≈0,30ms/300campioni | Uniforme30 FPS NON DIMOSTRATO; traffico≈29,2aggiornamenti/s al p95. Nessuna misura compositore. |
| Modello traffico |30 prove400 veicoli/12.000 segmenti, step+positionsp95≈0,024ms. Rete reale1.221 segmenti/36.000 step: seed riproducibile e via chiusa esclusa | PASS vincoli implementati, non evacuazione |
| Ottimizzatore |2 workload congelati×30,p95≈177/129ms entro60s | PASS pilot, esclusa codaHTTP/carico e simulazione fisica; non deadline globale |
| Servizio30min |121 campioni/1.800 s;8 senza listener,3 cambi PID durante riavvii; healthp95≈3,8ms quando disponibile,RSSmax≈227MiB | FAIL continuità; nessuna prova di assenza leak. Client30min ininterrotto NOT RUN. |
| Disco | Minimo2.085.511.168byte sotto riserva2GiB; finale≈2,995GB dopo dedup | Incidente conservato; riserva ripristinata. CPU/RAM aggiuntiva non risolve cache piene. |
| Layout |375×812,768×1024,1440×1000 senza scroll documento; pannelli separati con scroll interno | PASS smoke, WCAG completo NOT RUN |
| Inglese |28check automaticiPASS/1.599 voci; frasi dinamiche/attributi misti ancora visibili | PARZIALE |
| Safari finale | Profiling del browser esterno non eseguito | NOT RUN |

Regressione finaleVM:231 unit+53 web+19 domain+60 decision=**363 PASS**, più110 WII locali. Client22 suite MJS PASS. WarningPROJ core-env e deprecazioneRasterio conservati; non equivalgono da soli a errore del workergeo separato. Primo fixturepower fallito poi corretto,3GET iniziali senza parametriHTTP400, primi samplerPID errati conservati nelle prove grezze ed esclusi dalle serie finali valide.

## Preservazione e prossimi controlli

368 file archivio job verificatiSHA,0 modificati;114 coppie deduplicate ancora presenti/identiche. Nessuna modifica ai moduli motore/forcing monitorati. Nuovo replayPROPAGATOR/REFlEx end-to-end NOT RUN: gateM5–M7 e fallimento storicoREFlEx restano invariati. Nessun dispatch operativo.

Priorità: gestione archiviDPC/EFFIS/vento fine senza perdita di evidenze o aumento implicito quote; upstream elettrico e completezza locale; inglese dinamico; soak e Safari senza riavvii concorrenti; replay fisici su riserva disco sufficiente. Non promettere tutti i dati in ogni zona/orario.

Ripetibilità: inVM `PYTHONPATH=src:tests core-env/bin/python -m unittest discover -s tests/unit`, poi analogamenteweb/domain/decision e WII col proprioambiente. Client: ciascun fileMJS in `tests/browser`/`tests/web` conNode16, escludendo il solo helperfixture; `node tests/web/traffic-model.test.mjs <snapshot-traffic.json>` per rete reale. Aprire `/?view=map&diagnostics=...` per probeDOM opt-in. Conservare protocollo, versione, seed, snapshot e campioni senza rilassare soglie a posteriori. Screenshot locali in `reports/framework-audit/`.
