# Revisione grafica responsive

Run `professional-ui-20261016T064202Z`. Sorgente `2bf6bd804e95dd36f2d188ff8e4946a7e165344f`, prima proposta `ef0d6bbc5fc8178ebd71ea76146592c41b59f9d2`. Reviewer Codex self-check.

L’interfaccia usa ora una navigazione blu scuro con icone SVG locali, superfici chiare, tipografia più leggibile, controlli e spaziature coerenti. Mappe e pannelli mantengono la gerarchia monitoraggio → livelli → decisioni. La pagina di confronto fisico usa lo stesso stile. Su tablet/telefono mappa e pannello passano a una colonna; navigazione touch, campi più grandi e pulsanti cartografici ridisposti. Nessun font remoto, libreria o servizio aggiuntivo.

## Prove eseguite

**PASS 136controlli**: monitoraggio44, meteo36, design56. **21scansioni axe,0violazioni**; risultati incompleti automatici conservati nei log. Quattro sezioni e pagina fisica senza overflow nelle8dimensioni elencate in [verification.json](design/verification.json), da320 a1920pixel, incluso orientamento orizzontale812×375. Verificati tastiera, focus visibile, reduced-motion, apertura controlli su cellulare, filtri meteo e due chiamate reali al solver/verificatore nella VM isolata. Nessun job fisico avviato. Feedback filtri: n=35, p95=17.5ms nel workload limitato del test.

Comandi dal Mac come solo client QA, backend/solver nella VM:

```sh
HAZARDIA_BASE_URL=http://127.0.0.1:8081 node tests/browser/monitoring.cjs OUTPUT-monitoring
HAZARDIA_BASE_URL=http://127.0.0.1:8081 node tests/browser/weather.cjs OUTPUT-weather
HAZARDIA_BASE_URL=http://127.0.0.1:8081 node tests/browser/design.cjs OUTPUT-design
```

Usare le variabili HAZARDIA_PLAYWRIGHT_PATH, HAZARDIA_BROWSER_EXECUTABLE e HAZARDIA_AXE_PATH descritte nella configurazione QA locale se i moduli/browser non sono sul percorso standard. Test contro il prefisso isolato `repro-check-20261016-v2`, stesso guest, cache/quota meteo originale condivisa. Piano prima di staging/test; harness aggiuntivo identificato perSHA nel riepilogo. Primo passaggio100controlli riuscito; dopo la rifinitura dei pulsanti mobili rieseguite le tre suite complete. Raw `experiments/runs/professional-ui-20261016T064202Z`.

## Rilascio locale e limiti

PASS aggiornamento di3file statici sulla dashboard8080; SHA256 verificati, 816JSON utente preesistenti conservati, nessun riavvio backend. Runtime sempre stessaVM4vCPU/8GiB/19GiB. NON è una prova su tutti i dispositivi/browser reali: Safari/Firefox/hardware touch e test utenti NOT RUN. Nuovo soak30min/stress100k/simulazioni fisiche NOT RUN; precedenti blocchi di ricerca restano. Non si deduce efficacia operativa, accuratezza scientifica o soddisfazione utenti dal nuovo aspetto.
