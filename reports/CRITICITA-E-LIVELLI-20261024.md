# Criticità e livelli —24ottobre2026

Run `critical-layers-20261024`, base `c22487f`, servizio nella VM.

Le campiture giallo/arancio precedenti provenivano principalmente dalla sintesi FWI/DC EFFIS sulle zone meteo-idro. Potevano sovrapporsi a DPC, mentre la legenda restava sotto una mappa a schermo intero. La correzione rende la legenda un controllo Leaflet visibile, con classi della sorgente attivata, validità e missing/stale. Nessuna riclassificazione scientifica.

Controlli: Sfondo sopra la lista livelli; Pericoli · simulazioni contiene i risultati FIRE/FLOOD; meteo nel proprio pannello. Criticità territoriali è un livello separato con master, DPC edEFFIS indipendenti. Default DPC soltanto. EFFIS bassa non mostrata salvo opzione esistente; non equivale a mancante. Le fonti stale/missing sono grigie tratteggiate se geometria presente; fuori copertura non si inventano poligoni. Se entrambe attive, messaggio di sovrapposizione invita alla lettura separata. Indici EFFIS non sono allerte ufficiali né incendi osservati. DPC non è un perimetro di allagamento.

PASS verifica manuale browser in-app con servizioVM: DPCiniziale; entrambi→data-attention=effis,dpc; soloEFFIS→effis; masterOFF→stringa vuota e legenda nascosta; masterON→effis. Spegnendo il risultato Incendi la criticitàEFFIS resta attiva. Legenda FWI completa di6classi, graymissing e validità24ottobre. DPC4classi separate. Fonte selezionabile e parametri a destra. Mobile375×812: document.scrollWidth375, nessun overflow orizzontale. Screenshot `reports/critical-layers/{effis,options,mobile,delivery}.png`. Sintassi moduli controllata con `node --input-type=module --check`.

Il click su zona apre il pannello corretto; pioggia zonale e criticità non si sopprimono più implicitamente. Non sono modificate acquisizioni, soglie, cache scientifiche o forzanti; nessun job fisico avviato per questa verifica. NOT RUN Safari dedicato, nuove prove native e qualificazione rischio/operatività. Reviewer Codex.
