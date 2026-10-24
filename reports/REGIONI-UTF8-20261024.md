# Nomi regionali UTF-8 —24ottobre2026

Run `region-utf8-20261024`, codice base `72291fd`. Causa verificata nella VM: DBF Istat2026 senza fileCPG; apertura Fiona predefinita interpreta UTF-8 come Latin-1. Lettura comparata predefinita/UTF-8/ISO-8859-1 eseguita: solo UTF-8 conserva i nomi bilingui corretti.

Correzione `scripts/prepare_region_boundaries.py`: apertura con encoding=UTF-8, metadato della codifica nel prodotto. Rigenerazione da archivio già verificato SHA256 `b011a590656c3a3ebc297fba80726a376aa843b6f164641cf6a4a990021a81d6`, nessuna acquisizione. Raw Istat e copia dell’asset precedente conservati nel runVM.

Comando: `/home/hazardia/m0/reflex-env/bin/python scripts/prepare_region_boundaries.py --runtime /home/hazardia/hazardia-runtime` nella VM. PASS verifica esatta20geometrie/codici/label-point invariati, esattamente2nomi cambiati:

- Valle d’Aosta/Vallée d’Aoste (apostrofo ASCII originario mantenuto nell’asset).
- Trentino-Alto Adige/Südtirol.

PASS nessun marcatore mojibake nei20nomi. PASS browser in-app: entrambi i nomi visibili nella mappa del NordItalia; URL dell’asset versionato per evitare la vecchia cache. Output SHA256 `fb31b1e6ed4a2f410a88f437e2f1d225b82bf4e98c4b477836195661c1c1ed1f`. Evidenze `reports/region-utf8/verification.json`, screenshot `delivery.png`; run completo nella VM. Reviewer Codex.

Il comando ha emesso warning preesistenti PROJ (directory dati e sintassi init deprecata); nessun errore, geometrie identiche verificate. NOT RUN nuove simulazioni/benchmark, fuori ambito. Nessuna sostituzione generalizzata di accenti o traslitterazione dei nomi esteri.
