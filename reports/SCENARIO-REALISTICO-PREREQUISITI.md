# Scenario realistico: verifica degli input e primo esperimento

Run `realism-assessment-20261018`,18ottobre2026, base `ab39ab19f7f11d46d7a44cc4b63246b4315755d9`+dirty, commit consegna Git/PUBLICATION.json. Reviewer Codex self-check. È un incremento di qualificazione scientifica del piano originario, non un nuovo hazard o simulatore. **Scenario realistico completo: BLOCKED**; non dichiarato realizzato da questo audit.

## Esiti eseguiti

**PASS integrità tecnica dei3risultati manuali FonteVetica:**15asset di input e1782artefatti verificati perSHA nella VM,72eventi spaziali orari per ciascun run, griglia30m, DSM/WorldCover e meteo realmente consumati. Tutti usano soltanto2realizzazioni; il campo atmosferico è un unico modello deterministico. Il controllo di integrità non è una validazione della previsione.

**PASS prova su sette giorni antecedenti:** acquisizione HTTPS reale in VM di10048byte da Open-Meteo ICON Global per il punto rappresentativo FonteVetica. `past_days=7`, `forecast_days=4`, temperatura/RH/vento/pioggia, UTC, vento m/s. Ricevuta SHA256 `5ab687997da9220a4b771670583ab5ed8e179534c224578841f8278a94b9c7aa`, acquisita18/10 alle15:05:06UTC. Protocollo fissato prima dell’acquisizione:168ore, codici iniziali65/85/95, partenza al prossimo orario UTC futuro, nessun tuning sui risultati. Inizio18/10 alle16UTC. Sono recenti previsioni archiviate e previsioni disponibili alla consultazione; NON stazioni o osservazioni sul combustibile, né dati necessariamente disponibili al momento del rogo del17.

La stima hFFMC1977 già presente nel framework, fatta evolvere sulle168ore precedenti, produce umidità al punto di16,3522568/16,3521900/16,3521767%. Dispersione residua0,0000801punti percentuali fra le tre inizializzazioni. Il reset FFMC85 esistente equivale a16,2989619%. **Risultato negativo rispetto all’ipotesi di un grande errore dovuto al solo reset in questo punto/istante:** differenza centrale circa0,05323punti. Non giustifica abbassare arbitrariamente l’umidità per prolungare l’incendio e non dimostra che l’umidità vera sia16,35%.

Il nodo atmosferico restituito è42,375/13,75, quota modello1233m. È distinto dal punto della località richiesto; questo conferma che il dettaglio dello sfondo satellitare non rappresenta la risoluzione meteorologica in montagna. Un test puntuale non può inizializzare tutto il dominio di30km. La finestra fino all’innesco futuro comprende il breve tratto di previsione noto alla data di consultazione, non è interamente una storia osservata. Nessuna nuova forzante è stata applicata ai risultati già esistenti.

**PASS6test VM:** finestra168h completa; nessun effetto dalla pioggia successiva all’inizio; pioggia dell’ultimo intervallo concluso effettivamente consumata; gap, finestra incompleta, null e unità errate rifiutati. Python3.12 dell’ambiente geo esistente, nessuna installazione. **NOT RUN** nuovi job PROPAGATOR, nuovi scenari UI, ensemble, calibrazione/skill storica. Workspace e input di produzione non modificati; nessun riavvio.

## Cosa manca per il caso richiesto

| Elemento | Stato attuale | Criterio per avanzare |
|---|---|---|
| Terreno e copertura georiferiti | PASS tecnico, risoluzione30m e fonte2021 dichiarati | Conservare datum/epoca/errori DSM e qualità locale |
| Specie, quantità e stato stagionale del combustibile | BLOCKED qualificazione | Mappa fuel documentata, distinzione forestale e stato dell’erba; WorldCover non basta |
| Umidità iniziale e durante l’evento | PASS fattibilità puntuale, BLOCKED qualificazione spaziale | Storia antecedente su tutti i nodi, sensibilità e confronto con misure/modello qualificato; non RH diretta |
| Meteo spaziale variabile nel tempo | PASS coupling tecnico, BLOCKED accuratezza locale | Confronto con dati locali, limiti orografici e incertezza previsionale dichiarati |
| Innesco ipotetico futuro | Possibile, deve restare esplicito | Punto/ora scelti senza presentarli come osservati |
| Ricostruzione FonteVetica2026 | BLOCKED | Punto/ora e perimetri osservati con date e provenienza; la notizia non li fornisce |
| Mezzi e soppressione | BLOCKED realismo operativo | Effetti/logistica/tempo di lavoro/acqua/limiti atmosferici supportati da dati; le azioni native non certificano categorie reali |
| Incertezza e validazione | BLOCKED | Ensemble dimensionato con pilot, sensibilità e caso osservato indipendente; nessun ottimo fisico dichiarato da una singola coppia |

