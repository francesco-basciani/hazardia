# Livelli raggruppati, legende e identità browser —25 ottobre 2026

Run `layer-console-20261025`, baseline `ac8f6709a8d429e336a71bcdb409480165751daa`, reviewer Codex self-check. Incremento cartografico richiesto dall’utente; runtime dati/modelli nella VM esistente. Nessun nuovo provider, database o motore.

## Scelte e comportamento

Quattro gruppi: Previsioni e criticità; Osservazioni; Territorio e infrastrutture; Cartografia e catalogo. Edifici, centri abitati, sanità, emergenze, istruzione, strade, reti, acque e cavi aerei hanno voci individuali nello stesso gruppo territoriale. Il catalogo di ricerca e i confini sono strumenti cartografici separati. Le voci non duplicano le istanze o acquisizioni dei livelli: riutilizzano gli interruttori e i nodi reali esistenti. Icone SVG coerenti e controllo a occhio per visibilità; il nome apre i parametri nell’unico inspector destro. Simulazioni/traffico non reintrodotti nel Monitoraggio.

Il codice precedente NON limitava il disegno degli edifici per zoom. Ora `layer-menu-model.js` definisce zoom minimo15 per gli edifici nel solo Monitoraggio; la stessa funzione è usata nel filtro di rendering e nell’indicatore UI. Zoom insufficiente non disattiva la scelta né equivale a dati mancanti. Altre categorie non ricevono una restrizione inventata. L’acquisizione territoriale automatica già esistente da zoom11 e i limiti delle etichette geografiche sono distinti dalla visibilità delle geometrie; disponibilità e copertura OSM restano parziali. Nessuna modifica alla visibilità dello studio FIRE o ai dati usati dal solver/esposizione.

Le vere istanze DOM delle legende criticità, simboli e meteo, gli stati dei moduli osservati e il collegamento licenze sono raccolti in “Legenda e stato”. Restano scale distinte, riferimenti temporali e aggiornamenti originali. Rimosse le finestre flottanti duplicate e le intestazioni/chiusure annidate; conservata la scala della mappa. “Pioggia e allerte” apre anch’esso l’inspector destro, con attivazione esplicita degli accumuli; aprire/chiudere parametri non spegne un livello.

Favicon HAZARDIA originale, derivata dal marchio vettoriale già presente: SVG e ICO16/32/48. Caricamento comune attraverso i18n per tutte le pagine applicative. ICO generata con Pillow già disponibile nella VM; nessuna installazione. Non usa il logo di terzi.

Riferimento progettuale verificato nel sorgente primario di [God’s Eye View](https://github.com/bilawalsidhu/gods-eye-view): [lista compatta e intestazioni di gruppo](https://raw.githubusercontent.com/bilawalsidhu/gods-eye-view/main/src/ui/styles/layers.css), [icone browser](https://raw.githubusercontent.com/bilawalsidhu/gods-eye-view/main/index.html). Implementazione HAZARDIA propria, adattata ai dati realmente integrati. Il dominio indicato nel README reindirizzava a un sito editoriale: nessuna falsa verifica visiva del prodotto live.

## Verifiche

PASS test client puri: categorie, soglia14/15, conservazione comportamento non-Monitoraggio, assenza di soglie spurie; matematica territoriale7check; i18n28check; simboli25check; clock e DST. Comandi `node tests/browser/{layer-menu-model,territorial-math,i18n,map-symbols,monitor-clock}.mjs`, eseguiti sul client Mac per assenza di Node nella VM (primo tentativo VM fallito e conservato). Nessun runtime applicativo/scientifico spostato sul Mac.

PASS10test backend osservazioni nella VM: `PYTHONPATH=src .../core-env/bin/python -m unittest discover -s tests/web -p test_observed_layers.py`. SVG/ICO serviti HTTP200 con media type corretti. Evidenze grezze, protocollo finale e log in `experiments/runs/layer-console-20261025/`; il protocollo finale dichiara esplicitamente i controlli esplorativi già eseguiti.

Verifica UI e limiti aggiornati alla consegna sotto. NOT RUN nuovi replay fisici, FPS/p95/carico: nessun cambiamento a fisica, richieste dei provider o quantità di dati acquisiti. L’incremento non dimostra miglioramento numerico delle prestazioni né qualificazione scientifica. Gate M0–M7 e FAIL storico REFlEx invariati.

### Esito UI finale

PASS browser integrato, viewport ordinario1011×1034 e390×844:19voci, distribuite2/4/9/4; ogni voce presente una sola volta. Zero legende/stati flottanti residui dentro `#monitor-map`;3legende originali nell’host unificato. Un solo figlio non-hidden dell’inspector dopo il cambio parametri/legenda. Nessun overflow orizzontale osservato. Nessun errore console JS osservato. Screenshot locali `reports/layer-console/{delivery,legend,mobile-en}.png`, esclusi dalla pubblicazione curata.

PASS zoom12/14 insufficienti e15/16 sufficienti nell’indicatore reale. Estratto OSM sull’Aquila:1742edifici nel catalogo parziale; selezionato “Comune dell’Aquila Municipio”, apertura attributi originali e zoom16, legenda unificata effettiva con1203aree Edificio OSM e1punto nell’inquadratura verificata. Tale prova non implica completezza territoriale: riusati snapshot preesistenti, provider Overpass in timeout e quota giornaliera raggiunta esplicitati nelle fonti del catalogo. Nessun download ulteriore aggirando quote.

PASS apertura Pioggia e allerte, attivazione/disattivazione accumuli, opzioni conservate anche in inglese; spegnimento aggiorna lo stato invece di lasciare “calcolo in corso”. IT/EN verificati e italiano ripristinato. Passaggio avanti del clock coperto dalla suite client preesistente, senza modificare la timeline. PASS reload nativo Safari della scheda Monitoraggio, riscontro AX del nuovo menu, pulsante legenda e soglia edifici. FaviconSVG/ICO HTTP200 e due linkhead distinti; nessuna modifica alle preferenze di Safari o promessa di invalidazione immediata della cache icone del browser.

FAIL esplorativo corretto: pulsante legenda poteva ricadere sotto l’inspector; riservata una fascia sopra la timeline e verificato il cambio bidirezionale dei pannelli. Durante reload molto rapido si è anche osservata una destinazione del click diversa dopo il caricamento tardivo del CSS: stylesheet ora dichiarato in head prima del rendering, inserimento dinamico deduplicato. I linkhead sono aggiunti con patch minima, preservando l’entry WII concorrente nella VM e nel worktree; l’entry WII non viene inclusa nel commit/pubblicazione di questo incremento. La scheda WII non è stata modificata.

Indicatore ambrato compatto sul pulsante Legenda solo se lo stato meteo/modulo attivo segnala missing, errore o copertura incompleta; observer limitato ai nodi di stato già esistenti, disconnesso all’unload. Nessun polling o nuova acquisizione introdotti dalla riorganizzazione.
