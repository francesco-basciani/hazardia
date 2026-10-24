# Cavi aerei e tralicci —24ottobre2026

Run `aerial-power-20261024`, base `6efaf5d`. Runtime nella VM esistente.

La voce del livello apre direttamente la vista ostacoli aerei: linee aeree di ogni tensione e sostegni, con esclusione delle sottostazioni e dei cavi interrati/posa sconosciuta. Le linee note mantengono il colore per tensione, le sconosciute il tratteggio; spessore4px nel preset. Tensione bassa inclusa per non omettere possibili ostacoli. I filtri tradizionali rimangono in un gruppo richiudibile: modificarli abbandona il preset esplicitamente. Inquadra cavi acquisiti rimane immediatamente accessibile.

PASS `node tests/web/observed-layer-model.test.mjs`: regressioni filtri tradizionali e magnitudo; preset include tensione bassa/sconosciuta e sostegni, esclude posa interrata/sconosciuta e sottostazioni. PASS verifica sintassi modulo.

PASS browser in-app su VM: attivazione al primo click, acquisizioneREADY,189elementi selezionati su192, inquadratura, avviso copertura parziale e filtri avanzati chiusi; nessun errore console. Fonte acquisizione OSMAPI24ottobre11:03:11, bounds[13.43795,41.87285,13.46208,41.89081],187oggetti con tensione non disponibile sul totale. Sono oggetti, non189linee o ostacoli certificati. Screenshot reports/aerial-power/delivery.png.

I dati esistenti possono inferire overhead dal tipo line/minor_line; la UI lo dichiara. Non attestano cavi nudi/non isolati, quota, freccia, corrente presente o disponibilità di corridoi. Assenza di oggetti non significa area libera. Nessuna integrazione automatica con solver, tempi di intervento o risultati fisici; nessun job fisico lanciato. NOT RUN: qualificazione ostacoli aeronautici, inventario gestore completo e verificaSafari dedicata.
