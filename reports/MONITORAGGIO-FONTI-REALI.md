# Monitoraggio con fonti reali

Run `monitor-real-20261017`, base `e2b9404080479a678aa54c760d583cae5f7a254c`, reviewer Codex self-check. Incremento M2/M5/M6/M7 per FR-MONITOR-FUSION-01. Fonte di verità per gli esiti: CHECKLIST.md. Non chiude i gate scientifici precedenti.

## Cosa è disponibile

Nella stessa dashboard, **Monitoraggio → Attenzione territoriale**, vengono acquisiti nella VM:

- **EFFIS / Copernicus EMS, modello Météo-France**: FWI (pericolosità meteorologica incendio) e DC (Drought Code, secchezza del combustibile profondo), per oggi e domani. Indici nativi numerici in TIFF WMS, classificati con le soglie pubblicate da EFFIS; circa10km di risoluzione del modello e campionamento cartografico WMS0,1°. L'emissione/run del modello non è fornita dal servizio e resta sconosciuta; giorno richiesto e acquisizione sono espliciti. Indici meteorologici, non incendi osservati, misure locali di moisture o rischio d'impatto qualificato.
- **Dipartimento della Protezione Civile**: bollettino nazionale di criticità/allerta con187zone per ciascun giorno, motivazioni separate per rischio idraulico, temporali e idrogeologico, nomi e Comuni. Non sono poligoni di allagamento. Revisione GitHub ufficiale bloccata nello snapshot; emissione interpretata dal nome/documento in Europe/Rome, conservata separatamente dalla data interna del JSON.
- **Contesto meteo**: sulla posizione interrogata vengono affiancati, quando il campo esistente li copre, temperatura/vento previsti e accumulo di precipitazione del giorno UTC solo con24intervalli completi. Sono campioni del modello ICON distinto, non nuove soglie di alluvione e non dati assimilati in EFFIS/DPC. Umidità relativa spaziale assente nel campo corrente dichiarata non disponibile; il prodotto puntuale preesistente resta separato.

Le evidenze nella stessa posizione sono collegate in una scheda spiegabile senza sommare indici incompatibili in un nuovo punteggio arbitrario. Filtri indipendenti per hazard, giorno e FWI/DC; classi basse opzionali, livelli trasparenti, click sulla mappa e pulsante accessibile **Esamina il centro della mappa**. Il pannello è richiudibile sulla mappa. **Inquadra copertura delle fonti** apre la vista Italia; sfondo EOX a zoom4–11 con contesto continuo attorno all’inquadratura italiana mantenendo i precedenti limiti di traffico/RAM. I risultati dei simulatori precedenti restano attivabili in Configurazione come scenari di ricerca e sono nascosti inizialmente. Nessun job fisico o decisione parte dalla consultazione.

## Provenienza, qualità e degradazione

Servizi gratuiti, nessuna nuova dipendenza/servizio/installazione. EFFIS e DPC CC-BY4.0 con attribuzione; EOX è il precedente servizio facoltativo per ricerca non commerciale CC-BY-NC-SA4.0. Open-Meteo resta entro cache/quote precedenti per l'uso non commerciale. La nuova acquisizione non aggiunge chiamate Open-Meteo.

Acquisizione isolata in un subprocess del `geo_python` già configurato, timeout180s, singolo produttore, cache condivisa3ore, risposta HTTP di aggiornamento immediata; polling mentre il monitoraggio è visibile. Il worker limita ogni risposta e il totale a16MiB; archivio256MiB, oltre il quale nuovi download sono bloccati con errore visibile. Il primo snapshot completo ha scaricato **2.714.911byte**. I file originali, URL, ricevute HTTPS Date, SHA256 e prodotti trasformati sono conservati nella VM; manifest e livelli vengono verificati prima della lettura. Layer fire limitati al viewport con margine; prodotti degli altri giorni caricati su richiesta e cache browser rinnovata al cambio snapshot.

**11geometrie DPC su187** risultano non valide dopo la decodifica del TopoJSON ufficiale. Il dato negativo è mantenuto: la classe cartografica è UNKNOWN, il testo ufficiale e il livello originale rimangono consultabili; non vengono silenziosamente riparati o trasformati in zone verdi. I contorni sono semplificati a0,001° per consultazione, senza usarli per calcolo fisico/area/esposizione. Per il17ottobre rimangono2zone di attenzione visualizzabili; per il18ottobre20, mentre una ulteriore zona con attenzione è tra le geometrie non qualificate. Il servizio DPC è quindi PARTIAL.

