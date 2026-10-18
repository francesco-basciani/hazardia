# Scenario nominale e alternative

Run `nominal-layout-20261018`,18ottobre2026; base privata957313af2dc9e32dae987848fabca68e3df1d828 con modifiche, revisore stesso agente Codex. SHA finale in Git e PUBLICATION.json.

Il nominale resta nella mappa principale a larghezza piena. Le alternative occupano le righe sotto: due colonne su desktop, una fino a900px; una sola alternativa usa tutta la larghezza. Cambiare selezione modifica soltanto il destinatario dell’editing, senza scambiare mappe, nomi o risultati. Il nominale resta visibile e protetto.

Un nuovo workspace parte con un nominale senza inneschi, squadre o risultati. Configurazioni e casi già salvati sono conservati. Ogni alternativa ha Modifica ed Elimina; Annulla eliminazione recupera l’ultima eliminata nella posizione originale durante la sessione. Eliminazione impedita durante calcoli pendenti. Gli artefatti nativi restano archiviati nella VM. Non esiste un cestino persistente dopo reload.

## Verifiche

PASS76check browser complessivi, di cui9controlli axe a375/768/1440px. Suite nominal-layout25, scenario-authoring23, forecast-profile14 e midrun-edit14. Nessuna scrittura nelle workspace reali durante i test: trasporti di salvataggio/calcolo isolati, dati nativi letti soltanto. Verificati creazione, ordine e identità Leaflet attraverso selezioni, eliminazione, annullamento, reload, unità/geometrie sulla mappa scelta e replay meteo/tempo del caso reale esistente. Sommario completo: reports/nominal-layout/verification.json.

FAIL iniziali conservati in experiments/runs/nominal-layout-20261018: authoring-1 usava ancora #map come editor selezionato, ora mappa nominale permanente; nominal-1 attendeva750ms prima del salvataggio iniziale, sostituiti con attesa dello stato osservabile. Entrambe le suite corrette rieseguite PASS.

Comandi riproducibili (Node/Playwright/Chrome locali già disponibili; nessuna installazione):

```sh
node tests/browser/nominal-layout.cjs <nuova-directory-output>
node tests/browser/scenario-authoring.cjs <nuova-directory-output>
node tests/browser/forecast-profile.cjs <nuova-directory-output>
```

Impostare HAZARDIA_PLAYWRIGHT_PATH al modulo Playwright, HAZARDIA_BROWSER_EXECUTABLE al Chrome installato, HAZARDIA_AXE_PATH alla copia axe.min.js verificata; scenario-authoring usa anche HAZARDIA_FIELD_FIXTURE dal precedente run dynamic-fire-domain. Servizio locale8080 inoltrato alla VM. Raw privati conservati nella directory del run, fixture già descritte nei report precedenti. Nessun nuovo job fisico, restart backend o acquisizione forzata di dataset.

## Il vento influenza il fuoco?

Sì: src/hazardia/adapters/workers/fire_studio.py converte velocità in km/h, campiona velocità e direzione distribuite per ogni ora e le imposta nelle BoundaryConditions realmente consumate da PROPAGATOR insieme a DEM, vegetazione e umidità del combustibile. La direzione meteorologica indica da dove arriva il vento. Le scie animate visualizzano i dati, ma non sono il collegamento fisico. Il caso previsto usa ICON Global tramite Open-Meteo, risoluzione dichiarata circa11km: interpolazione sulla griglia non crea osservazioni di vento30m o raffiche locali.

PASS audit del percorso e riscontri nativi precedenti in reports/FISICA-METEO-E-SQUADRE.md e PREVISIONE-CON-DATI-REALI.md. Il vecchio confronto modificava congiuntamente più forzanti: non attribuire le differenze alla sola direzione. NOT RUN nuovo esperimento isolato direzione/intensità in questo incremento UI. BLOCKED calibrazione e skill locali, efficacia/logistica mezzi e gate scientifici completi M5–M7 invariati. Nessun beneficio operativo dedotto dall’interfaccia o dalle sole differenze dei perimetri.
