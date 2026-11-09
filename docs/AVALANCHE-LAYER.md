# Valanghe — perimetro corrente

Il livello mostra il potenziale pericolo territoriale e i dati mancanti, con neve/meteo a72ore e terreno alla risoluzione documentata. Il monitoraggio dei sentieri è stato rimosso su richiesta dell'utente del30ottobre2026: nessun caricamento o aggiornamento degli incroci dalla mappa. Codice e cataloghi precedenti restano archivio; gli endpoint legacy non sono stati ritirati in questo incremento UI e non vengono più chiamati dal livello.

“Detect” non significa che una valanga in corso sia stata osservata: tale capacità non è disponibile. Distacco e propagazione restano da validare; nessun segnale non equivale a sicurezza. Il lavoro futuro privilegia terreno/PRA, neve, instabilità e scenari di propagazione, con incertezza esplicita. Esposizione/rischio differiti.

## Funzioni storiche superate: sentieri

# Identificare un sentiero

Passare sul tracciato mostra nome/riferimento e ID OSM; cliccarlo apre i dettagli e lo evidenzia con un bordo azzurro e un’etichetta persistente. Il colore interno mantiene la valutazione valanghe. Nome o riferimento assenti sono dichiarati; ogni tratto resta identificabile tramite ID OSM. La selezione riguarda le porzioni acquisite dello stesso way, senza estenderla a tutto l’itinerario. **Rimuovi selezione sentiero** elimina l’evidenziazione.

# Sentieri e valanghe · 30 ottobre 2026

In **Valanghe → Sentieri e valanghe** sono disponibili i tracciati OSM del Gran Sasso, con riferimenti CAI dove dichiarati nei tag. Rosso corallo: sole porzioni intersecanti il potenziale modellato; ambra tratteggiata: vicinanza entro 250 m in pianta, non zona di arrivo; bianco: altri tratti mappati, non sicuri; grigio: dati incerti o fuori copertura. Le valutazioni precedenti/non allineate diventano grigie. Cliccare un tratto o scegliere un esempio per leggere itinerario, fonte, date, difficoltà/accesso dichiarati e lacune.

**Carica/aggiorna sentieri nell’area visibile** acquisisce una finestra italiana fino a 2.500 km²: avvicinare prima la mappa. Non è ancora un inventario nazionale acquisito. L'incrocio si aggiorna con le nuove versioni della previsione a 72 ore; la fonte OSM viene riusata e ha una propria data. Nessuna certificazione CAI/INFOMONT indipendente, previsione di distacco o percorribilità. Mancano zone d'arrivo/runout: un sentiero a valle può essere esposto anche senza intersezioni. [Rapporto e prove](../reports/avalanche-trails/REPORT.md).

---

# Gran Sasso30m esteso e lacune separate ·30ottobre2026

«Gran Sasso · dettaglio terreno e profili» e «Pendii orientali · dettaglio30m» inquadrano ora la finestra30m estesa a circa1.824km², compresi i pendii prima rappresentati200m. Nella parte estesa i contorni derivano dalla pendenza del DSM30m, con interpolazione lineare del livello30° e semplificazione3m, senza inventare dati della neve a questa risoluzione. Rimangono i610supporti30m originari e i20profili locali sintetici nei loro limiti di rappresentatività; altrove neve da colonna nazionale e vegetazione/suolo/substrato a supporto1km.

Due comandi indipendenti: **Mostra potenziale pericolo** (turchese pieno) e **Mostra dati mancanti e incertezze** (contorni grigi per dati necessari mancanti/neve non verificata; ambra per suolo/substrato parziali nelle aree di potenziale). I contorni non sono livelli di gravità. Anche senza contorni di lacuna mancano verifiche locali di stabilità e contatto neve-suolo. Nessun segnale non significa sicurezza. Eliminati i bordi interni fra riempimenti contigui; fuoriAOI resta il terreno200m. [Rapporto, prove e limiti](../reports/avalanche-gran-sasso-detail/REPORT.md). Le sezioni successive descrivono gli incrementi storici.

---

# Suolo/substrato nazionali e contorni corretti ·30ottobre2026

La vista combinata include ora SoilGrids WRB (suolo stimato) e carta litologica ISPRA100k: contesto nazionale su campioni1km, con classi miste e lacune esplicite.177.403/178.340supporti di rilievo con suolo e161.501con substrato; non precisione puntuale o osservazioni del contatto neve-suolo. Il GranSasso mantiene le associazioniARSSA250k. Cliccare un’area o usare «Valuta una posizione» per leggere fonti, classi presenti e campioni mancanti. Tratteggio=suolo/substrato parziali o mancanti.

