# ADR-0011 — Campo di vento regionale per visualizzazione

Decisione16/10/2026, richiesta esplicita utente: particelle trasparenti con dati reali su tutto l’Abruzzo, piano gratuito e stessaVM.

Aggiungere un DTO interno regional_wind_display0.1.0 distinto dal weather0.3.0 usato per le simulazioni. Acquisire315punti/4giorni/2variabili con modelloICON-EU fisso e coordinate effettive conservate. Cache/quote condivise nellaVM e prenotazioni atomiche;315equivalenti per refresh, massimo8/giorno, TTL3h, cap2MiB e cache64MiB. Calcolare componenti eIDW4 nellaVM; bilineare e Canvas2D client sono solo rendering. Interpolare i componenti, non gli angoli. Nessuna estrapolazione fuori dal rettangolo e nessuna sostituzione delle forzanti CIMA.

Renderer proprio senza nuove dipendenze, massimo650particelle/30fps/DPR1.5, cancellazione trasparente, pausa e stop su navigazione/visibilità/layerOFF, frecce statiche per reduced-motion. EOXSentinel2024 opzionale e gratuito per uso non commerciale, con attribuzione, RAM8MiB e16MiBdownload, fornisce lo sfondo regionale; le ortofoto restano al dettaglio.

Alternative: duplicare il punto esistente non rappresenta un campo reale (rifiutato); iframe/serviziWindy commerciali aggiungono dipendenza/condizioni non necessarie (non adottati); ingestioneGRIBDWD diretta richiederebbe nuovi decoder e gestione dati più ampia (non eseguita). Nessuna misura comparativa prestazionale fra alternative.

Limiti: inizializzazione modello non esposta; forecast non osservazione, ricampionamento non calibrazione; interpolazioneIDW e griglia0.1° semplificano il campo; animazione amplificata non rappresenta trasporto fisico. Quota conservativa non garantisce disponibilità del provider. PolicyNC del servizio non equivale a una licenza commerciale. Modello/feed e licenze devono essere ricontrollati per future modifiche. Evidenze/negativi/comandi in VENTO-REGIONALE.md e CHECKLIST.md; non chiude le milestone scientifiche.
