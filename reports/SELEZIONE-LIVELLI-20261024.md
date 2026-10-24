# Selezione di ulteriori livelli — 24 ottobre 2026

Run `layer-selection-20261024`, base HAZARDIA `6fc3327`; revisore Codex, analisi documentale e lettura delle cache nella VM. Nessuna implementazione o modifica di configurazioni attive. M0–M7 e qualificazione scientifica invariati.

## Metodo ed esito

PASS: rivalutato il repository ufficiale bilawalsidhu/gods-eye-view, README, DATA_SOURCES e LICENSE alla revisione `9d3548c27c2cd4bf80ea39cbb3f0634ab1c5a06b`. Copie originali e SHA256 in `/home/hazardia/hazardia-runtime/runs/layer-selection-20261024/`; ricevute in [audit.json](layer-selection/audit.json). Download documentali circa183KiB nella VM; nessuna installazione. È una nuova verifica documentale, non un aggiornamento del codice di riferimento già esaminato il23ottobre. La licenza del codice non concede automaticamente i diritti sui dati terzi.

PASS: esaminata la classificazione effettiva `src/hazardia/osm_catalog.py` e letti79snapshot delle cache territoriali della VM, selezionati con angolo sudovest entro12.8–14.9E e41.5–43.1N. Deduplicati10157oggetti OSM identificati, mantenendo per ID il timestamp OSM maggiore. Il filtro è un intorno di studio, non il poligono regionale. Le date degli snapshot e bounding box sono nell'audit. Nessuna acquisizione OSM aggiuntiva né modifica delle cache.

Questi sono oggetti già recuperati, non nuovi oggetti censiti oggi. Le cache sovrapposte sono parziali e possono avere epoche diverse, geometrie proxy e attributi mancanti. Il conteggio dei tag non certifica la geometria, l'operatività o la completezza territoriale; ponti/tunnel possono includere infrastrutture non stradali e un'infrastruttura può essere suddivisa in più oggetti OSM. Zero significa non trovato negli estratti esaminati, non assenza nel territorio. Non sono stati eseguiti test prestazionali o nuove simulazioni fisiche: NOT RUN, non pertinenti a questa valutazione.

## Incremento consigliato: filtri tematici sui dati esistenti

| Priorità e livello proposto | Riscontro locale nei tag conservati | Integrazione utile e limite |
|---|---|---|
| 1. Acqua per antincendio |44 `emergency=fire_hydrant`;0 water_tank/suction_point/fire_water_pond | Separare dal generico emergenze; pressione, portata, accessibilità e funzionamento sconosciuti restano sconosciuti. Non classificare laghi/invasi automaticamente come punti di pescaggio autorizzati |
| 1. Ponti, sottopassi e vincoli di accesso |30oggetti bridge,71tunnel,1ford;12vie highway con almeno uno tra maxheight/maxweight/maxwidth/width | Filtrare per funzione stradale/ferroviaria/idrica; mostrare limite legale distinto da fisico. Non equivale a routing verificato, strada aperta o chiusura osservata |
| 1. Rete idrica e opere idrauliche |16oggetti waterway;5 dam/weir/man_made=dyke | Già nel gruppo ambiente/servizi; rendere distinguibili corsi d'acqua, dighe, sbarramenti e argini. Mancano portata attuale, stato e capacità; non sostituisce HMC/REFlEx o idrometri |
| 1. Strutture sensibili |2ospedali/cliniche,12strutture educative,1social_facility | Raffinare i livelli sanità/istruzione già esistenti senza duplicarli; tipo di assistenza da social_facility e social_facility:for se presenti. Nessuna deduzione di pazienti, posti disponibili o persone esposte |
| 2. Impianti e infrastrutture critiche |5sottostazioni,4distributori carburante,1oggetto industriale,65oggetti railway | Sottocategorie dei gruppi servizi/trasporto: sottostazioni distinte dai cavi aerei. Tag industriale non dimostra presenza di sostanze pericolose, rischio Seveso o stato operativo |
| 2. Punti di raccolta e appoggio aereo |0assembly_point,0helipad | NOT RUN nuova ricerca mirata e copertura locale; nessun nuovo controllo vuoto. Assembly_point non implica area di accoglienza pubblica e helipad non implica base antincendio disponibile |

Le prime cinque righe hanno presenza positiva negli estratti; il nuovo filtro visuale e la sua verifica restano NOT RUN. Preservare tutte le proprietà OSM originali. Nessuna nuova categoria diventa automaticamente input di ottimizzazione/esposizione solo perché visualizzata.

