# Abitati, esposizione e linee elettriche

Run `territorial-exposure-20261019`,19ottobre2026, Europe/Rome. Base privata `bdc1f9366e44d35100ab5db9de623a122664bb48` con modifiche; revisore stesso agente Codex. SHA finale in Git/PUBLICATION.json. Decisione ADR-0015, requisiti FR-TERR-CONTEXT-01/FR-AIR-CONTEXT-01. Runtime e analisi nella VM esistente; Chrome/Node sul Mac soltanto per QA dell’interfaccia.

## Funzioni consegnate

PASS livelli per abitati/strutture e linee elettriche nel Monitoraggio e su tutte le mappe di scenario; filtri separati, popup con fonte e valori disponibili, selezione della geometria dalla tabella e mappe sempre sopra le configurazioni. Il Monitoraggio carica il contesto della vista dettagliata, senza trasformare gli oggetti cartografici in un’allerta. Nelle simulazioni il modello di lettura usa il job della singola mappa, non il risultato dello scenario selezionato altrove.

PASS confronto temporale: frequenza di contatto entro l’ora e fine orizzonte, primo contatto simulato, frequenza fra membri e mediana condizionata. La probabilità media sulle celle resta distinta nel popup. Inventari diversi e bozze non calcolate sono segnalati. Nessun ricalcolo fisico né modifica degli artefatti originali per ottenere questo livello.

PASS pianificazione su priorità reali disponibili con solver/verificatore esistenti; categorie aeree escluse quando qualifiche degli ostacoli e d’impiego mancano. Il replay controlla anche vecchie proposte. L’inventario richiesto dall’utente resta distinto dalla disponibilità conservativa per il piano automatico. Le simulazioni manuali con aerei restano ipotetiche; non sono rotte o missioni verificate.

## Fonti e dati mancanti

| Fonte | Uso verificato | Limiti |
|---|---|---|
| GeoNames già acquisito |210località puntuali nel dominio FonteVetica|Punti non confini urbani; alcune modifiche della fonte risalgono al2014; popolazione assente|
| ESA WorldCover2021 sulla griglia nativa30m |1200poligoni edificati, classe50; minimo900m² e limite esplicito|Classificazione pregressa, ricampionamento e troncamento; non tutti i singoli edifici o le nuove costruzioni|
| OSM API/Overpass|Parser e acquisizione limitati, cache, importatore; tipi/nomi/voltage/height quando presenti|Live500/502/504/timeout; piccolo estratto400oltre50000nodi; inventario incompleto|
| Estratto OSM locale già verificato|3ways `power=minor_line` e sostegni nell’area dell’Aquila|Snapshot15ottobre2026, bbox `[13.375,42.345,13.405,42.36]`; tensione e altezza delle3linee ignote; non copertura nazionale alta tensione|
| Prodotti nativi originali|Probabilità e tempi su ciascuna geometria|Previsione condizionale non calibrata;8realizzazioni dello stesso forecast non sono8previsioni indipendenti|

Nel caso FonteVetica le linee non sono disponibili. Il sistema lo dichiara; non disegna tracciati né deduce assenza di ostacoli. Popolazione, occupazione, vulnerabilità, destinazioni d’uso non cartografate e copertura completa restano BLOCKED. Il catalogo regionale sulle linee elettriche è stato individuato ma la consultazione ha prodotto un redirect loop; nessun dataset regionale è stato dichiarato acquisito o licenziato. Nessun accesso a servizi ENAV/eTOD certificati è stato eseguito.

