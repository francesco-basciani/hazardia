# Riordino dashboard e unità di evacuazione

Run `workspace-repair-20261016`, base `841424a3498419ac2018d2e15a24f427ae125e1c` + modifiche tracciate nei checksum di `reports/workspace/verification.json`. Reviewer: Codex self-check. Richiesta: ridurre controlli dispersi, rendere meteo leggibile, avvicinare confronto alle mappe e chiarire/abilitare le risorse decisionali.

## Risultato utilizzabile

**PASS** configurazione unica aperta dal pulsante accanto alla mappa: cartografia/confini, scenari/trasparenza, dettagli meteo. Ora/livello meteo e lettura temperatura, vento e pioggia al centro della vista restano presso la mappa. Vento animato più leggibile, campo temperatura trasparente predefinito; pioggia nulla resta senza colore. Comandi mappa unica/affiancate, sincronizzazione e inquadratura sono immediatamente sopra il confronto. Annotazioni e dettagli tecnici sono richiudibili. Nessun cambio di sorgente o risoluzione meteorologica.

**PASS** editor fino a 8 unità di evacuazione: clic «Posiziona» poi mappa, coordinate, disponibilità, arrivo manuale. I valori arrivano realmente al problema del solver; unità indisponibili e arrivi incompatibili sono respinti dal verificatore. Coordinate determinano il punto mostrato: nessun percorso o tempo di viaggio è dedotto dalla distanza. I benefici restano coefficienti sintetici di ricerca: per arrivo `a` secondi, fattore `max(0,1-a/600)/0.8` sui coefficienti nominale/stress esistenti; 2min conserva il riferimento, 8min lo riduce a un quarto. Nessuna calibrazione di efficacia. L'inventario personalizzato è di sessione, registrato nell'immutabile problema della decisione; «Salva impostazioni di base» non salva queste righe. Rolling e preset non accettano simultaneamente questi override.

**BLOCKED** completamento antincendio: posizioni/tipi di squadre, Canadair ed elicotteri non modificano ancora PROPAGATOR. Il confronto di evacuazione mantiene lo stesso pericolo fisico. Il confronto fisico separato resta l'esperimento di barriera ideale, non un inventario operativo. Non dichiarare soddisfatta la richiesta di flotta antincendio.

## Quale meteo alimenta cosa

Il meteo della mappa è consultazione, selezionabile per ora. Ogni risultato esistente conserva il proprio forcing e mostra origine/data accanto al confronto. Le nuove simulazioni selezionano per default FORECAST: FIRE utilizza vento reale puntuale Open-Meteo costante per <=1h, terreno reale, vegetazione/umidità del combustibile ancora ipotetiche. FLOOD usa la serie puntuale reale di pioggia/temperatura/umidità atmosferica/vento/pressione/radiazione, con parametri non calibrati. I prodotti storici mantengono ERA5. **BLOCKED** FR-FIRE-FORCING-01 completo: vegetazione reale, stima qualificata dell'umidità del combustibile e forcing distribuito/variabile nel tempo. **NOT RUN** nuovi job fisici in questo incremento, che non modifica gli adapter nativi.

## Verifica e ripetizione

Tutto il backend e i test Python sono nella VM Ubuntu22.04ARM64, 4vCPU/8GiB; Chrome155 su Mac è il client di visualizzazione/test. Nessuna nuova installazione, nuova sorgente o aumento dei limiti. Riavvio backend solo su coda inattiva; 857 JSON precedenti confrontati: solo i due contatori di traffico mappe cambiano, i restanti 855 restano identici. 14 file sorgente distribuiti corrispondono ai checksum locali.

Comandi dal checkout guest, con `PYTHONPATH=src`:

```sh
/home/hazardia/hazardia-runtime/core-env/bin/python -m unittest discover -s tests/unit -v
/home/hazardia/hazardia-runtime/core-env/bin/python -m unittest discover -s tests/domain -v
/home/hazardia/hazardia-runtime/decision-env/bin/python -m unittest discover -s tests/decision -v
/home/hazardia/hazardia-runtime/core-env/bin/python -m unittest discover -s tests/web -v
```

**PASS** 70 unit +19 domain +18 decision +14 web =121 test. Browser: impostare `HAZARDIA_PLAYWRIGHT_PATH`, `HAZARDIA_BROWSER_EXECUTABLE`, `HAZARDIA_AXE_PATH`, poi `node tests/browser/workspace-repair.cjs OUTPUT`. **PASS** 30 verifiche inclusi clic di posizionamento, POST e problema restituito, disponibilità, meteo e controlli; 6 scansioni axe senza violazioni a375/768/1440px, nessun errore JS o POST job nativo. Artefatti grezzi: `experiments/runs/workspace-repair-20261016/`, risultati finali `final-v5/`, screenshot non redistribuiti su GitHub per preservare le condizioni delle immagini di sfondo.

## Esiti negativi preservati

- **FAIL**, poi corretto: prima assertion software attendeva VALID invece del corretto VALIDATED_FOR_SIMULATION.
- **FAIL**, poi corretto: Canvas nascosto con dimensioni zero; guardia prima di createImageData. Axe segnalava link attribuzioni senza sottolineatura.
- **FAIL**, poi corretto: modifica intermedia handler inquadratura aveva sintassi JS errata; verifica sintassi e nuova suite.
- **FAIL** harness selettore CSS non quotato; corretto senza cambiare funzionalità.
- **FAIL**, poi corretto: coordinate da mappa a6decimali respinte dalla validazione HTML step a5decimali; step=any con limiti server preservati.
- Tessere temporaneamente mancanti durante raffiche contro proxy con ammissione limitata: massimo3 retry locali progressivi, quota e fonte invariate. Screenshot dopo completamento e dissolvenza tessere; indisponibilità persistente resta possibile e segnalata.
- VM con ritardo169s rispetto al Mac: riavvio del servizio timesyncd già presente, poi scarto circa1s. Nessuna configurazione/installazione, causa della ricorrenza non dimostrata. Gate di scadenza/skew e prefisso di cache non attuale preservati; qualificazione della stabilità orologio **BLOCKED**.
- Prima verifica finale tentava di leggere un harness browser non distribuito nel guest: selezione ristretta ai14 file runtime, confronto **PASS**; test browser è eseguito sul client, non nel guest.

Queste sono evidenze ingegneristiche, non uno studio di usabilità o una validazione fisica. **NOT RUN** dispositivi fisici, Safari/Firefox, nuovo soak30min e carico100k. Full M5–M7 restano **BLOCKED**. Prossimo incremento scientifico: input fisici qualificati e interventi antincendio con manifest consumati e confronto nativo abbinato; non sostituire la fisica con coefficienti grafici.
