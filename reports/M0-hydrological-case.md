# M0 — Dossier del caso idrologico reale

15 ottobre 2026. Run `m0-hydro-data-20261015T154619Z`. **Ricognizione/acquisizione e controlli tecnici eseguiti; caso fisico ancora BLOCKED. M1 non avviata.** Tutte le acquisizioni, letture geospaziali, conversioni dei dati e figura sono state eseguite nell'unica VM Linux esistente. Nessun nuovo servizio, modello o dominio; nessuna installazione, messaggio esterno o spesa.

In parole semplici: ora abbiamo dati reali e licenze verificabili per approfondire un piccolo bacino della zona già esaminata. Abbiamo anche misurato perché non si possono ancora usare per dichiarare una previsione attendibile: il ritaglio precedente è incompleto, le stazioni vecchie e nuove non coincidono e mancano ancora le serie e la relazione livello–portata adatte allo stesso evento.

## Fonti e acquisizione effettiva

- **FOCA v4**, Claps et al., Politecnico di Torino, [record11217292](https://zenodo.org/records/11217292), DOI10.5281/zenodo.11217292. Licenza `cc-by-4.0` letta dall'API e archiviata; [descrizione scientifica primaria](https://essd.copernicus.org/articles/16/1503/2024/). Acquisiti11membri: confini/outlet nazionali in shapefile e tre serie storiche locali. Lettura via HTTP Range206 del normale archivio pubblico: il file intero488009899byte non è stato scaricato. Verificati CRC32 dei membri decompressi e SHA256 locali; il checksum MD5 del ZIP intero **non** è stato verificato.
- **SIR Regione Toscana**, [catalogo idrometri](https://dati.toscana.it/dataset/idrometri), [archivio storico](https://sir.toscana.it/consistenza-rete), [licenza ufficiale](https://sir.toscana.it/licenze) CC BY-SA4.0. Catalogo effettivamente ricevuto:204stazioni, CRS EPSG3003. Non confondere il numero con pagine indicative/vecchie copie del catalogo. Letti metadati, legenda, disponibilità e tabella pubblica di pioggia2024 per Bagnone TOS09000015.

L'attribuzione e le condizioni share-alike dei derivati SIR vanno conservate separatamente da quelle FOCA; non attribuiscono una licenza unica a tutto il framework. I diritti sui vecchi campioni CIMA non sono stati risolti né presunti, ma questi nuovi dati hanno proprie condizioni esplicite. Dati idrologici aperti non equivalgono a forcing/calibrazione già pronti.

Protocollo di acquisizione fissato prima dei payload: preferire la zona originaria, dati pubblici con diritti chiari, nessuna selezione sulla qualità di una simulazione; massimo32MiB di payload remoti in questo incremento e4MiB per risposta. Emendamento prima dell'estrazione: consentire un membro decompresso fino a64MiB per il confine nazionale, conservando il limite rete. Il maggiore è53.56MB decompresso/12.37MB compresso. HTTP206 controllati per intervallo esatto; se ignorati, rifiuto del download completo.

## Candidati e problemi misurati

Il candidato principale per ulteriori verifiche è **Bagnone a Bagnone, FOCA D003**, scelto prima dei risultati di un modello; non è ancora un caso qualificato. Sono stati controllati anche due candidati vicini, senza sostituire il vecchio esperimento Caprio.

| Candidato FOCA | Area del poligono | Copertura del bacino nel vecchio AOI nominale | Distanza outlet FOCA dalla stazione SIR di nome corrispondente | Anni con coppie numeriche finite |
|---|---:|---:|---:|---|
| D003 Bagnone |52.3617km²|5.9288%|940.45m|39anni nel1929–1970|
| D012 Magra a Piccatello |77.8119km²|21.1411%|577.88m|22anni nel1934–1970|
| D022 Taverone a Licciana |77.7831km²|0%|3488.38m|12anni nel1933–1951|

Misure in EPSG32632; trasformazioni con asse longitudine/latitudine esplicito. Il vecchio AOI è[9.90,44.30,9.99,44.42], non un bacino certificato. Le coperture sono intersezioni geometriche, non stime di area allagata. La trasformazione del catalogo SIR ha precisione limitata anche secondo il fornitore: nessuna identità di sezione si deduce dal nome o dalla sola distanza.

I poligoni selezionati sono validi; FOCA contiene631confini e631outlet. Due outlet sono esterni al rispettivo poligono di circa16.88m e17.39m: discrepanza conservata, non corretta con snapping automatico e non attribuita senza prova a un errore del dataset. Occorre verificare sezione/outlet/risoluzione prima della delineazione.

I file storici contengono106righe annuali1911–2016, molte con NaN; **non**106anni osservati né idrogrammi di evento. Per D003 le39coppie finite terminano nel1970, mentre il SIR elenca disponibilità15minuti dal2013: nessuna sovrapposizione temporale. Prima di qualsiasi statistica di frequenza va confermato anche l'ordine delle colonne nel dizionario di supporto. Nessun Q0 è stato stimato da questi numeri.

## Pioggia reale e accesso alle serie

La tabella pubblica Bagnone2024 contiene366date valide:214giorni indicati con `-` (precipitazione nulla, **non dato mancante**), nessun giorno marcato mancante nella tabella. La legenda distingue `»` come dato mancante. Le somme giornaliere coincidono esattamente, usando Decimal, con i12totali mensili pubblicati: totale aritmetico1922.2mm. Non è un'analisi di estremi o una verifica della misura sul campo.

Il fornitore indica **Anno PRE-VALIDATO**. L'intervallo è giornaliero9→9; offset UTC, ancoraggio della data e disponibilità storica non sono stati qualificati. Non è stato interpolato o trasformato in pioggia oraria HMC. La presenza di una sola stazione non garantisce pioggia rappresentativa dell'intero bacino.

Le pagine delle serie15minuti di pioggia e livello dichiarano dati non validati e presentano richiesta tramite e-mail/CAPTCHA. Nessuna richiesta è stata inviata, nessun CAPTCHA aggirato, nessun indirizzo utente utilizzato. L'acquisizione delle serie resta BLOCKED: serve esportazione manuale oppure autorizzazione specifica alla procedura di richiesta, con i relativi dati necessari.

Il link pubblico “scale di deflusso” è stato effettivamente scaricato: HTTP200, CSV931byte con21righe di intestazioni/legenda e **zero righe numeriche di scala**. Quindi download tecnico PASS, disponibilità della scala utilizzabile FAIL; non convertire livelli in portate con coefficienti inventati. Il fatto che il CSV abbia un nome corretto non costituisce una prova di contenuto.

## Verifiche e ambiente

Ambiente: Ubuntu22.04/aarch64, Python3.10.12, Fiona1.8.21, pyproj3.3.0, rasterio/Pillow dell'ambiente REFlEx esistente; freeze completo nel run. Prima della validazione congelati58file di input/codice/provenienza, poi ricontrollati. Un primo inventario ha emesso un warning sulla ricerca dei dati PROJ; i controlli formali usano esplicitamente `PROJ_LIB=/usr/share/proj`. Il warning originale e quello di sintassi CRS deprecata sono conservati nei log, senza dichiarare precisione topografica.

| Controllo | Stato | Evidenza |
|---|---|---|
| Licenze pubbliche FOCA/SIR, payload e membri ZIP | PASS | `sources/*.http.json`, metadata Zenodo, `foca-ranges-*.json`, CRC/SHA. |
| Catalogo, geometrie, serie annuali e parsing pioggia | PASS |18controlli in `hydro-data-validation.json`; contenuti e qualità espliciti. |
| Totali pioggia, confronto indipendente con tabella | PASS |12totali coincidono, `quality-and-map.json`. |
| Vecchio AOI sufficiente per uno dei tre bacini | FAIL | Coperture5.93%,21.14%,0%; non cambia la validità del precedente pilot numerico dichiaratamente incompleto. |
| Scala di deflusso pubblica utilizzabile | FAIL | HTTP200/CSV con sole intestazioni,0righe numeriche. |
| Serie15minuti, identità sezione e Q0/tconc/calibrazione | BLOCKED | Procedura e-mail/CAPTCHA, disallineamenti e qualificazione fisica mancanti. |
| HMC sul bacino reale, confronto con evento osservato | NOT RUN | Nessun forcing/evento compatibile pronto; nessuna nuova esecuzione dei simulatori. |
| Figura satellitare del problema geografico | PASS | `bagnone-basin-coverage.png`, generata nella VM dal Sentinel hashato precedente; nessuna previsione di allagamento. |

Il conteggio aggregato delle verifiche non è un giudizio di validità del caso: i FAIL/BLOCKED restano visibili. Gli esperimenti precedenti e le sorgenti CIMA originali sono preservati. Git SHA/dirty null con motivo: cartella non Git. Revisore Codex con controlli separati di totali e copia; revisione idrologica indipendente pendente.

Comandi completi, timestamp, script e stdout/stderr sono nei log `hydro-*.json` e `foca-*.json` sotto `experiments/runs/m0-hydro-data-20261015T154619Z/`. Nel guest:

```sh
cd /home/hazardia/m0/m0-hydro-data-20261015T154619Z
python3 fetch_public.py LABEL URL
python3 inspect_foca_zip.py
python3 acquire_foca_members.py NOME_MEMBRO ...
PROJ_LIB=/usr/share/proj /home/hazardia/m0/reflex-env/bin/python validate_hydro_sources.py
PROJ_LIB=/usr/share/proj /home/hazardia/m0/reflex-env/bin/python quality_and_map.py
```

Questi comandi documentano l'esecuzione originaria; non rilanciarli nella directory congelata. Un replay richiede una nuova directory/run e conserva i vecchi risultati. Archivi/checksum/environment/manifest sono nel run; chiavi SSH escluse.

## Prossimo incremento eseguibile e decisioni necessarie

Il protocollo in `M0-hydrological-validation-protocol.md` specifica riconciliazione delle sezioni, dominio completo, forcing, Q0/tconc e confronto osservato. La preparazione tecnica del dominio completo può proseguire in M0; la scelta del bacino definitivo dipende dalla disponibilità di serie/scala riferite alla medesima sezione. La figura mostra perché riutilizzare semplicemente il vecchio ritaglio sarebbe inappropriato.

Per il caso Bagnone servono le serie15minuti e la scala di deflusso valida con metadati della sezione: l'export manuale del portale è un input umano concreto, non un aumento di RAM. Nessun contatto è stato avviato. Non sono necessarie nuove risorse per le verifiche completate. Il dossier non chiude il gate M0 né autorizza M1, una sostituzione CIMA o un uso operativo.

Chiusura contabile: 13,104,470 byte di payload di fonte; stima cumulativa conservativa 2,026,535,111 byte (1.887 GiB) su5GiB, includendo traffico locale per prudenza. Filesystem usato5.72GB, disponibile13.85GB; configurazione19GiB/8GiB/4vCPU invariata. Archivio guest14,800,223byte, SHA256 `59d47a67c406d3fc8cfd55e2aa3df207566b824ed66877e6d43c71eca05243f6`,70file verificati dopo la copia.
