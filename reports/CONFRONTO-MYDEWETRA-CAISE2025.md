# HAZARDIA e MyDewetra: sovrapposizioni, differenze e riuso

Revisione documentale del 21 ottobre 2026, ID `mydewetra-review-20261021`.
Revisore: Codex, self-check; non valutazione scientifica indipendente.
Nessuna installazione, modifica del runtime, nuova simulazione o modifica del manoscritto.

## Giudizio

**Una parte consistente del Monitoraggio ricostruisce funzionalità già presenti in
MyDewetra. Questo non rende inutile HAZARDIA, ma impedisce di presentare come
novità scientifica una piattaforma multi-hazard con dati meteorologici, satellite,
mappe temporali, modularità e segnalazioni di soglia.**

Il paper fornito descrive una reingegnerizzazione industriale, non un nuovo
algoritmo di propagazione o di ottimizzazione delle risorse. Non descrive né valuta
l'allocazione robusta con risorse condivise fra hazard, la verifica separata dei
candidati entro una deadline, o il recupero selettivo delle decisioni sotto guasto.
Questi restano possibili elementi distintivi del piano HAZARDIA, da dimostrare:
la loro assenza nel paper non dimostra la loro assenza nel prodotto completo,
né la loro originalità rispetto alla letteratura restante.

## Fonti e perimetro effettivamente esaminato

- PDF dell'utente: *Engineering Early Warning Systems: an Industrial Experience*,
  Burastero et al., 16 pagine, tutte lette; figure 1–5 e tabella 1 controllate
  visivamente. SHA256 `6a475b27493f12ca86abad03f713c657e30a63e5f83254a3525466a028fe1c4c`.
  I numeri di pagina sotto sono quelli del PDF ricevuto.