Semantica primaria: [OSM power=line](https://wiki.openstreetmap.org/wiki/Tag:power%3Dline), [minor_line](https://wiki.openstreetmap.org/wiki/Tag:power%3Dminor_line), [istanze Overpass e limiti](https://wiki.openstreetmap.org/wiki/Overpass_API), [licenza OSM](https://www.openstreetmap.org/copyright), [WorldCover](https://esa-worldcover.org/en/data-access), [GeoNames](https://www.geonames.org/). Il rilievo degli ostacoli per l’aviazione richiede qualificazione distinta: [ENAV, valutazione ostacoli](https://www.enav.it/cosa-facciamo/soluzioni-mercati/valutazione-ostacoli-e-interferenze-elettromagnetiche). La stima solare è basata sulle formule approssimate [NOAA](https://gml.noaa.gov/grad/solcalc/calcdetails.html); non simula visibilità, fumo, illuminazione, quote o abilitazione notturna.

## Esperimenti e risultati

PASS audit in sola lettura dei job originali `job-ebe51c3a0c4b4832bda1ab3f117e6ec6` e `job-6ef11525dfe94014906dd353cc1bc202`:10asset/1188artefatti verificati per SHA, stesso inventario1410geometrie ciascuno,2820valutazioni. Native arrays invariati e145pin upstream verificati. Due poligoni WorldCover hanno contatto in4/8membri in entrambi gli scenari:

| Geometria | Primo contatto A, minuti | Primo contatto B, minuti |
|---|---:|---:|
|builtup-2072|1555,7|1459,75|
|builtup-2061|1676,8667|1640,6667|

Sono tempi minimi condizionati nei membri simulati; non tempi osservati o garanzie. B non dimostra un beneficio in questa misura. Non attribuire causalmente ogni differenza alla reale efficacia di un Canadair: valgono i limiti stocastici e di qualificazione già registrati. Un punto GeoNames usa un buffer sperimentale75m; i poligoni usano100m d’interfaccia. La frequenza di contatto con queste geometrie non coincide con rischio alle persone o con la probabilità che un’intera città bruci.

FAIL conservati: prima versione con soli200poligoni più grandi e limite200valutazioni ometteva piccoli oggetti vicini al fronte; primo piano `NO_EXPOSED_ASSETS`. Estesi i limiti, con minimo di una cella edificata900m² e valutazione1600geometrie massime, senza cambiare terreno, meteo, umidità o output del simulatore. Questo è un cambiamento di inventario/analisi, non un miglioramento fisico dimostrato. Le località GeoNames sono escluse dall’obiettivo automatico per evitare di sommare indiscriminatamente un punto di contesto all’edificato; completezza e possibili sovrapposizioni fra classi restano minacce alla validità.

PASS piano reale HiGHS/verificatore sul riferimento `job-487cb86fa6774e2a97ab123fe0948fc9`, inventario con un mezzo terra e un Canadair richiesti disponibili: `VALIDATED_FOR_SIMULATION`, proposta solo a terra, aereo escluso con motivazione. Prova finale14,667s con maschere trattenute solo per obiettivi esposti, confermata nel sommario. Nessun nuovo job fisico per il piano. Non è un benchmark p95 né un ottimo fisico globale.

PASS86controlli browser complessivi:19nuova integrazione,12Monitoraggio con linee reali,16ricalcolo/ripresa,25nominale/ordine/eliminazione e14profilo forecast. Incluse12scansioni axe a375/768/1440px. PASS13test VM (6nuovi,7policy) e7controlli geometrici/solari Node. I test di modifica workspace e le richieste fisiche sono isolati; contesti e risultati nativi sono reali. Mainrev108 e caso forecastrev1 identici prima/dopo. Harness iniziali falliti per attesa troppo corta, zoom iniziale assunto e dialogo Configurazione chiuso; corretti e rieseguiti, log originari conservati. Nessun nuovo job fisico, nessuna dipendenza aggiunta, nessun servizio a pagamento.

Acquisizioni automatiche limitate a10richieste OSM/giorno; la diagnosi separata del400ha verificato il limite50000nodi. Non è stato scaricato un estratto nazionale. Il riuso del raw locale12.207.956B non è un nuovo download; l’importatore in VM è stato eseguito e mantiene SHA, licenza e copertura. Pipeline generica per bbox e snapshot, nessuna estrapolazione della cache abruzzese ad altre regioni o Paesi.

## Orologio e ambiente

FAIL iniziale: VM indietro di circa2h50rispetto a Mac/strumento UTC, pur mostrando uno stato NTP storico sincronizzato. È stata chiesta e ricevuta autorizzazione esplicita dell’utente. PASS riallineamento, RTC e NTP verificati, drop-in `/etc/systemd/timesyncd.conf.d/hazardia-resume.conf` con polling32–120s (arrotondamento osservato128s). Le date precedenti e i manifesti fisici non sono stati riscritti; timestamp guest anteriori alla correzione vanno letti con questa limitazione. Offset finale e RTT in `runtime-release.json` del run privato.

Runtime unico4vCPU/8GiBRAM/19GiBdisco. Cinque restart del backend a coda fisica vuota durante l’incremento, nessun altro intervento privilegiato o installazione. Il contesto ha due worker limitati e timeout100s; l’ottimizzatore conserva il proprio budget60s. Il modello è in un processo isolato esistente; i livelli aggiunti non eseguono PROPAGATOR nel browser.

## Ripetibilità e stato scientifico

```sh
# Nella VM, app/ e ambiente geo esistente:
PYTHONPATH=src PROJ_LIB=/usr/share/proj "$GEO_PYTHON" -m unittest discover -s tests/decision -p test_territorial_context.py -v
PYTHONPATH=src PROJ_LIB=/usr/share/proj "$GEO_PYTHON" tests/native/territorial_audit.py "$RUNTIME" CONTEXT_ID_A CONTEXT_ID_B
# QA UI sul servizio locale, senza salvare configurazioni utente:
node tests/browser/territorial-context.cjs NUOVA_DIRECTORY
node tests/browser/territorial-monitor.cjs NUOVA_DIRECTORY
node tests/browser/territorial-math.mjs
```

Per Playwright usare HAZARDIA_PLAYWRIGHT_PATH, HAZARDIA_BROWSER_EXECUTABLE e HAZARDIA_AXE_PATH, come nelle suite precedenti. API e importazione di snapshot sono documentate in INSTALLAZIONE.md. Sommario pubblicabile `reports/territorial-exposure/verification.json`; raw privati `experiments/runs/territorial-exposure-20261019`. Snapshot OSM originali, dati di runtime e immagini non vengono inclusi nella pubblicazione del codice.

BLOCKED qualificazione del rischio umano, inventario nazionale/eTOD/quote/corridoi/abilitazioni, efficacia/logistica e gate scientifici completi M5–M7. NOT RUN nuovi esperimenti fisici, forecast ensemble indipendenti, held-out, benchmark30/p95, soak, idraulica urbana o operazioni aeree. L’incremento è evidenza ingegneristica di dati parziali, lettura nativa e degradazione conservativa; non prova H1–H3 né risultati scientifici anticipati per JSS.
