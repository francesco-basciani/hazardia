# Prerequisiti e primo controllo nativo degli invasi HMC

16ottobre2026. Run `missing-prerequisites-20261016T055356Z`. Reviewer Codex self-check; nessuna revisione idraulica esterna. Sorgente applicativo di partenza eb85990; harness nuovo identificato perSHA nel piano preregistrato prima di compilazione/esecuzione, non presentato come già contenuto in quel commit. Tutte le prove scientifiche/compilazione dentro la VM Linux esistente. [Risultati](prerequisites/verification.json).

## Risultato dell’installazione richiesta

**Non risultano pacchetti runtime mancanti rispetto ai manifest del progetto.** 32pacchetti Ubuntu installati,25versioni Python fissate corrispondenti (4fire,2decision,19geo-extra),10comandi richiesti disponibili,4addon GRASS,import nei4ambienti e145hash dei motori PASS. Non abbiamo reinstallato né aggiornato arbitrariamente componenti già funzionanti. Installazione nuovi pacchetti: NOT RUN perché nessun prerequisito dichiarato assente. Nessun sudo, download di nuovi motori, aumento risorse o nuovo servizio.

Il primo comando di ispezione con `rg` nella VM non ha funzionato: ripgrep non è installato. È uno strumento facoltativo di ricerca, non una dipendenza del framework; l’ispezione è proseguita con Python senza bisogno di privilegi. Non è un errore HMC né un motivo per bloccare la piattaforma.

I requisiti funzionali incompleti del piano non sono pacchetti da installare: pipeline forecast/salute fonti, strategie multiple, capacità ottimizzate, interventi fisici alluvionali e relative mappe, casi storici, dati qualificati e scala richiedono sviluppo e prove. Questo controllo non li riclassifica PASS.

## Incremento eseguito senza nuovi motori

Il sorgente HMC approvato contiene `HMC_Module_Phys_HydraulicStructure.f90`. Abbiamo collegato un harness alle routine native **non modificate** già compilate: `HMC_Phys_Dam_Spilling` e `HMC_Phys_Lake_Tank`. Nessuno stub fisico o algoritmo sostitutivo.

Input sintetici congelati in storage-pilot-plan.json prima del run: cella100m², invaso massimo1000m³, curva volume-livello[0,500,1000]m³/[0,5,10]m, soglia statica0.5, rilascio massimo configurato1m³/s e passi10/1000s. Lago con minimo100m³, coefficiente0.1/h e passo3600s. Tolleranza numerica max(1e-4,abs(atteso)×1e-5), non soglia di accuratezza fisica.

| Caso | Risultato nativo | Esito |
|---|---|---|
| Invaso sotto volume statico450m³ | Resta450, nessuno sfioro | PASS |
| Invaso sotto quota sfioro800m³ | Resta800, nessuno sfioro | PASS |
| Sfioro limitato da950m³,10s | Volume940m³, uscita equivalente10m³ | PASS |
| Volume iniziale1200m³ sopra capacità | Volume finale1000m³, uscita equivalente200m³ | PASS |
| Passo lungo1000s da950m³ | Volume minimo500m³ rispettato, uscita450m³ | PASS |
| Lago da1100m³ | Finale1000m³;100m³ trasferiti alla cella a valle | PASS |
| Lago sotto minimo50m³ | Volume50m³ invariato, nessun rilascio | PASS |

**21asserzioni PASS su7casi**, esecuzione exit0; ripetizione del runner documentato PASS. GNUFortran11.4.0, Ubuntu22.04ARM64. Il primo contatore diagnostico `stdout.count('PASS')` riportava22occorrenze perché includeva anche il marcatore finale ALL_COMPONENT_CHECKS_PASS: non erano22asserzioni. Il conteggio corretto per righe PASS è21; output originale preservato, runner riutilizzabile corretto. Nessun test fallito nascosto o soglia allentata.

## Unità e limiti da preservare nell’integrazione

