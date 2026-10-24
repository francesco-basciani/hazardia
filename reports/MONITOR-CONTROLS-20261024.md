# Monitoraggio — toolbar, configurazione e terremoti (24 ottobre 2026)

Run `monitor-controls-20261024`, baseline `c4992c2`, reviewer Codex self-check.

PASS: orario selezionato compatto accanto alla ricerca (`24 ott, 20:00`), badge Previsione quando futuro; istante UTC canonico, secondi e offset restano nel dettaglio title/datetime. L'orologio attuale non occupa una terza riga. Ricerca/orario condividono una toolbar; header ridisposto per contenere lingua/configurazione senza invadere zoom/centra. Sfondo e nomi delle località spostati nel pannello Configurazione, rimossi dai livelli; controlli originali riutilizzati, niente doppio stato. Parametri dei livelli sempre a destra.

Terremoti: il precedente clic sul nome apriva solo parametri; la casella separata era necessaria per attivare il livello. Ora il nome attiva e apre i parametri con un clic; resta possibile spegnere dalla casella. Badge di acquisizione visibile durante il caricamento; zero eventi, errore e copertura parziale rimangono distinti. Nessuna modifica al catalogo, ai filtri di magnitudo, alle quote o alle finestre osservate. Il periodo sismico non è una previsione e non segue artificialmente il cursore futuro.

PASS reale: INGV, ultimi 7 giorni, M≥0, bounds [10.67322,40.00658,16.22681,43.85037], acquisizione 24/10/2026 20:20:29 Roma, finestra 17/10 18:20Z→24/10 18:20Z: 214 feature e 214 simboli disegnati. Osservazione iniziale 218 eventi su bounds diversi; non è lo stesso campione. Screenshot mostra cerchi per magnitudo. Allargando la vista compare correttamente copertura parziale; non dichiarata copertura mondiale completa dei piccoli eventi. Nessun evento osservato equivale a previsione sismica o certificazione di danno.

PASS: 47 test web VM (`PYTHONPATH=src ../core-env/bin/python -B -m unittest discover -s tests/web`), incluse 10 prove backend del catalogo. Suite client `node tests/browser/monitor-clock.mjs`, `node tests/browser/i18n.mjs`, `node tests/web/observed-layer-model.test.mjs`; cambio DST con due ore locali uguali conserva offset distinti, formato breve separato dai dati canonici.

PASS manuale IAB: 1440×900,1011×1034,390×844, toolbar e header senza sovrapposizione; mobile senza overflow orizzontale; +1h aggiorna l'orario in alto e il badge Previsione; IT/EN. Un primo clic automatizzato subito dopo reload ha raggiunto Istruzione durante il layout: prova ripetuta tramite albero accessibile dopo stabilizzazione, attivazione sismica e simboli verificati. Nessun successo dedotto da quel primo tentativo. Override viewport ripristinato e lingua italiana ripristinata.

NOT RUN: verifica nativa diretta Safari, nuovo benchmark FPS/carico, replay fisici. Motori, forcing, ottimizzatore, verifier e contratti non modificati; non sono necessari nuovi esperimenti fisici per questo incremento UI. Gate scientifici e FAIL storico di replay REFlEx invariati. Non è un audit di tutte le fonti.

Evidenze: `reports/monitor-controls/{browser,verification}.json`, screenshot desktop/tablet/mobile/delivery nella directory locale; log `experiments/runs/monitor-controls-20261024/`. Tutta acquisizione/API in VM esistente, nessuna installazione o costo. Gli screenshot restano locali secondo l'esportazione curata delle immagini.
