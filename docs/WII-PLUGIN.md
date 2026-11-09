# Collegare il servizio WII indipendente a HAZARDIA

WII è un progetto/repository separato in `../WII`, con pacchetto `wii` e servizio autonomo8081. HAZARDIA non ne importa il codice, non apre SQLite e non possiede worker WII. L'integrazione è il client HTTP `hazardia.web.wii_client.APIClient` e il renderer dei livelli.

Configurazione nel runtime HAZARDIA:

```json
{"enabled": true, "mode": "client", "port": 8081}
```

`enabled:false` disattiva la sola integrazione. La vecchia configurazione `{"enabled":true}` usa ora il client per default; il worker embedded è stato rimosso. La console precedente `/wii.html` reindirizza a quella autonoma preservando la query.

Le API `/api/wii/*`, manifest/OpenAPI/catalogo v1, tre livelli GeoJSON, schemi storici e artefatti rimangono compatibili. Il proxy ammette soltanto una porta loopback configurata e richieste WII limitate; le protezioni HTTP e le quote sono conservate. Il database resta nella VM nella sua posizione originale. HAZARDIA mantiene le proprie API fisiche/decisionali senza modificarne l'autorità.

Contratto del provider: [OpenAPI](http://127.0.0.1:8081/api/wii/v1/openapi). Guida completa: [WII](../../WII/docs/HAZARDIA-INTEGRATION.md). [Verifiche dell'estrazione](../reports/WII-REPOSITORY-20261025.md).


## WII: inventario e livello nazionali unici ·25ottobre2026

Decisione utente corrente: Abruzzo è un focus di acquisizione, non un modello separato. WII espone un solo livello nazionale, alimentato dalla vista canonica del medesimo SQLite per fonti istituzionali e crawler. Il vecchio ID rischio Abruzzo è alias del prodotto nazionale. Crawler limitato orario, controllo input30s, ricostruzione automatica sul singolo worker; errori/quote restano espliciti. Scala nazionale annualizzata comune; grigio per dati mancanti, verde non significa rischio assente. Le metriche storiche archiviate non validano la nuova fusione; gate scientifici/operativi invariati. Dettagli nel progetto WII: docs/UNIFIED-INVENTORY.md; report reports/wii-unified/. Nessuna modifica ai motori fisici. Questa decisione supera la precedente separazione del pilota.


## WII: verifica temporale unificata ·25ottobre2026

Valutazione autorizzata su fit<=2022/test2023–2025 esclusi dal fit: API provider GET/POST`/api/wii/validation/unified`, rapporto a pagina intera WII`/wii.html?view=validation`. Dettagli nel repository WII: reports/unified-validation/REPORT.md e protocollo immutabile.81,6%del supporto dei perimetri EFFIS nel20%Italia vs76,9%baseline50km; non veri punti d’innesco. Sulle coordinate native nel20%area regionale:49,6%Piemonte/48,8%Puglia/35,5%Abruzzo; accuratezza/completa rilevazione non qualificate, Abruzzo solo3blocchi annuali informativi. Preservare per-regione/per-anno e definizioni separate; anni già esaminati in ricerche precedenti, nessuna qualifica prospettica/operativa. Nuovi test non sostituiscono il livello di produzione né modificano la fisica. Prima implementazione/baseline corretta conservata e dichiarata, nessuna selezione di parametri sul test.