Il TIFF WMS EFFIS non dichiara nodata: zero/nonfinito è trattato conservativamente come copertura non verificata e non come classe bassa. Le celle non mostrate non attestano sicurezza. Mancanza fonte, fallimento del livello, scadenza, clock discontinuo e dati incompatibili restano distinti dal valore basso. Le mappe scadute sono grigie/tratteggiate e datate. Capacità di consapevolezza territoriale sempre DEGRADED finché mancano sensori/esposizione e modello d'impatto; capacità d'impatto locale UNAVAILABLE. Ripristinare una fonte ripristina solo la rispettiva capacità. Non è una nuova dimostrazione sperimentale delle ipotesi JSS sul sistema completo.

Durante l'esplorazione l'orologio guest era indietro; successivamente è tornato coerente senza modifiche privilegiate eseguite da Codex. L'acquisizione finale registra differenza circa1s rispetto alla Date HTTPS. Il cache store conserva questo riferimento, segnala skew e sospende la freschezza su arretramenti dell'orologio; non inventa l'ora di emissione EFFIS.

## Verifiche effettive

- PASS7test unitari nella VM: soglie, unknown, decodifica archi inversi, cache alterata/path, assenza, scadenza/clock rollback, throttling e perdita DPC con EFFIS conservato.
- PASS17regressioni web nella VM.
- PASS26controlli browser: fonti e giorni, livelli/filtri, click ed esame accessibile, evidenze abbinate, meteo mancante dichiarato, responsive375/768/1440,3axe senza violazioni, navigazione Simulazioni conservata, inquadratura nazionale, perdita/scadenza/ripristino e errore di consegna del livello. Fault injection nel solo browser, nessuna modifica ai dati reali del server.
- PASS17verifiche sui file reali: hash, corrispondenza cella/valori/classi ai TIFF, conservazione testi/Comuni/classi DPC e astensione sulle geometrie non valide.
- PASS acquisizione a cache vuota via AttentionStore e subprocess reale nella VM: **8,45s in una sola prova**, non p95; sorgenti DPC PARTIAL ed EFFIS AVAILABLE attese.
- PASS riavvio locale controllato a job inattivi, nessun job interrotto, hash dei JSON preesistenti verificati prima/dopo. Nessun motore CIMA sostituito.
- FAIL iniziali: layerECMWF indicato da un esempio ufficiale non esposto dal servizio corrente; avvio worker senza PYTHONPATH e successivo shadowing di http.py con avvio diretto; rifiuto iniziale dell'intera fonte DPC per le geometrie non valide; controlli UI iniziali nascosti in Configurazione e harness che precedeva il caricamento; Node16 inadatto al test e iniezione axe bloccata da CSP. Correzioni verificate e prove negative mantenute. CSP di produzione conservata: bypass solo nel contesto automatizzato per axe.
- NOT RUN: radar/idrometri/pluviometri/hotspot live, soil/fuel/vulnerabilità qualificati, forecast d'impatto locale, replay storico con skill/falsi positivi/lead-time, test internazionali, p95/soak/device reali. Soglie operative e gate scientifici M5–M7 BLOCKED.

Raw locale `experiments/runs/monitor-real-20261017/`; dati originali e manifest nella VM `~/hazardia-runtime/web-state/attention/snapshot-*/`. Riepilogo pubblicabile `reports/monitoring/real-sources-verification.json`. Esiti positivi circoscritti all'integrazione software e alla fedeltà ai prodotti sorgente, non all'accuratezza predittiva locale.

## Riproduzione

Con app e runtime installati secondo docs/INSTALLAZIONE.md, avvia il servizio VM e apri Monitoraggio; il controllo acquisisce e poi aggiorna la cache condivisa quando necessario. Profilo concreto in `profiles/monitoring/italy.json`, nessun token richiesto. La prima connessione richiede rete; assenza rete non produce un all-clear.

```sh
# Nella VM, dalla root del repository con runtime già attivo
curl -H 'X-Hazardia-Research: 1' -H 'Content-Type: application/json' \
  -d '{}' http://127.0.0.1:8080/api/monitoring/refresh
curl http://127.0.0.1:8080/api/monitoring
../core-env/bin/python -m unittest tests.unit.test_attention -v
../core-env/bin/python -m unittest discover -s tests/web -v
```

L'endpoint di aggiornamento rispetta3ore di cache e non forza download ripetuti. Il test browser `tests/browser/attention.cjs` richiede Playwright/Chrome/axe come gli altri harness e non avvia simulazioni. Un profilo geografico separato non dimostra da solo l'integrazione delle fonti locali in Senegal o altrove.

Fonti consultate17ottobre2026: [DPC repository/licenza](https://github.com/pcm-dpc/DPC-Bollettini-Criticita-Idrogeologica-Idraulica), [EFFIS accesso](https://forest-fire.emergency.copernicus.eu/downloads-instructions), [EFFIS classi](https://forest-fire.emergency.copernicus.eu/about-effis/technical-background/fire-danger-forecast), [EFFIS licenza](https://forest-fire.emergency.copernicus.eu/about-effis/data-license).
