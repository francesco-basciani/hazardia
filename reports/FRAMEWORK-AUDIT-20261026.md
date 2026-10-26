# Audit funzionale del framework · 26 ottobre 2026

**Esito PARZIALE.** Corretti blocchi reali degli aggiornamenti e della rappresentazione futura. I livelli esistenti sono stati controllati per dati/attivazione/limiti; WII, rete elettrica e alcune integrazioni restano degradati o non disponibili. Non è una certificazione scientifica o operativa.

Run `framework-audit-20261026`; base privata `d845c9dc10760f3442976c3e7b71d7b15ead2a0f`, modifiche di questo incremento. Ambiente: VM Linux esistente6CPU/16GiB, acquisizione/elaborazione e test Python nella VM; browser IAB Chromium156 su Mac,857×1014,DPR2. Revisore: Codex, autoverifica tecnica. Le prove includono il runtime con WII/TCIP già presenti; il lavoro parallelo dei loro consumer è preservato e non incluso nel commit di questo audit. Nessuna nuova libreria, quota o risorsa hardware.

## Difetti riprodotti e corretti

1. **DPC/EFFIS bloccati da CACHE_FULL.** Archivio270.222.799byte con molte copie identiche. Condivisione di file immutabili identici mediante hardlink e conteggio degli inode unici: stesso contenuto e stessi nomi logici, nessuno snapshot eliminato. Dopo compattazione75.734.320byte, quota256MiB invariata.
2. **Vento regionale e previsione puntuale scaduti per archivio pieno.** Lettura trasparente e verificata del JSON compresso; compattazione senza perdita e nuovi refresh entro quote esistenti. Il vento passa da64.782.869 a9.957.468byte; il meteo puntuale da13.947.892 a1.817.041byte. Tutti gli hash dei contenuti decodificati prima/dopo coincidono. Recupero complessivo261,444,731byte. Ricevuta: [storage-recovery.json](framework-audit-20261026/storage-recovery.json).
3. **EFFIS del giorno successivo senza poligoni.** Il worker richiedeva un bollettino DPC dello stesso giorno anche per la sola geometria. Usa ora la partizione pubblicata più recente, precedente o coincidente, entro7giorni, mantenendone data/revisione. Non copia classificazioni né estende allerte DPC. Il27ottobre passa da0 a187zone,183classificabili. Rielaborazione locale con gli stessi dati scaricati e timestamp originali; snapshot precedenti conservati. [Ricevuta](framework-audit-20261026/effis-reprocessing.json).
4. **Stati poco comprensibili:** il pannello territoriale senza dati a zoom ampio indica ora il caricamento da zoom11; non è una nuova restrizione alla visibilità delle emergenze già caricate. Il pannello accumuli spento spiega come attivarlo. Date radar/Sentinel leggibili nella timezone di Roma.
5. **Guida e fonti obsolete:** la pagina dichiarava i sensori non integrati e rimandava a vecchi comandi di evacuazione. Testi riallineati a radar/pluviometri, piano incendio, confronto e player comune; collegamento al confronto integrato. Nuovi testi IT/EN.

6. **Ritorno al Monitoraggio prima del layout ripristinato.** Rilevato nel controllo visivo finale: la richiesta meteo poteva usare dimensioni non valide dopo la pagina informativa, con errore transitorio e mappa senza valori. Ripristino della dimensione prima di riattivare meteo/sfondi, camera conservata nel ridimensionamento, query sospesa su dimensioni nulle. Stato di caricamento/copertura ora visibile sulla mappa, rimosso quando i dati sono pronti; ora fuori orizzonte esplicitata. Dopo la correzione:30ritorni caldi,23etichette presenti in tutti, centro invariato,0avvisi d’errore, p95ritorno→valori144ms/max145ms (include driver/polling; non cold-cache o compositore). [Evidenza](framework-audit-20261026/view-switches.json). Le prove intermedie a0etichette prima del ridisegno sono conservate nell’evidenza privata, non conteggiate come PASS.

## Matrice dei livelli e controlli effettivi

Catalogo attuale:21voci, compresi catalogo e configurazione cartografica. Conteggi relativi all’area/orario della prova, non garanzia di completezza nazionale.

