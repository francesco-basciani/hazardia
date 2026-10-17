# Monitoraggio territoriale: requisito e stato effettivo

Revisione `monitor-fusion-review-20261017`, base `07eb050effff8546f6a541e16a11b7c93574e404`, reviewer Codex self-check. Solo riesame del codice e chiarimento dei requisiti; nessuna nuova acquisizione, simulazione, installazione o modifica al runtime.

## Riscontro

`src/hazardia/web/static/monitoring.js` mostra prodotti di scenari selezionati e livelli meteo. Non è un motore di fusione territoriale continua. `src/hazardia/adaptation/alerts.py::AlertBook.update` richiede esplicitamente `qualification == SYNTHETIC_RESEARCH`, impatto conosciuto e soglia della fixture. Questo prova l'esistenza del ciclo software di ricerca, non l'allertamento territoriale reale. Hash sorgenti nel raw locale `experiments/runs/monitor-fusion-review-20261017/review.json`.

## Fonti consultate il 17 ottobre 2026

- [Sistema nazionale, Protezione Civile](https://www.protezionecivile.gov.it/it/approfondimento/il-sistema-di-allertamento-nazionale/): integrazione di previsioni, radar, satelliti e sensori; zone omogenee e soglie territoriali; effetti differenti a parità di pioggia. Le allerte regionali restano prodotti dell'autorità competente.
- [EFFIS data and services](https://forest-fire.emergency.copernicus.eu/applications/data-and-services): catalogo di FWI e componenti, Drought Code, combustibili e rilevamenti attivi. Consultare il catalogo non equivale ad aver acquisito o integrato questi prodotti; licenze, endpoint, accesso, copertura e quote ancora da verificare per l'uso concreto.

Non è stato esaminato alcun algoritmo privato di Allarmeteo. Non si attribuisce a quel servizio la metodologia specifica di HAZARDIA.

## Incrementi eseguibili nell'ordine originale

1. M2: censire e verificare accesso/diritti/temporalità per indici incendio/siccità e bollettini/zone ufficiali, conservando snapshot reali nella VM. Integrare i connettori concreti senza pretendere tutte le fonti globali disponibili.
2. M2/M5: costruire prodotti territoriali spiegabili separati per hazard con meteo spaziale, storico antecedente, contesto e copertura qualificata; mostrare in mappa evidenze e provenienza. Un segnale meteo resta tale finché non è qualificata la stima d'impatto.
3. M5/M6: aggiornamenti deduplicati, scadenza, qualità dati e graceful degradation; acquisizione mancante produce valutazione parziale/non disponibile, mai automaticamente verde. Collegamento esplicito alla preparazione di una simulazione.
4. M7: replay storico senza dati futuri, valutazione falsi positivi/lead time e trasferibilità; niente promessa di accuratezza derivata dalla sola UI.

FR-MONITOR-FUSION-01 in SPEC definisce criteri e differenze tra osservazione, previsione, attenzione interna e allerta ufficiale. Nessuna soglia operativa scelta in questa revisione. Il requisito è confermato, la funzionalità completa è ancora da implementare e verificare; non si chiude M5–M7.
