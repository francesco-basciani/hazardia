# Riesame gate M0 e avvio M1 — 15 ottobre 2026

**Esito: PASS del gate di fattibilità M0 sui criteri originali di PLAN. M1 autorizzata dall'utente: «Procedi con M1!».** Non è un nuovo esperimento, né una rivalutazione dei risultati falliti. Riesame delle evidenze già eseguite; autore/revisore Codex, revisione idrologica indipendente ancora pendente.

| Criterio originale M0 | Evidenza eseguita | Esito |
|---|---|---|
| Mac/VM, vincoli locali, piattaforma | Inventario iniziale, Linux ARM4vCPU/8GiB/19GiB, unico runtime E-M0-023…025 | PASS |
| Repository ufficiali, dipendenze e licenze motori | Commit upstream fissati e testi licenza EUPL1.2 archiviati; nessun campione dati CIMA senza diritti usato | PASS |
| Mini-run reali dei tre motori | PROPAGATOR, HMC compilato, REFlEx0–4; manifest Linux/RNG e unified-VM, originali ed errori preservati | PASS |
| Compatibilità I/O HMC→REFlEx | Ponte numerico su griglia comune, sezioni/portata/unità/tempi; semantica Q0 bankfull/volume/assenza arrivi chiarita E-M0-007…015/021 | PASS fattibilità tecnica |
| Sorgenti satellite/meteo/territorio/esposizione e diritti | Cataloghi e alternative nel report iniziale, payload Copernicus e FOCA/SIR verificati; limiti accesso registrati | PASS assessment, non ogni connettore pronto |
| Isolamento e ripetibilità | Confronto Mac/Linux, worker seed1thread e policy con limiti; ambiente unico VM E-M0-024 | PASS per fixture provate |
| Scelte stack/engine e benchmark | ADR-0001/0002/0003, performance-baseline; nessuna performance di prodotto inventata | PASS assessment |
| Contratti ed evidenza scientifica |11confini,124PASS/78negativi, offline replay e manifest; registro scientifico e protocollo | PASS M0 fixtures |

Le precedenti etichette di gate BLOCKED avevano esteso impropriamente la chiusura M0 fino alla qualificazione completa di un caso storico reale. La correzione riguarda la classificazione del gate, non la verità dei fallimenti o le condizioni per rivendicare accuratezza. Nessun risultato sperimentale riscritto. Gli input incompleti bloccano il relativo scenario, non ogni sviluppo degli adapter.

Restano FAIL/BLOCKED gli originali problemi upstream, la qualificazione dei parametri/forcing reali, accuratezza e identità delle sezioni dei casi esaminati. Questi vincolano l'uso dei prodotti: M1 integra esecuzioni genuine con metadati di qualità e scenari di ricerca espliciti; M2/M3 verificano conseguenze/sicurezza; M7 effettua validazione storica. Nessuna qualificazione operativa dedotta. La compatibilità REFlEx sperimentale di due righe rimane dichiarata/versionata, non nuova fisica o sostituzione di CIMA.

Gli esempi principali M1 saranno in Abruzzo. Fonti geografiche reali non rendono reali un innesco, combustibile o temporale di scenario: ognuno resta identificato come osservato, ricostruito o sintetico. Si implementano soltanto ingestione, adapter, job/manifest/errori e relativi test, nell'ordine M1.1–M1.5. Nessun decision engine, UI M3, framework agentico o Digital Twin. Budget invariato; inizializzazione Git locale nell'attività di sviluppo autorizzata, nessun push/deployment/contatto esterno.
