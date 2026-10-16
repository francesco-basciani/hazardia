# Cosa puoi provare adesso

**La dashboard funziona sul tuo Mac attraverso la VM:** apri http://127.0.0.1:8080/. Il Mac visualizza la pagina; calcoli, dati e tutti i modelli sono nella stessa VM Linux.

Vedi l'Aquila su una vera immagine satellitare Sentinel-2. Sopra compaiono l'incendio calcolato da PROPAGATOR e gli allagamenti calcolati da HMC+REFlEx. Puoi cambiare le risorse del test, confrontare i piani e avviare una nuova esecuzione fisica. Per l'incendio puoi cambiare anche innesco, durata e seed. La [guida pratica](DASHBOARD-GUIDA.md) indica i passaggi.

Le mappe non sono un disegno e i simulatori non sono mock. **Gli scenari sono però condizionali e non calibrati:** non stiamo ricostruendo un incendio o un'alluvione realmente avvenuti il 13 luglio 2024. Alcuni parametri, persone e risorse sono creati per verificare il software.

Le due mappe possono avere la stessa acqua o lo stesso incendio: l'intervento attualmente confrontato è l'evacuazione sintetica. Cambia chi resta esposto, non spegne il fuoco e non elimina l'acqua. Il cursore incendio usa tempi di arrivo reali del modello; per l'alluvione mostriamo solo il massimo, senza inventare un filmato della piena.

## Cosa è stato verificato

I modelli girano davvero; il solver sceglie assegnazioni, un secondo componente ne ricontrolla i vincoli; i job hanno coda, stato, annullamento e retry. I test comprendono il guasto reale del solo processo alluvionale del test: l'incendio rimane utilizzabile. Le allerte e i guasti nel laboratorio sono etichettati come replay sintetici. Non partono messaggi o operazioni reali.

Sul piccolo caso fissato,30 decisioni su 30 hanno prodotto un piano verificato; il 95° percentile è circa 0,82 secondi. Le simulazioni fisiche richiedono più tempo. L'interfaccia è stata provata a 375/768/1440 pixel. Il registro ufficiale e i report riportano anche le prove fallite.

## Perché esistono ancora FAIL, BLOCKED e NOT RUN

- **FAIL**: una prova è stata eseguita e ha fallito il criterio. Alcuni sono errori software poi corretti, conservati per tracciabilità. Il carico grafico artificiale da 100.000 poligoni rimane un limite aperto; i test da 1.000/10.000 passano. Non significa che PROPAGATOR o HMC siano disinstallati.
- **BLOCKED**: il risultato complessivo non può essere dichiarato raggiunto con le evidenze attuali. Per validare le previsioni servono eventi corrispondenti, dati e parametri fisici qualificati, calibrazione e controllo esperto. Abbiamo acquisito osservazioni ufficiali 2020/2013 e un forecast reale corrente, ma non si possono usare per certificare scenari diversi del 2024.
- **NOT RUN**: quel controllo o parte del software non è stato completato/eseguito. Esempi: installazione indipendente su una seconda macchina, casi fisici grandi e studio principale delle alternative/ablazioni. Non vengono trasformati in PASS perché la pagina è visibile.

Il framework completo e il paper scientifico non sono dichiarati terminati. Rimangono anche parti software esplicitate nel registro, fra cui portafoglio di strategie e ottimizzazione generale delle capacità. La bozza di lavoro del paper e le evidenze sono mantenute dallo stesso Research Recorder; nessun articolo è stato inviato o pubblicato.

La macchina è performante e i limiti attuali della VM sono stati sufficienti per queste prove. Più RAM/CPU aiuterebbero carichi maggiori; non sostituiscono i dati mancanti o la validazione fisica. Non è stato necessario aumentare risorse o sostenere spese per rendere disponibile questa dashboard.
