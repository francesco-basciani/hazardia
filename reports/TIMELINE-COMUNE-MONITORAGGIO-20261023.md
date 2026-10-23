# Timeline comune del Monitoraggio —23ottobre2026

Run `monitor-timeline-20261023`, base28d1eca+dirty, reviewerCodexself-check.

PASS: barra «Previsioni e criticità», unico Riproduci/Pausa, tempo comune per meteo, indici incendio/secchezzaEFFIS, bollettiniDPC e accumuli sulle zone. Selezione manuale meteo/giorno territoriale e seek comandano lo stesso tempo. I prodotti giornalieri restano giornalieri; nessuna interpolazione di classi d’allerta. Pioggia per zona usa l’ora iniziale richiesta e mantiene il proprio calcolo asincrono nella VM.

La barra non dipende più dal checkboxMeteo. L’orizzonte è l’unione delle finestre effettivamente registrate dalle fonti previsionali, non una durata simulata inventata; testati anche orizzonti diversi e intervalli mancanti. Il registro filtra finestre invalide o più lunghe di14giorni e conserva il tempo al refresh. «Copertura» distingue la validità temporale di ogni prodotto; non certifica freschezza, copertura spaziale o qualità, indicate nei rispettivi livelli.

Radar e sensori seguono la consultazione temporale soltanto dove possiedono osservazioni; nessuna proiezione futura. Terremoti, immagini e infrastrutture conservano le proprie date, non diventano previsioni. Lo studio dei simulatori rimane nella sezioneSimulazioni con il proprio orologio già condiviso tra incendio/meteo. La barraMonitoraggio non avvia simulatori/ottimizzatori né genera previsioni nuove.

PASS:15suiteclientNode sulMac, inclusi registro temporale e veri handler playback con DOMfixture: smooth/pause/resume/seek, orizzonti distinti, vuoti e gap. Comando: `node tests/browser/monitor-timeline.mjs`, `node tests/browser/monitor-playback.mjs`; le altre13suite.mjs passano. Due script browser esistenti aggiornati per i nuovi nomi accessibili, ma non rieseguiti integralmente. Raw `experiments/runs/monitor-timeline-20261023/`.

PASS browserintegrato1280×720: riproduzione conMeteoOFF, orologio e livelloDPC/EFFIS entrambi24ottobre; alla pausa13:22:41.203UTC i dataset di clock e mappa coincidono. Selezione manuale24ottobre16:00Roma → entrambi14:00UTC e prodotti24ottobre. A fine orizzonte meteo valido maEFFIS/DPC non disponibili, esplicitato anziché riusare le zone del giorno precedente. Nessun erroreconsole, nessuno scroll del documento. p95lavoroUI3,2ms su120frame correlati conMeteoOFF: misura circoscritta, non benchmark completo.

PASS preservazione nel guest:311file e95job invariati. Servizio e acquisizioni nella VM esistente, nessuna nuova dipendenza o risorsa. M5–M7 e blocchi fonti/vento fine invariati. NOT RUN nuovi test fisici, Safari e caricoend-to-end. Estratto `reports/monitor-timeline/verification.json`; screenshot locale `reports/monitor-timeline/delivery.png`.
