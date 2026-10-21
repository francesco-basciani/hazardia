# Legenda degli oggetti cartografici — 21 ottobre 2026

Run `map-symbols-20261021`; base privata3d224787197fe7ce18f4f069454c81575f8fc4fb + modifiche UI mirate; reviewer Codexself-check. Fonte dell'interpretazione: codice effettivo `territorial-layers.js`, `osm_catalog.py`, `event-markers.js` e contesto realmente caricato nella VM. Non sono nuove osservazioni o esecuzioni fisiche.

La linea fucsia tratteggiata era ed è un tracciato elettrico aereo OSM; la tensione è negli attributi quando disponibile, non si presume alta tensione o quota verificata. I vecchi cerchi viola erano condivisi da categorie diverse. Adesso abitati/residenziale sono viola, sanità turchese, istruzione blu, emergenze arancio; linee/sostegni elettrici rimangono fucsia. Idranti, DAE e polizia hanno etichette specifiche ricavate dai tag, non sono indicati come squadre disponibili.

La legenda sulla mappa è richiudibile e scorrevole, con dettagli espandibili per ogni voce. Mostra geometria punto/area/tracciato, conteggi degli oggetti inseriti nei livelli correnti, fonti/limiti semantici. Colori, tratteggi e riempimenti sono definiti dalla stessa funzione usata per i layer, incluse le frequenze di contatto simulate; non si convertono in rischio umano. Distinti località puntuali GeoNames, edificato WorldCover2021 e aree residenziali OSM. Nome geografico e confini Istat hanno voci proprie. I riferimenti incendio/alluvione e le rispettive campiture restano esplicitamente simulati. Meteo/allerte conservano le scale dedicate.

Popup e tooltip territoriali mostrano categoria e nome; i testi OSM sono inseriti come testo DOM, non HTML. Legenda aggiornata con filtri e vista, senza nuove acquisizioni introdotte dal controllo. I caricamenti del contesto durante QA sono quelli del percorso esistente. La UI riusa dati/risultati presenti; nessun simulatore o ottimizzatore avviato, nessun caso utente modificato. Piattaforma generica e responsabilità M0–M7 invariate.

| Verifica | Esito | Evidenza |
|---|---|---|
| Corrispondenza tra stile e significato, categorie distinte, punto/area/linea, ferrovia versus linea elettrica, contatto simulato e unknown, idrante versus DAE | PASS | `node tests/browser/map-symbols.mjs`:25controlli; `experiments/runs/map-symbols-20261021/unit.json` |
| Contesto reale caricato e voci specifiche | PASS | Browser integrato, areaL'Aquila42.3525,13.39; lettura16voci, incluse3linee elettriche,31sostegni,44idranti,2DAE in uno snapshot della vista. I conteggi possono cambiare con zoom/inventario |
| Filtro elettrico | PASS | Disattivazione: linea e sostegni rimossi da mappa/legenda; altri livelli conservati. Ripristino/ricaricamento verificato |
| Dettagli, nessun errore console, overflow e prova visuale | PASS nel checkpoint consegnato | `experiments/runs/map-symbols-20261021/ui-proof.json`, `ui-final.png`; non attestano ogni browser/dispositivo |
| Nuove prove fisiche, efficacia, p95, verificaSafari e telefono | NOT RUN | Non richiesti per questo cambiamento di simbologia; gate scientificiM5–M7 BLOCKED invariati |

Nessuna installazione o modifica amministrativa. Servizio e dati nella VM esistente, aggiornamento di soli asset web. Controllo unitario UI in Node sul client di sviluppo; verifica end-to-end nel browser contro il servizio VM. Raw originali e manifest privati preservati. Prossimo incremento pertinente: validazione dell'usabilità con utenti e browser/dispositivi reali, senza dedurre accuratezza geografica dalla leggibilità dei simboli.
