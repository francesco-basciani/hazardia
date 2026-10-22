# Ripristino della mappa di Monitoraggio e del quadro meteo

22 ottobre2026, run `monitor-map-restore-20261022`, parent `0ac55b1a29ac40ba07724f6c91977f6e637ac77b` + documentazione preesistente dirty preservata. Reviewer Codex self-check. Richiesta: mappa poco leggibile e condizioni meteorologiche apparentemente scomparse. Scope FR-24/26, FR-WX-VIEW-01, QR-11–14; nessuna modifica del piano scientifico o al riferimento architetturale MyDewetra.

## Diagnosi osservata

Nella scheda dell’utente era selezionato Satellite regionale/ortofoto, ma il proxy non poteva più acquisire tessere. Contatore persistente 65.017.285 byte, limite 67.108.864 byte; riserva richiesta per quattro fetch concorrenti 2.097.152 byte: ammissione bloccata. Cache RAM vuota dopo i precedenti riavvii. Lo sfondo rimaneva grigio con confini e nomi sovrapposti. Non era un’assenza di territorio o dati meteorologici.

Era inoltre selezionata la sola Pioggia prevista: vento, temperatura e umidità erano disattivati. La previsione disponibile mostrava piogge deboli soprattutto sul mare; meno di0,1mm è intenzionalmente trasparente. Questo spiega parte dell’apparente vuoto, senza dimostrare assenza di altri rischi. Screenshot iniziale `reports/monitor-map-restore/before.png`.

## Correzioni

- Il proxy espone `can_download_tiles`, coerente con la stessa riserva già applicata al download. Il Monitoraggio controlla tale stato prima di aggiungere il layer satellitare. A quota esaurita seleziona esplicitamente OpenStreetMap e mostra il motivo. Nessun aumento/azzeramento dei contatori; ulteriori errori cartografici restano visibili. Anche l’indisponibilità del controllo di stato porta alla cartografia di riserva con indicazione esplicita.
- Vista iniziale **Quadro meteo**: temperature, umidità relativa, probabilità di precipitazione, vento animato e campo trasparente della pioggia prevista. Le singole viste restano selezionabili. Controlli «Scegli i livelli» sulla mappa per temperatura, umidità, vento, pioggia, probabilità e nuvole. Pioggia e nuvole restano alternativi per non confondere due campi sovrapposti.
- Legenda meteo espandibile; data e stato restano visibili anche quando le scale sono chiuse. Fonte, validità, copertura incompleta, cache e mancanti mantengono le semantiche esistenti. Le transizioni grafiche non cambiano previsioni o forzanti fisiche.
- Etichette senza riquadri, contrasto adatto alla cartografia stradale, nomi e confini più leggeri; massimo32 indicatori distribuiti sull’intera inquadratura. Prima, il limite poteva consumare i32indicatori nelle righe superiori di una vista larga: ora colonne/righe sono ridotte uniformemente. Le etichette evitano i pannelli della mappa e si ridistribuiscono quando si apre la legenda.

Queste modifiche riguardano il Monitoraggio. Nessun nuovo job fisico o effetto sugli incendi/alluvioni è derivato da questa correzione grafica. Lo sfondo satellitare resta disponibile solo nei limiti di copertura, fonte e quota già dichiarati; il fallback non equivale al ripristino del servizio satellitare.

## Verifica

Tutto il backend e le acquisizioni restano nella VM esistente,4vCPU/8GiB, nessuna installazione/sudo/costo. Riavvio a coda inattiva:90job preesistenti (77SUCCEEDED,8CANCELLED,5ERROR), nessuna interruzione.145file motori e8file workspace/casi invariati viaSHA256. Stato satellite dopo il riavvio: stessi contatore/limite,0richieste upstream del nuovo processo,0errori,`can_download_tiles=false`.

Comando nella VM, dalla directory app:

```sh
PYTHONPATH=src:tests/unit ../core-env/bin/python -m unittest test_maps test_regional_satellite test_osm_tiles test_map_weather -v
```

**PASS27test**. Controlli JavaScript puri sul client di sviluppo, senza browser esterno: `rain-clarity.mjs`18,`rain-series.mjs`14,`viewport-weather-state.mjs`16,`weather-render-plan.mjs`6013: **PASS6061check**, includendo equivalenza di campionamento, mancanti, riuso DOM e piani di rendering. Primo tentativo render-plan FAIL per stub DOM senza `classList`, conservato nell’output della sessione; accesso opzionale al tema ripristinato senza alterare dati o fixture. Run finale in `render-plan.log`.

**PASS UI reale IAB**, tramite gli strumenti computer-use: fallback automatico, tre variabili numeriche distribuite (°C/UR/probabilità), particelle e campo precipitazioni, toggle temperatura, mutua esclusione nuvole/pioggia, ritorno al preset. Desktop1280×720 e scheda utente2252×1034; telefono375×812 e tablet768×1024, larghezza documento uguale al viewport (nessun overflow orizzontale). Acquisizione meteo completata prima di giudicare il rendering: la prima cattura mobile intermedia non mostrava ancora i valori, la verifica dopo l’adattamento li mostra. Screenshot finali e riepilogo `reports/monitor-map-restore/ui.json`. Scheda utente aggiornata mantenendo URL/caso; nessuna modifica alle sue configurazioni di simulazione.

Campione breve del canvas desktop:1250frame accumulati; finestra mobile di120campioni, p95 intervallo33,4ms e p95 costo disegno0,2ms, circa30fps. Non è un nuovo benchmark completo QR-11–14, un test di Safari fisico o un soak. Non dimostra prestazioni universali. Override viewport temporaneo ripristinato, scheda di QA separata chiusa a fine lavoro.

| Attività | Esito |
|---|---|
| Diagnosi e fallback reale senza aumento dei download satellitari | PASS |
| Ripristino meteo combinato e selezione dei singoli livelli | PASS UI/software |
| Regressioni mappe/meteo e preservazione simulatori/workspace | PASS |
| Nuove simulazioni fisiche, skill meteorologica/idrologica, allerta qualificata | NOT RUN |
| Nuovo benchmark completo QR-11–14, dispositivi fisici e soak | NOT RUN |
| Full M5–M7 scientifici | BLOCKED, invariati |

Nessun dato inventato per riempire la mappa, nessuna risoluzione del modello aumentata dalla densità delle etichette. Riferimento per i dati: snapshot reali della cache Open-Meteo nella VM, con provenienza mostrata nella UI.

## Incidente finale e ripristino della VM
Durante la copia finale delle evidenze, SSH ha restituito Connection refused. `utmctl list` mostrava HAZARDIA-M0-ARM64 stopped; causa non determinata. Riavviata la stessaVM, risorse invariate, con `utmctl start 6706102A-6B83-4DE2-8475-D8D8E067BE41`, poi servizio esistente e tunnel solo127.0.0.1. HTTP200 e verifica postboot PASS:8fileworkspace/145pin/90job preservati; contatore satellitare identico,nessun job interrotto. Evidenza `after-vm-restart.json`. Nuova verifica visiva sulla scheda utente dopo il riavvio.
