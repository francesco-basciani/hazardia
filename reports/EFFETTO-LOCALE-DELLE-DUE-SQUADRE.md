# Effetto locale delle due squadre — 19 ottobre 2026

**Esito:** le due azioni sono consumate dal motore e preservano le proprie maschere ideali, ma il piano contiene poco l’incendio complessivo. Il risultato precedente−1,094% di superficie media e indice prudenziale8→8 rimane valido. Non equivale a un piano antincendio realistico efficace.

La nuova diagnosi è esplorativa e successiva alla segnalazione utente; non costituisce un esperimento principale preregistrato né una nuova prova causale/calibrazione. Run `intervention-local-effect-20261019`, base638d10e50830c821769e01b136f735ba39afd71c+dirty. Nessun nuovo run fisico. Riferimento `job-c7999234d3e74a63845d3439a0eba08c`, piano `job-4bcbd12dc46d4fa4b6d0ffa18142551c`; confronto congelato `ideal-native-ee81c4a50a2847288db97f06f9904d32`.

## Misura nelle maschere esatte

La verifica usa **build_mask del sorgente PROPAGATOR fissato**, all_touched=True, stessa griglia/trasformazione del worker. Ogni area300×300m copre100celle30m,9ha. Sono maschere ideali di combustibile rimosso istantaneamente dal minuto60, non produttività qualificata di una squadra reale. Le due categorie sono dichiarate squadre a terra, ma questo piano usa fuel_removal anziché un modello logistico/operativo calibrato.

| Unità | Celle con probabilità>0 inA, su100 | Celle con probabilità>0 inB | Primo contatto nativo inA |
|---|---:|---:|---|
| unit-07566430 |96|0|26h31min14s|
| unit-027eb4bc |91|0|25h08min08s|

Sono celle raggiunte in almeno una delle8realizzazioni del pilot, non osservazioni né persone salvate. Probabilità media sulle maschereA0,4375 e0,43125, B0per entrambe. Area media raggiunta nelle due maschereA3,9375 e3,88125ha, B0. I log già verificati registrano200celle modificate dal minuto60. I dati di arrivo sono letti soltanto dove il corrispondente stato fire è positivo, evitando gli zeri delle celle non raggiunte.

L’incendio può aggirare due piccole aree e continuare sul combustibile circostante. L’ottimizzatore attuale assegna un’area locale presso ciascun obiettivo esposto con un proxy additivo di copertura: **non cerca ancora la combinazione di interventi che minimizza realmente la propagazione tramite feedback fisico** e non riposiziona squadre dinamicamente. Il proxy0non è stato confermato dal criterio prudenziale nativo8; questo rimane un risultato negativo. Non si aumenta l’efficacia artificiosamente per ottenere una differenza più vistosa.

## Vista disponibile

Aggiunto **Dettaglio interventi**, accanto al dettaglio degli inneschi e alla panoramica. Inquadra le geometrie dichiarate negli scenari visibili e sincronizza centro/zoom delle mappe. Un riferimento senza risorse mantiene zero interventi; non gli vengono aggiunte squadre o maschere di combustibile. Il comando non ricalcola alcun modello.

Confronto lasciato a48h, centro42,40765/13,73851, zoom15 alla verifica; i due quadrati inB restano senza raster arancione mentre la stessa zona inAè raggiunta. Area complessiva48h962,30→940,03ha. Il dato locale non deve nascondere il risultato finale limitato o l’incompletezza degli inventari.

## Verifiche e limiti

| Attività | Esito | Evidenza |
|---|---|---|
| Lettura output nativi con checksum, rasterizzatore upstream e145pin | PASS | `reports/intervention-local-effect/verification.json` |
| Riduzione locale nelle maschere ideali | PASS descrittivo |96/91celle→0; nessuna efficacia reale dedotta |
| Miglioramento del criterio prudenziale complessivo | FAIL, confermato dal pilot precedente |8→8; nessun nuovo risultato alterato |
| Dettaglio condiviso e due unità | PASS |2mappe stesso centro/zoom15, tempo48h,2simboli; `ui-verification.json` |
| Layout comando1440/768/375 | PASS |3record,nessun overflow,comando visibile |
| Input/scenari/job invariati | PASS |`integrity.json`; sola selezione/inquadratura client |
| Ricerca di nuovi piani, calibrazione, nuovi run/ensemble,axe/FPS/p95 | NOT RUN |nessun nuovo miglioramento scientifico rivendicato |
| Efficacia/logistica/inventari completi e fullM5–M7 | BLOCKED |qualifiche precedenti invariate |

Negativi di diagnosi: primo import di propagator senza PYTHONPATHfallito, poi usato il percorso fissato `/home/hazardia/m0/fire-src`; alcuni tentativi di scroll dopo cambio viewport non mostravano la zona prevista, poi statoDOM/centro condiviso e vista effettiva verificati. Nessuna installazione, costo, privilegi, restart o modifica motori. Screenshot `experiments/runs/intervention-local-effect-20261019/local-effect-48h.png`.

Da VM, directoryapp, ripetizione di sola lettura:

```sh
PYTHONPATH=src:/home/hazardia/m0/fire-src /home/hazardia/m0/fire-env/bin/python tests/native/intervention_local_effect_audit.py --runtime /home/hazardia/hazardia-runtime --comparison ideal-native-ee81c4a50a2847288db97f06f9904d32 --out /tmp/intervention-local-effect.json
```

Reviewer Codex self-check, consegnaGit/PUBLICATION.json. Prossimo incremento scientifico: ricerca di candidati e selezione con feedback fisico sugli obiettivi dichiarati, quantificazione della varianza e qualificazione di efficacia/tempi/logistica; nessun ottimo globale o comportamento di vere squadre rivendicato da questo aggiornamento.
