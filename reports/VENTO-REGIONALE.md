# Vento reale sull’Abruzzo con particelle trasparenti

Run `regional-wind-20261016T071443Z`. Codice finale `74bd696867fa88cffd3f9ae498d57a71b19b568b`; sorgente iniziale5891913, correzione API8883e1c. Reviewer Codex self-check.

## Come provarlo

Apri **Monitoraggio → Vento sull’Abruzzo → Inquadra Abruzzo**. Scegli l’ora e usa **Pausa/Riprendi particelle**. «Particelle del vento regionale» spegne solo il campo; «Meteo» spegne tutti i livelli meteorologici. Colori e movimento indicano intensità/direzione; la scala è inm/s. Le etichette del punto all’Aquila restano opzionali, inizialmente spente. Su telefono «Inquadra Abruzzo» riporta la mappa in vista. Con prefers-reduced-motion si mostrano frecce statiche, con ripresa esplicita disponibile.

## Dati e trasformazioni

Acquisizione reale PASS: **315località**,15×21,41.6–43.0°N/12.9–14.9°E ogni0.1°;96ore UTC16–19ottobre2026. DWD ICON-EU, vento a10m, velocità inm/s e direzione meteorologica FROM, modello unico fisso; nearest-cell ed elevation=nan ripetuto per ciascuna località. **940016byte** scaricati. RawSHA256 `1f3c8ec8c0506262853afda252ae3bb8d24d131c8246b18eb49d20ca78ab02a1`; prima disponibilità osservata **16/10/2026 alle09:18:21Roma** (`2026-10-16T07:18:21.304127Z`). L’inizializzazione del modello non è esposta dal provider e resta UNKNOWN.

Le coordinate effettive315 del modello sono preservate; offset massimo rispetto alla richiesta 3465.09m. Conversione U=−speed×sin(FROM), V=−speed×cos(FROM), ricampionamento IDW sui4punti effettivi più vicini e interpolazione bilineare dei componenti nel renderer. Non si interpolano angoli359°/1°. Campionamento di visualizzazione circa8–11km; griglia ICON-EU dichiarata0.0625°/~7km alla data della verifica. Nessuna estrapolazione oltre il rettangolo, che include mare e regioni vicine.

La velocità delle particelle è amplificata per la leggibilità: non sono traiettorie fisiche di masse d’aria. Il campo regionale è per visualizzazione, **non sostituisce le forzanti puntuali attuali nei simulatori**. La risoluzione fotografica non aumenta quella meteorologica.

## Piano gratuito, cache e sfondo

Solo endpoint pubblico Open-Meteo per uso non commerciale, senza chiavi o pagamento. Conteggio prudenziale:315località per acquisizione, anche se è un solo HTTP; massimo8tentativi/giorno e intervallo3h, cioè2520equivalenti/giorno, oltre ai massimi48 del punto. Risposte≤2MiB, cache regionale≤64MiB; quoteSQLite condivise fra schede e processi nella stessaVM. Le verificheGUI non hanno richiesto ulteriori acquisizioni regionali. Il provider può essere indisponibile: non è un servizio illimitato o garantito.

Sfondo regionale Sentinel-2 cloudless2024/EOX, gratuito non commerciale CC-BY-NC-SA4.0 e attribuzione visibile, consultazione tramiteVM, cacheRAM8MiB/downloadcumulativo16MiB, zoom8–11. Contesto satellitare limitato10–18°E/40.5–44°N per evitare margini vuoti nelle viste larghe; il campo vento resta nel suo rettangolo originale. Al dettaglio si conservano ortofoto Abruzzo2018–2019; il ritaglio Sentinel locale resta disponibile offline. Nessuna immagine è redistribuita suGitHub.