Rimossi i grandi riempimenti dei supporti1km: nazionale da pendenze90m mediate200m, contorni semplificati75m e ritagliati alla copertura originaria; GS30m. I contorni seguono porzioni ripide, non aree di distacco né precisione nivologica fine. Piccole porzioni ripide possono essere escluse dalla media200m: nessun segnale non significa sicurezza. Nuova palette turchese/blu petrolio, distinta dagli edifici; contorni grigi senza riempimento per pendenza mancante, grigio trasparente per neve locale non verificata. Restano invariati i limiti di stabilità, attrito/acqua basale e runout. Suolo e roccia sono contesto cartografico, non nuovi coefficienti meccanici o probabilità.

Il nuovo ciclo automatico realmente completato usa ICON-EU30ottobre00UTC e riferimento30ottobre06CET→2novembre06CET, tutte2.464+20colonne disponibili. Cartografia congelata/checksummed, ricombinata automaticamente ai successivi cicli neve/meteo. [Rapporto e verifiche](../reports/avalanche-national-ground/REPORT.md). Le sezioni sotto descrivono incrementi precedenti, superati da questo aggiornamento dove indicato.

---

# Potenziale pericolo combinato ·30ottobre2026

La vista iniziale ora evidenzia le combinazioni di neve modellata e terreno ripido, con temperatura, vegetazione e fondo cartografato consultabili per posizione. In Monitoraggio → Livelli → Valanghe usare **Gran Sasso · dettaglio terreno e profili**, poi cliccare un’area oppure «Valuta una posizione». Il pannello mostra le cause, la scala dei dati e ciò che manca. Grigio: dati necessari o neve locale non verificati; tratteggio: suolo/substrato mancanti. Colori diversi descrivono combinazioni fisiche, senza scala di gravità ufficiale.

Terreno nazionale1km da pendenza nativa90m e WorldCover2021; dettaglio GranSasso30m, suoli/substrato1:250000. Aggiunti20profili SNOWPACK locali sintetici, con trasferimento limitato a stessa fascia/copertura/esposizione e supporto5km/300m; altrove colonna nazionale10km esplicita. Temperature aria e superficie terreno da NWP, senza inferire attrito misurato. Vegetazione cartografata2021, non stato attuale dell’erba. Il worker aggiorna automaticamente le previsioni72h e comprende i20profili nei nuovi cicli. Rimangono mancanti suolo/substrato nazionale, stabilità osservata, attrito/acqua basale, accumuli locali e zone d’arrivo. **Potenziale pericolo, non probabilità calibrata o distacco garantito.**

Provenienza, risultati, riproduzione e verifiche nel [rapporto combinato](../reports/avalanche-potential/REPORT.md). Le sezioni precedenti sotto descrivono gli incrementi storici e i loro limiti allora vigenti, superati dove indicato da questo aggiornamento.

---

# Aggiornamento automatico attivo ·29ottobre2026

Lo snapshot statico descritto sotto è storico. La richiesta successiva ha attivato un worker autonomo nella VM: acquisizione neve/meteo, corsa ICON-EU unica e SNOWPACK72h, controllo ogni5min/nuovo ciclo completo circa6h. APIstato/versione, refresh mappa60s, misure nivometriche separate, missing/stale/errore espliciti e valutazione per coordinate/click. I risultati restano condizionali su campioni10km: non rilevano affidabilmente distacchi sui singoli pendii. Profili osservati, stabilità, vegetazione/suolo/substrato nazionali e probabilità calibrata mancanti.

Fonte corrente, architettura, quote, conservazione, riproduzione e prove: [rapporto aggiornamento automatico](../reports/avalanche-auto/REPORT.md). Worker`../HAZARDIA-Avalanche/src/hazardia_avalanche/worker.py`, controllore`web/avalanche_refresh.py`; opt-in`avalanche-auto-config.json`con enabledtrue. Funziona con Mac,VM e servizioHAZARDIA accesi; non serve tenere la mappa aperta. Superati i divieti storici di aggiornamento automatico/core di questo incremento.

---

# Valanghe in HAZARDIA

In Monitoraggio → Livelli → Valanghe, attivare il livello e usare «Inquadra copertura nazionale». Il pannello destro permette di scegliere fattori combinati sulle intere 72 ore oppure neve al suolo a +24, +48, +72 ore. I valori sono consultabili cliccando le celle oppure usando «Campione valanghe» e «Apri valori del campione». Il GeoJSON con provenienza si scarica dal pannello.

