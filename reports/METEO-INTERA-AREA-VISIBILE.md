# Meteo sull’intera area inquadrata

Run: `viewport-weather-recovery-20261020`; base `8af90af1499e4cdbafeae46904b22f6dd3cad3ac` + modifiche di questo incremento. Commit finale: cronologia Git / PUBLICATION.json. Reviewer: Codex, self-check.

## Diagnosi e modifica

FAIL iniziale riprodotto: `WEATHER_CACHE_FULL`, archivio 65.430.345 byte contro budget64MiB; campo Abruzzo scaduto con bounds42.0,13.3–42.9,14.2. Nessuna nuova acquisizione consentita. Il client poteva inoltre non riprovare l’ultima inquadratura dopo un’acquisizione concorrente o cooldown.

PASS recupero:130 JSON compressi senza perdita,11.409.624 byte al momento della migrazione; sorgenti, receipt e snapshot conservati. Ogni compressione verifica i byte decompressi prima di sostituire il file; letture continuano a controllare SHA raw, receipt e normalizzazione. Audit indipendente44 campi, inclusa prima acquisizione successiva. Supporto anche allo storico antecedente condiviso. Nessun aumento budget o eliminazione di esperimenti. La compattazione si ripete quando necessaria; se anche l’archivio compresso raggiunge il limite, il sistema segnala esplicitamente indisponibilità, senza scaricare oltre budget.

PASS client: caricamento legato all’area visibile, retry dopo busy/cooldown, avviso di copertura parziale direttamente sulla mappa, conservazione per scheda del campo fresco ancora adeguato quando altre schede consultano altre aree. Cache privilegia il campo completo più fine fra quelli freschi adeguati. Nessuna estrapolazione oltre il dominio acquisito. Nello studio questo vale per consultazione delle previsioni aggiornate; i risultati fisici mantengono le proprie forzanti congelate e il loro dominio, senza sostituzione silenziosa con altro meteo.

## Esecuzioni reali nella VM

POST `/api/weather/map/refresh` con bounds, seguito da GET `/api/weather/map`; script riproducibile `experiments/runs/viewport-weather-recovery-20261020/live-views.py` (copia privata). Fonte `DWD ICON Global via Open-Meteo`;9 variabili,81 nodi,95 record orari validi per campo. Controllate lunghezze e finitezza di u/v,temperatura,pioggia,umidità,pressione,nuvole,raffiche,radiazione per tutti i record. Snapshot completi conservati nella VM sotto `runs/viewport-weather-recovery-20261020`; URL/SHA/tempi in `reports/viewport-weather-recovery/live-views.json`.

| Vista | Bounds richiesti | Esito | Passo campionato lat×lon |
|---|---|---|---|
| Italia |35,6–48,20|PASS|2,125°×2,275°|
| Europa |34,−12–72,35|PASS|6,175°×7,65°|
| Senegal |12,−18–17,−11|PASS|0,825°×1,15°|

I3 download canonici:1.564.318 byte raw. Nessun confronto di skill meteo o risoluzione locale equivalente è deducibile: il campionamento ampio è intenzionalmente rado e interpolato per visualizzazione; non è una griglia europea campionata a11km.

PASS UI IAB:721×1034 CSSpx, zoom con pulsanti dalla vista Abruzzo all’Italia e poi Europa/Mediterraneo; canvas `weather-field.dataset.coverage=1` in entrambe le viste, vento sull’intera mappa,15 indicazioni temperatura/umidità distribuite, pioggia colorata dove prevista. Avviso d’attesa38s osservato durante cambio vista, poi scomparso a copertura completa. Screenshot privati `italia-ui.png`, `europa-ui.png`; JSON leggibile `reports/viewport-weather-recovery/ui.json`. Nessuna configurazione di scenario modificata. NOT RUN nuova verifica Safari e matrice1440/768/375, axe/FPS/p95/soak; non attribuire la verifica IAB aSafari.

## Test e comandi

VM, dalla cartella app:

```sh
PYTHONPATH=src:tests/unit PROJ_LIB=/usr/share/proj /home/hazardia/hazardia-runtime/core-env/bin/python -m unittest test_map_weather test_antecedent_weather test_regional_wind
```

PASS34 test,18,625s: parsing/integrità, compattazione lossless, gzip alterato/conflitto, riuso senza download, preferenza campo più fine, cooldown e regressioni meteo antecedente/vento regionale. PASS16 assert della policy client con `node tests/browser/viewport-weather-state.mjs`; PASS sintassi moduli modificati e `git diff --check`.

## Negativi preservati e limiti

- FAIL iniziale migrazione: confronto integrale di snapshot dopo compressione includeva `age_s` variabile e ha fallito dopo la corretta compressione. Riavviato il servizio e svolto audit indipendente dei dati; non dichiarata uguaglianza del tempo trascorso. Script negativo conservato.
- FAIL harness unittest iniziale:4 import mancanti senza `tests/unit` nel PYTHONPATH; corretto ambiente, esecuzione finale34PASS. Nessuna installazione.
- FAIL harness UI: riferimento precedente `designBrowser` non disponibile; ripreso tramite browser esistente. Nessun dato modificato.
- FAIL controllo finale su ID globale atteso: scheda concorrente era tornata su Abruzzo. Verificata lettura integra del campo Italia e assenza di nuove richieste provider nel controllo successivo; la copertura locale delle due viste è provata separatamente da DOM e screenshot. Non confondere lo snapshot globale corrente con l’area di ogni scheda.
- NOT RUN poli/attraversamento antimeridiano, rete e quote artificialmente esaurite in UI, nuove prove fisiche e skill/calibrazione. Full gateM5–M7 BLOCKED invariati; questo incremento corregge la consultazione meteo, non qualifica i simulatori.

## Ambiente e conservazione

StessaVM4vCPU/8GiB/19GiB, nessuna installazione/privilegio/costo. Due restart backend con code fisiche/preparazioni controllate vuote, nessun nuovo job fisico;90directory (77SUCCEEDED/8CANCELLED/5ERROR) e workspace rev119, SHA `4247a5f71d3a7daca55ccf0efff7ce1b446f40060e6ffe51f4aec6b34a8570de` al controllo finale. Nessun confronto hash antecedente ricostruito da supposizioni. Archivio finale21.468.207byte,6acquisizioni odierne comprese quelle automatiche delle viste; limiti locali invariati48acquisizioni/giorno,65s fra nuove aree,1MiB/risposta,64MiB archivio.

Fonte gratuita non commerciale: [Open-Meteo prezzi](https://open-meteo.com/en/pricing), [condizioni](https://open-meteo.com/en/terms), verificate2026-10-20. Il servizio gratuito ha limiti e non garantisce disponibilità; nessun piano illimitato o a pagamento attivato. Il budget locale considera81località per acquisizione (massimo3888equivalenti/giorno per questo percorso),9variabili e4giorni. Nessun bypass durante le prove.

Prossimo incremento eseguibile: qualificazione di input/interventi e feedback fisico secondo piano originale; per visualizzazione globale ad alta densità servirà valutare un’acquisizione a tasselli entro budget misurati, senza equiparare interpolazione e dettaglio nativo.
