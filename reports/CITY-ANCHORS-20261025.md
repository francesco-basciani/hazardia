# Correzione dei punti delle località — 25 ottobre 2026

Causa: i renderer Monitoraggio e Simulazioni centravano il contenitore del nome sulle coordinate. Il pallino `::before` precedeva il testo, quindi era a ovest dell’ancora, con distanza dipendente dalla lunghezza del nome. Il precedente audit di disponibilità non aveva verificato questa geometria visuale.

Correzione: ancora Leaflet a sinistra, pallino assoluto centrato su quella stessa ancora, testo a destra. Nessuno spostamento artificiale delle coordinate, cambiamento degli archivi o della fisica. Modificati monitoring.js, map-names.js e lo stile condiviso region-boundaries.css.

Coordinate già presenti nell’asset VM: L’Aquila42.3489203/13.3979672, OSM node70990193; Teramo42.66123/13.69901, GeoNames3165803. Verificata la posizione DOM contro la proiezione WebMercator del centro/zoom effettivo: 6 controlli a zoom8/9/10, errori0,30–1,02px entro tolleranza1,5px per arrotondamento Leaflet. I controlli a zoom10 misurano anche un marker DOM fuori vista: non si afferma che entrambe le città siano visibili in quell’inquadratura. Prova visiva finale a zoom9 con entrambe le città in vista. Dati di confronto in city-anchors/verification.json, screenshot locale city-anchors/delivery.png e run privato city-anchors-20261025.

`node tests/browser/weather-render-plan.mjs`:6023 controlli PASS. Nuovi test fisici/FPS/Safari non eseguiti per questa correzione cartografica. Revisione dello stesso autore, non indipendente. Gate scientifici e limiti dei dati invariati.
