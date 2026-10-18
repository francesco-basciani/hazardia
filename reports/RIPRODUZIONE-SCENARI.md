# Riproduzione dei risultati — 18 ottobre 2026

Run `playback-repair-20261018`; parent `435a45fa5457d691e6d5e5f0d1e72637a7101264` + modifiche; commit finale nel manifest PUBLICATION. Reviewer: Codex self-check. Ambito FR-26/27/28, FR-FIRE-AUTHOR e timeline; nessun cambiamento dei modelli o del piano M0–M7.

Il vecchio timer avanzava ogni secondo senza attendere le immagini delle tre mappe. Ritardando di1800ms ciascuna risposta PNG, il token di rendering veniva superato dal passo successivo: per6secondi ora e mappe restavano a24h. Il log negativo è conservato in `experiments/runs/playback-repair-20261018/slow-before.log`, con JSON/screenshot. Il probe rapido e il primo controllo IAB precedente alla correzione avanzavano: il guasto è riprodotto nelle condizioni lente, senza attribuire con certezza queste condizioni al click originario dell’utente. Due pulsanti Riproduci separati, entrambi sotto le mappe, rendevano inoltre ambiguo quale tempo si stesse avviando.

La riproduzione ora attende download e decodifica di tutti i risultati richiesti prima del campione successivo. Il PNG originale viene scaricato una sola volta e riusato come blob per Leaflet; `data-source-url` conserva il riferimento all’asset nativo. Cache limitata con revoca dei blob non correnti. Pausa invalida il rendering pendente e ripristina l’ora effettivamente dipinta; HTTP503 mantiene l’ultimo quadro e presenta un errore. Durata massima presa dai risultati disponibili; senza risultati il comando è disabilitato. La timeline Evoluzione dell’incendio è sopra le mappe, con Riproduci incendio/Pausa incendio. In modalità Meteo del risultato non compare un secondo player: il campo congelato segue il risultato. Previsioni aggiornate mantiene il player di consultazione separato; il cambio fonte aggiorna immediatamente le mappe.

## Verifiche

- **PASS**28controlli dedicati con i tre risultati nativi Fonte Vetica72h già disponibili nella VM: progressione reale dei tre PNG, pausa, seek, passi avanti/indietro, rete lenta1800ms, nessun salto del primo campione, un download per URL, pausa durante caricamento, HTTP503, fine72h/ripartenza, fonti meteo, bozza senza risultato, responsive e immutabilità workspace.
- **PASS**30regressioni `dynamic-fire.cjs`: trasporto/preparazione/cancellazione/batch con risposte QA isolate dichiarate, rotellina disabilitata, monitoraggio, nessuna scrittura ai workspace reali. Fixture meteo congelata del run precedente; non nuovo fetch provider misurato.
- **PASS**6axe senza violazioni,375/768/1440, Chrome155.0.8059.84 su Mac come client della VM. Solo per iniettare axe il profilo QA usa bypassCSP; il secondo probe, prima dell’iniezione axe bloccata, ha eseguito i controlli funzionali con CSP normale. La CSP applicativa resta invariata.
- **PASS**IAB utente, stessa scheda ricaricata:24→35,25h, aree native e valori meteo aggiornati; pausa a35,25h. Screenshot `iab-paused.png` nel raw. Nessuna nuova finestra.
- **PASS**workspace principale e caso invariati prima/dopo il test; nessun nuovo job scientifico.
- **FAIL**tentativi harness intermedi conservati: controllo nascosto non aperto; iniezione axe rifiutata dalla CSP; attesa fissa300ms alla ripartenza insufficiente per PNG reali. Corretti apertura dettagli, profilo axe e attesa del quadro effettivo. Nessun errore JavaScript nel test finale.
- **FAIL tracciabilità parziale**il probe rapido dopo la correzione ha sovrascritto per errore il primo screenshot/JSON rapido. Rinominati `after-fast-probe.*` per evitare falsa attribuzione. Restano il log originale `probe.log` e tutti gli artefatti negativi lenti; non si ricostruiscono gli originali perduti.
- **NOT RUN**nuove esecuzioni PROPAGATOR, benchmark p95/FPS/soak, dispositivi fisici, nuova validazione scientifica. **BLOCKED**qualificazione input/interventi/skill e fullM5–M7, invariati.

## Ripetizione

Backend/runtime già avviati nella VM esistente; nessuna installazione o riaccensione. Client browser con Playwright locale. Impostare `HAZARDIA_PLAYWRIGHT_PATH`, `HAZARDIA_BROWSER_EXECUTABLE` e `HAZARDIA_AXE_PATH` ai runtime locali documentati nelle precedenti prove; cartella output deve essere nuova.

```sh
node tests/browser/fire-playback.cjs <nuova-cartella-output>
HAZARDIA_FIELD_FIXTURE=experiments/runs/dynamic-fire-domain-20261018/field-italy.json node tests/browser/dynamic-fire.cjs <nuova-cartella-regressione>
```

Il primo test legge per default `http://127.0.0.1:8080/?view=results&case=fonte-vetica-20261018` e inietta ritardi/errori soltanto nel proprio browser; non modifica le bozze reali. Richiede il caso72h disponibile, oppure `HAZARDIA_SAVED_CASE` con pari struttura/tempi. I raw locali comprendono gli esiti negativi, log e screenshot; il sommario pubblicabile è `reports/playback-repair/verification.json`. Il test non ricrea i tre job: helper e preregistrazione in `reports/FONTE-VETICA-20261018.md`.
