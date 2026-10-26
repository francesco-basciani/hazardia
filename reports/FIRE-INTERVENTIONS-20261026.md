# Interventi antincendio: visibilità e accoppiamento fisico

Run `fire-interventions-20261026`, 26 ottobre 2026; revisione di partenza `ecfab305f3dd49fcef348ec1b57947cc618f8251`, modifiche del presente commit. Esecuzione e analisi geospaziale nella VM esistente; revisore: Codex (autoverifica tecnica, non validazione scientifica indipendente).

## Difetto corretto

La vista Piano d’intervento eliminava esplicitamente le risorse manuali sia dagli overlay nominali sia dal renderer di authoring. Queste continuavano a essere salvate e passate al motore, ma non comparivano sulla mappa del piano. Rimossa l’esclusione: squadre e geometrie sono visibili e selezionabili in entrambe le viste. La testata riporta numero di interventi attivi/futuri al tempo simulato; icone future attenuate, attivazione leggibile e avviso se il risultato dimostra fronti già esauriti prima dell’azione. Nessuna deduzione da dati mancanti o da un frame allo stesso istante dell’azione. Contrastata la testata sullo sfondo satellitare. Nuovi messaggi IT/EN. Nessuna modifica a fisica, input salvati, motori o ottimizzatore.

## Diagnosi degli scenari salvati

Workspace revisione119, input e risultati congelati dal 18 ottobre, non previsione corrente. Il nome assegnato dall’utente non garantisce assenza di interventi.

| Scenario salvato | Interventi | Esito medio finale | Evidenza |
|---|---:|---:|---|
| Senza interventi | 1 Canadair ideale a +36h30 | 1,53 ha | Fronti esauriti a +5h15; linea non intercetta le celle raggiunte dal riferimento |
| Scenario 1 | 2 a +0 | 1,215 ha | 207 celle di combustibile cambiate; 21 celle di probabilità finale diverse dal precedente |
| Scenario 3 | 3 a +0 | 0,09 ha | 134 celle di combustibile cambiate; 32 celle di probabilità finale diverse |

Questi confronti diagnostici hanno configurazioni preesistenti: non sostituiscono il confronto controllato seguente. L’effetto `fuel_removal` è una barriera ideale uguale tra categorie, non una calibrazione fisica del Canadair o delle squadre.

## Quattro esecuzioni native controllate — PASS tecnico

Protocollo congelato prima delle esecuzioni: [protocol.json](fire-interventions/protocol.json). Stessi terreno, griglia30m, meteo congelato, innesco, seed1729, due realizzazioni e calendario comune delle condizioni al contorno. Orizzonte6h; intervento a +30min. Geometria scelta da una linea preesistente che intercetta l’impronta del fronte: prova di accoppiamento, non strategia valutata su dati indipendenti. Comando in VM: `fire-env/bin/python -m hazardia.adapters.workers.fire <case-dir>`, separato per ciascun caso, un processo alla volta, thread limitati1.

| Caso | Area media a +6h | Celle positive | Input modificato a +30min | Differenze finali dal riferimento |
|---|---:|---:|---|---:|
| Nessun intervento | 1,53 ha | 33 | Nessuno | 0 |
| Canadair nativo sulla linea del fronte | 0,18 ha | 3 | Umidità in44celle | 30celle |
| Rimozione ideale del combustibile sulla stessa linea | 0,18 ha | 3 | Vegetazione in14celle | 30celle |
| Canadair nativo lontano dal fronte | 1,53 ha | 33 | Umidità in44celle lontane | 0 |

Tutti i frame prima dell’attivazione sono numericamente identici. Il controllo lontano ha lo stesso SHA256 finale del riferimento: escluso un effetto artificiale globale dovuto alla sola presenza della risorsa. Durata singolo worker6,77–6,90s su questa fixture, non benchmark generale. [Ricevuta completa](fire-interventions/native-verification.json).

![Confronto degli output nativi](fire-interventions/comparison.png)

## Verifiche software, interfaccia e preservazione

- `node tests/browser/fire-comparison-status.mjs`: PASS20assertion originali, nuovi casi conteggio/attivazione/tempi ignoti/non mutazione e fronte esaurito strettamente prima dell’azione.
- `node tests/browser/studio-view-state.mjs`: PASS8, navigazione a0 e ripresa locale conservate.
- Browser reale della dashboard: PASS selezione unità manuale nel piano; Canadair futuro e messaggio a +36h30; Scenario1 mostra2interventi, Scenario3 mostra3; confronto mostra tutti e tre gli scenari con i rispettivi interventi. Nessuna risorsa aggiunta/cancellata per la prova UI. [Schermata](fire-interventions/delivery.png).
- [Preservazione indipendente](fire-interventions/preservation.json): workspace completo identico prima/dopo, revisione119, richiesta sorgente identica e tutti i pin motori identici. Spazio libero finale2.845.626.368byte, oltre riserva2GiB. La ricevuta nativa precede questa verifica separata.

Artefatti privati VM: `/home/hazardia/hazardia-runtime/runs/fire-interventions-20261026/`; quattro request/plan/output/frame/log separati, protocollo e controlli. Copia evidenze host: `experiments/runs/fire-interventions-20261026/`. Nessun nuovo download, modifica di quote, cancellazione archivio o avvio di job nel workspace utente.

## Limiti invariati

Le superfici visualizzate sono cumulative delle celle raggiunte: un intervento successivo non cancella celle già bruciate. Deve intercettare combustibile/fronte futuro al tempo opportuno. I parametri nativi e ideali non dimostrano efficacia operativa o spegnimento garantito. Due realizzazioni non qualificano probabilità; questo meteo storico congelato non è una previsione del26ottobre. Validazione fisica storica, gate M5–M7, REFlEx e prestazioni su grandi carichi restano invariati/NOT RUN in questo incremento.
