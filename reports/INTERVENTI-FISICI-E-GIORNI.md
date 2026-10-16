# Interventi fisici e simulazioni di più giorni

**16 ottobre 2026 — primo incremento verificato sull’incendio.**

Il confronto iniziale non cambiava le aree perché mostrava evacuazione: modificava l’esposizione, non il fuoco o l’acqua. La nuova pagina **http://127.0.0.1:8080/physical-fire.html** mostra invece due simulazioni effettive PROPAGATOR e i rispettivi raster orari. È accessibile anche dal nuovo link nella dashboard.

Per provare: lascia la **fascia tagliafuoco ipotetica** nel pannello B, scegli1/2/3giorni e muovi **Ora simulata**. Premi **Vicino all’intervento** per esaminarne il dettaglio o **Inquadra estensioni** per confrontare l’intero incendio. Selezionando **Nessun intervento** in B ottieni il controllo identico ad A. Il pulsante **Riproduci** avanza tra i risultati orari salvati; non crea una previsione mentre guardi la pagina.

La fascia è una modifica ideale del combustibile impostata nel modello a+15minuti, non una squadra realmente capace di realizzarla in quel tempo. Il terreno è reale, ma combustibile/umidità sono sintetici, con due sole realizzazioni. Non sono ancora un confronto automatico tra mezzi, lanci aerei e squadre del decision engine, né una previsione di un incendio storico validata.

Per le alluvioni non è stato creato un falso confronto fisico: la catena corrente restituisce il massimo allagamento. HMC ha componenti per invasi e laminazione che richiedono nuova integrazione e dati; argini/pompe locali richiedono una valutazione idraulica specifica. Le alternative concrete sono in [ADR-0009](ADR-0009-physical-interventions-and-days.md); è stato richiesto quale intervento sviluppare per primo. Nessun nuovo simulatore è stato installato o sostituito.

## Verifiche tecniche effettive

Run `physical-days-20261016T040414Z`, commit UI iniziale8492f36 e successivob739bfd; tutti i comandi SSH e stdout/stderr nei log JSON del run. Preparazione/integrazione/rendering nella VMUbuntu22.04aarch64,4vCPU/8GiBRAM/disco19GiB; Pythonfire3.12/Numba0.62.1 e geospaziale3.10/rasterio1.2.10. Browser client Chrome155 sul Mac, nessun modello sul Mac. Nessuna installazione privilegiata, nuovo dataset grande, pubblicazione, costo o push.

| Attività | Esito | Evidenza / interpretazione |
|---|---|---|
| Meteo4giorni | PASS |96record orari ERA5 UTC13–16luglio2024, acquisizione nellaVM; acquire-4days.json, raw/receipt/hash conservati |
| Dominio iniziale64² | FAIL |baseline PropagatorOutOfBoundsError dopo5h; non estesa artificialmente a72h |
| Preparazione iniziale dominio esteso | FAIL |PYTHONPATH mancante, ModuleNotFoundError; nessun risultato riutilizzato come successo |
| Preparazione corretta1024²/30m | PASS |DSM completo dal tile1grado già disponibile, quota551,629–2838,689m; expanded-prepare-repair.json |
| Esecuzioni native72ore | PASS | baseline25,284s, fascia23,671s e controllo no-op24,219s; singole misure, nonp95. Tutti259200s e72frame. Non performance operativa o studio di scalabilità |
| Invarianza no-op vs assenza evento | FAIL |114172celle diverse; scheduler-control.json; sensibilità osservata, causa generale non stabilita |
| Abbinamento calendario controllo/trattamento | PASS |A usa no-op900s, B usa vegetation_changes900s, stesso seed/meteo/terreno/innesco; distinti raster realmente prodotti |
| Frame pubblicati | PASS |144PNG da144matrici native, tutti shape1024²/probabilità finite0–1 e bordo non bruciato; aree ricalcolate in float64 e confrontate alle statistiche con tolleranza numerica; publication.json |
| Assenza azione nel pannello B | PASS |selezione B=baseline carica stessi file nativi e produce differenza0; non si finge un nuovo run indipendente |
| Interfaccia | PASS |prima suite17controlli: orizzonti24/48/72, playback, cambio30frame,DOM2raster, responsive375/768/1440,nessunPOSTmodelli,nessunerroreJS; axe0violazioni con incompleti contrasto conservati |
| Fisica alluvionale con mitigazione e72ore | NOT RUN |decisione sul caso/intervento e nuova integrazione necessarie, non presentate come pronte |
| Calibrazione/efficacia reale/ensemble esteso/30minstabilità | NOT RUN |nessuna conclusione scientifica H1–H3; fullgates precedenti restanoBLOCKED |

Manifest del confronto: `/home/hazardia/hazardia-runtime/web-assets/physical-days-20261016T040414Z/comparison.json`, SHA-256 `69ddda1244015b7470ca6ed823ccf1aa7011157733c3a4e202bff0600b6fb684`. Conserva URL e hash dei PNG e delle matrici native, statistiche e configurazione. La probabilità è la media su due realizzazioni; l’area media è la somma delle probabilità×900m², non l’area del solo contorno dei pixel positivi. Non si misura il beneficio reale della fascia.

I vecchi contratti/job adapter e il confronto di evacuazione non vengono dichiarati aggiornati a72ore: questo è un laboratorio fisico separato che rende verificabile la nuova capacità prima dell’integrazione generale. I test e i limiti precedenti non sono sovrascritti. Ulteriori controlli UI/integrità/trasporto sono aggiunti sotto soltanto dopo l’esecuzione.

Verifica finale UI `browser-v2/results.json`: PASS18controlli,30cambi frame p95end-to-end100,281ms (automazione+rete+decode, non la sola misura inputack),30pan RAF≈60,002FPS; screenshot reports/dashboard-evidence/physical-days-20261016/confronto-72h.png. Zero violazioni axe ai3formati, contrasto ancora incompleto/manuale. I frame vengono conservati due alla volta nel DOM; le etichette geografiche hanno limite e anticollisione. Loading delle ortofoto è separato da loading/validità dei raster fisici.

Final integrity PASS:145enginehashes,144nativeframes and144PNG individually rehashed; manifestSHA69ddda1244015b7470ca6ed823ccf1aa7011157733c3a4e202bff0600b6fb684; final-integrity-budget.json. Conservative cumulative traffic3,087,176,564B/5,368,709,120B; freeguestdisk12,627,730,432B;4CPU/8GiB/19GiB unchanged. Evidence archive transport PASS257files, SHA524451d63e000953c69779040454b62ff7979d325a48f93d08df5b705a34f708, transport-verification.json. Mac only copy/hash inspection and browser display. New native experiments do not establish H1–H3 or physical field accuracy.
