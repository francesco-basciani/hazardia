# Visibilità della propagazione nelle prime ore — 19 ottobre 2026

**PASS correzione UI; nessuna modifica della fisica.** Segnalazione utente: il tempo avanza, ma l’area sembra ferma intorno a+3h. Il controllo precedente del solo orizzonte72h non verificava adeguatamente questa visibilità iniziale.

Nel caso aperto `optimized-physical-fonte-vetica-20261019`, i due run nativi e i PNG crescono realmente:3,99375ha a3h;4,71375ha a3h15;23,05125ha a6h;103,48875ha a12h. Prima di24h45 i due scenari hanno la stessa propagazione, come verificato nell’esperimento precedente: gli interventi sono attivi da1h ma proteggono zone raggiunte più tardi. Non si modifica il simulatore per creare una differenza precoce.

## Diagnosi osservata

Alla scala effettivamente aperta (zoom12), il PNG3h ha bounding box alfa17×19pixel su1024², pari a circa18,33×20,56pixel dello schermo osservato. Il simbolo dell’innesco è30×30pixel ed era centrato sullo stesso punto: nascondeva il piccolo fronte. A6h il riquadro dei pixel non trasparenti diventa circa40,97×48,69pixel dello schermo e a12h81,94×82,23. Sono estensioni visuali del supporto probabilistico, non nuovi perimetri osservati o misure di area.

La riproduzione iniziale ha superato3h ed è arrivata oltre19h; la lettura DOM mostrava frame078/079, non un’immagine bloccata a3h. La verifica puntuale successiva ha confermato frame012/024/048 a3/6/12h su entrambe le mappe. La segnalazione individua quindi un problema concreto di scala/occlusione nel caso esaminato; non prova l’assenza di altri difetti su casi diversi.

## Modifiche

- Icona dell’innesco mantenuta visibile, sollevata rispetto al punto geografico tramite anchor15/47 anziché15/15, con stelo e piccolo richiamo sul punto. Coordinate e input invariati; collisioni dei simboli aggiornate per lo spostamento visuale.
- **Dettaglio inneschi** inquadra i punti delle mappe confrontate, fino a zoom15. La scala resta fissa durante la riproduzione, senza inseguimento automatico che possa mascherare la crescita. **Inquadra scenari** restituisce la panoramica dell’intero risultato. Non cambia terreno, risoluzione del modello o risultati fisici.
- Ogni mappa mostra superficie media del campione nativo e incremento rispetto al precedente, con intervallo in minuti. A3h:3,99ha e+0,64ha/15min; a6h:23,05ha e+2,16ha/15min. I numeri non sono interpolati fra campioni. La dissolvenza resta soltanto visuale.

La sessione è lasciata a6h e zoom15 per permettere di vedere il fronte. Le previsioni, le categorie delle risorse e l’ottimizzatore non sono stati ricalcolati o alterati.

## Verifiche

| Attività | Esito | Evidenza |
|---|---|---|
| Crescita array e PNG dopo3h, area indipendente e checksum | PASS |21assertVM su2job×4tempi,145pin; `reports/early-fire-playback/verification.json` |
| Diagnosi occlusione alla scala osservata | PASS |DOM raster1104×1108, PNG1024² e bbox alfa3/6/12h; `png-extents.json` |
| Superficie/tempo reali nell’interfaccia e immagini corrette | PASS |3/6/12h, frame012/024/048 completi, entrambi i simboli anchor−47px, zoom15 fisso; `ui-verification.json` |
| Formattazione senza interpolazione e regressioni orizzonte/verdetti | PASS |20assertJS, inclusi tempi frazionali, dati mancanti e crescita nulla |
| Layout confronto e piano | PASS |6record1440/768/375,2mappe/1mappa, pulsante visibile e nessun overflow |
| Integrità | PASS |caso identico prima/dopo,90job invariati,145pin invariati; `integrity.json` |
| Nuovi run fisici, efficacia/benchmarkp95/FPS/axe/drag-regression/heldout | NOT RUN |nessun nuovo risultato fisico rivendicato |
| Calibrazione, efficacia/logistica/fullM5–M7 | BLOCKED |gate precedenti invariati |

Negativi conservati nel registro della sessione: il primo formatter usava `findLastIndex`, assente nel Node locale; sostituito con scansione compatibile,20assert passati. Un controllo UI dopo cambio viewport ha selezionato Monitoraggio e fallito il selettore del confronto; sezione effettiva ispezionata e ritorno verificato alle due mappe. Nessun input sovrascritto. Nessuna installazione/restart/backend mutation dei modelli/costo/servizio pubblico.

## Ripetibilità

Run `early-fire-playback-20261019`, sorgenti di partenza `d63f90a2f434ca0617b10292fe9bd6c0eb8cf855`, modifiche UI/audit successive. Preregistrazione e snapshot prima della modifica nella VM `runs/early-fire-playback-20261019/before.json`, copia privata `experiments/runs/early-fire-playback-20261019`. Reviewer: Codex self-check; SHA di consegna in Git/PUBLICATION.json. Screenshot prima/dopo e letture client nei file del run e nel riepilogo UI.

```sh
# VM: lettura dei risultati esistenti, nessuna nuova simulazione
PYTHONPATH=src /home/hazardia/m0/reflex-env/bin/python tests/native/early_fire_display_audit.py --runtime /home/hazardia/hazardia-runtime --case optimized-physical-fonte-vetica-20261019 --out /tmp/early-fire-audit.json
# Verifica JavaScript da checkout sorgenti
node tests/browser/fire-comparison-status.mjs
```

I limiti del confronto fisico precedente restano validi: riduzione media−1,094%, criterio prudenziale8→8, efficacia ideale non qualificata. Il miglioramento di visibilità non costituisce miglioramento del piano decisionale. Prossimo incremento scientifico invariato: varianza e feedback fisico sul disallineamento proxy–risultati, qualificazione inventari/input/interventi/logistica secondo il piano originale.