Fonti ufficiali consultate16/10/2026: [API multipunto e nearest](https://open-meteo.com/en/docs), [modello ICON-EU](https://open-meteo.com/en/docs/dwd-api), [limiti e uso gratuito](https://open-meteo.com/en/terms), [conteggio e attribuzione](https://open-meteo.com/en/pricing), [licenza e servizi EOX2024](https://www.eox.at/2025/03/sentinel-2-cloudless-2024/).

## Prove verificabili

**PASS110test software** (63unit/19domain/14decision/14web), **164controlli browser** (26regional/38weather/56design/44monitor), **24scansioni axe0violazioni** con incomplete automatiche conservate.8viewport/orientamenti320–1920; tastiera, movimento ridotto, pausa, layerOFF, navigazione, integrità quote, sfondo reale e selezione ora verificati.2solver/verifier call nel prefisso isolato, nessun job fisico nuovo.

Prestazioni nell’esecuzione isolata Chrome155.0.8059.84 sul Mac come client, backend nella VM: 650particelle, n=87intervalli, p95intervallo=33.400ms, p95costoJSdisegno=0.400ms. Targetgrafico30fps; misura breve, non certificazione di tutti i dispositivi. Memoria delle serie diagnostiche limitata120campioni;180/320/650particelle in funzione della larghezza, DPR≤1.5. Il canvas è trasparente per oltre90%dei pixel nel test, con scie effettivamente disegnate.

Verificatore indipendente nellaVM: **1890confronti U/V** contro il raw congelato; massimoerrore di arrotondamento 0.00005000m/s, non soglia di accuratezza meteorologica. **145file motori invariati**. Comando riproducibile, con output nuovo:

```sh
../core-env/bin/python scripts/verify_regional_wind.py \
  --cache /home/hazardia/hazardia-runtime/web-state/regional-wind \
  --runtime /home/hazardia/hazardia-runtime \
  --output /percorso/NUOVA-verifica.json
```

QAclient: `HAZARDIA_BASE_URL=http://127.0.0.1:8081 node tests/browser/regional-wind.cjs OUTPUT`, con le variabiliPlaywright/Chrome/axe della guida installazione. Altre suite: weather.cjs/design.cjs/monitoring.cjs. Raw log, manifest, acquisizioni positive/negative e archivio cache con SHA verificato: `experiments/runs/regional-wind-20261016T071443Z`. Piano iniziale prima dell’acquisizione; nuovi harness e contesto satellitare introdotti dopo la prima ispezione, non dichiarati integralmente preregistrati. I passaggi di rifinitura sono tracciati dai commit e dai log separati.

## Errori conservati e rilascio

FAIL iniziale di un test: attesoSOURCE_MISSING anzichéSOURCE_TIME per orizzonte incompleto; corretto il test, non allentata la validazione. PrimoHTTPError senza corpo/status conservato. Secondo tentativo diagnosticoHTTP400 documenta che elevation deve avere315elementi; terzo tentativo correttoHTTP200. Due retry diagnostici espliciti, distanziati oltre65s, conservano tutte3le prenotazioni; il limite automatico3h non è stato rimosso. Non attribuire retroattivamente un codiceHTTP certo al primo tentativo.

Prima vista regionale con WMS ortofoto inutilizzabile a quella scala; aggiunto il mosaico satellitare e poi ampliato il solo contesto di sfondo per i margini grigi. Nessun vento inventato. Corretto anche il ripristino involontario dell’ora regionale da parte del refresh del punto; le due selezioni restano controllabili. Ricevute di payload identici conservano il first-seen immutabile, senza corruzione del confronto cache.

PASS deploy9file e successivo contesto satellitare, con backup sorgenti e due riavvii guardati su coda vuota; 823JSON preesistenti preservati (contatori traffico mutabili esclusi dal confronto). Ultimo frontend di centratura mobile copiato senza riavvio. Tutto il backend/acquisizione/preprocessamento nella stessaVM; il browser disegna le particelle come client. Nessuna installazione, aumento risorse, azione operativa o deployment pubblico. [Riepilogo verificabile](weather/regional-verification.json).

**NOT RUN:** nuovi modelli CIMA, forzanti regionali complete nei simulatori, validazione meteo osservativa/calibrazione, nuovo soak30min/100kstress, dispositivi fisici/Safari/Firefox e studio utenti. FullM5–M7 restanoBLOCKED; nessuna conclusioneH1–H3 o skill operativa.


## Chiusura dopo controllo dell’orologio VM

Durante la verifica finale hostUTC12:44:25 e guestUTC07:48:55 mostravano circa17730sdi scarto, pur con NTP dichiarato attivo/sincronizzato. Questo poteva far classificare FRESH la cache ormai vecchia. Causa precisa dell’iperVisore non isolata; osservato dopo una sospensione. A coda vuota è stato eseguito **`sudo -n systemctl restart systemd-timesyncd`**, servizio già installato, senza installazioni o modifiche di configurazione. EsitoPASS; scarto attuale host/guest inferiore3s, prova in final-runtime.json.

La UI ora confronta prudenzialmente età cache del servizio e del browser: oltre120sdi disaccordo, oppure cache scaduta secondo il browser, il dato è segnalatoSTALE e il modulo di nuove simulazioni puntuali è disabilitato. Il controllo non sostituisce la corretta sincronizzazione del sistema per API/CLI dirette. Verifiche nuove PASS: clock-skew-downgrades-source e browser-expiry-downgrades-source; nuovo totale **166controlli browser**,24axe0violazioni.

Aggiornamento **automatico** reale riuscito dopo la risincronizzazione: campo `openmeteo-wind-fba446622ae6fb3410604fa0`, rawSHA256 `fba446622ae6fb3410604fa0e11224bca76fccf92add73d948a13da516715e20`, 940751byte, first-seen `2026-10-16T12:48:01.473900Z`.4prenotazioni regionali totali oggi (due rifiuti più due acquisizioni riuscite), non quattro successi. Il primo dataset940016B resta immutato. Sul nuovo dataset:1890confronti aggiuntiviPASS,145enginehash invariati; il checker restituisce il vecchio nome di campo max_rounding_error_ms con unità **m/s**, non millisecondi.

Frame test aggiornato:650particelle,n=87,p95intervallo=33.400ms,p95disegnoJS=0.200ms.12file runtime/script corrispondono agliSHA del sorgente; limite conservativo download nel checkpointfinale 3688198505/5368709120B. Verifica primaria aggiornata in regional-verification.json; prove precedenti, cronologia e negativi preservati. Nessun nuovo modello CIMA, costo, installazione o cambio delle risorseVM.
