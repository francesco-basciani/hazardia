# Innesco, interventi nativi, vento nel tempo e degradazione

Run `fire-studio-20261016`; base host `0870880ccb91b3ad7619624fd80361e8ffbc45eb` + modifiche con checksum in `reports/fire-studio/verification.json`. Reviewer Codex self-check. Esperimenti ingegneristici iterativi, non valutazione H1–H3. Fonte normativa: richiesta esplicita dell'utente su innesco, categorie/posizioni/tempi delle squadre, meteo e graceful degradation.

## Cosa si può provare

**PASS** nuova voce «Innesco e squadre», pagina `/fire-studio.html`: scegli l'innesco con clic, categoria, inizio dell'intervento e due estremi della sua linea d'azione. Fino a8 linee, lunghezza1–2000m, nel terreno preparato; nessuna geometria fuori copertura accettata. A è controllo senza interventi, B usa linee e variazioni del vento dell'utente. Esecuzioni native distinte, snapshot immutabili, stesso seed,2realizzazioni e calendario di eventi. Nessuna riduzione disegnata a posteriori. I risultati orari si confrontano sulle mappe satellitari e si riaprono tramite gli identificativi `?a=job-…&b=job-…`. Lo storico nella pagina conserva i confronti della sessione; i job immutabili restano nella VM dopo reload.

**PASS** categorie collegate alle classi originali PROPAGATOR `WaterlineAction`, `CanadairAction`, `HelicopterAction`, `HeavyAction`. Squadra a terra=linea d'acqua, mezzi aerei=linea di lancio, mezzo pesante=linea di combustibile non vegetato. Si usano rasterizzazioni e parametri upstream senza coefficienti inventati per la UI. Il posizionamento non calcola viaggio, costruzione, autonomia, rifornimenti, voli o efficacia verificata sul campo. L'intervento è un'ipotesi di azione già eseguibile alla data indicata, non una prova che una squadra reale possa farlo. Umidità addizionale/decadimento sono quelli nativi; non sostituire questi valori con ranking empirici delle categorie.

**PASS** vento puntuale aggiornato ogni ora; B può cambiare velocità/provenienza da un'ora scelta, marcando la revisione come ipotetica. Tabella dei7campi effettivi: vento, temperatura, umidità atmosferica, pioggia nell'ora successiva, pressione e radiazione. Serie del run congelata distinta dalle nuove previsioni del menu. **BLOCKED** accoppiamento completo: temperatura/RH/pioggia non diventano ancora umidità del combustibile. Questa rimane un input manuale, vegetazione uniforme legacy5, DEM reale30m. La pagina dichiara il limite in vista. Non assimilare RH al moisture percent nativo.

**PASS** orizzonti3h/6h/24h/48h/72h supportati dalla richiesta FIRE0.4.0 con asset `fire_plan`; schema/validatore richiedono serie oraria completa, dati identici alla sorgente congelata salvo revisioni esplicite, categoria e geometria valide. I vecchi contratti restano leggibili; più di1h richiede0.4.0 con piano. Native worker isolato e coda persistente esistenti, massimo1job fisico della coda alla volta/4accodati, watchdog900s, limite512MiB perjob e riserva1GiB. Uscita del dominio è errore, non una previsione completa troncata. Queste durate fisiche asincrone non sono la deadline decisionale sperimentale60s.

## Risultati misurati

