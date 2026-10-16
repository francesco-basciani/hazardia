# ADR-0008 — Adattamento esplicito di ricerca e confine della qualifica

15 ottobre 2026, autorizzazione continua originale M0–M7. Nessuna sostituzione di simulatore o estensione ai sette domini futuri.

Decisione: aggiungere un supervisore monotono esterno al solver/verificatore, progressi sintetici delle missioni e un registro immutabile del replay di disponibilità/allerte. SQLite continua a gestire i job; piccoli record JSON esclusivi registrano le revisioni di ricerca. Nessun nuovo servizio o framework di agenti. Le proposte di un contesto superato sono rese non correnti prima della revisione umana.

Alternative: non usare ERA5 come forecast emesso in anticipo; non associare il meteo corrente 2026 a raster del 2024; non riempire con zero variabili mancanti; non dichiarare riparato un servizio reale togliendo un guasto sintetico. Il replay controllato permette di verificare il software conservando questi blocchi scientifici. Una previsione corrente reale MET Norway è stata acquisita separatamente e valutata; la sua integrazione fisica non viene inventata.

La tabella delle sei capacità è diagnostica, con regole conservative su ammissibilità e mantenimento delle viste storiche. Non si dichiara implementata una ricerca ottima di tutte le combinazioni di capacità o una politica di protezione civile. I valori/tempi/effetti della preparazione sono parametri del test, separati dalla qualifica dei prodotti fisici.

Conseguenze: dashboard verificabile e utilizzabile per prove locali; M5/M6 hanno evidenze tecniche ma il gate completo mantiene i blocchi di meteo/evidenza fisica. Il test di 0,8 s ha richiesto un margine di chiusura maggiore; i failure raw restano conservati. La propagazione di un crash reale verso altri hazard è stata verificata separatamente dalle iniezioni simboliche. Il prossimo rilascio scientifico deve risolvere le dipendenze storiche e i limiti M7, senza cambiare retroattivamente questi risultati.
