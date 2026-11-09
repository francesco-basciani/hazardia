# Third-party research runtime

CIMA PROPAGATOR, HMC and REFlEx are separate upstream engines under EUPL-1.2,
pinned by runtime configuration and executed in isolated dependency environments.
They are not included or relicensed by this package. Any declared experimental
compatibility patch is recorded by source and patch SHA256. Copyright/license
texts remain with each upstream checkout. HAZARDIA publication/distribution
license is not yet chosen; local implementation is not a release authorization.

Python/jsonschema/rasterio/GRASS and other runtime dependencies retain their
own licenses. Existing environment freezes are evidence, not a complete SBOM.
Public Copernicus/Sentinel/Open-Meteo inputs require their own attribution;
source records and acquisition timestamps are retained separately.

Publication requested by the owner on 2026-10-16 covers a curated source snapshot and reconstruction instructions; it does not add an implicit new HAZARDIA licence, publish runtime credentials, or grant redistribution rights for regional orthophotos. Small public-data snapshots retain separate notices in reproducibility/snapshots/ATTRIBUTION.md. Upstream engines are fetched separately with pinned archives and their own licence texts; the declared REFlEx patch remains subject to upstream obligations.


## WII: inventario e livello nazionali unici ·25ottobre2026

Decisione utente corrente: Abruzzo è un focus di acquisizione, non un modello separato. WII espone un solo livello nazionale, alimentato dalla vista canonica del medesimo SQLite per fonti istituzionali e crawler. Il vecchio ID rischio Abruzzo è alias del prodotto nazionale. Crawler limitato orario, controllo input30s, ricostruzione automatica sul singolo worker; errori/quote restano espliciti. Scala nazionale annualizzata comune; grigio per dati mancanti, verde non significa rischio assente. Le metriche storiche archiviate non validano la nuova fusione; gate scientifici/operativi invariati. Dettagli nel progetto WII: docs/UNIFIED-INVENTORY.md; report reports/wii-unified/. Nessuna modifica ai motori fisici. Questa decisione supera la precedente separazione del pilota.


## WII: verifica temporale unificata ·25ottobre2026

Valutazione autorizzata su fit<=2022/test2023–2025 esclusi dal fit: API provider GET/POST`/api/wii/validation/unified`, rapporto a pagina intera WII`/wii.html?view=validation`. Dettagli nel repository WII: reports/unified-validation/REPORT.md e protocollo immutabile.81,6%del supporto dei perimetri EFFIS nel20%Italia vs76,9%baseline50km; non veri punti d’innesco. Sulle coordinate native nel20%area regionale:49,6%Piemonte/48,8%Puglia/35,5%Abruzzo; accuratezza/completa rilevazione non qualificate, Abruzzo solo3blocchi annuali informativi. Preservare per-regione/per-anno e definizioni separate; anni già esaminati in ricerche precedenti, nessuna qualifica prospettica/operativa. Nuovi test non sostituiscono il livello di produzione né modificano la fisica. Prima implementazione/baseline corretta conservata e dichiarata, nessuna selezione di parametri sul test.

## New observation-layer sources ·26October2026
NASA FIRMS/NOAA-20 VIIRS recent public Europe CSV:free/open Earth-science data;credit NASA FIRMS/NOAA-20. This is thermal-anomaly observation data,not confirmed wildfire locations. No NASA webpage imagery or logos are redistributed here.
Arpa Piemonte hydrometric data:CC BY4.0,source attribution **Fonte: Arpa Piemonte - www.arpa.piemonte.it**;[legal terms](https://www.arpa.piemonte.it/note-legali). Normalization keeps observed heights,timestamps and gauge datum/missingness;spatial display is a derived consultation. No provider endorsement implied.
EFFIS observed perimeter source remains the existing native archive and its CC BY4.0 attribution;the optional client does not copy WII archives intoGit. Source links,coverage and qualifications are documented in reports/OBSERVATIONS-CLOSURE-20261026.md.
