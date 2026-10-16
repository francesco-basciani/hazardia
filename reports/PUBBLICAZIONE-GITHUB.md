# Codice completo e ricostruzione HAZARDIA

16 ottobre 2026 · run `github-repro-20261016` · revisore Codex, autocontrollo tecnico. Destinazione autorizzata dall’utente: [francesco-basciani/hazardia](https://github.com/francesco-basciani/hazardia), repository esistente, pubblico e inizialmente vuoto.

## Cosa è pronto

Il sorgente corrente comprende applicazione, dashboard, contratti, adapter/worker CIMA, solver e checker, coda, strumenti di test e procedure per ricostruire tutto il runtime. [Guida di installazione completa](../docs/INSTALLAZIONE.md), [riproducibilità e contenuto del repository](../docs/RIPRODUCIBILITA.md).

Sono stati aggiunti configurazione UTM, generazione cloud-init/ISO senza password o chiavi private, script opzionale di creazione VM, elenco prerequisiti Ubuntu, bootstrap non privilegiato degli ambienti e dei tre motori, acquisizione degli input con hash fissati, rigenerazione dei due esempi e della coppia incendio72h, controlli e pubblicazione curata del sorgente. Nessun motore sostituito, nessun servizio commerciale obbligatorio.

## Prove reali

| Attività | Esito | Evidenza e limite |
|---|---|---|
| Immagine Ubuntu fissata, seed con sola chiave pubblica, ISO NoCloud | PASS | `reproducibility/utm-assets.json`; immagine SHA86e13258…, ISO921600B; riuso immagine locale verificata, nessun nuovo download OS |
| Schema cloud-init | PASS | `cloud-init-schema.json` nel run; warning perché il controllo non privilegiato non legge lo stato dell’istanza di sistema, non un errore di schema |
| Nuovo avvio VM dal nuovo script UTM | NOT RUN | File e istruzioni forniti; non avviata una seconda VM né eseguita installazione privilegiata |
| Ricostruzione in directory indipendente nella stessa VM | PASS | Nuovi ambienti Python, HMC ricompilato, quattro addons GRASS in prefisso privato, configurazione e260hash di file; `reproducibility/installation-verification.json` |
| Modelli e dati autonomi rispetto a `m0` | PASS | Percorsi dei motori/ambienti nel nuovo prefisso; archivi e raster riusati solo come cache opzionale con hash, non come ambienti o binari del vecchio runtime |
| PROPAGATOR60min e HMC→REFlEx6h | PASS | Nuovi job `job-e41295cae2054771937f4cab1517e09e` e `job-76fdd79efa034cae8cc4a426ed1c4f24`; prodotti georiferiti, contratti/hash controllati, qualifica UNQUALIFIED_RESEARCH |
| Coppia nativa incendio72h e144PNG | PASS | Nuovi dati/array e due esecuzioni native;144hash NPZ e144hash PNG uguali agli originali del fixture; nessuna inferenza di efficacia reale |
| Test software | PASS |85:38unitari,19dominio,14decisione,14web/bootstrap/pubblicazione; `reproducibility/backend-tests.json` |
| Dashboard servita dal runtime ricostruito | PASS |54controlli principali +18fisici,375/768/1440, tastiera,15scansioni axe0violazioni (incompletes conservati localmente), persistenza, solver, playback; JSON in `reproducibility/` |
| Integrità vecchi motori | PASS |145file originari invariati; il runtime della dashboard dell’utente non è stato sostituito per effettuare il collaudo |
| Export completo sorgente, controllo pattern segreti e omissioni dichiarate | PASS | `scripts/prepare_publication.py` legge il commit, non file locali non versionati; `PUBLICATION.json` generato nella copia pubblica |
| Autenticazione pubblicazione | PASS via SSH | HTTPS locale senza credenziali BLOCKED; accesso SSH esistente verificato con dry-run, senza nuove autorizzazioni o lettura/stampa di token |
| Push e verifica remoto | PASS | Primo commit pubblico `039df1c68cceb1b36c4fb58e1729b3faed7f194f`; clone indipendente da GitHub, tutti i191file confrontati byte/hash con PUBLICATION.json, albero esatto e nessuna cronologia privata |
| Nuova macchina/OS indipendente, acquisizione completa da rete da zero | NOT RUN | Sistema Ubuntu esistente e cache di input con hash; non confondere nuovo prefisso con un nuovo OS |

## Ripetibilità numerica: risultato positivo e limite

[Audit misurato](reproducibility/numerical-replay-audit.json): probabilità e primo arrivo FIRE60min identici cella per cella; coppia72h identica nei144NPZ/PNG. Per FLOOD, la ripetibilità **bitwise stretta è FAIL**:197celle valide differiscono, massimo scarto assoluto `1.4901161193847656e-08 m`. Maschera,1220celle positive e profondità massima `0.1786166876554489 m` coincidono. La causa dello scarto non è stata isolata: non viene attribuita con certezza a uno specifico componente o corretta modificando gli input. Esecuzione valida e uguaglianza bitwise sono verifiche differenti.

Un solo fixture, stesso hardware/OS e parametri congelati: non sono eventi indipendenti, validazione storica, accuratezza fisica o prova H1–H3.

## Problemi individuati e corretti

- FAIL iniziale di estrazione sicura: l’archivio Python standalone contiene collegamenti terminfo che escono dalla directory di estrazione. Omissione della sola banca dati terminale opzionale, mantenendo il filtro sicuro; terminfo è fornito da Ubuntu. Nessun sorgente CIMA modificato.
- FAIL primo FIRE: l’archivio ufficiale PROPAGATOR usa `src/propagator`, mentre la vecchia copia preparata esponeva `propagator` direttamente. Configuratore corretto per entrambe le disposizioni; nuovo prefisso ricostruito e simulazioni ripetute.
- FAIL primo verificatore: chiamata al controllo prodotto senza passare la richiesta accettata. Corretto il verificatore, poi eseguita l’intera verifica con85test PASS. Il fallimento non era un output fisico invalido.
- Difetto preventivamente trovato nel tool di pubblicazione: un vecchio `PUBLICATION.json` avrebbe introdotto un hash autoreferenziale obsoleto in una successiva esportazione da clone pubblico. Ora il file viene rigenerato, con test dedicato PASS.

I log negativi originali rimangono nel run locale. Il protocollo formale di questa consegna è stato scritto dopo i primi controlli di preparazione/installer: non viene presentato come preregistrazione precedente a tutte le prove. Le versioni/input erano congelati prima delle nuove esecuzioni native; non si tratta della campagna scientifica principale.

## Pubblicazione e licenze

Il repository pubblico contiene il sorgente completo della versione corrente e le istruzioni; scarica separatamente gli upstream ufficiali e i grandi raster. Non contiene chiavi, dischi VM, ambienti installati, cache, stato personale, ortofoto da redistribuire o bozza editoriale del paper. La cronologia privata originale è preservata localmente; il primo commit pubblico è una fotografia curata, così non pubblica vecchie immagini con diritti non verificati. I successivi aggiornamenti conservano la storia pubblica con normali push, senza force-push.

CIMA, GRASS, Python e i dati conservano diritti/attribuzioni propri. La patch REFlEx è dichiarata e accompagnata da riferimento upstream e testo EUPL. Non è stata scelta implicitamente una nuova licenza per il codice originale HAZARDIA; vedere NOTICE. Le limitazioni scientifiche/M5–M7 e le funzionalità ancora mancanti restano esplicite.

## Prossimo incremento

Dopo la pubblicazione, riprendere il piano applicativo originale: laminazione, argini e pompaggio richiesti tutti dall’utente, con verifica HMC e valutazione idraulica prima di eventuali adozioni sostanziali. Rimangono da eseguire un boot/installazione su nuovo OS indipendente e la qualificazione scientifica: il bootstrap non li dichiara completati.

## Consegna pubblicata

Repository: https://github.com/francesco-basciani/hazardia . Primo push SSH effettivo e clone remoto verificati il2026-10-16: commit `039df1c68cceb1b36c4fb58e1729b3faed7f194f`,191file di manifest più PUBLICATION.json. Questo aggiornamento documentale viene pubblicato come normale commit successivo, preservando la storia pubblica. Il controllo byte/hash del clone è PASS; non è una nuova prova di installazione su OS vergine.

Checkpoint risorse dopo il collaudo: stima conservativa download3.433.583.372B su5.368.709.120B, spazio libero guest9.422.553.088B;4vCPU/8GiBRAM/19GiBdisco invariati. Server/tunnel temporanei8081 chiusi; dashboard originale8080 preservata.
