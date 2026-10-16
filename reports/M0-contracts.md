# M0 — Contratti tra componenti: esempi e prove eseguite

Data: 15 ottobre 2026. **Esito dell'incremento: PASS per il freeze sperimentale G-01; gate M0 ancora BLOCKED per qualificazione idrologica e dati reali. M1 non avviata né autorizzata.** Il piano originale M0–M7 continua, senza le estensioni della proposta esplorativa.

In parole semplici: abbiamo fissato come i futuri componenti dovranno descrivere ciò che si scambiano e provato a intercettare messaggi sbagliati. Questo evita, per esempio, di leggere un allagamento in metri come un tempo di arrivo o usare una previsione che al momento della decisione non era ancora disponibile. Non è una nuova funzione visibile della piattaforma: backend, dashboard e decision engine restano da implementare nelle rispettive milestone.

## Ambiente, identità e procedura

Tutte le generazioni e validazioni eseguite in HAZARDIA-M0-ARM64: Ubuntu22.04/aarch64, kernel5.15.0-198-generic, Python3.10.12, jsonschema3.2.0 Draft7 già installato; copyright e versioni Debian/Python archiviati. Stessa VM,4vCPU/8GiB/19GiB, nessun nuovo pacchetto, dataset o servizio commerciale. Mac soltanto editing, controllo SSH e copia/hash delle evidenze. Directory non Git: SHA e dirty null con motivo esplicito; nessun commit inventato. Seed non applicabile ai controlli deterministici.

Run conservati:

- `experiments/runs/m0-contracts-20261015T152857Z`: primo tentativo,117PASS/2FAIL. Difetto nella generazione dei due negativi di disaccordo griglia: Python manteneva riferimenti condivisi anche dopo deepcopy. I dati arrivati al validatore erano ancora coerenti; non è prova che abbia accettato griglie discordanti.
- `experiments/runs/m0-contracts-20261015T153248Z`: nuovo run che supera il precedente con copia JSON per valore, preservando il primo.113file di input/ambiente congelati e hash verificati prima della validazione. `validation-frozen.json`:124PASS/0FAIL. `validation-offline.json`: stessi124esiti, rete impedita a livello socket nel processo Python (non sandbox del sistema operativo).

Comandi effettivi nel guest, dalla directory del secondo run:

```sh
python3 build_fixtures.py
# Freeze SHA256 di113file; script esatto nel log contract-freeze.json sul Mac.
python3 validate_contracts.py frozen
# Replay con socket.connect/create_connection disabilitati;
# script esatto nel log contract-audit-offline.json sul Mac.
```

Per rigiocare senza rigenerare/sovrascrivere il freeze:

```sh
cd /home/hazardia/m0/m0-contracts-20261015T153248Z
python3 validate_contracts.py user-replay-01
```

Scegliere un suffisso nuovo: il file di risultato è creato in modo esclusivo. Non rieseguire il builder sulla directory congelata. Gli esempi sono in `contracts/valid/`, i78negativi in `contracts/invalid/`, aspettative in `contracts/cases.json`, schemi in `contracts/*.schema.json`. Gli archivi copiati sul Mac contengono lo stesso albero sotto `guest/<run_id>/`. Il manifest di ciascun run e le liste SHA256 consentono di verificare la copia. La procedura completa SSH, stdout/stderr, timestamp e exit sono nei log `contract-*.json`.

## Risultati

| Attività | Stato | Evidenza osservata |
|---|---|---|
| Undici confini SPEC7.1 | PASS | Territorio, osservazione, meteo, input/output simulatore, risorsa, effetto, richiesta/risposta decisione, autorizzazione, manifest:11meta-validazioni,11esempi validi,11roundtrip. |
| Coerenza positiva | PASS | Bundle base più7varianti: terminali distinti, successo solo simulativo su dati fittizi qualificati, profilo Senegal isolato, UTC con frazioni. Nessuna strategia calcolata. |
| Rifiuti attesi | PASS |78negativi:campi/versioni/unità/griglie/tempi, efficacia sconosciuta, safety, sovrapposizioni/turni/autonomia, trasferimento non autorizzato, proof assente, candidato tardivo, autorizzazione incoerente, hash/percorso errato. |
| JSON e immutabilità locale | PASS | Rifiuto chiavi duplicate/NaN/Infinity; apertura esclusiva non sovrascrive file esistente. Nessun servizio di persistenza implementato. |
| Riferimento a esperimento reale | PASS | Hash di `vm-validation.json` del precedente run VM verificato nel guest contro il riferimento fissato prima della prova; soltanto identità dei byte, non qualificazione fisica. |
| Isolamento fixture e sorgenti | PASS | Audit separato: ogni negativo modifica solo il record dichiarato; tutti11confini coperti;113hash input invariati,125sorgenti originali CIMA invariati. |
| Prima generazione dei negativi griglia | FAIL | Due casi non esercitavano il disaccordo previsto. Conservati nel primo run, corretti soltanto nel successivo. |
| Implementazione adapter/API/verifier/solver/UI | NOT RUN | Cartelle applicative non implementate; nessun requisito FR/QR dichiarato completato. |
| Calibrazione alluvionale/vero forcing/ground truth | BLOCKED | Contratti non risolvono Q0/tconc/calibrazione, completezza bacino/DSM o diritti sui campioni idrologici CIMA. |

Totale124 per esecuzione =33controlli individuali +8bundle/varianti +78negativi +3JSON +1creazione esclusiva +1riferimento reale. I due replay non sono248campioni scientifici indipendenti. Esiti e dettagli completi nei JSON; autore/verificatore Codex, revisione indipendente pendente.

Scelte, mappatura degli stati, gestione UNKNOWN e compatibilità: `ADR-0003-M0-contract-fixtures.md`. Errori strutturali `SCHEMA`; errori semantici con codici distinti quali `GRID_MISMATCH`, `FUTURE_SOURCE`, `SAFETY_UNKNOWN`, `UNKNOWN_EFFECT`, `STATUS_MAPPING`, `PROOF_REQUIRED`, `DEADLINE`, `AUTH_PROPOSAL`, `CHECKSUM`. Dettagli non sostituiscono la verifica applicativa indipendente prevista da SPEC.

## Prossimo incremento eseguibile

Restare in M0: preparare il dossier del piccolo caso idrologico reale, con confini di bacino verificabili, diritti e disponibilità di precipitazione/portata osservata, estimator Q0 e tconc espliciti, controlli di stabilità e confronto osservato. Si può completare autonomamente la ricognizione delle fonti pubbliche entro i limiti; uso di dataset senza licenza chiara, contatti esterni o approvazione fisica richiedono le rispettive decisioni/competenze. Non serve aumentare CPU/RAM per i controlli di questo incremento: i blocchi attuali riguardano dati e significato fisico. M1 resta subordinata al riesame M0 e a una nuova autorizzazione.
