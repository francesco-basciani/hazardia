# Caso ideale: priorità territoriali, mezzi e confronto fisico

Run ideal-priorities-20261017, base215a9cf973327627bf8b6a981027ceca437fd41b, reviewer Codex self-check. Contratto e motivazioni: ADR-0013. Tutti acquisizione/preparazione/HiGHS/PROPAGATOR/servizio nella medesima VM, nessun install/costo/risorsa aumentata. Mac solo modifica e browserQA.

## Caso disponibile

In Simulazioni e risorse aprire «Priorità territoriali e piano ideale», poi «Apri caso ideale verificato». Il caricamento è esplicito e solo su workspace vuoto: il normale avvio resta pulito. Due scenari72h, un innesco ipotetico comune, quattro mezzi ipotetici:2squadre a terra,1Canadair,1elicottero. Tutti pronti e a0min nel caso estremo; pesi visibili e modificabili: sanità5, istruzione3, residenziale2, località2, soccorso3. Non sono priorità operative né conteggi di persone. Le categorie hanno uguale copertura ideale: nessuna efficacia differenziale dedotta.

Mappa:19oggetti OSM classificati (2sanità,8istruzione,8residenziali,1località);8relazioni/geometrie non ricostruite restano escluse e segnalate. Punti della stessa categoria entro100m raggruppati per l'ottimizzazione, non confusi con confini reali. Poligoni reali residenziali e punti OSM sono consultabili con fonte; nessun riconoscimento da immagini implementato. Copertura del piccolo snapshot lon13.375–13.405/lat42.345–42.36: parte del fronte rimane fuori e unknown. Popolazione, occupazione e vulnerabilità non disponibili.

È riusato lo snapshot VM da12.207.956byte già acquisito inmap-detail-20261015T204352Z, con sorgente API ufficiale OSM e hash nel prodotto. Nessun nuovo grande download. Tentativi precedenti falliti, senza rimpiazzi fittizi: Overpass principale406, private.coffee500, APIbbox più ampio400 per oltre50.000nodi. Il dataset è parziale, non una copertura nazionale. Fonti/licenza: https://www.openstreetmap.org/copyright ; semantica poligoni https://wiki.openstreetmap.org/wiki/Tag:landuse%3Dresidential ; limiti https://wiki.openstreetmap.org/wiki/Overpass_API .

## Ottimizzazione e limiti del significato

HiGHS sceglie unità→obiettivo minimizzando punti di priorità residui; i punti sono peso×probabilità media/massima nella geometria sul prodotto di riferimento. Per punti cartografici si usa un'influenza ipotetica75m dichiarata. Media e massimo non sono membri di ensemble meteo; senza probabilità affidabili si usa il massimo del set, con blend esplicito configurabile. Ogni unità copre idealmente un obiettivo e ogni obiettivo al massimo una unità. Logistica, strade, turni e consumabili sono valori ipotetici confermati, mai inventario reale. La proposta nativa consiste in quadrati300m di rimozione ideale del combustibile attorno agli obiettivi, distinti dalle geometrie cartografiche.

Decisione principale decision-7a190c97c55240be9c8e76b1f0e751e4: VALIDATED_FOR_SIMULATION dal verificatore indipendente, optimal HiGHS entro la formulazione discreta; tempo osservato 2.157s, inclusa preparazione/coda. Indice proxy massimo 20.5→13.0 (non persone salvate, non beneficio fisico dimostrato). Con ground-1 indisponibile, decisione decision-be7a8b8b65154d56980644bfe328b9a1 esclude l'unità, seleziona tre mezzi e porta l'indice residuo a14.5. Questa è prova di riassegnazione, non validazione completa della graceful degradation o del rolling horizon.

## Prova fisica separata

Due nuove esecuzioni native72h×288frame, stesso terreno, forzante oraria congelata, umidità combustibile15% manuale, fuel5uniforme, seme1729 e2realizzazioni. Riferimento job-14a5f13dcb6f4680be96dc872ea28709; piano job-723e581ab6cf40de9810c8314e1c4249. Tutti288frame del riferimento hanno hash identico al precedente prodotto senza azioni. Il piano consuma4geometrie,484celle modificate a0min; area finale 347.13ha contro 0.09ha.

Il risultato estremo deriva dalla rimozione istantanea del combustibile vicino all'innesco, che blocca quasi subito il fronte. Non dimostra che quattro mezzi reali possano proteggere347ha, né l'ottimalità fisica della proposta. Il solver ottimizza un proxy e l'esperimento verifica soltanto che quel piano venga consumato dal simulatore. Nessuna calibrazione/skill o azione reale. Nuovi job sono replay congelati, non una previsione meteo corrente.

## Riproduzione nella VM

Preparare un prodotto fire baseline senza interventi e uno snapshot OSM con diritti/provenienza. Quindi, dalla directory app:

```sh
PYTHONPATH=src /home/hazardia/m0/reflex-env/bin/python scripts/build_priority_areas.py --raw /percorso/osm-map.json --out ../web-assets/priority-areas.json --bounds 13.375 42.345 13.405 42.36 --source 'https://api.openstreetmap.org/api/0.6/map.json?bbox=13.375,42.345,13.405,42.36'
```

Copiare examples/fire/ideal-fleet.json, sostituire job_id con il baseline completato e dichiarare flotta/pesi/arrivi. La disponibilità e le ipotesi del file devono essere controllate da chi prepara il caso; non è inventario regionale. Con servizio locale già attivo:

```sh
PYTHONPATH=src ../core-env/bin/python scripts/prepare_ideal_example.py --runtime /home/hazardia/hazardia-runtime --request /percorso/richiesta-ideale.json
```

Lo script usa la stessa API limitata, attende entrambi i job e pubblica soltanto l'asset locale opt-in; --replace è necessario per sostituire un caso pronto. Non modifica il workspace utente. Fonti/raw/VMdisk non vengono pubblicati suGitHub.

## Registro

PASS24test VM decisione, compresi nuovi policy/unità/qualifiche, indisponibilità, no doppio target, rifiuto effetti fisici non supportati, regressione0.5. PASS21browser: opt-in, inventoryvuoto, flotta esplicita, mappa/ranking/copertura, invalidazione dopo modifica, conferma delle ipotesi, ricalcolo con mezzo perso,375/768/1440,3axe senza violazioni, workspace reale preservato. PASS controllo nativo288hash ed eventi4/484. FAIL intermedi mantenuti: download406/500/400, primo retryHTTP al riavvio, action_timesB conteneva un evento del vecchio piano non presente nelle nuove risorse; richieste parziali annullate e clock corretto usando comparison_times comune. Il primo harness del watchdog aspettava soltanto100ms: sul filesystem VM il salvataggio atomico non era terminato prima della rimozione della directory temporanea. Corretto con attesa della prova persistita e pubblicazione dello stato timeout in memoria prima della scrittura, fuori dal lock HTTP. Preparazione iniziale senza raggruppamento di punti conservata come pilot distinto, non confusa con i risultati finali.

NOT RUN benchmark>=30p95 della nuova policy, carico/soak/crossbrowser/device fisici, validazione storica o nazionale/estero, rolling automatico integrato nello studio, stima popolazione e detection satellitare, efficacia realistica e ricerca dell'ottimo fisico. BLOCKED fullM5–M7, fuel reale/moisture estimator, logistica/calibrazione. Nessun risultato scientifico H1–H3 stabilito. Raw experiments/runs/ideal-priorities-20261017; stessa directory runs nella VM e decisioni inweb-state.
