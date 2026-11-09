# WII: progetto e repository indipendenti

Il sorgente di WII è mantenuto in un repository Git separato. Il pacchetto è `wii`; console, worker, API, test, dipendenze e asset Leaflet appartengono al nuovo progetto.

Nella VM il sorgente è `/home/hazardia/wii/app`. Avvio:

```sh
cd /home/hazardia/wii/app
PYTHONPATH=src /home/hazardia/hazardia-runtime/wii-env/bin/python -m wii --runtime /home/hazardia/hazardia-runtime serve --port 8081
```

[Console WII](http://127.0.0.1:8081/wii.html) · [Pilota Abruzzo](http://127.0.0.1:8081/wii.html?pilot=abruzzo).

Il database e gli archivi restano nelle posizioni originali; il nome storico della directory dati non è una dipendenza dal servizio HAZARDIA. Il confronto di29tabelle (righe,ROWID,BLOB,schema) e391file è identico prima/dopo. Nessuna conversione di ID o schemi persistiti. Un solo proprietario del worker, stessi limiti e qualificazioni scientifiche.

HAZARDIA conserva soltanto il client API e il livello cartografico. Disabilitarli non arresta WII. La documentazione corrente del progetto è [README WII](../../WII/README.md); le precedenti guide sono conservate in `WII/docs/history/`.
