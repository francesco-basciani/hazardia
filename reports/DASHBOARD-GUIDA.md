# HAZARDIA — Guida per le prime prove

Apri **http://127.0.0.1:8080/** sul Mac. Il servizio, i dati, HiGHS e tutti e tre i simulatori CIMA sono nella VM Linux **HAZARDIA-M0-ARM64**; il browser è il client. Non occorrono account o servizi a pagamento. L'accesso è locale tramite tunnel SSH.

## Una prova di cinque minuti

1. Lascia **Alluvione · HMC + REFlEx** e premi **Calcola confronto**. Le due mappe usano la stessa immagine Sentinel-2 e lo stesso prodotto fisico. Il piano modifica i gruppi esposti e le assegnazioni sintetiche, non l'acqua del raster.
2. Cambia il numero delle unità. Togli **Percorso di accesso aperto**, ricalcola e osserva le assegnazioni: la strada chiusa impedisce gli interventi. Riattiva il percorso.
3. Scegli **Incendio · PROPAGATOR**. Il cursore del tempo usa i primi arrivi prodotti realmente dal simulatore. Per l'alluvione mostriamo il massimo sull'intervallo: non disponiamo di una serie temporale allagata da riprodurre.
4. Prova **Incendio + alluvione**, quattro unità e trasferimenti autorizzati. Disattiva i trasferimenti e ricalcola. Le due aree e le risorse sono dichiarate sintetiche.
5. In **Continuità e allerte · laboratorio**, applica il guasto di prova della previsione alluvionale: l'incendio resta calcolabile; l'alluvione viene bloccata. **Nuovo snapshot sintetico disponibile** fornisce una nuova evidenza positiva del test, senza pretendere di riparare un guasto reale.
6. Premi **Riavvia replay allerte**, poi **Prossima emissione di prova**. Puoi registrare la presa visione, aggiornare o risolvere l'allerta. Queste emissioni sono create per verificare il software e non sono previsioni meteo reali.

**Avanza 10 minuti e ricalcola** conserva i progressi/consumi del piano precedente secondo un modello sintetico lineare. Le missioni da dieci minuti possono risultare già completate. Se il prodotto fisico esce dal suo intervallo di validità, il sistema deve fermare il ricalcolo: non estende artificialmente la previsione.

Le opzioni di preposizionamento confrontano arrivo a2/8minuti con beneficio sintetico `beneficio × (1−arrivo/600s)`. Non dimostrano l'efficacia reale di una strategia.

## Avviare davvero un modello

Apri **03 · Nuova simulazione fisica**. Puoi scegliere PROPAGATOR o HMC+REFlEx. Per l'incendio imposta seed, durata e cella d'innesco; per l'alluvione il caso attuale mantiene l'impulso di pioggia dimostrativo di sei ore. **Avvia simulazione** inserisce un job nella VM; lo stato appare in **Job nella VM**. Un solo job fisico alla volta, coda limitata. Le mappe rimangono navigabili. **Annulla** rende inutilizzabili eventuali output parziali; **Riprova** crea un nuovo job con collegamento al precedente. Dopo il successo viene aggiunto il nuovo prodotto all'elenco.

I modelli impiegano da decine di secondi a minuti sul caso attuale; il limite sperimentale di60secondi riguarda la decisione su prodotti già disponibili. Non promette una simulazione fisica completa entro60secondi.

**Esporta risultato** scarica il JSON della proposta, inclusi vincoli, tempi e contesto. **Registra revisione di ricerca** salva una presa visione locale. Non parte nessun mezzo, messaggio o azione operativa.

## Cosa è reale e cosa è ancora sperimentale

Reali: territorio/coordinate dell'Aquila, pixel Sentinel-2 del13luglio2024, DSM Copernicus, meteo ERA5 retrospettivo, esecuzioni PROPAGATOR/HMC/REFlEx, raster/tempi del modello, ottimizzazione e verifica. REFlEx usa una copia di compatibilità con due modifiche documentate; non è dichiarato upstream invariato.

Sintetici/non calibrati: innesco e combustibile, umidità, impulso di pioggia e Q0, esposizione e disponibilità delle risorse, efficacia dell'evacuazione, aree di competenza del test e replay delle allerte. I punti esposti sono controlli positivi su celle del modello, non un censimento. L'immagine del2024 non rappresenta necessariamente un incendio o un'alluvione avvenuti quel giorno. La vista è una simulazione condizionale su territorio reale.

Mancano la validazione storica indipendente, un bacino idrologico completo e calibrato, inventari operativi e una catena di previsioni reali temporalmente coerente. La dashboard serve alle prove di ricerca; non è un sistema di allertamento operativo certificato.

## Se riavvii Mac o VM

Dal Terminale del Mac, nella cartella del progetto:

```sh
cd /Users/basciani/Sviluppo/Workspaces/CODEX/PROGETTI/HAZARDIA
/Applications/UTM.app/Contents/MacOS/utmctl list
# Solo se la VM è ferma:
/Applications/UTM.app/Contents/MacOS/utmctl start HAZARDIA-M0-ARM64
ssh -i .m0-runtime/ssh-key -p 22227 -o UserKnownHostsFile=.m0-runtime/known_hosts hazardia@127.0.0.1
```

Nella VM:

```sh
cd /home/hazardia/hazardia-runtime/app
../core-env/bin/python scripts/web_service.py start --runtime /home/hazardia/hazardia-runtime
```

In un altro Terminale del Mac, dalla stessa cartella del progetto, se il tunnel non esiste già:

```sh
ssh -i .m0-runtime/ssh-key -p 22227 \
  -o UserKnownHostsFile=.m0-runtime/known_hosts \
  -o ExitOnForwardFailure=yes -N \
  -L 127.0.0.1:8080:127.0.0.1:8080 hazardia@127.0.0.1
```