## Fonti e accessibilità verificate

[CIMA sul ruolo di RISICO](https://www.cimafoundation.org/en/news/propagator-how-to-simulate-fire-dynamics/) descrive la necessità dell’umidità vegetale; la nostra stima hFFMC non è RISICO. [API ufficiale PROPAGATOR](https://cimafoundation.github.io/propagator_sim/0.2.0/reference/propagator/) distingue fuel, umidità percentuale e vento km/h. Ispezionati anche i sorgenti originali pin nella VM: classi1latifoglie/2arbusti/4erba/5conifere/6agroforestale;0NO_FUEL è gestito esplicitamente dal backend. Non emerge un errore di scambio erba/conifere. Le differenze per zone umide/muschio rispetto all’helper upstream sono ipotesi del crosswalk da qualificare, non classi osservate di combustibilità.

[Open-Meteo DWD](https://open-meteo.com/en/docs/dwd-api) documenta modello globale11km e giorni precedenti: sorgente accessibile gratuitamente entro il piano di ricerca e i budget esistenti. La prova ha effettuato una sola richiesta puntuale aggiuntiva (budget locale preregistrato1richiesta/256KiB), senza aggirare quote mediante chiamate ripetute. Il quota-store del campo mappa non è stato modificato; questa singola richiesta di ricerca è registrata nel raw separatamente.

[Carta forestale CFI2020 CREA/MASAF](https://cfi-sinfor.crea.gov.it/Home/CartaForestale): materiale utile per specie/tipologie, ma accesso al vettoriale richiede richiesta formale e credenziali; non disponibile come download anonimo. Non inviata email né accettate condizioni per conto dell’utente. Il sito distingue maschera bosco validata e attributi derivati senza ulteriori controlli: non è automaticamente una fuel map calibrata.

[Carta tipologico-forestale Abruzzo](https://geoportale.regione.abruzzo.it/Cartanet/catalogo/agricoltura-uso-del-suolo/carta-tipologico-forestale-della-regione-abruzzo-tipologie): catalogo ufficiale con WMS di consultazione, epoca2006/pubblicazione2009 e licenza regionale da verificare per usi computazionali/redistribuzione; nella scheda non è fornito un download vettoriale. Vecchia epoca e mera consultabilità non qualificano lo stato del2026. Non scaricati atlanti/PDF massivi.

[EFFIS Rapid Damage Assessment](https://forest-fire.emergency.copernicus.eu/about-effis/technical-background/rapid-damage-assessment) e [accesso dati](https://forest-fire.emergency.copernicus.eu/applications/data-and-services) sono possibili fonti indipendenti per perimetri osservati, con copertura/limiti e accesso agli estratti da verificare. Nessun perimetro osservato FonteVetica2026 è stato acquisito o dichiarato assente in modo esaustivo. Assenza di un poligono scaricato non significa assenza dell’incendio.

## Riproduzione e prossimo incremento

`PYTHONPATH=src <geo-python> scripts/assess_fire_initialization.py --raw <snapshot-OpenMeteo.json> --start 2026-10-18T16:00:00Z --output <nuovo-risultato.json>`; lo script rifiuta di sovrascrivere le evidenze. `PYTHONPATH=src <geo-python> -m unittest discover -s tests/unit -p test_fire_initialization_assessment.py -v`. Audit nativo: `PYTHONPATH=src <geo-python> tests/native/fire_realism_audit.py <runtime> <job-id>...`. Solo Linux VM per queste analisi; nessun nuovo pacchetto. Raw `experiments/runs/realism-assessment-20261018`, copia VM omonima. Sintesi pubblicabile `reports/realism-assessment/verification.json`; snapshot/provider/state restano privati.

La scelta richiesta all’utente distingue previsione condizionale con innesco ipotetico da ricostruzione dell’evento. Per la prima: prossimo incremento eseguibile è inizializzazione antecedente distribuita verificata e dimensionamento ensemble, poi nuovo caso separato e confronto di interventi con assunzioni dichiarate; non modificare silenziosamente FonteVetica o calibrare per farlo durare giorni. Per la seconda: prima inventario di osservazioni/cronologia, separazione calibrazione/held-out e verifica diritti; mancanti non rimpiazzati con cronaca o icone. Le qualifiche scientifiche e i gate completiM5–M7 restano BLOCKED. Questo report non chiude la richiesta di scenario realistico.