## Prodotto disponibile

Snapshot `avalanche-factors-20261029-01`, importato dagli output immutabili di `../HAZARDIA-Avalanche`. Riferimento 29/10/2026 20:00 UTC, termine 01/11/2026 20:00 UTC (21:00 CET in entrambi i casi). ICON-EU corsa unica del 29/10 ore12UTC; SNOWPACK3.7.0/MeteoIO2.11.0 già eseguiti nel progetto autonomo. L’integrazione non riesegue SNOWPACK e non aggiunge un motore al dispatcher FIRE/FLOOD.

2.464 colonne campionate su griglia10km; 2.463 output primari disponibili, IT0081 mancante per fallimento numerico. Impronte della griglia EPSG3035, origine4040000/2680000, ritagliate sul confine GISCO Italia2024; le coordinate dei campioni non sono i centri delle celle. Selezione del rilievo: quota≥600m oppure quota≥200m con dislivello locale≥300m su11km. Include colline e non è una delimitazione legale delle montagne. Celle e campioni non sono versanti né aree di distacco; non si interpolano condizioni locali dentro le celle.

Le combinazioni sono descrittive: pendenza campionata≥30° con aumento netto massimo di SWE>0,001kg/m² (72campioni) e/o acqua nel manto>0,001kg/m² (64campioni), entrambe53. Sono massimi sull’intero periodo e possono avvenire in ore diverse. 19solo carico,11solo acqua,53entrambe,2.380senza combinazioni selezionate,1mancante. I conteggi si sovrappongono e non misurano eventi, superfici, percentuali di probabilità o livelli EAWS. La tolleranza numerica non è una soglia critica di distacco; la pendenza inferiore a30° non esclude valanghe. Per leggibilità, i campioni senza combinazioni sono nascosti nella vista iniziale e attivabili con un’opzione esplicita; la vista neve mostra tutta la copertura campionata.

