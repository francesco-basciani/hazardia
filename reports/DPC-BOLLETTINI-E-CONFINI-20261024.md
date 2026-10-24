# DPC: bollettini e confini —24ottobre2026

Run `dpc-geometries-20261024`, base `c1e9a77`. Runtime, download, Fiona/Shapely e ricalcolo della sola sintesi cartografica nella VM. Nessuna esecuzione PROPAGATOR/HMC.

## Problema verificato

Snapshot iniziale `snapshot-705824c022904e18a20a9a6e31208bea`, bollettino23ottobre15:30Roma, valido23/24ottobre. 187zone con tutti e3i livelli testuali noti, ma11geometrie TopoJSON non valide. Il messaggio UI confondeva indisponibilità del confine e del bollettino. Pescara24ottobre: nessuna allerta idraulica, gialla per temporali e idrogeologico.

## Recupero eseguito

Scaricato lo shapefile ufficiale dello stesso identico bollettino/revisioneDPC `00a10a83c84adc7aaefe58cd4e10ed388034d1e1`;3,216,018byte, SHA in source-receipt.json. Sostituzione soltanto delle geometrie TopoJSON invalide con geometrieSHP valide, dopo corrispondenza univoca di tutti187nomi, uguaglianza dei3livelli ufficiali, CRSgeograficoWGS84 e bounds entro0.002gradi. Nessuna bufferizzazione, riparazione automatica o riclassificazione. Conservati source URL, codice zona, invaliditàTopo originaria e provenienza dell’alternativa.

PASS:7zone recuperate, incluso Pescara. Restano4geometrie invalide anche inSHP: Bacino di Levante/Carso, Salento, Iglesiente, Gallura. Classificazioni testuali mantenute per187/187; confini qualificati183/187. Il testo delle4zone resta consultabile dal selettore di tutte le zone.

Snapshot derivati immutabili: `snapshot-88c5cfb98c2746a4a3c15749679ca258` e finale `snapshot-fb36d05e13c94c5d8439dc1185144df8`. Il secondo riallinea anche lo statoEFFIS aPARTIAL. Timestamp di acquisizione e validità originali invariati: nessuna falsa freschezza. Vecchi manifest e prodotti conservati.

EFFIS24ottobre:181/187zone classificabili,6mancanti (4geometrie sopra + Prealpi trevigiane/BacinoPiave e Alta pianura trevigiana orientale/BacinoLivenza senza campioni validi). EFFIS25ottobre dispone della griglia sorgente ma non di una sintesi zonale abbinata al bollettino in questo snapshot; DPC25ottobre non disponibile nello snapshot. Non vengono estrapolate allerte precedenti.

## Interfaccia

PASS: conteggi separati di bollettini/confini/indici e nomi delle zone problematiche, selettore187zone; Pescara mostra il confine recuperato e le due allerte gialle. Salento dichiara bollettino presente e confine problematico, mantenendo i3livelli ufficiali. Avvisi leggibili nel pannello scuro. La consultazione senza punto selezionato invita al click geografico invece di suggerire assenza di meteo. Corretta anche una race del selettoreGiorno che ripristinava il giorno precedente prima di aggiornare la timeline. Verificato25ottobre02:00Roma: nessuna coperturaDPC/sintesiEFFIS viene inventata. Legenda di un prodotto geometrico vuoto dichiara missing.

## Verifica e limiti

PASS:13testVM `PYTHONPATH=src:tests/unit /home/hazardia/m0/reflex-env/bin/python -m unittest test_attention_zones test_attention`; fallback valido, livelli discordanti rifiutati, nomi non univoci/non abbinati rifiutati, alternativa lontana rifiutata, entrambe geometrie invalide mantengono il bollettino ma non promuovono la classificazione cartografica. SintassiJS PASS. UI browser in-app, zero errori console, screenshot reports/dpc-geometries/. NON è un benchmark.

PASS custodia:311file scientifici invariati,95righejob identiche, hashengine invariati. Python3.10.12/Fiona1.8.21/Shapely1.8.0/pyproj3.3.0; prova versione e hash in preservation.json.

FAIL esplorativo: confronto CRS con uguaglianza che include assi rifiutava il CRSgeografico ufficiale; nessuna attivazione del primo tentativo. Corretto mediante equivalenzaWGS84 ignorando solo ordine assi, secondo convenzione coordinateFiona. Warning preesistenti PROJ directory e sintassiinit deprecata registrati; nessuna riproiezione nel fallbackSHP.

Alternativa Sardegna: verificata fonte regionaleCCBY4.0 [RNDT](https://geodati.gov.it/geoportale/visualizzazione-metadati/scheda-metadati?metadataid=R_SARDEG%3A2077b604-e4ec-4915-9675-469c6a2911ae), download1,294,345byte. Geometrie valide ma versione2015 non equivalente alla suddivisione corrente:3nomi diversi; distanzeHausdorff dei confini ~7.1kmIglesiente e11.8kmGallura. NOT INTEGRATED; non sostituire solo perché il nome coincide. Primo confronto esatto di nomi terminatoKeyError suFlumendosa-Flumineddu; ripetuto come confronto dichiaratamente parziale. Risultati in regional-alternative.json.

BLOCKED: completare i4confini richiede una fonte ufficiale corrente compatibile o una correzione qualificata. NOT RUN integrazione versionata dei cataloghi regionali alternativi, assimilazione radar/sensori, qualificazione idraulica/operativa e verificaSafari dedicata. Dati mancanti non sono assenza di pericolo. Nessuna affermazione di copertura informativa globale completa.

## Riproduzione

Per acquisizioni future il worker tenta automaticamente loSHP dello stesso bollettino se ilTopoJSON contiene confini invalidi, entro8MiB e budget totale16MiB. Fallback fallito esplicito, nessun override dei livelli. Per riprocessare una ricevuta esistente usare `scripts/rebuild_dpc_geometries.py --runtime ... --archive ... --receipt ... --expected-snapshot ... --report ...`; rifiuta checksum/revisione errati e cambi concorrenti della snapshot, crea una nuova derivazione, conserva la data originale. Raw nel runVM. ReviewerCodex.
