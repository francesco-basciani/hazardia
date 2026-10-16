# ADR-0003 — Freeze degli esempi di contratto M0

Data: 2026-10-15. Stato: **adottato per gli esperimenti di conformità M0**, non implementazione o autorizzazione M1. Prosegue il piano originale; estensioni della proposta Control Room rinviate per scelta utente. SPEC §7.1 invariato. Complementa ADR-0001 e rispetta ADR-0002: ogni esecuzione nella stessa VM Linux.

## Decisione e alternative

Freeze di undici schemi JSON Schema Draft-07, versione del messaggio `0.1.0`, esempi positivi e negativi, con harness sperimentale fuori da `src/` e `tests/`. Il validatore già disponibile nella VM è Ubuntu `python3-jsonschema` 3.2.0, MIT (copyright completo archiviato); nessuna installazione/download aggiuntivo. Scelta circoscritta alla verifica degli esempi, non vincolo di libreria per le future API.

Alternative: Draft2020-12 con nuovo ambiente/dipendenze, Pydantic come modello applicativo, controlli solo manuali. Il draft presente basta ai costrutti usati (oggetti chiusi, tipi, enum, const, nullable); rinviato il primo, evitata l'implementazione applicativa del secondo, insufficienti i soli controlli manuali. Meta-validazione degli schemi e controllo semantico separato sono entrambi necessari. Le regole trasversali non sono tutte esprimibili in JSON Schema.

Fonti primarie consultate: [specifica Draft-07](https://json-schema.org/draft-07/), [API jsonschema3.2.0](https://python-jsonschema.readthedocs.io/en/v3.2.0/validate/). La documentazione precisa che `format` richiede un checker esplicito: si usa `FormatChecker` con formato sperimentale `utc-timestamp`, verificato anche con una data impossibile. L'accesso alle fonti è attività di controllo sul Mac, non runtime HAZARDIA.

## Regole del freeze

- Ogni messaggio contiene `schema_version`, `kind`, `id`, `provenance`, `payload`. Oggetti chiusi: proprietà sconosciute e versione diversa vengono respinte. Nessuna conversione implicita, nessun valore mancante interpretato come sicurezza positiva.
- UTC in forma ISO8601 con `Z`, secondi e frazioni opzionali fino a sei cifre; fuso IANA originale nella provenance e nel profilo territoriale. Bbox sempre longitudine/latitudine CRS84, distinta dal CRS di lavoro. Le griglie dichiarano CRS, datum verticale, shape, trasformazione affine a sei valori e NoData esplicito. Unità di campo e prodotto esplicite.
- `null` ammesso solo dove lo schema lo prevede (per esempio calibrazione, efficacia sconosciuta, seed non applicabile, identità Git assente motivata nel pilot). `UNKNOWN` è conoscenza insufficiente, non valore predefinito accettabile per una strategia validata. Una richiesta può legittimamente ricevere `UNVERIFIED`.
- Stesso job/input/snapshot, griglia, intervallo, motore/revisione/patch devono corrispondere nei messaggi collegati. Questo fixture richiede forcing già allineato; un futuro resampling deve essere dichiarato e tracciato dall'adapter. Non è una prova di trasformazione geospaziale.
- Q0 è `BANKFULL_REFERENCE`, mai implicitamente primo campione HMC; la qualificazione può restare `UNKNOWN` nei risultati esplorativi. `MAXIMUM_DEPTH` in metri non diventa arrivo temporale. Nessun beneficio da `UNKNOWN_EFFECT`; il soccorso alluvionale non modifica la portata.
- La decisione è research-only; verifica indipendente positiva necessaria per `VALIDATED_FOR_SIMULATION`. Autorizzazioni di esempio solo `SIMULATION_ONLY`, legate a proposta/versione, attore proprietario e scadenza. Nessuna azione operativa reale implementata o emessa.

Mappatura esplicita, senza sostituire i termini normativi FR-13/QR-02:

| Reason FR-13 / successo | Terminale pubblico QR-02 / successo | ProposalStatus |
|---|---|---|
| VERIFIED | SUCCESS | VALIDATED_FOR_SIMULATION |
| PROVEN_INFEASIBLE | INFEASIBLE_PROVEN | PROVEN_INFEASIBLE |
| TIMEOUT_UNPROVEN | TIMEOUT | TIMEOUT_UNPROVEN |
| INVALID_INPUT | ERROR | INVALID |
| SAFETY_UNVERIFIED | UNVERIFIED | UNVERIFIED |
| DEPENDENCY_UNAVAILABLE | BLOCKED | DEPENDENCY_UNAVAILABLE |

`SUCCESS`/`VERIFIED` denotano il ramo positivo di esempio; i terminali non-successo conservano i valori SPEC. Un timeout non fornisce una prova di infeasibilità. I tempi scritti nei fixture sono asserzioni da verificare, non misure di performance del prodotto. Nessun solver/verifier applicativo viene eseguito.

Compatibilità: consumo esatto `0.1.0`; roundtrip preserva i valori JSON e gli sconosciuti espliciti. Nessuna accettazione automatica di versioni future. Una modifica al wire format richiede nuova versione, ADR, migrazione esplicita e test su entrambi i formati; una correzione soltanto editoriale lascia il wire format invariato. Il test `0.2.0` è respinto per tutti gli undici record. Nessuna migrazione reale è stata implementata perché esiste un solo formato.

## Evidenze e limiti

Run iniziale `m0-contracts-20261015T152857Z`:117PASS/2FAIL; due fixture negativi con griglie condivise cambiavano tre record insieme, cancellando il disaccordo atteso. Conservati integralmente. Run successivo `m0-contracts-20261015T153248Z`: copia per valore JSON nella generazione,113file congelati prima dei test,124PASS/0FAIL,78negativi isolati controllati separatamente, replay senza connessioni socket con identici esiti. Fonte della correzione dichiarata, nessun fallimento storico riscritto.

L'harness verifica questo insieme finito di esempi, non ogni input possibile. Non legge i valori dei raster, non verifica qualsiasi EPSG, non effettua fusione/deduplicazione generale, non certifica prove matematiche del solver, identità umane o efficacia fisica. Contesto chiuso con un record per tipo e proprietario unico; la variante Senegal controlla soltanto il profilo, non la portabilità della catena scientifica. Schemi, fixture e controlli sono dello stesso autore; revisione indipendente pendente. Gli adapter M1 dovranno rieseguire e ampliare questi controlli sui loro veri prodotti. La qualificazione idrologica resta BLOCKED; nessuna conclusione RQ1–RQ3.