## Cosa prendere dal riferimento, con quali condizioni

- Dighe e datacenter sono esempi di filtri tematici OSM: il reference distribuisce estratti finiti, non inventari mondiali completi. Dighe già presenti nel catalogo HAZARDIA; datacenter=0negli estratti verificati, utilità secondaria rispetto a rete elettrica/acqua/sanità. Nessun nuovo controllo datacenter ora.
- Immagini stradali KartaView/Panoramax: utili per esaminare ingressi e accessi, con data e diritti per immagine. Candidato nuovo; NOT RUN query locale e prova end-to-end. La documentazione Panoramax conferma catalogo/API e riuso; la pagina termini KartaView via web ha restituito solo caricamentoJS, quindi la dichiarazione del reference non è una verifica indipendente completa dei termini. Non garantire copertura Abruzzo/Italia/Senegal né attualità delle foto.
- Anomalie termiche FIRMS: priorità di completamento dell'incarico precedente, non nuovo livello. BLOCKED dall'assenza di MAP_KEY gratuita configurata. Conservare distinzione fra anomalia, incendio confermato e simulazione. Nessuna chiave richiesta a nome dell'utente.
- Perimetri NIFC/WFIGS: prodotto statunitense; non trasferire la copertura all'Italia. Perimetri locali verificati ancora BLOCKED come nel report23ottobre. Radar MRMS statunitense non sostituisce radarDPC già integrato. Il feed fulmini nowCOAST del reference copre Americhe/Pacifico, non è la soluzione Abruzzo. AQHI canadese non è qualità dell'aria locale. Connettori diversi richiedono fonti europee/regionali e verifica propria.
- Webcam, traffico osservato, aeromobili selezionati: ancora candidati subordinati a utilità, diritti, freschezza e copertura; niente credenziali o feed commerciali nuovi. Non importare automaticamente tutti i feed di telecamere del reference.
- Popolazione, idrometri, suolo/vegetazione e fumo: esigenze precedenti da completare/qualificare con fonti appropriate; OSM da solo non dà censimenti di persone, livelli idrometrici live, umidità del combustibile o dispersione del fumo.
- Preservate esclusioni confermate per livelli militari, missioni/orbite, GNSS,ALPR,cavi sottomarini,radio,Transit/BikeShare. Terremoti e traffico simulato restano le eccezioni esplicitamente autorizzate successivamente, già realizzate nei rispettivi percorsi.

## Organizzazione e prestazioni da verificare nell'implementazione

Riutilizzare catalogo e un'unica geometria per oggetto, con filtri dedicati; caricamento su richiesta per area e zoom, semplificazione/aggregazione e limiti di oggetti. Livelli inizialmente spenti, simboli/legenda precisi, opzioni a sinistra come da ultima richiesta. Nessun nuovo pannello Risorse/accessibilità autonomo, nessuno scenario/traffico simulato nel Monitoraggio. Rendering nel browser, acquisizione e cache nella VM.

Il riuso evita download duplicati, ma non prova fluidità: NOT RUN benchmark di queste nuove viste. Prima di attivarle verificare conteggi e geometrie, on/off, missing e dati scaduti, mobile/Safari e tempi/frame/memoria al limite. Nessun incremento RAM/CPU necessario dimostrato dalla sola analisi.

Prossimo incremento eseguibile consigliato: acqua antincendio + vincoli e attraversamenti stradali + rete idrica, quindi affinamento delle strutture sensibili. Solo dopo una ricerca positiva e qualificata aggiungere foto stradali/nuovi feed osservati. Questo report non introduce nuovi requisiti normativi o controlli nella dashboard.

## Fonti primarie consultate

- [God's Eye View: sorgenti e diritti](https://github.com/bilawalsidhu/gods-eye-view/blob/9d3548c27c2cd4bf80ea39cbb3f0634ab1c5a06b/DATA_SOURCES.md).
- [OSM idranti](https://wiki.openstreetmap.org/wiki/Tag:emergency%3Dfire_hydrant), [accesso emergenze](https://wiki.openstreetmap.org/wiki/Key:emergency), [limiti in altezza](https://wiki.openstreetmap.org/wiki/Key:maxheight).
- [OSM rete idrica](https://wiki.openstreetmap.org/wiki/Key:waterway), [strutture sociali](https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dsocial_facility), [punti di raccolta](https://wiki.openstreetmap.org/wiki/Tag:emergency%3Dassembly_point).
- [Panoramax](https://docs.panoramax.fr/), [FIRMS chiave gratuita](https://firms.modaps.eosdis.nasa.gov/api/map_key/).