- [Scheda Springer](https://link.springer.com/chapter/10.1007/978-3-031-94569-4_8):
  CAiSE 2025, pubblicazione 15 giugno 2025, pp.125–142. La versione editoriale ha
  estensione e bibliografia differenti: non si presume identità integrale con
  il PDF ricevuto; il testo integrale editoriale non è stato acquisito.
- [Artifact GSSI](https://github.com/gssi/caise2025-cima), commit
  `7d69bed33e9a20ade1188c732a29971228685722`: albero ricorsivo completo, 4 file,
  README, LICENSE Apache-2.0, questionario/risposte XLSX e gitignore. Non contiene
  il codice eseguibile della piattaforma. Risposte XLSX non rianalizzate.
- [Sorgenti CIMA](https://github.com/CIMAFoundation/mydewetra-src), commit
  `4c20f78dc20a702defca33e71f23c324be9f417f`: albero ricorsivo completo, 22 file,
  comprendenti archivi. Ispezionati README, termini rev8, documentazione DDS e
  algorithms, archivio backend v2 e archivio v3 `ps-vm-backend-v1.3.4`.
  Non è stata letta tutta la UI v2, né avviato codice esterno.
- Piano e protocollo HAZARDIA; sorgenti `decision/controller.py`,
  `decision/supervisor.py`, `decision/verifier.py`, `decision/rolling.py`,
  `rain_assessment.py`, `web/static/weather-display.js`; report del confronto
  fisico ottimizzato e del bank sintetico CAiSE. Base Git HAZARDIA
  `f7da679f5d39193f77eb619468f1e67fb51ab655`, con documentazione di ricerca già
  modificata da altro lavoro nella directory. Modifiche preesistenti preservate.

Metadati, hash e indici delle fonti in `reports/mydewetra-review/audit.json`.
Scratch privato in `tmp/pdfs/coauthors-caise2025`; nessuna redistribuzione del PDF.

## Confronto rispetto al piano originale e alla piattaforma

| Tema | Nel paper MyDewetra | HAZARDIA effettiva / implicazione |
|---|---|---|
| Multi-hazard e più paesi | Incendi, frane, alluvioni; installazioni cloud e nazionali, pp.5–6 | Architettura generica con primi due hazard: sovrapposizione forte, non novità autonoma. |
| Dati eterogenei | Stazioni, meteo, satellite, radar; serie storiche, pp.5–6 | Meteo, EFFIS, DPC, territorio/OSM reali; rete osservativa/radar equivalente non qualificata. MyDewetra ha una base operativa descritta molto più ampia. |
| Mappe nel tempo | DDS basato su plugin GeoServer; livelli WMS, p.7 | Layer e meteo temporali già presenti, rendering meteo canvas nel browser. Separare pubblicazione dei dati e visualizzazione è un riferimento utile, non prova di maggiore velocità. |
| Segnalazioni precipitazione | Sentinel somma le osservazioni pluviometriche delle ultime 6h e valuta soglie; messaggi e aggiornamento WebSocket, p.8 fig.2 | Cumulate previste per zona e allerte DPC separate già presenti. Non equivalgono a osservazioni pluviometriche né a soglie idrologiche locali qualificate. |
| Moduli e autorizzazioni | Portale, servizi applicativi, gateway, identity provider e autorizzazioni, p.7 | Contratti e worker isolati sono coerenti, ma modularità/controllo accessi non sono principi nuovi. Non serve clonare tutta la topologia cloud nella VM. |
| Decisioni | Supporto a valutazione umana e compilazione/revisione di bollettini, pp.5,12–13 | Piano originale include solver robusto, checker e confronto fisico: funzionalità diverse da una segnalazione di soglia. Qualificazione reale degli effetti e della logistica ancora BLOCKED. |
| Graceful degradation | Servizi disaccoppiati e metriche, pp.7–8; nessun esperimento equivalente descritto | Esistono controlli e prove software/sintetiche. La preservazione qualificata delle capacità operative non è dimostrata dal solo isolamento dei processi. |
| Tempo di risposta | Nessun benchmark equivalente sul percorso decisionale | Supervisore e limite 60s implementati; benchmark fisso di 30 chiamate nel bank sintetico. Non misura il tempo delle nuove simulazioni fisiche. |
| Evidenza industriale | Questionario 20 partecipanti, confronto effort su 3 funzionalità, SonarQube, pp.9–14 | HAZARDIA ha test e pilot tecnici, ma non uno studio utenti equivalente né la stessa esperienza operativa. |

Il confronto fisico già registrato in HAZARDIA non dimostra superiorità:
due interventi ideali riducono la superficie media di circa1,094%, ma il criterio
prudenziale sulle priorità resta8→8, contro il proxy del solver che prevedeva0
(`reports/CONFRONTO-FISICO-PIANO-OTTIMIZZATO.md`). I nuovi confronti B0–B4 sono
un bank autoriale sintetico, non una valutazione contro MyDewetra in esecuzione.

La bozza editoriale corrente ha inoltre un taglio esplorativo su ammissibilità
rivedibile, versioni, dipendenze e responsabilità del riesame: non coincide con
la reingegnerizzazione del paper. Tuttavia MyDewetra gestisce già autorizzazioni,
aggiornamenti informativi e revisione dei bollettini. La differenza deve essere
formulata su obblighi e comportamento specifici; non su generiche parole quali
provenienza, autorizzazione o revisione. Ledger e propagazione concorrente del
ciclo proposto non sono implementati in HAZARDIA, come già dichiarato nel protocollo.

Anche una generica “reference architecture per EWS” richiede cautela: è esplicita
agenda futura degli autori a p.14. Non basta aggiungere un diagramma architetturale
per rendere distinto il contributo.

## Cosa riprendere, come funziona e cosa possiamo replicare

### 1. Pubblicazione cartografica temporale separata dal client

Il DDS normalizza formati diversi e pubblica livelli WMS. Nei sorgenti v2
`dds_client2.py` espone proprietà, disponibilità temporale, serie puntuali e di
area, stili e timeline. Sono client verso DDS: non costituiscono da soli il plugin
GeoServer descritto nel paper.

**Replicabile:** catalogo dei livelli con unità, provenienza, orari realmente
disponibili, geometria e scala esplicite; raster/tiles prodotti e riusati lato
server, senza ricalcolare ogni superficie per ogni vista browser. HAZARDIA ha già
cache e rendering limitato: occorre misurare entrambe le soluzioni sullo stesso
viewport/dataset prima di introdurre un nuovo servizio o promettere guadagni.
WMS non garantisce da solo tiles in cache o animazioni fluide; non sostituisce
il vento animato e non rende più fini dati meteo grossolani.

**Prova necessaria, NOT RUN:** prototipo isolato, output numericamente coerente,
p50/p95, frame time/memoria e richieste al cambio viewport su desktop e Safari.
Installare GeoServer o riscrivere la UI non è una conclusione di questa revisione.

### 2. Regole esplicite per le precipitazioni e distinzione delle fonti

L'esempio p.8 è concreto: nuova misura → persistenza → evento → somma 6h →
confronto soglia → aggiornamento layer. Sentinel è il nome di un servizio di
soglie; in questo diagramma non indica il satellite Copernicus Sentinel.
Non sono pubblicati nel paper valori di soglia locali o una conversione generale
da pioggia ad allerta di alluvione.

**Replicabile:** valutazione versionata di cumulate e superamenti, con stazione o
zona, finestra, qualità/completamento, soglia motivata, validità e causa leggibile.
Non servono obbligatoriamente RabbitMQ o WebSocket per la prima versione locale;
il contratto informativo è separato dal trasporto. Osservazioni e previsioni vanno
valutate e mostrate distintamente, senza riempire i mancanti con zero.

### 3. Un ritrovamento aggiuntivo: classi QPF per zone meteo

Il modulo pubblico v3 `ps-vm-backend` è successivo al paper: manifest v1.3.4,
pubblicato8ottobre2026. Contiene `docs/algoritmo-conversione-qpf-zdv.md`,
`ps_vm_core/qpf_conversion.py`, modello dati, migrazioni, endpoint e test.
**Non attribuire retroattivamente questo algoritmo al paper2025.**

La policy documentata classifica il massimo di precipitazione inserito per una
durata ragguagliandolo linearmente a24h. Le classi del modulo sono <5,5–<20,
20–<60,60–100 e>100mm equivalenti24h. Fra durate/intervalli prevale la classe
più severa. Per esempio13mm/3h diventa104mm equivalenti24h: non significa che
il modello abbia previsto104mm effettivi nelle successive24ore. Il codice usa
prodotti interi per evitare arrotondamenti alle soglie.

**Replicabile:** campiture discrete comprensibili, legenda con quantità/durata,
regola documentata, soglie configurate per zona, gestione atomica della promozione
della mappa. Il codice controlla soglie mancanti e non modifica lo stato a metà.
È una soluzione interessante per la chiarezza del Monitoraggio.

**Non trasferibile automaticamente:** quei numeri come soglie di pericolo idraulico
o colori ufficiali giallo/arancio/rosso. ZVM, zone DPC idrogeologiche/idrauliche,
bacini e comuni non sono sinonimi. Non usare la media areale grossolana di HAZARDIA
come se fosse il massimo QPF di ingresso del modulo. Occorrono semantica,
geometrie, politica e qualificazione adeguate; nessuna soglia è stata attivata.

### 4. Metriche operative e valutazione con persone

Prometheus raccoglie metriche dei servizi, separatamente dalla mappa dei rischi.
Un pannello può rendere immediati ritardo delle fonti, tempi di coda, fallimenti,
cache e stato dei worker. Il principio è replicabile nella VM usando anche
i log già disponibili, senza installare tutta l'infrastruttura industriale.

Il questionario a20 partecipanti è una lezione utile: verificare se si trovano
funzioni e si completano compiti reali, oltre ai test del DOM. Alcune domande
tecniche ricevono solo4risposte;3/20 giudicano peggiori usabilità e findability.
È evidenza descrittiva, non prova universale di interfaccia migliore. SonarQube
misura problemi rilevati staticamente, non accuratezza fisica né sicurezza sul
campo. La fig.5 mostra anche0% di coverage in entrambe le versioni e security
review E: “0bug rilevati” non significa assenza di difetti reali.

**Replicabile:** studio di compiti preregistrati con utenti esterni allo sviluppo,
tempi/errori/comprensione dei mancanti, più analisi statica con configurazione e
versione congelate. Non possiamo riutilizzare come risultati nostri i miglioramenti
di effort industriale misurati dagli autori su tre funzionalità diverse.

## Possiamo riusare e avviare il loro codice?

**Parzialmente sì per ispezione; avvio completo non verificato.**
Il sito ufficiale e i termini indicano EUPL per i sorgenti MyDewetra. L'artifact
GSSI ha Apache-2.0: tale licenza non si estende alla piattaforma o ai suoi dati.
Riuso di codice, accesso ai servizi e riuso dei dataset sono verifiche distinte;
prima di incorporare file occorre controllare licenza effettiva e attribuzioni
del componente e delle dipendenze. Nessun codice MyDewetra è stato incorporato.

Il vecchio backend pubblicato è Python2.7 e i file Sentinel sono client del
servizio esterno, non il motore Java/Spring descritto. Nel nuovo modulo v3 ci sono
dipendenze Git SSH su `acroweb3-server-lib` v1.6.1 e `acroweb3-server-api-lib`
v1.5.1: entrambe restituiscono404 all'API GitHub anonima al momento della verifica.
Questo significa non reperibili pubblicamente con quell'accesso, non prova che
non esistano. L'archivio non è l'intera architettura fig.1: il modulo include
anche Kafka fra le dipendenze, mentre il paper parla di RabbitMQ. Versioni e
componenti non vanno mescolati assumendo equivalenza.

Per una replica del sistema degli autori servono release/configurazioni esatte,
DDS/plugin, servizi di soglia, dipendenze, schemi e dati di prova con licenze e
istruzioni. Una richiesta ai coautori sarebbe utile; non è stata inviata alcuna
comunicazione né usato il portale autenticato.

## Registro e prossimo incremento consigliato

| ID | Attività | Esito |
|---|---|---|
| MD-01 | Lettura integrale PDF16p e verifica figure/tabelle | PASS documentale |
| MD-02 | Verifica artifact ufficiali, commit e archivi selezionati | PASS statico |
| MD-03 | Confronto con piano e codice/evidenze HAZARDIA | PASS analitico, non prova di novità |
| MD-04 | Primo recupero metadati con Python host | FAIL TLS CA locale; ripetuto con curl verificato, senza disabilitare TLS |
| MD-05 | Replica completa MyDewetra | BLOCKED per questa verifica: stack/dipendenze/dati completi non ottenuti |
| MD-06 | Esecuzione QPF/DDS/Sentinel e benchmark comparativo | NOT RUN |
| MD-07 | Superiorità HAZARDIA, originalità globale e validazione operativa | NOT RUN / gate preesistenti BLOCKED |

Consiglio: trattare MyDewetra come precedente diretto per il Monitoraggio e come
possibile infrastruttura con cui interoperare. Riprendere anzitutto chiarezza di
zone, classi, finestre e provenienza; valutare poi un percorso server per la
cartografia con un benchmark controllato. Conservare come oggetto della ricerca
le decisioni ammissibili e rivedibili, l'allocazione e il comportamento sotto
informazione/capacità parziale, con baseline adeguate e limiti espliciti.

Nessuna sostituzione del piano M0–M7, del modello fisico, dei gate o della
topologia è stata decisa. Nessun claim di novità o di efficacia è acquisito da
questa lettura; il PDF integrale finale e i componenti mancanti sono il prossimo
materiale utile per consolidare il confronto, non un prerequisito per terminare
questa analisi documentale.
