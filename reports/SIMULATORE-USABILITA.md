# Simulatore: percorso e campionamento temporale

Run `fire-usability-20261017`, base `5bdc9c871bf1041bbf865826de2ae38a103f4ac5`, reviewer Codex self-check. FR-FIRE-WORKSPACE-01 e FR-26; nessuna sostituzione del simulatore CIMA. Tutti i calcoli e la persistenza sono nella VM esistente.

## Modifiche

- Scenari sempre visibili come schede con stato e durata calcolata; **Crea alternativa** copia il caso selezionato, mantiene il precedente e predispone il confronto fra origine e copia.
- Percorso esplicito: posizionare/trascinare gli inneschi, creare un’alternativa, aggiungere o spostare le unità e disegnarne linea/area, calcolare i casi da confrontare. Nomi delle categorie visibili anche sui pulsanti compatti.
- **Durata del confronto** si applica a tutti i casi; accorciamenti incompatibili con eventi già definiti vengono rifiutati. La durata richiesta è distinta da quella dei risultati precedenti. Cambiare durata richiede ricalcolo.
- Nuovi calcoli PROPAGATOR con output effettivi ogni900s, cioè15minuti. Intervalli interni gestiti dal simulatore, vento ancora orario. Nessuna interpolazione o animazione inventata di perimetri. I vecchi prodotti orari rimangono immutati e leggibili.
- Timeline basata sul tempo fisico dei frame, non sull’indice nell’array; pausa, passo e velocità espressa in campioni. Precaricamento del frame richiesto e transizione visiva breve; nessuna immagine intermedia sintetica. Errori di caricamento conservano la vista precedente con messaggio. Metadati di confronto distinguono anche cadenze/durate diverse.
- Due nuovi esempi24h salvati accanto ai4casi preesistenti, preservati integralmente: senza interventi e fascia da+1h. La vista iniziale seleziona questa coppia a15minuti. Sono replay ERA5 e moisture25% manuale, non previsione di un evento attuale. Le categorie mantengono l’effetto ideale di rimozione del combustibile, senza efficacia sul campo dedotta.

## Prove

PASS due job nativi: `job-a1304b9f54634eab9ae27f56ad20e2d9` e `job-fd11b1c543124d95a5c8ff8af210217b`, entrambi24h/96frame. Tutti i tempi verificati a incrementi900s; renderer indipendente verifica shape, range, hash e area. I primi3PNG A/B, prima dell’intervento, hanno hash identici. Aree finali1,395ha e0,54ha: controfattuali su parametri ipotetici, non una misura di efficacia operativa. Nell’esempio A l’area è già1,395ha a3h e rimane invariata fino24h; non viene forzata una crescita grafica per occupare tutta la durata.

PASS19controlli workflow browser: duplicazione, conservazione geometrie originali, durata comune24h, stato precedente3h distinguibile, selezione confronto e payload;375/768/1440senza overflow e3axe sulla pagina radice senza violazioni. Fixture browser intercettata: non modifica la workspace reale e non avvia nuovi job. PASS7controlli su un risultato nativo reale: passo0,25h, frame001/004/096 correttamente mostrati a15min/1h/24h, play a incrementi15min. La fixture con due copie dello stesso risultato serve solo al test UI, non al confronto fisico.

PASS16test firelab/workspace e17regressioni web (insiemi in parte sovrapposti, non sommati come prove indipendenti). Nuovo esempio aggiunto con revisione controllata e verifica di conservazione dei4casi precedenti. Riavvio backend solo a job inattivi per aggiornare la descrizione dei nuovi job. Il testo storico delle prime due richieste menzionava ancora il precedente stepping orario; gli output effettivi900s e il sorgente eseguito sono le evidenze di cadenza. Descrizione corretta per le richieste successive, senza modificare le richieste sperimentali salvate.

NOT RUN72h alla nuova cadenza, benchmark p95/soak, dispositivi fisici, studio di usabilità con utenti, equivalenza numerica vecchio/nuovo stepping e skill/efficacia operativa. La suddivisione delle chiamate step cambia rispetto al precedente adattatore; non si presume identità stocastica con i job orari. I gate scientifici M5–M7 rimangono BLOCKED. La riproduzione usa risultati di job completati, non streaming di una simulazione in esecuzione.

Raw `experiments/runs/fire-usability-20261017/`; input, serie e workspace prima/dopo nella VM `~/hazardia-runtime/fire-usability-20261017/`. Riepilogo pubblico `reports/workspace/fire-usability-verification.json`. Codice: worker fire_studio/studio_render, frontend fire-studio, harness tests/browser/fire-usability.cjs e fire-cadence.cjs. Gli harness usano gli stessi parametri d’ambiente Playwright/Chrome/axe dei precedenti; per la cadenza indicare HAZARDIA_FINE_JOB_ID di un job reale già concluso con output15minuti. La verifica software non dimostra da sola che il flusso sia intuitivo per ogni utente.
