# Probabilità di pioggia e nuvole leggibili

Run `rain-probability-clouds-20261020`,20ottobre2026. Base `7c9317f770e8b169c66f4fdc583c2b40e65b7a2c` + modifiche; SHA finale Git/PUBLICATION.json. Reviewer Codex, self-check. Verifica tecnica esplorativa, non studio di accuratezza previsionale preregistrato.

## Risultato

PASS: probabilità di precipitazione acquisita dall’API come decima variabile `precipitation_probability`, validata0–100%, mostrata come `Prob. pioggia` sulle indicazioni distribuite e selezionabile separatamente in Monitoraggio e Simulazioni. Attiva inizialmente insieme alle nuvole, senza alterare scenari/risorse. La probabilità proviene dagli ensemble del provider: non viene calcolata dai millimetri, dall’umidità o dal colore delle nuvole. Il dato indica precipitazioni >0,1mm, inclusa eventuale neve, nell’ora successiva alla validità indicata. Fonte/metodo e intervallo dichiarati; il provider non identifica qui il singolo ensemble/run per ogni valore.

[Documentazione ufficiale Open-Meteo](https://open-meteo.com/en/docs), consultata2026-10-20: probabilità riferita all’ora precedente del timestamp provider. Normalizzazione usa quindi il valore n+1 per rappresentare la prossima ora, come la pioggia. Interpolazione spaziale/temporale solo di consultazione, nessuna probabilità locale calibrata o previsione al minuto dedotta. L’endpoint ICON Global restituisce realmente la variabile; non è stato necessario cambiare il modello del vento/temperatura/territorio.

PASS nuvole: palette continua azzurro→lavanda→chiaro con copertura crescente, opacità massima0,68 rispetto a0,34 precedente, zero a cielo sereno. Transizioni spaziali/temporali interpolate; satellite, confini, nomi e interazioni restano visibili. La scala0/25/50/75/100% misura copertura nuvolosa, non intensità della pioggia né allerta; pioggia conserva la propria scala inmm/ora. Legenda dei livelli aggiornata. Rappresentazione di campo previsionale, non immagine di nuvole osservate da satellite.

## Prove e configurazione

Stessa VM4vCPU/8GiB/19GiB, nessuna nuova installazione/costo/privilegio. Un restart backend a code fisiche/preparazioni vuote; recupero jobinterrotti `[]`. Nessun nuovo jobfisico. Workspace principale rev119/SHA `4247a5f71d3a7daca55ccf0efff7ce1b446f40060e6ffe51f4aec6b34a8570de` invariato rispetto al controllo iniziale;90job (77SUCCEEDED,8CANCELLED,5ERROR) invariati.

PASS probe reale1località42.4,13.7,1giorno, `models=icon_global`, `hourly=precipitation_probability,cloud_cover`; raw conservato VMrun/probability-icon-probe.json. PASS acquisizioni automatiche81nodi/95ore/10variabili via API della dashboard, snapshot `map-weather-6a591483e0ca8c01be41de18`, raw546072byte, disponibile2026-10-20T20:28:16.406991Z, bounds40.0,11.7–44.0,17.6. Range probabilità0–100% e nubi0–100%; tutti i valori finiti entro limiti. Audit53campi in cache, di cui50precedenti senza probabilità ancora leggibili/verificati per rawSHA/receipt/normalizzazione; non aggiunta probabilità inventata agli archivi. Dettagli e URL completi in `reports/rain-probability-clouds/verification.json`. Snapshot completo privato nella VMrun/new-field.json.

Budget invariati48acquisizioni cache/giorno,65s fra nuove aree,1MiB/risposta,64MiBarchivio. Al controllo11/48 e30.265.151byte, oltre al piccolo probe manuale separato registrato sopra.10variabili/4giorni nella stessa richiesta, nessun nuovo percorso di polling o servizio commerciale; [piano gratuito](https://open-meteo.com/en/pricing) e [condizioni](https://open-meteo.com/en/terms) restano quelli già verificati. Campionamento viewport variabile e copertura globale mantengono i limiti dichiarati nel report precedente.

PASS36testVM,4,949s:

```sh
cd /home/hazardia/hazardia-runtime/app
PYTHONPATH=src:tests/unit PROJ_LIB=/usr/share/proj /home/hazardia/hazardia-runtime/core-env/bin/python -m unittest test_map_weather test_antecedent_weather test_regional_wind
```

Test nuovi: probabilità80% con pioggia0mm non viene convertita o annullata; allineamento n+1; rifiuto None/−1/101/bool; vecchi snapshot senza campo conservano modello/schema normalizzato precedente. Regressioni acquisizione/cache e storico/vento comprese. Log `reports/rain-probability-clouds/unit-tests.log`.

PASS12controlliJS (`node tests/browser/cloud-probability.mjs`): differenza colori/opacità, trasparenza cielo sereno, on/off, interpolazione probabilità, mancanza nei dati legacy. PASS16assert policyviewport (`node tests/browser/viewport-weather-state.mjs`), sintassi6moduli e `git diff --check`.

PASS UI IAB1280×720: intera vista coperta (coverage1),8949pixelcampionati nuvolosi,2511piovosi;18indicazioni percentuali0–92,23% al primo orario. Toggle nuvole: pixel6783→0→6783 nella vista con pannello aperto; toggle probabilità: etichette→0→ripristino. Legende distinte e nessun overflow orizzontale osservato. Replay20/10/20:05Z→22/10/14:50:18.240Z, probabilità del primo indicatore68,46→2,64%, poi pausa; transizione grafica fra record, non nuova previsione a quel minuto. JSON `reports/rain-probability-clouds/ui.json`; screenshot privato `experiments/runs/rain-probability-clouds-20261020/monitor-clouds.png`.

PASS confronto salvato:2mappe mantengono le forzanti originali, probabilità mancante dichiarata una volta nella legenda senza ripetere n/d su ogni indicatore; selettore disponibile, nessun fetch/innesto di probabilità attuale nei risultati passati. `reports/rain-probability-clouds/frozen-ui.json`. Controllo iniziale contentDocument dal parent non accessibile tramite il runtimeUI, ripreso con frameLocator; nessun FAIL prodotto rilevato. Nessuna modifica dello scenario per verificare i livelli.

## Limiti e prossimo incremento

NOT RUN Safari, matrice responsive375/768/1440, nuovaaxe/FPS/p95/soak, eventi meteorologici estremi, calibrazione probabilistica e nuovi calcoli CIMA. BLOCKED fullgateM5–M7 e qualificazione fisica/operativa rimangono invariati. I campi preesistenti senza probabilità restano tali; la consultazione aggiornata non retrodata una previsione. La visibilità più marcata non migliora risoluzione o accuratezza del modello.

Prossimo incremento eseguibile secondo piano: qualificazione degli input/interventi e feedback fisico; nessun nuovohazard o deployment introdotto.
