# Aggiorna e riprendi: verifica e correzione

Run `recalculate-resume-20261018`,18ottobre2026, base b52021b766bca79ae5fe3c86790cfa744354a82c con modifiche. Revisore: stesso agente Codex; SHA finale Git/PUBLICATION.json.

## Difetti riprodotti

FAIL prima della correzione, PASS dopo: alternativa senza inneschi impediva il ricalcolo dell’intero gruppo; diverso ordine delle proprietà JSON fra input e copia salvata poteva rendere sporco un risultato invariato; prova dell’intervento nell’ispettore confrontava testo JSON e indicava modificata una squadra realmente consumata. Negativi conservati in ui-before/verification.json nel run privato. Non è possibile attribuire con certezza tutti i sintomi riferiti dall’utente a una sola causa senza lo stato transitorio originale.

La prova nativa prima della modifica, senza bozza vuota, ha invece completato entrambi i job e ripreso il tempo: non è stato riprodotto un deadlock generale del solver. Le etichette rimanevano Aggiorna e riprendi durante il calcolo, rendendo l’attesa poco chiara.

## Correzione

Confronto canonico dei valori, compatibile con firme di sessione precedenti; confronto canonico anche della squadra realmente consumata. Bozze senza inneschi restano sulla mappa ma non bloccano avvio e ripresa degli scenari validi. Il nominale invariato viene riutilizzato solo se gli eventi consumati, normalizzati con gli eventi orari, coincidono con il calendario comune richiesto. Un nuovo intervento a un minuto non già presente richiede ancora il ricalcolo dei riferimenti, evitando confronti con calendari numerici diversi. Nessun riutilizzo di input cambiati.

Pulsante disabilitato Calcolo in corso durante preparazione/coda/motore/prodotti; progresso reale conservato. Errori mostrati accanto alla timeline; interrompono i restanti invii e non avviano il replay. La ripresa automatica richiede tutti gli scenari eseguibili coerenti con i rispettivi input. Modifiche successive durante l’attesa non vengono presentate come già calcolate. Il solver ricalcola l’orizzonte completo: nessun checkpoint fisico introdotto.

## Prove e comandi

PASS114controlli browser, di cui12axe a375/768/1440px. Suite recalculate-resume16, fire-recalculate22, midrun-edit14, smooth-resume23, nominal-layout25, forecast-profile14. Trasporti workspace/calcolo delle regressioni isolati; risultati originali letti soltanto. Nuovo test distingue chiaramente fixture di trasporto da verifica nativa.

```sh
node tests/browser/recalculate-resume.cjs <nuova-directory-output>
node tests/browser/fire-recalculate.cjs <nuova-directory-output>
node tests/browser/midrun-edit.cjs <nuova-directory-output>
node tests/browser/smooth-resume.cjs <nuova-directory-output>
node tests/browser/nominal-layout.cjs <nuova-directory-output>
node tests/browser/forecast-profile.cjs <nuova-directory-output>
# Questo comando avvia davvero il motore nella VM esistente; non salva modifiche utente.
node tests/browser/native-recalculate-resume.cjs <percorso-output.json>
```

Usare HAZARDIA_PLAYWRIGHT_PATH, HAZARDIA_BROWSER_EXECUTABLE e HAZARDIA_AXE_PATH come nei report delle suite precedenti; Chrome/Playwright sul Mac soltanto per QA, servizio e motore nella VM Linux su8080. Il test nativo richiede il caso forecast-fonte-vetica-20261018 preparato con i due scenari originali.

PASS prova reale dopo correzione: modifica del Canadair da60 a1440min, replay fermo a24h durante il calcolo; una richiesta nativa, nominale originale riutilizzato, risultato aggiornato pulito e avanzamento automatico fino a24h15min. Nessun errore JS, workspace reale del caso invariata rev1. Era presente anche lavoro utente nella coda: attesa osservata, nessuna cancellazione/interferenza.

Job prima: job-07a4d036ed8f44998727f8ea7290d446 (nominale), job-db69b0cb71ee476aa13a6850d6a766d1 (Canadair24h). Job dopo: job-a15cff67f4ce4d3581f3d06dfcc3f802. Tutti72h e8realizzazioni, medesima previsione congelata e inizializzazione168h. I due job modificati hanno griglia/opzioni/input asset identici; ciascuno consuma azione a24h su81celle moisture. PASS15asset e1782artefatti per SHA nei tre job. È una verifica del flusso e del consumo degli input, non prova di efficacia del mezzo o nuove repliche indipendenti per skill.

Sommario pubblicabile reports/recalculate-resume/verification.json; raw privati experiments/runs/recalculate-resume-20261018 (log, negativi, workspace isolate e audit nativo). Runtime esistente4vCPU/8GiBRAM/19GiBdisco,6,2GiB liberi; nessuna installazione o restart backend. NOT RUN nuovi benchmark p95/FPS, weather ensemble, held-out o checkpoint; BLOCKED validazione di efficacia/logistica/fuel/skill e gate scientifici completi M5–M7.
