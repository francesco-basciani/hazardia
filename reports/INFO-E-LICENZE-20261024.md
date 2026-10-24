# Info e licenze —24ottobre2026

Run `map-credits-20261024`, base `cb57cc4`. Servizio nella VM esistente.

La barra estesa del Monitoraggio si collassa al primo movimento/click/zoom o dopo5secondi, secondo le modalità ammesse dalle linee guida OSM. Rimane un pulsante accessibile Info e licenze che apre Info e guida. I crediti Leaflet dei livelli caricati vengono sincronizzati nella pagina mediante MutationObserver; add/remove dei livelli conservano la provenienza. Non rimuove o modifica le attribuzioni delle altre mappe.

Fonti: [OSMF](https://osmfoundation.org/wiki/Attribution_Guidelines), [EOX](https://cloudless.eox.at/documentation/faq). Per immagini/esportazioni statiche servono attribuzioni visibili pertinenti: questo intervento non introduce un exporter.

PASS browser: barra non visibile dopo5s; apertura pagina mediante pulsante; crediti OSM, WorldCover, EFFIS, DPC, GeoNames, Open-Meteo, INGV/USGS e Istat presenti con link. Nessuna nuova acquisizione scientifica richiesta. Screenshot in `reports/map-credits/`.

NOT RUN: verifica Safari dedicata ed export statici. Nessuna conclusione sulle prestazioni dei simulatori.