Lascia aperto quel Terminale e visita l'indirizzo della dashboard. Se la porta8080 è già occupata, non terminare processi sconosciuti: verifica se la pagina è già raggiungibile. Non rendere pubblico il listener.

Il servizio scrive `/home/hazardia/hazardia-runtime/web-server.log`. L'utility `web_service.py stop` arresta solo il proprio processo; non usarla durante una simulazione. Il riavvio classifica esplicitamente i job interrotti, senza presentarli come riusciti. La chiave SSH resta locale e non deve essere inclusa nei pacchetti di ricerca.

Per un riepilogo senza dettagli tecnici, leggi [lo stato in parole semplici](STATO-IN-PAROLE-SEMPLICI.md). Il registro completo resta [CHECKLIST.md](../CHECKLIST.md).

Il cursore media/peggiore non deve necessariamente cambiare il piano: sul caso fissato per il benchmark i due estremi hanno scelto le stesse assegnazioni. Questo è un risultato registrato, non una promessa di vantaggio della robustezza su ogni input.


Mappe aggiornate: scegli **Ortofoto Abruzzo · 20 cm · online**, cerca `L'Aquila` oppure `42.34892, 13.397967` e premi **Vai**. **Mappe più grandi** amplia la vista, un clic apre coordinate e riferimenti vicini. Per tornare ai prodotti dei simulatori premi **Centra area**. **Sentinel-2 · 10 m · offline** conserva lo sfondo locale senza rete. Date, fonti, limiti e verifiche in [MAPPE-DETTAGLIO.md](MAPPE-DETTAGLIO.md).


## Esempi Abruzzo pronti per le prove — 16 ottobre 2026
Sono state aperte due schede della dashboard, entrambe sulle ortofoto regionali e con due unità disponibili:

- **Incendio PROPAGATOR**, zona dell’Aquila vicina a Contrada Bernardi, punto di vista `42.35013, 13.38018`, zoom17; prodotto `job-12d0a90a7e01488aa6ffaf3b95523606`,29celle positive,60minuti. Il cursore consente di osservare i tempi del simulatore.
- **Alluvione HMC + REFlEx**, area dell’Aquila vicina al riferimento Pile, punto di vista `42.36417, 13.37694`, zoom17; prodotto `job-47a95533cf874b26ab06c512395274c1`,1220celle positive, profondità massima del prodotto≈0,179m su6ore. Il cursore è disabilitato: non esiste una sequenza temporale allagata in questo caso.

I nomi sono riferimenti geografici vicini, non delimitazioni amministrative. Entrambi gli esempi mostrano **30→17 persone sintetiche esposte**, con due assegnamenti verificati. Sono esecuzioni reali dei modelli già disponibili, con innesco/pioggia/Q0 e risorse/esposizione/effetti sintetici o non calibrati; non ricostruzioni validate di disastri storici. I due piani simulano evacuazione: l’estensione fisica arancione/blu resta invariata tra A e B.

Per provare: cambia **Unità disponibili** e premi **Calcola confronto**; chiudi **Percorso di accesso aperto** e ricalcola per vedere il vincolo; riaprilo. Nell’incendio usa il cursore del tempo. **Centra area** torna all’intera griglia, per un dettaglio locale usa le coordinate sopra. Le due schede restano aperte; ricaricando la pagina le impostazioni tornano ai valori iniziali e si possono reimpostare dai controlli. Tutto il servizio e i calcoli restano nella VM.

Verifica manuale UI/API PASS, run `abruzzo-showcase-20261015T234538Z`, sorgente `d88c78f`;16ottobreEurope/Berlin, acquisizione UTC15ottobre23:48. ProvaVM `experiments/runs/abruzzo-showcase-20261015T234538Z/showcase-proof.json`, stato visibile e screenshot in `reports/dashboard-evidence/abruzzo-examples-20261016/`. Nessuna modifica al framework, nessuna nuova simulazione fisica o conclusione scientifica.


## Confronto che cambia la fisica e dura giorni
Apri http://127.0.0.1:8080/physical-fire.html oppure il link **Apri il confronto fisico incendio su1–3giorni** nella dashboard. La nuova vista mostra raster reali PROPAGATOR con/senza fascia tagliafuoco ipotetica,72ore completate e selezione1/2/3giorni. Usa **Ora simulata**, **Riproduci**, **Inquadra estensioni** e **Vicino all’intervento**. È un esperimento separato dal piano di evacuazione: non misura l’efficacia di un dato numero di squadre. Parametri e limiti, inclusa sensibilità del modello agli eventi, in [INTERVENTI-FISICI-E-GIORNI.md](INTERVENTI-FISICI-E-GIORNI.md). Alluvioni con mitigazione fisica e giorni non ancora implementate: scelta dell’intervento e integrazione idraulica sono il prossimo punto aperto.

## Aggiornamento interfaccia — 16 ottobre 2026
La pagina iniziale ora mette al centro una mappa singola. «Affianca A / B» apre il confronto; «Risultati» contiene numeri e piano, «Dati e fonti» provenienza e laboratorio avanzato, «Guida» spiega i termini. Su telefono apri «Scenario e interventi» per i comandi laterali. Nuovi strumenti: misura, area, nota, viste e casi salvati nella VM, esportazione annotazioni GeoJSON. Disegni e note non modificano i simulatori. I casi salvati richiedono un nuovo calcolo del piano; confronto fisico incendio resta nell’apposita pagina su 1–3 giorni. Dettagli, limiti e distanza dai riferimenti commerciali: [UI-CONTROL-ROOM.md](UI-CONTROL-ROOM.md).