| Voce / gruppo | Esito verificato | Dati e limite |
|---|---|---|
| Meteo: vento, temperatura, umidità, precipitazioni, probabilità, nuvole, raffiche, pressione, radiazione | PASS tecnico | Open-Meteo/ICON;95recordorari. Campo campionato:7.695valori finiti per campo,0mancanti; copertura grafica della vista1. Vento regionale nuovamente FRESH. Pioggia molto bassa nella previsione provata: trasparenza sotto0,1mm intenzionale. |
| Variabili meteo combinate | PASS | Nuvole e pioggia attive insieme; raffiche/pressione/radiazione visibili. Quantità e probabilità restano misure alternative dello stesso overlay. |
| Timeline monitoraggio | PASS | Selezione27ottobre12:00, avanzamento continuo fino29ottobre23:00 e arresto a fine orizzonte. Orologio reale distinto dalla validità selezionata. Nessun radar futuro sostitutivo. |
| Criticità DPC | PASS acquisizione, PARZIALE geometria | Bollettino25ottobre con validità26ottobre,187testi/183geometrie qualificate. Al27nessun bollettino disponibile: nessuna allerta prolungata. |
| Indici EFFIS | PASS tecnico, PARZIALE |26e27ottobre:187zone/183classificabili; indici FWI/DC, non allerta ufficiale né probabilità d’incendio. |
| Accumuli pioggia | PASS, copertura parziale | A26ottobre13:00, prossime24h:61/62zone della vista complete. A fine previsione:0/62complete, esplicitamente incomplete, non0mm. Nessuna allerta alluvionale dedotta dai soli mm. |
| Radar osservato | PASS, copertura parziale | Radar-DPC26ottobre11:00Z,51%del mosaico valido. Futuro correttamente privo di osservazioni. |
| Pluviometri | PASS, parziale | ItaliaMeteo/MeteoHub: dati acquisiti dopo attivazione; nella vista ampia299/968sensori disegnati,294recenti. Diradamento e stazioni fuori vista distinti da guasto; reti CC BY4.0, dati provvisori. |
| Immagini recenti | PASS locale |2anteprime Sentinel23e21ottobre,entrambe scaricate; prima impronta attivata. Nuvole54,35%/99,46%. Vista≤1°per lato; anteprime, non raster analitici sovrapposti. |
| Terremoti | PASS | INGV197eventi acquisiti,171nella vista ampia con M≥0; filtro M≥3 restituisce0eventi in quella selezione, senza nuovo pulsante. Canvas presente e conteggi aggiornati. Classi/raggi testati; rilevabilità dei piccoli eventi non completa. |
| Centri abitati | PASS parziale |19località/aree nella vista urbana; OSM, non popolazione censita. |
| Sanità e assistenza | PASS parziale |13oggetti disponibili/disegnati; apertura/capacità non verificate. |
| Emergenze e soccorso | PASS parziale |47oggetti disponibili/disegnati, inclusi idranti/AED; non47squadre disponibili. |
| Istruzione | PASS parziale |12oggetti. |
| Strade e trasporti | PASS parziale |2.304oggetti attivati/disegnati. Percorribilità corrente non certificata. |
| Reti e impianti | PASS parziale |3oggetti della categoriaOSM generale. |
| Edifici | PASS parziale |1.712edifici attivati e visibili a zoom15; soglia e stato presenti. |
| Ambiente e acque | PASS parziale |493oggetti, non portate o livelli idrometrici. |
| Cavi aerei e tralicci | DEGRADATO |Providerlive in timeout; fallbackOSM verificato del17ottobre. Copertura limitata, tensioni/dateOSM spesso ignote; non inventario AT completo né sicurezza del volo. |
| Catalogo / confiniOSM / altri oggetti | PASS parziale |Catalogo interrogabile;7confiniOSM e4.562altri oggetti attivati/disegnati. Non confini amministrativi ufficiali. |
| Confini nazionali/regionali/provinciali | PASS |Tre interruttori indipendenti provati. NaturalEarth mondiale generalizzato, Istat2026 Italia per regioni/province; nessuna copertura provinciale mondiale dichiarata. |
| WII | DEGRADATO: aggiornamento BLOCKED |Il livello storico esistente e la legenda si caricano, ma il ricalcolo automatico restituisce WII_STORAGE_FULL. Database indipendente circa213MB,quota256MiB; non modificato per aggirare il limite. Nessuna previsione giornaliera o origine certa qualificata. |
| TCIP | PASS nei dataset pubblicati |Catalogo5rilasci; caricamento Benevento e cambio categoria a Firenze verificati. Comuni/quartieri parziali, periodi/categorie distinti. Nessun reato futuro o rischio personale dedotto. |

Evidenze UI grezze private: `experiments/runs/framework-audit-20261026/ui-layer-checks.json`; screenshot in `reports/framework-audit-20261026/`.

## Simulazioni, risorse e graceful degradation

