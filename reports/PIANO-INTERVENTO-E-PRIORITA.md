# Piano d’intervento a mappa singola —19ottobre2026

Richiesta: un pulsante per proporre il posizionamento delle squadre disponibili, tenendo conto di abitati, sanità, ferrovie, reti e altre infrastrutture critiche; confronto degli scenari in sottosezione separata. Incremento M3/M5/M6/M7 del piano originario, focus FIRE e architettura generica invariati. Run `intervention-plan-20261019`, parent `5205862` + modifiche; SHA finale in Git/PUBLICATION.json. Reviewer stesso agente Codex.

## Funzioni

**Simulazioni e risorse → Piano d’intervento** mostra una sola mappa dello scenario di partenza. Selezionare/mettere gli inneschi, aprire **Mezzi**, aggiungere le risorse realmente dichiarate per l’esperimento oppure copiare quelle dello scenario, indicare disponibilità e attivazione, controllare pesi/ipotesi e premere **Calcola posizionamento**. Nessuna squadra preinserita nel nuovo inventario. Il piano mostra le unità assegnate con marcatori numerati e aree di protezione ideali, obiettivo e attivazione; quelle indisponibili, non qualificate o prive di beneficio ammissibile restano elencate senza posizione inventata.

**Confronto scenari** conserva le mappe multiple e l’ordine di creazione dei casi, creazione/modifica/rimozione e replay preesistenti. Cambiare sottosezione non cancella dati o esecuzioni. La verifica fisica del piano resta un’azione esplicita: il pulsante di confronto nativo avvia i due job già previsti dal sistema e porta al Confronto. Ottimizzare non implica eseguire automaticamente altri modelli o inviare squadre reali.

Il riferimento per il piano deve essere senza interventi. Se necessario il pulsante prepara un riferimento con stessi inneschi e meteo; la preparazione fisica può durare più della decisione. Il limite60s riguarda la richiesta di ottimizzazione dopo disponibilità del riferimento. Il piano usa la previsione congelata del riferimento, non una sovrapposizione meteo grafica. Attivazioni non anteriori all’ora selezionata; valori allineati visibilmente nel modulo. Una richiesta API che retrodata le attivazioni viene rifiutata. Se si cambia scenario/inventario/priorità durante il calcolo, una risposta per gli input vecchi viene scartata. Le mappe rimangono consultabili.

## Politica esplicita delle priorità

Pesi relativi predefiniti, modificabili e **non ufficiali**: ospedali10; altre strutture sanitarie/assistenziali9; edificato residenziale/località8; istruzione e soccorso7; ferrovie e linee elettriche6; impianti e ponti5. I dati OSM sono interpretati attraverso tag espliciti. Sono inclusi binari/stazioni attivi cartografati, sottostazioni/impianti elettrici, opere idriche e ponti dichiarati. Disused/abandoned non diventano binari attivi. Non si deduce tensione mancante: le linee di distribuzione non sono rietichettate alta tensione. Centri GeoNames non duplicano i poligoni di edificato nell’obiettivo; proxy geometrici non qualificati esclusi.

Il solver minimizza un indice di esposizione pesata media/massimo sui prodotti nativi. Non è una graduatoria lessicografica ufficiale, una stima di persone salvate, un ottimo globale della lotta al fuoco o un piano logistico operativo. Le finestre locali di analisi mantengono la stessa rasterizzazione del modello; gli obiettivi lineari sono analizzati con fascia100m e posizione di protezione vicino alla porzione esposta. L’intervento di300m è ancora un’ipotesi ideale di rimozione del combustibile, non un modello calibrato della specifica categoria o una distanza di sicurezza. Il confronto fisico separato serve a misurare l’esito di questa ipotesi, senza promettere miglioramenti.

## Degradazione verificabile

Il solver primario HiGHS e il verificatore indipendente sono conservati. In modalità ideale0.6 un fallimento del processo/dei suoi requisiti o l’assenza di risposta utile entro la quota riservata consente un fallback greedy limitato nel tempo. Ogni prefisso accettato passa lo stesso verificatore, senza importare il solver o riusarene i vincoli. Esito marcatoDEGRADED, ottimalità non dimostrata. Nessun fallback aggira input di sicurezza mancanti, impegni non ricostruibili, risorse indisponibili o dati incoerenti. Nessuna assegnazione ammissibile produceNO_ADMISSIBLE_ACTION; non si inventano risorse.

Profilo per questa decisione: consultazione mappa disponibile, inventario parziale, assegnazione disponibile/degradata/indisponibile, assegnazione aerea indisponibile e effetto fisico non qualificato. Il replay controllato `solver_down` può usare il fallback soltanto per0.6; il comportamento legacy resta fail-closed. `safety_unknown` e fonti dichiarate scadute continuano a bloccare nuove proposte. Cambiamento della revisione di disponibilità/vincoli sospende il piano mostrato; servizio non verificabile sospende le proposte e conserva le mappe. Le indisponibilità dei mezzi nel modulo invalidano subito le assegnazioni e richiedono ricalcolo. Nessuna azione reale senza autorità umana; ogni risposta resta `operationally_approvable=false`.

