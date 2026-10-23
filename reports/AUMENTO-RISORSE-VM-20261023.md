# Aumento delle risorse della VM —23 ottobre 2026

La VM è stata riavviata con **6 vCPU e 16 GiB di RAM**, rispetto ai precedenti4vCPU/8GiB. La dashboard è nuovamente raggiungibile su http://127.0.0.1:8080/. Il disco resta19GiB: l’obiettivo40GiB è **BLOCKED** dallo spazio fisico sul Mac, circa13GiB liberi. Non sono stati cancellati dati.

Run `vm-upgrade-20261023`, commit di partenza `408966f1a3d62c057f6520488b1df1ba982af804` con modifiche documentali preesistenti conservate. Reviewer Codex self-check.

| Verifica | Esito | Evidenza |
|---|---|---|
| Nessun job attivo prima dell’arresto | PASS |95job terminali |
| Arresto ordinato | PASS | servizio fermato; `sudo -n shutdown -h now`; `utmctl status` stopped |
| Salvataggio CPU/RAM UTM | PASS | Sistema:16384MiB,6core, Salva; screenshot locale |
| Risorse riconosciute da Linux | PASS | `nproc`:6; `free -b`:16.740.196.352byte utilizzabili |
| Servizio VM e tunnel Mac | PASS | restart web_service.py, SSH loopback8080, HTTP200 |
| Integrità configurazioni e job | PASS |8file workspace/casi SHA256 identici;95stati invariati |
| Regressione software | PASS |68test core/web,0errori,in0,417s |
| Espansione disco40GiB | BLOCKED | host13GiB liberi; filesystem guest19.584.548.864byte,3.929.096.192liberi |
| Benchmark fisico prima/dopo | NOT RUN | nessun miglioramento prestazionale quantificato |
| Backup completo immagine disco | NOT RUN | nessuna copia del disco; file configurazioni/scenari verificati |

Le5ERROR e8CANCELLED sono esiti preesistenti, invariati dopo il riavvio. Nessun job scientifico eseguito o sostituito.

## Procedura e ripetibilità

Misure host: `sysctl -n hw.memsize hw.ncpu`, `memory_pressure`, `df -h /System/Volumes/Data`. Mac M4Pro,14core,48GiB RAM. UTM controllato tramite `/Applications/UTM.app/Contents/MacOS/utmctl`. Lettura diretta del bundle negata da macOS: nessuna modifica ai permessi; usata l’interfaccia ufficiale UTM, VM arrestata → Modifica → Sistema → Memoria16384MiB → Core6 → Salva → Avvia. Architettura e rete conservate. Per ripristinare la vecchia configurazione: arrestare ordinatamente e impostare8192MiB/4core nello stesso pannello.

Nel guest: `nproc`, `free -b`, `df -B1 /`; avvio da `~/hazardia-runtime/app` con `PYTHONPATH=src ../core-env/bin/python scripts/web_service.py start --runtime /home/hazardia/hazardia-runtime`. Tunnel SSH bindato a127.0.0.1:8080, portSSH22227. Nessuna esposizione pubblica.

Regressione: `PYTHONPATH=src:tests/unit:tests/web ../core-env/bin/python -m unittest test_traffic test_recent_imagery test_consultation_cache test_radar_service test_map_navigation test_maps test_regional_satellite test_osm_tiles test_map_weather test_bootstrap test_fire_workspace test_fire_cases`.

Preregistrazione, `before.json`, `after.json`, `tests.log`, AX prima della modifica e screenshot sono conservati in `experiments/runs/vm-upgrade-20261023/`; misure guest in `~/hazardia-runtime/runs/vm-upgrade-20261023/`. Primo comando d’audit fallito per nome colonna `status`, corretto in `state` prima di qualsiasi arresto. Nessuna modifica al database.

## Limiti e passo successivo

Il nuovo ambiente di riferimento è6vCPU/16GiB/disco19GiB. Le misure precedenti su4vCPU/8GiB restano immutate: maggiore capacità assegnata non prova un’accelerazione della dashboard, il cui rendering avviene nel browser. Non aumentati automaticamente worker, limiti cache o acquisizioni. M5–M7 scientifici restano BLOCKED.

Per ottenere40GiB realmente utilizzabili occorre liberare almeno la differenza di21GiB sul Mac, oltre a mantenere un margine per macOS, oppure scegliere uno spazio esterno adeguato. L’ampliamento del disco sarà seguito dalla verifica di partizione/filesystem; non eseguito ora per non promettere capacità priva di spazio fisico. Nessun dato cancellato o trasferito altrove.
