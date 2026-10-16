# ADR-0009 — Confronti fisici e orizzonti di giorni

**16 ottobre 2026. Stato:** confronto sperimentale incendio implementato e verificato; integrazione idraulica successiva **PROPOSED / in attesa del tipo di intervento scelto dall’utente**. Nessun nuovo motore idraulico installato o adottato.

## Problema concreto

Il confronto della dashboard iniziale usa lo stesso prodotto fisico A/B e simula evacuazione. Questo è corretto per un intervento IMPACT_ONLY, ma non soddisfa la nuova richiesta di visualizzare modifiche dell’incendio o dell’allagamento causate da mitigazione fisica. I limiti iniziali erano60minuti incendio e6ore alluvione nell’interfaccia; gli schemi congelati consentono al massimo3600s/12ore. Questi limiti non vengono rimossi senza verificare meteo, territorio e modello.

## Decisione attuata per l’incendio

Nuova pagina `/physical-fire.html`, distinta dall’ottimizzazione di evacuazione. Mostra due esecuzioni del **PROPAGATOR originale** con/senza fascia ipotetica di combustibile non bruciabile mediante `BoundaryConditions.vegetation_changes`. Nessuna area viene ridotta a posteriori. Confronto a meteo, terreno, innesco, seed e calendario di aggiornamenti abbinati. Disponibili72frame orari per ciascun caso, selezione1/2/3giorni, tempo/playback, controllo Bsenzaazione, provenienza/hash, mappe sincronizzate e ortofoto. L’intervento è una condizione ideale del simulatore: non un piano di costruzione, non l’effetto qualificato di un numero di mezzi.

Sono esperimenti isolati dalla coda e dai contratti0.2 congelati: quest’ultima non dichiara supporto generale a72ore/interventi. Fonte seed1729,2realizzazioni,1thread, spotting disattivato, combustibile uniformelegacy5 e umidità10% sintetici. Vento orario ERA5 retrospettivo13–16luglio2024; altri campi meteo acquisiti non diventano automaticamente una legge per l’umidità del combustibile. Area1024²×30m ottenuta dal DSM già in cache, senza nuovi download territoriali. Runtime/preparazione/rendering nella stessaVM, browser sul Mac.

## Evidenze e limite rilevante

Run `physical-days-20261016T040414Z`, log/comandi in experiments/runs corrispondente. Prima prova64² **FAIL**: baseline esce dal dominio a5ore; errore non ignorato. Dominio1024²: baseline e fascia completano72h, senza celle positive sul bordo. Run di controllo con evento900s vuoto/allNaN: **non è bitwise equivalente** al caso senza evento,114172celle con probabilità diversa alla fine. È una sensibilità alla segmentazione/programmazione e alle traiettorie stocastiche osservata su questa singola fixture, non una diagnosi generale del motore. La baseline pubblicata usa il calendario del controllo vuoto, abbinato al trattamento, per non confondere il cambio di calendario con l’intervento. Questo limite è visibile nella pagina; richiede ulteriori seed/realizzazioni e analisi specialistica prima di inferenze fisiche.

Non usare la grande differenza numerica di questa fascia ideale come prova di efficacia reale, di precisione predittiva o di corretto dimensionamento delle risorse. Non usare i tempi di una singola esecuzione per sostenere p95 o scalabilità generale. Il precedente FAIL100kGeoJSON resta storico: qui144raster sono caricati due alla volta, non139576celle DOM.

## Alluvioni: alternative e decisione ancora aperta

1. **Estendere HMC per invaso/laminazione**, mantenendo i motori scelti. Il sorgente locale contiene `HMC_Module_Phys_HydraulicStructure.f90`, lettura `info_dam.txt`, curve livello-volume e volumi/outflow. È un’affordance reale del codice, **non un’integrazione già eseguita**. Servono ubicazione, geometria, curva di invaso, stato iniziale, regole di scarico, dominio/bilancio idrologico e test del collegamento alle portate REFlEx. Anche un caso interamente ipotetico deve dichiarare tali assunzioni e verificarne i risultati. Non equivale a simulare un argine urbano o una pompa.
2. **Argini locali, pompaggio e idraulica transitoria2D**: valutare un motore aggiuntivo isolato, alimentato dalle portate HMC, con REFlEx conservato per la stima rapida. Candidato da valutare: LISFLOOD-FP; [articolo degli autori](https://gmd.copernicus.org/articles/16/2391/2023/index.html) documenta i solutori CPU/GPU e licenzaGPLv3, e [record del codice8.2](https://zenodo.org/records/13121102) identifica la distribuzione degli sviluppatori. BuildARM64, budget, versione/licenza esatta del pacchetto e simulazione locale **NOT RUN**. Nessuna dipendenza commerciale oGPU obbligatoria proposta; nessuna prestazione locale promessa. L’eventuale aggiunta è una decisione architetturale e va autorizzata prima dell’adozione.
3. Ripetere la mappa di massimo REFlEx per72ore oppure sottrarre arbitrariamente acqua/area in base al numero di mezzi: **rifiutato**, perché non produce l’effetto idraulico richiesto e confonderebbe animazione con nuova fisica.

L’utente è stato interpellato sul primo caso da realizzare: laminazione in HMC oppure argini/pompaggio con valutazione idraulica dedicata. Nessuna delle due integrazioni è dichiarata completata. Le informazioni sull’alluvione esistente e sul confronto di evacuazione rimangono disponibili.

## Accettazione del prossimo incremento idraulico

Fissare caso e intervento; dichiarare curve/volumi/portate/unità e ipotesi; eseguire baseline, controllo nullo e trattamento con stessi input; verificare bilancio, uscita/stato finale e condizioni al contorno; salvare prodotti distinti con hash, orizzonte e timestamp; validare mappa/differenza ed eventuale sequenza temporale. Conservare errore se il modello esce dal dominio o i dati non coprono i giorni richiesti. Nuovi schemi/versioni necessari prima dell’integrazione generale con job e solver; nessun riuso dei vecchi risultati come validazione del nuovo modello.