## Evidenze e limiti

| Attività | Esito | Evidenza |
|---|---|---|
| Regressioni decisionali, contratti vecchi/nuovi, vincoli, supervisore e geometrie | PASS |51testVM, `unit-final.log`; include ferrovie/cavi su griglia nativa sintetica dichiarata |
| Normale HiGHS su output PROPAGATOR esistente | PASS | `decision-313b02b86b5a4641a6f5abe363cc037c`,6,3201s,2mezzi assegnati; nessun nuovo job fisico |
| Processo del solver effettivamente assente, stesso problema reale congelato | PASS | fallback0,4516s,2assegnazioni, verificatore indipendentePASS, ottimalitàfalse |
| Sicurezza sconosciuta, disponibilità negativa, assenza di autorità | PASS | zero proposte in configurazione ignota; esclusione Canadair non qualificato e unità non disponibile |
| Inventario del caso FonteVetica | PASS come incompletezza esplicita |1200poligoni WorldCover2021; nessuna ferrovia/linea elettrica/struttura sanitaria disponibile nello snapshot. Non significa assenza sul territorio |
| Integrità modelli e workspace durante audit | PASS |145pin invariati, workspace principale/caso identici prima/dopo,12assert di audit |
| Interfaccia e flusso a mappa singola | PASS | Sei record layout1440/768/375, due proposte visibili, invalidazione/disponibilità/attivazione+60min e ritorno dal confronto; `reports/intervention-plan/ui-verification.json`; prove reali sullo stesso caso senza modificare i suoi inneschi/risorse/scenari salvati |
| Nuova qualifica di efficacia/logistica/pericolo locale | BLOCKED | Vincoli operativi, completezza cartografica, popolazione, vulnerabilità e capacità aeree mancanti |
| Nuovi run fisici,30ripetizioni/p95,heldout,fullM5–M7 | NOT RUN / BLOCKED | Questa è verifica tecnica del piano, non chiusura dei gate scientifici |

Le durate riportate sono singole prove ingegneristiche, non distribuzioni prestazionali. I casi di calcolo dell’interfaccia con mezzi ipotetici sono registrati separatamente e non vengono usati come efficacia operativa. Il confronto nativo può ancora risultare peggiore del riferimento, come già previsto dal flusso precedente.

## Negativi conservati

1. Audit1: crash del worker per errore d’indentazione introdotto nella gestione del nuovo esito senza assegnazioni. RispostaERROR, nessun candidato mostrato; corretto e ripetute regressioni.
2. Audit2: preparazione oltre30s su maschere ripetute dell’intera griglia. TIMEOUT_UNPROVEN, nessun candidato inventato. Corretto con finestre locali e centro del fronte precalcolato; test di equivalenza rispetto alla maschera globale, inclusi bordi e geometrie esterne. Audit3 passato6,32s.
3. HarnessIAB: selettori/frameclick mentre cambiavano altezza e scroll non affidabili, e attesa del selettore terminata prima del risultato. Verifica tramite controlli accessibili e statoDOM dopo risposta; nessuna di queste attese è una misura del motore.
4. Nessuna geometria reale di ferrovia/cavo nell’area FonteVetica verificata: integrazione geometrica provata con fixture dichiarata, non dati infrastrutturali inventati sul caso reale.

## Ripetibilità

Nella VM, da `/home/hazardia/hazardia-runtime/app`:

```sh
PYTHONPATH=src PROJ_LIB=/usr/share/proj /home/hazardia/m0/reflex-env/bin/python -m unittest discover -s tests/decision -v
PYTHONPATH=src /home/hazardia/hazardia-runtime/core-env/bin/python tests/native/intervention_plan_audit.py --root /home/hazardia/hazardia-runtime --out /home/hazardia/hazardia-runtime/runs/intervention-plan-20261019/audit-new
```

Il secondo comando richiede il riferimento reale esistente e non altera i file dei motori. Crea soltanto artefatti decisionali/di audit; nessuna nuova acquisizione massiva o job fisico. Run raw in `experiments/runs/intervention-plan-20261019`, riepilogo nativo `reports/intervention-plan/native-verification.json`. StessaVM4vCPU/8GiB/19GiB, nessuna installazione/sudo/costo/deployment. Versioni/asset originari nei manifest dei job. I vecchi pesi a5categorie restano leggibili; le nuove categorie hanno peso0 per client legacy che non le dichiarano. AR-EXT-01, separazione simulatore/decisione/dati/UI e protocollo H1–H3 invariati; nessun supporto scientifico dedotto dai risultati tecnici.

L’inventario del modulo del piano è dichiarato nella sessione UI: non è un registro operativo persistente dei mezzi. Le richieste e risposte decisionali restano archiviate immutabilmente nel backend. Due squadre ipotetiche inserite per la verifica restano visibili nella sessione corrente; il codice non precarica mezzi. La gara temporale di risposta tardiva è protetta nel codice ma il suo timing nel browser è NOT RUN.
