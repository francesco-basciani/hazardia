# Scenari incendio sulla mappa

Run `fire-sandbox-20261017`; base privata `074583787e3766014048f37624e23f40bfd83ad2`; reviewer Codex self-check. Preregistrazione, input e output grezzi: `experiments/runs/fire-sandbox-20261017/`. Incremento autorizzato dalla richiesta esplicita di trascinamento, timeline, geometrie e scenari aggiungibili. Nessuna nuova dipendenza, servizio, acquisizione o modifica ai sorgenti PROPAGATOR. Runtime nella stessa VM entro i limiti esistenti.

## Interazione

In **Simulazioni e risorse → Incendio · innesco e squadre** la mappa è l'area di lavoro. Trascina dalla barra uno o più inneschi e le unità, poi trascina le icone per spostarle. Su touch è disponibile anche la selezione della categoria seguita dal tocco sulla mappa. Selezionando un'unità si può disegnare una linea (due estremi) oppure un poligono (vertici e Chiudi area); i vertici restano trascinabili. Il minuto di attivazione si può modificare nelle proprietà; un nuovo elemento usa l'ora corrente del cursore.

La timeline comune ha play, pausa, passo avanti/indietro, cursore e velocità di riproduzione. Riproduce i frame orari effettivamente calcolati: non è streaming del solver né una simulazione che si ricalcola istantaneamente mentre trascini. Una modifica crea una bozza esplicitamente distinta dal risultato; **Calcola scenario** ne aggiorna l'evoluzione completa. Non c'è ripartenza del solver da un checkpoint temporale: il replay applica tutti gli eventi dagli istanti registrati. Il frame iniziale non viene inventato come risultato nativo.

**＋ Nuovo** duplica la configurazione selezionata, con un nuovo nome e senza attribuirle i risultati del genitore. Nessun vincolo ai soli A/B: aggiungi altri scenari, seleziona quello da modificare e spunta quelli da confrontare. La stessa mappa sovrappone i raster con colori distinti e mantiene la tabella delle superfici allo stesso tempo relativo. Se inneschi/meteo/parametri differiscono la didascalia lo segnala: non attribuire tutta la differenza alle unità. **Calcola scenari modificati** li accoda in sequenza; una revisione della previsione durante la sequenza interrompe il confronto anziché cambiare tacitamente sorgente. I job già avviati proseguono nella VM anche chiudendo il browser; la sequenza dei job ancora da inviare è del client.

Le configurazioni e gli identificativi dei job sono salvati nella VM con revisione e conflitto esplicito fra client, esportabili in JSON. I risultati nativi restano immutabili. Un nuovo calcolo conserva il precedente durante l'attesa e in caso di errore. Non c'è un limite di due scenari: resta un budget di 60KB per le configurazioni salvate. I singoli job conservano i limiti di 16 inneschi,8unità,32vertici per area,72ore, linea2km/area4km² e coda/timeout esistenti. Il territorio preparato è ancora il caso dimostrativo; un disegno fuori copertura viene rifiutato.

## Traduzione fisica

Il codice upstream installato `propagator/io/actions.py` implementa già WaterlineAction, CanadairAction e HelicopterAction come modifiche dell'umidità e HeavyAction come variazione verso combustibile non vegetato, lungo linee rasterizzate. Non modella automaticamente una flotta operativa con equipaggi, tempi di viaggio e logistica.

La nuova ipotesi richiesta dall'utente è esplicita: `effect: fuel_removal`. Per linea o poligono viene usata la rasterizzazione upstream (`build_mask`, all_touched) sulla griglia reale e passata una `BoundaryConditions.vegetation_changes` temporizzata con il codice nativo di terreno non vegetato. La geometria modifica quindi gli input del modello, non il perimetro visualizzato a posteriori. La superficie già bruciata non viene cancellata. La categoria è conservata ma, in questa ipotesi, **non implica diversa efficacia**: uomini, Canadair ed elicotteri non vengono dichiarati fisicamente equivalenti nel mondo reale. Si tratta di un controfattuale ideale comune. Le vecchie linee native senza `effect` mantengono la semantica precedente e restano leggibili.

