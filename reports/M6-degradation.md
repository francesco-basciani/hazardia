# M6 — Continuità del servizio e preparazione

15 ottobre 2026. **PASS per le prove tecniche controllate; qualifica operativa, meteo reale integrata e ottimizzazione generale delle capacità BLOCKED/NOT RUN.** Run `m6-degradation-20261015T200034Z`, codice backend e5ec104, interfaccia corretta fino e1214e6. Reviewer: Codex self-check. Tutto il runtime nella VM esistente, senza nuove dipendenze o variazioni di risorse.

## Comportamenti verificati

L'API espone le sei capacità richieste e ne mostra stato, causa, confidenza e timestamp nel **laboratorio di replay sintetico**. Non è presentato come un monitor operativo dell'infrastruttura. I job reali e i loro errori sono riportati separatamente. Gli input sconosciuti di sicurezza impediscono una nuova proposta; le mappe storiche restano consultabili. La perdita del coordinamento toglie l'autorizzazione ai trasferimenti, la chiusura della strada impedisce assegnazioni e una risorsa persa viene esclusa. I vincoli sono nuovamente controllati dal verificatore indipendente.

Una revisione concorrente non aggiornata viene rifiutata. Le proposte precedenti diventano `STALE_CONTEXT` dopo un cambiamento del replay e non sono revisionabili come correnti. Il recupero sintetico crea un nuovo record positivo identificato e datato; non basta togliere un flag con una revisione vecchia. Questo verifica il meccanismo di recupero su evidenze create per il test, senza sostenere che sia stato riparato un servizio esterno.

`integration-third/results.json`: **12 gruppi PASS**, comprese 7 iniezioni, rifiuto del recupero obsoleto, preparazione, continuità HTTP, ciclo allerte e crash reale. I 14 test di decisione/adattamento e le precedenti 33+19 regressioni passano. I fallimenti iniziali sono conservati: fixture unitaria incompleta, margine del watchdog, guardia del nome processo troppo specifica, migrazione del vecchio replay e due difetti del test/UI. Correzioni senza allentare i criteri.

| Guasto controllato | Comportamento osservato | Punteggio diagnostico conservato |
|---|---|---:|
| Previsione alluvionale persa | Nuove proposte FLOOD bloccate; FIRE verificato | .85 |
| Sicurezza sconosciuta | SAFETY_UNVERIFIED, nessun piano | .35 |
| Fonte scaduta | STALE_PRODUCT, mappe storiche leggibili | .80 |
| Coordinamento perso | Solo assegnazioni autorizzate nell'area di origine | .75 |
| Solver perso | DEPENDENCY_UNAVAILABLE, quadro territoriale leggibile | .65 |
| Percorso chiuso | Piano vuoto; esposizione nominale congiunta 60 | .75 |
| Unità 1 persa | Nessuna assegnazione a quell'unità; esposizione nominale 32 | .75 |

Il punteggio usa pesi di ricerca `[3,2,2,1,1,1]` e valori NOMINAL=1, DEGRADED=.5, UNAVAILABLE=0. La baseline diagnostica senza guasti è già .85: quadro e previsioni non sono calibrati. Il punteggio della perdita alluvionale non cambia perché FORECASTING era già DEGRADED; la causa e l'insieme delle decisioni ammissibili cambiano. **Limite osservato della metrica**, non evidenza di assenza di danno. Lo zero del fail-stop è un riferimento definito analiticamente, non una campagna sperimentale di un secondo sistema. Questi pesi non sono una politica operativa e non dimostrano H1.

## Crash reale distinto dalle iniezioni

Job creato dal test `job-5ed4fe3ee3744ff689105e7c9cf0dc9b`: il test ha atteso RUNNING, verificato il suo `/proc/PID/cmdline` e l'ID univoco, poi inviato SIGKILL esclusivamente al suo gruppo `hazardia.adapters.pipeline`. Il controller lo ha marcato ERROR, `usable_product=false`, con manifest conservato. Una nuova proposta FIRE ha superato la verifica indipendente. Non sono stati terminati altri job/processi e non si dichiara una riuscita idraulica per il job interrotto. Il primo tentativo con una guardia nominale errata è stato fermato dalla guardia e il job di test annullato esplicitamente.

Le precedenti prove M3 con un job CIMA alluvionale in esecuzione, navigazione/calcolo/pan, annullamento e nuovo ID di retry restano la prova del percorso lungo della dashboard. Il retry è stato annullato; non viene chiamato una nuova simulazione riuscita.

## Preparazione e interfaccia

Con la stessa ammissibilità si confrontano arrivo a 480 s e preposizionamento a 120 s. Il beneficio è moltiplicato per `max(0,1−arrivo/600)`: effetto dichiaratamente sintetico, prodotti fisici immutati. Le perdite previste migliorano per costruzione del modello; non è un risultato empirico sul campo.

`browser-third/adaptation-browser.json`: ricalcolo dopo avanzamento, FIRE conservato/FLOOD bloccato, revisione disabilitata durante errore, ciclo OPEN→ACKNOWLEDGED→UPDATED→RESOLVED e controlli visibili a 375/768/1440 px PASS; nessun errore JavaScript. Il test precedente ha individuato il testo di un numero in virgola mobile che allargava una riga a 415 px su telefono: formattazione e layout corretti, valori esatti conservati nel JSON. Un altro tentativo correttamente fallito ha trovato una gara fra aggiornamento dello stato e calcolo: i controlli del replay ora sono serializzati e la prova attende la revisione visibile.

## Ripetizione e limiti

Nella VM, con servizio avviato e senza job utente attivi, usare un nuovo percorso:

```sh
../core-env/bin/python tests/integration/verify_m6.py \
  --runtime /home/hazardia/hazardia-runtime --run /tmp/NUOVO-m6-run
```

**La suite modifica il replay globale e termina il proprio job alluvionale di prova.** Non lanciarla durante prove dell'utente. Test del browser: `tests/browser/adaptation.cjs`; strumentazione del client Mac, backend e modelli sempre nella VM.

Il gestore attuale applica regole di continuità e misura capacità/perdita; non ottimizza una nuova funzione generale di utilità delle capacità. Meteo reale, efficacia locale, recupero di servizi esterni e validazione storica restano dipendenze aperte. Le capacità nominali sono nominali solo nel test software di ricerca. Nessuna azione operativa, notifica esterna o dispatch.
