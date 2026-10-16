# M0 — Protocollo di qualificazione del piccolo caso alluvionale

15 ottobre 2026. **Protocollo per le prossime prove; esecuzioni fisiche real-case NOT RUN.** Run di ricognizione `m0-hydro-data-20261015T154619Z`, candidato geografico D003 Bagnone. Non è un modello calibrato, una policy operativa o un'autorizzazione a M1. Vale l'architettura originale: HMC→REFlEx, incendi separatamente con PROPAGATOR; tutto nella stessa VM.

## 1. Identità della sezione e bacino

- Acquisire identificatore stabile, coordinate/CRS/datum, periodo di attività, rilocazioni e sezioni/scale di portata. Esplicitare la relazione tra D003 storico e TOS09000015 attuale; se non dimostrabile, trattarli come stazioni diverse e non trasferire Q0/calibrazioni. Confrontare anche nomi e distanze degli altri candidati, senza join per nome.
- Verificare l'outlet sulla rete e delineare l'intero bacino nel DEM, con margine sufficiente all'esterno. Confrontare poligono derivato e riferimento FOCA; registrare differenza di area e posizione e cause, senza soglia operativa inventata. Conservare lo scarto di16.88m tra outlet D003 e poligono finché non qualificato.
- Acquisire copertura del terreno completa: il Bagnone FOCA oltrepassa10°E e il vecchio tile/ritaglio non basta. DSM Copernicus non diventa DTM; eventuale DTM alternativo richiede propria licenza e audit. Stesso CRS metrico, datum verticale, allineamento, NoData e reali aree delle celle. Non riutilizzare le69reach del vecchio ritaglio come rete del bacino completo.

**Atteso:** sezione univoca, dominio completo e confronto geometrico motivato. **Stato: BLOCKED** per identità/scala; preparazione completa del terreno **NOT RUN**.

## 2. Dati temporali e selezione degli eventi

- Necessari pioggia e altre variabili effettivamente richieste dal runner HMC scelto, con copertura e risoluzione adeguate, e portata osservata alla sezione. Livello idrometrico richiede scala di deflusso valida nel periodo, con incertezza/limiti di estrapolazione. Una tabella di massimi annuali non è l'idrogramma di un evento.
- Conservare date di misura, pubblicazione/disponibilità, revisioni, unità, intervallo di accumulo e fuso/offset. Il giorno SIR9→9 non diventa mezzanotte UTC; `-` è zero nella tabella esaminata, `»` mancante. Non disaggregare arbitrariamente pioggia giornaliera in oraria. Dati non validati/prevalidati restano etichettati, inclusi i flag N/R/I/@/V/P del CSV.
- Dopo l'acquisizione completa, fissare eventi e separazione cronologica calibrazione/validazione/test prima di confrontare i simulatori. Valutare completezza, disponibilità di osservazioni di estensione e qualità senza selezionare sulla bontà della mappa. Eventuali cambi per dati mancanti diventano emendamenti espliciti.
- In replay predittivo usare solo informazioni disponibili al cutoff; se l'epoca di disponibilità non è dimostrabile, il caso è retrospettivo con limitazione dichiarata, non prova di allerta anticipata. Le osservazioni successive servono soltanto al punteggio.

**Atteso:** forcing e osservazioni confrontabili con traccia completa, finestra e split preregistrati. **Stato: BLOCKED**; export15minuti richiede la procedura pubblicata/manuale, nessuna richiesta inviata.

## 3. Parametri e ponte HMC→REFlEx

- Calibrazione HMC dei suoli/stato iniziale e warm-up: scegliere e fissare protocollo prima delle prove principali, con competenza idrologica; valori sintetici dei pilot non diventano locali. Separare calibrazione e prova held-out.
- Q0 deve rappresentare il riferimento a piene rive previsto dal modello, non il primo campione. Opzione preferibile da qualificare: sezione/rilievo e scala con evidenza del livello a piene rive. Una proxy di frequenza o regionalizzazione è un'alternativa da giustificare con assunzioni/stazionarietà/periodo e analisi di sensibilità; nessun periodo di ritorno o coefficiente fissato arbitrariamente in questo dossier. Le39coppie storiche D003 non attestano il bankfull del moderno idrometro e il CSV931byte non fornisce una scala.
- tconc: documentare metodo upstream effettivo, versione, area, lunghezza idraulica, quote e unità, ricavati dal bacino completo; verificare conversioni in secondi. Nessun valore ricavato dal vecchio ritaglio viene riqualificato per il bacino nuovo.
- Fissare mappatura tratti/sezioni, campionamento portate, finestre e unità m³/s. Dichiarare Qpeak e riferimento Q0, errore da campionamento e riduzione a volume triangolare/transito. Confrontare quantità commensurabili, non richiedere uguaglianza con l'integrale dell'intero evento per definizioni diverse. Verificare casi sotto/sopra Q0 senza inventare la risposta del modello.
- I prodotti massimi REFlEx restano profondità/estensione massima; nessuna mappa di arrivo o ricorrenza assegnata da nomi di campo come Q100.

**Atteso:** configurazione e semantica qualificate, incertezze e alternative registrate. **Stato: BLOCKED**, revisione idrologica necessaria; nessun parametro operativo inventato.

## 4. Prove da eseguire sul caso qualificato

1. Input/uscite e run identity: completezza, intervalli, unità/CRS/datum, contenuti raster/array, output per tutti i tratti e non solo exit0. Esiti PASS/FAIL distinti dal completamento del processo. Patch REFlEx sperimentale esplicita, originale conservato.
2. HMC: confronti controllati di passo fisico supportato e campionamento forcing, warm-up/stato, finite/nonnegative, progresso, timeout e log STOP. Usare il precedente4/2/1s solo come antecedente tecnico; definire condizioni reali e criteri di stabilità con esperto prima delle prove.
3. Portata: curva simulata/osservata sul medesimo intervallo e sezione, errore di picco e suo tempo, volume su finestre coerenti, RMSE ed eventuali NSE/KGE con definizione/versione. Riportare denominatori, mancanze e incertezza della scala. Le soglie di skill non sono state approvate; misurare non significa PASS di accuratezza.
4. Allagamento: confronto di estensione con osservazione satellitare/terrestre attribuibile all'evento e suo orario, maschere nuvole/NoData e risoluzione, IoU/precisione/recall ove giustificati. Il Sentinel2024-07-11 di sfondo non è ground truth di piena.
5. Regressioni: tratti a singolo pixel/bordi HAND, merge esplicito, NoData, rete completa e confronto originale/copia patchata; non generalizzare il precedente69reach a questo nuovo bacino senza esecuzione.
6. Performance del solo esperimento: tempo, CPU/RAM, disco, bytes, dimensione rete/griglia, thread/seed/versioni. Distinguere dal budget decisionale60s e dal futuro p95>=30richieste. Non avviare servizi/solver/UI M1–M3 per completare questo protocollo.

**Stato di tutte le sei prove real-case: NOT RUN.** La revisione di fonte/geometria/pioggia corrente è evidenza M0 di preparazione, non loro sostituto. La disponibilità dei dati non elimina il controllo umano né dimostra efficacia degli interventi. Il passaggio M1 richiede riesame dei prerequisiti e autorizzazione esplicita; nessun allargamento ai sette punti futuri.