`ignitions` contiene id, coordinate e minuto; il worker proietta tutti i punti sulla griglia e li inserisce ai rispettivi tempi. `comparison_times` conserva un orologio degli eventi comune tra scenari; un nuovo istante rende da ricalcolare anche i riferimenti già completati, per controllare l'effetto del calendario numerico. Il nuovo endpoint `/api/firelab/scenario` accoda un solo job, evitando un nuovo baseline ridondante per ogni scenario. Il precedente endpoint accoppiato rimane compatibile. `/api/fire-workspace` salva configurazioni validate; nessuna azione operativa reale.

## Evidenze eseguite

Dati: DEM1024²×30m già preparato, combustibile uniforme legacy5, umidità combustibile10%,2realizzazioni, seed1729,1thread Numba, spotting disabilitato, dominio con errore all'uscita. Meteo storico ERA5 a partire dal13luglio2024T13:00Z,3ore; stessi venti orari e calendario0/3600s. Gli inneschi sono42.350,13.380 a0min e42.352,13.382 a60min. Input esatti in `*-input.json` nel raw.

| Prova | Esito | Osservazione |
|---|---|---|
| Due inneschi, secondo dopo60min | PASS | Eventi consumati riportano1+1inneschi |
| Replica senza interventi | PASS | Hash dei tre NPZ identici al baseline |
| Area a60min | PASS |1506celle passate a non vegetato; primo frame identico al baseline, successivi differenti |
| Linea a0min | PASS | Maschera fuel realmente consumata dal worker |
| Superficie finale3h | PASS tecnico | baseline16.47ha; area a60min1.71ha; linea a0min2.295ha. Non è misura di efficacia di mezzi reali |
| Drag/drop e geometrie, scenari oltre B, play/pausa/rewind, salvataggio | PASS | Browser con mouse reale e payload API controllato; configurazioni QA ripristinate |
| Touch mobile | PASS | Tap categoria e mappa, nuovo innesco; configurazioni ripristinate |
| Responsive/accessibilità | PASS |375/724/1440px, nessun overflow,6scansioni axe senza violazioni nel flusso verificato |
| Regressioni VM | PASS |83unit+17web=100test |
| Poligono autointersecante | PASS |400INVALID_INPUT prima di accodare |

Gli esempi A/B/C consegnati sono tre job realmente completati. Un ulteriore calcolo avviato dalla nuova UI verifica anche accodamento, conservazione del risultato precedente e ricaricamento del prodotto nativo; i dettagli sono nel riepilogo di verifica. Una prova UI che intercetta il POST non viene contata come prova fisica.

### Esiti negativi conservati e limiti

FAIL iniziali nel raw: importazione di un vecchio risultato privo di `options` (resa compatibile con la fixture precedente, seed1729documentato); riduzione dell'orizzonte con revisioni vento esterne alla nuova durata (ora tagliate al termine; eventi innesco/unità fuori intervallo fanno rifiutare il cambio di durata); attesa del vecchio messaggio di autosalvataggio nel harness (stato di caricamento corretto). Un precedente edit con errore di indentazione è stato fermato da py_compile prima della distribuzione. Le verifiche finali sono distinte dai tentativi falliti. Nessun errore scientifico è stato eliminato dal raw.

NOT RUN: nuove prove multi-innesco/poligoni72h, benchmark p95/soak, Safari/Android reali, campo, validazione storica, solver che riparte da checkpoint o streaming dei frame incompleti. La prova touch è emulazione Chrome, non certificazione su dispositivi fisici. La vecchia baseline72h resta una prova distinta. BLOCKED invariati: fuel reale, estimator T/RH/pioggia→fuel moisture, efficacia/logistica delle squadre, capacità/ottimizzazione residue e gate scientifici completi M5–M7.

Riproduzione esplicita:

```sh
python3 tests/native/fire_sandbox_api.py /cartella/evidenze-native
HAZARDIA_PLAYWRIGHT_PATH=/percorso/playwright \
HAZARDIA_BROWSER_EXECUTABLE=/percorso/chrome \
HAZARDIA_AXE_PATH=/percorso/axe.min.js \
node tests/browser/fire-sandbox.cjs /cartella/evidenze-ui
```

Il primo comando invia4job reali al servizio locale già predisposto nella VM. Il secondo usa una workspace preesistente con risultati e almeno una risorsa nel secondo scenario; intercetta il POST del calcolo e ripristina le configurazioni al termine. I vecchi nomi dei harness browser delegano al nuovo test; il precedente harness nativo delega al nuovo replay API.