Lo sfioro restituisce **mm per passo** normalizzati per area, anche se i commenti intermedi parlano di m³/s; il tank restituisce **mm/h** e aggiorna il flusso profondo a valle inmm per passo. Il controllo di volume converte mediante area/1000 e, per la portata, anche mediante tempo. Non collegare questi array a REFlEx come se fossero direttamente m³/s. I valori geometrici sono inventati, non un invaso reale dell’Abruzzo.

PASS compilazione/esecuzione componenti, rilasci e bilanci su parametri scelti; NOT RUN bacino con invaso e afflussi reali, propagazione temporale idrografi, integrazione HMC→REFlEx con azione, mappa differenziale, giorni, argini/pompaggio, zero/negativi/curve malformate, convergenza/stabilità/calibrazione ed efficacia sul campo. Il driver è compilato con controlli runtime, ma gli oggetti upstream riusati mantengono i loro flag di build: nessuna promessa di bounds checking completo dentro HMC. Le prove sui soli componenti non chiudono FR-FLOOD-ACTIONS-01 né M5–M7.

## Ripetere la prova

Nella VM dopo il bootstrap, dalla directory app; scegliere un output nuovo:

```sh
../core-env/bin/python scripts/verify_hmc_storage.py \
  --engine-source /home/hazardia/repro-check-20261016-v2/engines/upstream/hmc-src \
  --output /home/hazardia/hazardia-runtime/runs/NUOVO-storage-check
```

Adattare solo il percorso alla propria cartella hmc-src compilata. Script e harness sono in Git; manifest registra hash sorgenti/oggetti/driver, compilatore e comandi. In questo run il runner è stato copiato in un layout isolato sotto `missing-prerequisites-20261016T055356Z/replay-source` e rieseguito, senza sovrascrivere il primo esperimento. Log e manifest risiedono anche nella VM in `/home/hazardia/hazardia-runtime/runs/missing-prerequisites-20261016T055356Z`. Mac solo controllo/copia/hash. La dashboard e gli archivi utente non sono stati modificati da queste prove.

## Prossimo lavoro concreto

Costruire un fixture di bacino HMC con struttura dichiarata, validare gli input invaso/curve/forzanti e la conversione di unità, confrontare idrografi matched senza/con invaso, quindi REFlEx e rappresentazione nella piattaforma. Argini/pompaggio restano da valutare con idraulica locale: qualsiasi nuovo motore sostanziale va presentato prima di adottarlo. I tre interventi sono già richiesti dall’utente; nessuna scelta esclusiva pendente. Fonti/forecast, portafoglio decisioni, scala e validazione restano nel piano originale; nessuna nuova autorizzazione ordinaria di milestone richiesta.


## Chiarimento: completare le integrazioni rimaste

La richiesta riguarda tutte le integrazioni funzionali del piano, non solo i pacchetti. Open-Meteo è già collegato; questo non chiude il resto del lavoro. Ispezione aggiuntiva `remaining-integrations-20261016T063454Z`: PASS lettura dei sorgenti HMC nella VM, senza installare o modificare motori.

Per il prossimo fixture, `HMC_Module_Info_Point.f90:169–179` legge conteggi diga/centrali da `dominio.info_dam.txt`; `HMC_Module_Data_Static_Point.f90:592–750` legge geometria, volumi, parametri di sfioro, file curva volume-livello e impianti. Le righe della griglia vengono invertite; il codice della diga deve identificare le celle nel raster choice/mask. Il parsing dei rilasci cambia con il formato/versione: occorre verificare quello esatto del sorgente fissato. Estratti integrali e SHA256 sono conservati nel run.

**NOT RUN:** fixture integrato, idrografi senza/con invaso e nuove mappe REFlEx. Nessuna nuova simulazione o efficacia dichiarata da questa sola ispezione. Argini e pompaggio restano richiesti; un eventuale motore fisico aggiuntivo va valutato e presentato prima dell’adozione. Gli altri blocchi restano quelli di `VERIFICA-PIANO.md`, aggiornati dal successivo incremento meteo.