Neve iniziale da NWP e profili sintetici: mancano stratigrafia e stabilità osservate, distribuzione locale degli accumuli da vento, acqua basale/attrito neve-suolo. Vegetazione, suolo e substrato non sono integrati nel prodotto nazionale. Nessuna probabilità calibrata, diagnosi verificata di strati deboli, previsione di scorrimento, conseguenze o rischio. Le definizioni [EAWS](https://www.avalanches.org/standards/avalanche-problems/) descrivono ulteriori condizioni fisiche necessarie: questi indicatori da soli non costituiscono diagnosi dei problemi valanghivi.

## Tempo e aggiornamento

Il livello ha un proprio selettore e un’etichetta permanente con data/anno/orario. È uno snapshot congelato indipendente dal cursore meteo generale. Dopo il termine viene marcato SCADUTO; resta consultabile come archivio e non viene esteso o presentato come previsione corrente. Non esiste ancora un aggiornamento automatico della catena di calcolo nazionale.

## Contratto locale e riproduzione

`GET /api/avalanche/layer` legge soltanto `RUNTIME/avalanche/{manifest.json,layer.geojson}`. Schema `hazardia.avalanche-screening/1.0`, SHA256 verificato, limite16MiB, categorie coerenti con i fattori numerici, identificativi unici, orizzonte72h e probabilità/grado sempreNULL. Un file mancante o invalido restituisce503, senza inventare valori. Nessun percorso, URL, import o comando è accettato dal client. Il modulo UI carica i dati solo all’attivazione, rimuove geometrie/etichetta alla disattivazione e non accede a database WII/TCIP.

L’importatore `scripts/import_avalanche_snapshot.py` richiede l’ambiente geografico della VM Linux esistente. Input: `factors.geojson`, `assessment.json`, `national-points.geojson`, `italy-boundary.geojson`. Output in una directory nuova; scritture esclusive, nessuna sostituzione silenziosa di snapshot. Il runtime corrente conserva gli input in `~/hazardia-runtime/avalanche-inputs`, il prodotto in `~/hazardia-runtime/avalanche` e la ricevuta in `~/hazardia-runtime/backups/avalanche-layer-20261029`. Copia locale del prodotto e manifest in `data/avalanche-snapshots/20261029-01`.

Verifiche e limiti della consegna: `reports/avalanche-layer/`, requisito FR-AVALANCHE-LAYER-20261029. Non sono autorizzate implicitamente qualificazione operativa, nuove risorse, servizi pubblici o dispatch.


## Valanghe: spazio conservato ed evoluzione72h ·30ottobre2026

Richiesta corrente autorizza recupero conservativo e incremento mirato della mappa. PASS tecnico: recupero conservativo e ripristino completo22.578file; workerREADY su2.484colonne, riferimento30ottobre19CET→2novembre19CET;9.936finestre verificate e28.568proiezioniJS coerenti; API/mappa reali e popup fattori controllati.53teststandalone e34testvalanghePASS. GranSasso71/73/249unità con potenziale nelle finestre0–24/24–48/48–72h, non eventi o probabilità.110job eworkspace core preservati. Browser finale senza errori; screenshot delivery.png e dettagli nel core reports/avalanche-evolution-space-20261030/REPORT.md, audit.json, projection-audit.json, ui-windows.json e backup/restore-receipt.json. Nessuna milestone scientifica chiusa: strati deboli, stabilità, vento locale, attrito e runout indisponibili. PayloadAPI83,9MB e costo completo su rete/mobile ancora da migliorare/misurare; cambio periodo146–187ms è solo roundtripcontrolloDOM locale. Prossimo passo: qualitàsource-time e campioneHRL/PRA nel piano già approvato, senza un nuovo indice non validato.

Contratto aggiuntivo metadata.temporal_schema=hazardia.avalanche-windows/1.0, forecast_windows[colonna][lead0/24/48/72], supporti stati[a,b]/precipitazioni(a,b], carico precedenteNULL al riferimento. Potenziale proiettato sulle stesse geometrie; nessun fallback temporale o probabilità. Scope standalone mantenuto; core solo consumer e supervisore preesistente.


## CTX — TINITALY e vista essenziale ·30ottobre2026

Incremento autorizzato dopoAbruzzoMap: vista essenziale reversibile per strade/percorsi, nomi e meteo sovrapposti; lacune mantengono toggleindipendente e non sono sentieri. AnteprimaTINITALY10m separata, campione9km², nessun aggiornamento del terreno del motore o diSNOWPACK. Metadati unità/datum daqualificare; rasterneve senza timestamp/provenienza/diritti delderivato non assimilati; campioneTCDancoraNOTRUN. PASStecnico sintassi2JS/HTTPassetSHA/browser ripristino;110job/workspace eprodotto72h invariati. Prove: reports/avalanche-tinitaly-20261030/REPORT.md, publication-audit.json, clean-view-final.json, terrain-preview-ui.png, delivery.png. Mantiene l’orizzonte72ore e gli stessi conteggi del prodottoEV. Nessun gate scientifico chiuso.


## QV — correzione dei contorni di qualità ·30ottobre2026

La segnalazione utente di reticoli grigi identifica un difetto di rappresentazione dei supporti: i contorni delle lacune sono sostituiti da simboli informativi raggruppati perzoom (? grigio/i ambra), con spiegazione selezionabile. Non sono perimetri o posizioni di distacco. Toggle qualità indipendente; poligoni originali, classi, querycoordinate/export e previsione72h conservati.40testLinuxPASS inclusi6nuovi QuickJS; verifica indipendenteShapely su7142geometrie/3viste, conteggi conservati e ancore nel supporto.3JS serviti conSHA verificato,110job/workspace eprodotto nativo invariati. Nessuna validazione scientifica da questa correzione. Evidenze core reports/avalanche-quality-markers-20261030/REPORT.md, tests.log, annotation-audit.json e publication-audit.json. Le precedenti descrizioni del grigio come contorno sono storia, superate da questa rappresentazione.


## SURF — valutazione ad aree ripristinata ·30ottobre2026

Richiesta utente successiva: rifiutata la UI a punti interrogativiQV e ripristinata la valutazione territoriale. Vista primaria con tutte le2.121unità di pendio cartografate:464potenziale e1.657neve/dati locali non verificati nel riepilogo72h, con superfici senza bordatura tecnica. Zeroicone ?/i;446rettangoli con pendenzaNULL restano lacune nei conteggi/dettaglio/export, non pendii inventati. Riattivati riepilogo72h originario e comandi diretti neve24/48/72/colonneSNOWPACK; finestre temporali conservate. Visibilità/modalità/periodo/toggle conservati nella sessione della stessa scheda; vista essenziale opzionale nasconde anchePOI contestuali e ripristina stati precedenti. UIprecedenteQV superata, dati e prove conservati.46testLinuxPASS (6nuovi), sintassi3JS e audit realeinputinvariati;110job/workspace preservati. Prove core reports/avalanche-slopes-restored-20261030/: protocol.json, audit.json, avalanche-surfaces-tests.log e browser-views.json. PASStecnico, nessuna chiusura scientifica o affermazione di neve osservata in aree non verificate.
