# ADR-0002 — Unico ambiente di esecuzione nella VM Linux

Data: 15 ottobre2026. **ACCEPTED per collocazione del runtime, su istruzione esplicita dell'utente.** Non autorizza M1 né modifica i modelli, i limiti della VM o i criteri scientifici.

## Decisione

Tutti i componenti eseguibili di HAZARDIA risiedono e girano sulla stessa macchina Linux: inizialmente la VM UTM `HAZARDIA-M0-ARM64`. Comprende acquisizione/cache dati, preparazione geospaziale, PROPAGATOR, HMC, REFlEx, validazione numerica, produzione delle mappe e, nelle milestone autorizzate successive, backend, scheduler, decision engine/solver e build/servizio della dashboard.

Il Mac ospita UTM e serve da client di sviluppo, controllo e visualizzazione. File possono essere copiati sul Mac come documentazione/evidenza; non sono input runtime obbligatori fuori dalla VM. Nessuna dipendenza eseguibile da `.m0-venv`, font macOS, cartelle condivise o servizi scientifici sul Mac. Un browser client può mostrare risultati o pagine servite dalla VM; i servizi e i calcoli restano nella VM. La dashboard non è ancora implementata.

## Isolamento all'interno della stessa macchina

Unica VM non significa unico processo o unico ambiente Python. Conservare ambienti separati per fire (Python3.12/Numba0.62) e flood (Python3.10/GRASS/GDAL legacy), processi isolati, watchdog e file con provenienza. Questo evita conflitti di dipendenze e mantiene contenimento dei guasti e sostituibilità dei motori. Non richiede un secondo computer o una VM per ogni hazard.

Risorse attualmente autorizzate invariate: 4vCPU,8GiBRAM,19GiBdisco principale,5GiBdownload cumulativi. Le successive misure devono distinguere il carico totale di questa VM dalle prestazioni del client grafico, senza usare implicitamente tutti i core/RAM del Mac per i simulatori.

## Conseguenze e alternative

Il precedente split Mac/Linux resta evidenza storica di portabilità e confronto, non topologia applicativa da adottare. L'alternativa backend sul Mac + flood nella VM è respinta dall'utente. Nessun requisito multi-hazard, solver-pluggable, robustezza, deadline60s o sicurezza è ridotto. Su un futuro server Linux la stessa topologia deve funzionare senza dipendenza dal Mac; eventuali distribuzioni ulteriori richiedono decisione separata.

## Verifica M0

Run `m0-unified-vm-20261015T150415Z`: cache originale trasferita e verificata, accesso HTTP dalla VM, preprocessing, simulazioni, lettori e rendering da eseguire/verificare esclusivamente nel guest. Esiti effettivi nel report `M0-unified-vm.md` e in CHECKLIST; questo ADR non dichiara esecuzioni non ancora controllate. Nessuna funzionalità di M1 autorizzata per effetto di questa decisione.
