# Riproduzione fluida e stato del ricalcolo

Run `smooth-resume-20261018`,18ottobre2026. Base `02143bd00cc50087c7432dc95c68a7016c8d0df2`+dirty; SHA consegna Git/PUBLICATION.json. Reviewer Codex self-check. Runtime e simulazioni nell’unica VM4vCPU/8GiB/19GiB; Mac solo editing, QA browser e copia evidenze. Nessuna installazione, nuovo dataset o nuovo job fisico avviato dall’agente.

## Diagnosi

Il messaggio generico “calcolo nella VM in corso” nascondeva una sequenza di quattro job reali avviati dall’utente. Osservati RUNNING/SUCCEEDED, poi tutti SUCCEEDED; identificativi e configurazioni nel raw privato. Nessuna evidenza di deadlock del motore in questi job. Il ricalcolo completo impiega minuti; non è esecuzione interattiva del solver dal punto di pausa.

Un secondo limite effettivo: intenzione di ripresa e coda vivevano soltanto nelle variabili JS. Aggiornare la pagina perdeva quel contesto pur conservando i job nella VM. Ora sessionStorage conserva ora, selezione, coda e intenzione di ripresa per lo stesso tab/caso, con firme degli input. La configurazione scientifica e i job restano salvati nella VM. Configurazioni incompatibili non recuperano il contesto vecchio. Copre reload dopo salvataggio; NON garantisce recupero transazionale da crash durante la finestra fra richiesta accettata e persistenza, né coordinamento di più tab esecutori.

Nel caso dell’utente la crescita del fuoco era inoltre già terminata: primo campione con `queued_front_events=0` a5,25h/4,25h/3,75h/5,25h nei quattro scenari, tutti con288frame fino a72h. Il primo contiene effettivamente il Canadair configurato a2190min (+36h30), effetto `fuel_removal` conservato dalla vecchia configurazione. Non si deve inventare una nuova crescita per mostrare un intervento tardivo. I fronti esauriti sono ora indicati anche nelle intestazioni delle mappe. È un esito del modello su input non calibrati, non prova che il rogo reale si spenga in quel momento. Il nome utente “Senza interventi” è conservato anche se contiene una risorsa; non viene riclassificato automaticamente come baseline.

## Correzioni e qualificazione

PASS: replay con requestAnimationFrame e dissolvenza continua fra PNG nativi adiacenti di15min. Al campione esatto si usa il PNG originale; i valori numerici restano quelli dell’ultimo campione nativo, identificato nella tabella. Nessun array/probabilità scientifica viene riscritto o interpolato. Dissolvenza iniziale da trasparente, nessuna estrapolazione oltre l’orizzonte o attraverso gap. La dissolvenza non è una nuova predizione fisica, né uno spegnimento/cancellazione del passato. Riduzione movimento rispettata.

PASS: tempo frazionario condiviso con il meteo, particelle non ricreate ad ogni frame grafico, pausa al tempo visibile e pulsanti precedente/successivo sui campioni nativi. Attesa esplicita dei PNG di tutte le finestre; pausa durante caricamento mancante resta in pausa e conserva l’istante. Dati meteorologici e forzanti native invariati.

PASS: avanzamento ricavato dalle righe reali `HOUR … CELLS …` del log nativo, leggendo al massimo16KiB. Distinti coda, inizializzazione, ore simulate, produzione mappe e successo finale verificato dal job store. Nessun ETA inventato;72ore nel log non significa job SUCCEEDED. Il messaggio distingue ore calcolate e ora ferma del replay, conteggio scenari completati e ripresa automatica. Poll ogni1,5s secondo meccanismo esistente.

## Verifiche riproducibili

- PASS5test stdlib nella VM: `PYTHONPATH=src /home/hazardia/hazardia-runtime/core-env/bin/python -m unittest discover -s tests/unit -p test_fire_progress.py -v`.
- PASS23check `tests/browser/smooth-resume.cjs`: continuità, endpoint originali, pausa, validità meteo, gap, riduzione movimento, PNG mancante, ricalcolo/ricarica/coda una sola volta/ripresa a36h30, responsive e3axe.
- PASS23authoring +14midrun-edit +22scenario-clock: totale82check browser, includono6axe a375/768/1440 senza violazioni. Browser in verification.json. I test di ricalcolo usano risposte di trasporto controllate e input/PNG reali congelati: NON equivalgono a nuove prove fisiche.
- PASS osservazione UI IAB:4risultati reali, avvio da36h30, tempo/meteo in avanzamento, pausa e reload con posizione conservata. Nessun nuovo calcolo da questa verifica.
- PASS input dei4scenari principali identici prima/dopo; revisioni91→98 per il completamento della coda dell’utente. Caso FonteVetica rev20 identico. Non sovrascritti scenari o interventi.
- PASS syntax JS/diff whitespace. Un riavvio backend dopo verifica coda vuota; nessun job interrotto.

Comandi browser dal repository: impostare `HAZARDIA_PLAYWRIGHT_PATH`, `HAZARDIA_BROWSER_EXECUTABLE`, `HAZARDIA_AXE_PATH` e per authoring `HAZARDIA_FIELD_FIXTURE`, poi eseguire `node tests/browser/smooth-resume.cjs <directory-nuova>` (analogamente scenario-authoring.cjs, midrun-edit.cjs, scenario-clock.cjs). Node/Chrome sono gli strumenti QA sul Mac; il servizio/worker resta VM. Fixture meteo proveniente dal run dynamic-fire-domain-20261018; nessun download necessario al replay dei PNG.

FAIL precedente riprodotto con JS congelato: soltanto aggiornamenti discreti, nessuna dissolvenza intermedia. FAIL intermedi conservati: harness attendeva visibilità di uno stato salvato in pannello chiuso; PNG già in cache impediva la prova di mancanza; mancava aria-busy durante attesa al confine del campione, corretto; confronto float esatto di un vecchio test, corretto a tolleranza1e-8h e attivazione al minuto arrotondato già previsto dal contratto. Raw immutabili per ciascun tentativo, nessuna cancellazione dei negativi.

Misura descrittiva: 42 ore visuali distinte in1,5s su2mappe del fixture finale. Non è un benchmark FPS generale/p95 né uno studio utente. NOT RUN nuovo carico30/p95, soak, devicefisici, checkpoint/streaming, ensemble/held-out e nuova idrologia. BLOCKED qualificazione fuel/moisture/interventi/logistica/skill e gate completiM5–M7 invariati. Prossimo incremento scientifico: qualificare gli interventi con ensemble e vincoli logistici, come nel piano originale.

Evidenza pubblicabile: `reports/smooth-resume/verification.json`. Raw privati: `experiments/runs/smooth-resume-20261018/` (snapshot, negativi/finali, log e screenshot). Nessuna efficacia operativa dedotta dalla fluidità grafica.