| Prova | Esito | Risultato |
|---|---|---|
| Due casi identici,3h | PASS | Raster nativi identici; area media7,29ha entrambi |
| Vento B8m/s da270°,3h | PASS | Raster diverso; A7,29ha, B41,31ha; cambiano velocità e direzione |
| Direzione isolata,8m/s,270° contro90° | PASS | Baricentro a+550m est con vento daovest e−502,29m est con vento daest; terreno/innesco/fuel/seed uguali |
| Fascia mezzo pesante a+0min,3h | PASS | A7,29ha, B1,89ha; confronto con calendario nativo abbinato |
| Acqua/Canadair/elicottero,3h | PASS | Azioni effettivamente consumate:50/50/55celle di umidità addizionale; ciascun raster differisce dal controllo. Area media5,625ha per tutte e3 in questa fixture: non dimostra una graduatoria di efficacia |
| Baseline72h | PASS | 72frame, tempo nativo259200s,5732,64ha medie, nessuna uscita dal dominio |
| Interazione browser e forecast reale24h | PASS | Due nuovi job dalla pagina: A391,545ha, B0,09ha. Caso B volutamente ideale: fascia a+0min sul punto di innesco e revisione vento da+12h; non efficacia realistica di un mezzo |
| Nuovo confronto72h con interventi in entrambi i pannelli | NOT RUN | Verificata baseline72h e coppia24h; non equiparare le due prove |

Il confronto UI usa `job-b648439b325243f4bbdabada1b973408` e `job-7a2a49f4bd044e308928c3b14eaef6e2`, previsione `openmeteo-f188aba2c9a25ba8ac5bd417`,16ottobre2026ore20UTC→17ottobre20UTC. Esecuzioni41,746s e40,445s, attesa B41,851s, RSS campionato massimo circa1,233GB per gruppo. È un campione, non p95 o SLA. I due job hanno sorgenti Python stabili tra piano di esecuzione e manifest finale. Le altre prove si sono svolte durante lo sviluppo iterativo; i manifest conservano commit VM/dirty/hash effettivi, diversi dal solo commit host di base. Non usarle come studio causale preregistrato di efficacia.

## Degradazione: cosa è verificato e cosa manca

**PASS** ora visibili stato backend/meteo, risultati precedenti conservati, blocco di nuove previsioni con fonte non attuale e scelta esplicita del replay storico. Laboratorio di guasti accessibile dalla stessa pagina. Guasti iniettati restano marcati sintetici, separati dalla salute reale.

**PASS** perdita controllata FLOOD durante i job FIRE lascia completare FIRE; fonte scaduta controllata disabilita forecast ma non consultazione/replay esplicito; `safety_unknown` restituisce `SAFETY_UNVERIFIED` alle proposte; `solver_down` restituisce `DEPENDENCY_UNAVAILABLE`. Catalogo e risultati fisici precedenti restano leggibili. I guasti sono stati ripristinati al termine, conservando gli eventi. I test del supervisor esistenti verificano inoltre timeout/annullamento e isolamento fra job. **BLOCKED** M6 completo: questa verifica non prova ottimizzazione delle capacità residue, qualità delle decisioni degradate, resilienza infrastrutturale reale o fallback certificati. Il guasto FLOOD è un'iniezione di controllo, non lo spegnimento di un worker HMC reale.

## Ambiente, installazione, comandi

StessaVM Ubuntu22.04ARM64/4vCPU/8GiB, disco19GiB; nessun servizio a pagamento o pubblico. Mac è solo autore/client browser. Aggiunti nell'env FIRE i pacchetti IO richiesti dagli import upstream, con wheel PyPI e versioni/transitivi in `requirements/fire.txt`; NumPy2.3.5/Numba0.62.1 restano invariati. Rasterio1.4.4, pyproj3.7.2, shapely2.1.2, pydantic2.12.3, utm0.8.1, geopandas1.1.1 e relative dipendenze. Log/piani pip conservati; niente sudo/aggiornamenti globali. Cache pip finale294MiB, filesystem circa11GiB usati/8GiB liberi; limiti VM invariati. Nessun download di nuovi grandi dataset. Configurazione aggiornata dell'ambiente in `runtime-fire-studio.json`, precedente runtime-v2 non riscritto; ogni job congela la configurazione accettata.145file engine invariati,16file di sorgente distribuiti corrispondono al Mac;920/922JSON precedenti invariati, cambiano solo2contatori traffico mappe.

