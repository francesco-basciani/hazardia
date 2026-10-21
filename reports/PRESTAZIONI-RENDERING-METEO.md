# Rendering meteo: riduzione del lavoro ripetuto

Run `weather-performance-20261021`, base `6cb05dd7f17f3ae7efe1e4e4a79ec7f8f0fd14c6` + modifiche. SHA finale Git/PUBLICATION.json; reviewer Codex, self-check. Pilot tecnico UI, non benchmark scientifico preregistrato o prova di accuratezza fisica.

## Diagnosi e modifica

La vista ricreava fino32indicatori e relativi testi a ogni aggiornamento; riassegnava larghezza/altezza del canvas e allocava ImageData a ogni frame meteo. Riproiettava inoltre ogni pixel campionato e ogni nodo del campo vento quando la mappa era immobile. Le420scie avevano uno stroke con blur per ogni particella. Questi costi sono visibili nel sorgente e aumentano con la dimensione della mappa. Nessun indizio di saturazioneVM al controllo puntuale (load0,07/0,06/0,08); questo non esclude ogni causa esterna.

PASS modifica: riuso dei nodi DOM/formatterIntl/bufferImageData e canvas dimensionato solo quando cambia; cache limitata di geometrie e pesi bilineari per vista/griglia, invalidata su pan/zoom/resize/cambio griglia. I valori sono sempre letti dal record attuale; non vengono congelate previsioni o colmate mancanze. Piani separati per campo globale/fine, nessuna estrapolazione. Vento raggruppato per4colori, fino8stroke per frame (contorno scuro+linea) anziché420stroke con blur; stessa quantità di particelle, direzione/intensità e regole del movimento. La resa del contorno è modificata, non i dati. Le stesse ottimizzazioni condivise di raster/etichette valgono per lo studio; i risultati fisici restano invariati. Pulizia esplicita quando un record/livello non è disponibile, per evitare residui dopo il riuso.

## Misure reali UI

Client Mac16,8/AppleM4Pro/48GiB/macOS27.0.1; motore/versione IAB non identificati in questa prova. IAB, viewport1736×875 CSSpx,DPR1,32indicazioni,tutti i livelli predefiniti attivi, stesso campo `map-weather-2ca5531ecfcc0eb385c5c3dd` e vento fine `openmeteo-wind-5d227c8382c46b2e52c0cb12`, coverage1. Strumentazione bounded120campioni esportata in datasetDOM, identica prima/dopo. JSON before/after in reports/weather-performance.

| Misura, p95 finestra mobile120campioni | Prima | Dopo |
|---|---:|---:|
| Lavoro sincrono per aggiornamento meteo |12,5ms|8,8ms|
| Intervallo fra callback di disegno vento |66,6ms|33,5ms|
| Lavoro sincrono callback vento |0,1ms|0,2ms|

PASS miglioramento osservato della cadenza e del ridisegno nel pilot; il lieve aumento del costoCPUvento è riportato, non nascosto. Gli intervalli non misurano FPSglobali né tempoGPU. Le finestre sono sequenziali/correlate e le validità percorse differiscono (JSON), quindi non sono30ripetizioni indipendenti o stima causale esatta di una percentuale di accelerazione. Prima a1280×720 il redraw era5,1ms: non riprodotto un freeze universale. Lo screenshot utente può avere DPR/browser/dimensioni differenti; nessuna equivalenza automatica con quel dispositivo oSafari.

Durante il replay,32nodi creati/32indicatori presenti: non ricreati ogni frame. PASS ritorno all’inizio, pausa, zoomin con coverage1 e valori riposizionati; PASS768×1034 e375×1034 con coverage1,15/5indicatori e nessun overflow orizzontale. Override viewport ripristinato, schedaQA chiusa; configurazioni utente non toccate. Screenshot privato experiments/runs/weather-performance-20261021/monitor.png.

## Correttezza e ambiente

PASS6013assertJS deterministici: equivalenza bilineare entro1e−12 su6000posizioni incluse fuori dominio, riuso senza nuove proiezioni, nuovi valori sullo stesso piano, pan e piani separati, nodiDOMriusati/testi aggiornati/clear dei mancanti. PASS12regressioni colori/alpha/clear/buffer e16policyviewport; sintassi5moduli e gitdiff. Comandi:

```sh
node tests/browser/weather-render-plan.mjs
node tests/browser/cloud-probability.mjs
node tests/browser/viewport-weather-state.mjs
```

Test di sviluppoJS, non elaborazioni scientifiche host. Test e log in reports/weather-performance/js-tests.log. Acquisizione/preprocessing/API rimangono nella VM; rendering client verificato nel browser. Nessun nuovo jobCIMA, restart, installazione, costo o risorsa aggiunta. VM Linux5.15aarch64/Python3.10.12,4vCPU/8GiB/19GiB. HTTPpuntuale nellaVM: meteo0,516s/649468B, jobs0,003s/7783B, research0,0017s/4855B; singoli controlli, non distribuzioni di latenza. Snapshotbackend mainrev119/SHA4247a5f71d3a7daca55ccf0efff7ce1b446f40060e6ffe51f4aec6b34a8570de e90job(77success/8cancel/5error) coincidono con lo stato precedente. Nessuna modifica intenzionale al backend o alle sue quote.

## Negativi e limiti

NOT RUN Safari/retina/DPR2/GPUprofiling, stress2560/4K, heap/soak/p95end-to-end/axe, nuova prestazione multimappa e simulazioni fisiche. Il miglioramento osservato IAB non certifica ogni browser/hardware. Primo comando ricerca conteneva un file inesistente map-first.js, errore di ispezione senza impatto prodotto; ricerca proseguita nei file effettivi. Nessun FAILfunzionale rilevato nelle verifiche finali. FullgateM5–M7 BLOCKED e qualificazione scientifica invariati; nessuna dichiarazione di chiusura QRglobali. Prossimo incremento: verificare la stessa traccia nel browser/dispositivo effettivo se il rallentamento persiste, mantenendo invariata la qualificazione input/interventi prevista dal piano.