- Incendio salvato: avvio→+21h29, pausa stabile, ripresa→+27h, ritorno a0. Squadre visibili nella vista del piano. Nessun nuovo scenario o risorsa aggiunta durante l’audit. I4confronti nativi del precedente incremento26ottobre restano tracciati in [FIRE-INTERVENTIONS-20261026.md](FIRE-INTERVENTIONS-20261026.md): nessun intervento1,53ha, Canadair intercettante0,18ha, controllo lontano1,53ha; input storici congelati, non efficacia operativa.
- Ottimizzatore reale su baseline nativa salvata:12controlli PASS, decisione verificata in1.039s,2risorse assegnate; processo solver mancante→fallback verificato in0.132s. Dati di sicurezza ignoti→nessuna assegnazione. Questa fixture ha1.200geometrie di abitato ma mancano8categorie di priorità: non prova protezione completa delle infrastrutture. [Verifica](framework-audit-20261026/optimizer-verification.json).
- Traffico: configurazione salvata caricata senza sovrascriverla;38veicoli su1.221segmenti realiOSM, animazione e pausa a72s.44vie senza senso dichiarato,14escluse per restrizioni,2per accesso. Test del modello30prove/400veicoli/12.000segmenti PASS; riproducibilità, sensi e chiusure implementati nella suite. Nessuna congestione/evacuazione o influenza sui tempi d’intervento.
- Alluvioni: prodotti storici e contratti coperti dai test; nessun nuovo replayHMC/REFlEx o confronto fisico con interventi in questo incremento. Gate e fallimento storicoREFlEx invariati. La consultazione dei risultati non costituisce previsione corrente validata.

## Prestazioni e regressioni

| Prova | Risultato | Qualifica |
|---|---|---|
|13API in cache×30letture |390GET validi,0errori,p95massimo96.47ms |PASS soglia500ms su workload caldo; non acquisizione esterna |
|30cicli apertura pannelli,90azioni |p95evento→2requestAnimationFrame 33.0ms |PASS soglia200ms; non misura del compositore |
|Automazione apertura menu+inspector |p95568ms di round trip |Include attese/trasporto dell’automazione; non confondere con latenza UI33ms |
|Vento |Costo disegnop95≈0,3ms; intervallip95≈35ms a riposo/50ms durante interazioni |30FPSuniformi non dimostrati; nessuna garanzia di fluidità universale |
|Python VM |237unit+58web+19domain+60decision=374PASS |Log core-tests-final.log; warningPROJ conservato, nessun errore del workergeo |
|ClientNode16.20.2 |25suitePASS |[Ricevuta](framework-audit-20261026/client-tests.json); include6023check del renderer, composizione nuvole/pioggia e missing |
|Nuovi casi archivi/geometria |35test miratiPASS |Compressione attivo/raw/receipt, conflitto/corruzione/espansione, hardlink, futuro senza estendere allerte |
|Safari/compositore/cold-cache/soak30min |NOT RUN oggi |Nessun PASS ereditato dalle prove precedenti |

Soglie riprese dal protocollo di audit precedente, non rilassate dopo le misure. Nessun aumento RAM/CPU avrebbe risolto le quote piene. Un solo riavvio controllato del core, senza job fisici attivi; servizi WII/TCIP non riavviati. Hardware/quote preservati.

## Preservazione e problemi aperti

[Verifica indipendente](framework-audit-20261026/preservation.json): workspace completo identico, revisione119; configurazione traffico identica;372file archivio job e145pin motori invariati;0job fisici attivi; oltre3GBliberi alla verifica. L’ottimizzatore crea soltanto una nuova evidenza decisionale isolata, senza cambiare i workspace. Archivio DPC/meteo compattato con uguaglianza dei contenuti decodificati, originali logici e timestamp conservati.

**Aperti:** gestione della capacità WII indipendente senza perdita di archivi o aumento implicito della quota; disponibilità/completa copertura elettrica; quattro geometrie DPC non qualificate (testi disponibili); FIRMS live senzaMAP_KEY, idrometri e perimetri osservati locali non connessi/verificati; popolazione e vulnerabilità non qualificate. Queste assenze non sono0rischio. L’incremento non chiude M5–M7 né abilita operazioni reali.

Ripetibilità: suite Python con `PYTHONPATH=src:tests core-env/bin/python -m unittest discover -s tests/<suite>` nella VM; ogni fileMJS test non-helper conNode16. Script/protocolli e log completi privati in `runs/framework-audit-20261026` VM e `experiments/runs/framework-audit-20261026` host. Verifica da browser dei livelli mediante checkbox/inspector, senza mutare stato scientifico nascosto.