Ricostruzione: installazione standard della guida (che usa il lock FIRE aggiornato), `python3 scripts/bootstrap.py days --runtime "$HOME/hazardia-runtime"` per il terreno esteso/caso storico, poi servizio web usuale. Nessun nuovo framework/servizio o motore alternativo. La preparazione usa ancora la fixture pilota; il target geografico rimane generale ma un nuovo territorio reale richiede il relativo profilo, terreno, meteo e qualificazione: non è provato dal cambio del titolo della UI.

Test eseguiti nella VM con core-env e `PYTHONPATH=src`: `python -m unittest discover -s tests/unit -v`(78), `-s tests/domain`(19), `-s tests/decision`(18), `-s tests/web`(14):129PASS. Il decision-env è il subprocesso solver, non l'interprete della suite contratti. Dopo l'ultimo miglioramento al messaggio di preparazione,8test mirati ripetuti PASS. Client Chrome155: `tests/browser/fire-studio.cjs` esegue la coppia nativa e guasti; prima suite si arresta al solo rilievo axe della tabella. `tests/browser/fire-studio-view.cjs OUTPUT ACCEPTED_JSON` (browser-delivery finale) ripete reload/orizzonte/serie/storico e scansioni375/724/1440px dopo correzione:15PASS,3axe senza violazioni. I risultati del percorso precedente restano nei log, senza riclassificare la scansione fallita.

## Negativi e limiti conservati

- FAIL iniziali: import rasterio, poi utm mancanti nell'env core FIRE; aggiunte solo dipendenze IO isolate, non modificato upstream. Dry-run rasterio1.4.3 senza wheelARM64 disponibile FAIL; scelta versione stabile disponibile1.4.4 e pin integrale.
- FAIL adapter: passava WKT al parser legacy CIMA che attende altro formato; corretto costruendo le classi Action con LineString tipizzate.
- FAIL harness: assertion di latitudine come sottostringa respingeva una coordinata valida arrotondata; sostituita con tolleranza esplicita.
- FAIL UI: primo tilelayer regionale restringeva lo zoom iniziale11; corretti limiti espliciti8–20 prima di aggiungere gli sfondi. La linea involontariamente>2km è stata respinta correttamente dal backend; ora messaggio utile e contorno del terreno.
- FAIL axe: tabella scorrevole non raggiungibile da tastiera; aggiunti tabindex/region/etichetta,3scansioni finali PASS.
- NOT RUN dispositivi fisici/Safari/Firefox, nuovo soak30min e100k, validazione storica/vegetazione reale/efficacia di campo, trasferimento reale a nuovo territorio. Full M5–M7 rimangono BLOCKED.

Le2realizzazioni, i combustibili uniformi, il moisture manuale e l'idealizzazione delle azioni impediscono conclusioni scientifiche di previsione o efficacia. Stesso seed non garantisce campioni causali identici dopo biforcazioni stocastiche. Le immagini nitide non aumentano la risoluzione fisica30m. Prossimo incremento: selezione/verifica del modello di umidità del combustibile da T/RH/pioggia (FFMC orario è una fonte da valutare, non adottata), vegetazione reale e forcing distribuito; poi capacità/logistica delle unità e degradazione ottimizzata con benchmark.

Fonti di interfaccia: sorgenti locali upstream PROPAGATOR commit48b45078093692aa8dcca98f51849a5fbcd981a5(`io/actions.py`, `io/boundary_conditions.py`, `core/models.py`). Per l'analisi dell'umidità, documentazione primaria [CFFDRS hffmc](https://github.com/cffdrs/cffdrs_r/blob/master/R/hffmc.r) e [Canadian Forest Service, struttura CFFBP](https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/fbp97/Dev_and_Struct_of_the_CFFBP_System.pdf): richiedono stato iniziale e serie oraria; nessun codice/estimator copiato o installato, nessuna equivalenza automatica FFMC→combustibili locali dichiarata.
