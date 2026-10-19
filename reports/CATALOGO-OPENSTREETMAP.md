# Catalogo territoriale OpenStreetMap — 19 ottobre 2026

Richiesta: acquisire e riusare il patrimonio informativo OSM anche per futuri scenari sanitari. Incremento M2/M5/M7 dei dati territoriali esistenti; nessun nuovo simulatore sanitario o cambio del decision engine. Fonte dei requisiti: messaggio utente del19ottobre. Run `osm-catalog-20261019`, parent `c963847` + modifiche; SHA finale in Git/PUBLICATION.json. Reviewer: stesso agente Codex.

## Cosa cambia

Un catalogo generico sostituisce la selezione limitata a pochi tipi di oggetto. Conserva tutti i tag degli oggetti rappresentabili dell’estratto: anche chiavi non conosciute, specialità sanitaria, accessibilità, orari, posti letto **se dichiarati**, gestore, nomi, riferimenti e metadati OSM disponibili. Non inventa valori assenti e non presume che i valori cartografati siano attuali o verificati. I sorgenti degli import vengono archiviati per SHA256 in `territorial-sources/`; le normalizzazioni derivate sono separate e versionate.

Livelli nella sezione **Territorio ed esposizione → Catalogo OpenStreetMap · livelli**: sanità e assistenza, emergenze e soccorso, istruzione, trasporti, reti e impianti, edifici, ambiente/acque, confini, altri oggetti. Abitati e linee aeree mantengono i propri controlli. Ricerca per nome o attributo; un risultato centra la geometria e apre il dettaglio con tutti i tag e link all’oggetto OSM. I livelli più densi partono spenti. Stesso componente nel Monitoraggio e negli scenari; nessuna attivazione automatica di nuove simulazioni.

Geometrie: punti, linee e poligoni; relazioni multipoligono ricostruite solo se complete e valide, compresi buchi. In caso di geometria mancante si usa un centro **soltanto se presente nella fonte**, etichettato come proxy ed escluso da esposizione/ottimizzazione. Altrimenti l’oggetto resta nel raw e viene contato fra gli omessi. Vie con nodi mancanti non vengono collegate artificialmente. Cavi interrati restano nel catalogo reti, senza essere mostrati come ostacoli aerei.

Il solver mantiene le categorie di priorità già qualificate come esperimento. Strade, negozi, edifici generici e categorie sconosciute non diventano nuovi obiettivi o risorse per il solo fatto di esistere in OSM. Cliniche e farmacie possono ricevere l’analisi fisica condizionata quando presenti nel dominio, ma questa consegna non dimostra nuovi casi nativi su strutture sanitarie.

## Esecuzioni effettive

| Verifica | Esito | Evidenza |
|---|---|---|
| Parser/import reale nella VM, stesso estratto OSM del15ottobre | PASS | 9.722 oggetti con tag; 9.525 rappresentati, 197 omessi per geometria. SHA raw `4c3c76309a724f2fbdb95e4e793ede0eaa7f752c55c33ea5a54885eb73aa9cf7` |
| Fedeltà di tutti i tag rappresentati; conteggio senza perdite silenziose | PASS | `tests/native/osm_catalog_audit.py`, `reports/osm-catalog/verification.json` |
| Inventario reale completo dell’estratto rappresentato | PASS | 14 sanità/assistenza; 47 emergenze; 12 istruzione; 2.457 trasporti; 1.824 edifici; 516 ambiente; 34 elementi elettrici; 3 reti; 8 confini; 21 abitati; 4.589 altri |
| Filtro sulla bbox originaria tramite API | PASS | 9.474 oggetti intersecanti, incluse14strutture sanitarie; 9assert dell’audit |
| Tag sanitari, ignoti, geometrie incomplete, multipoligono con buco, assenza di disponibilità inferita; regressioni contesto | PASS | 10test VM, `unit-final.log`;7regressioni decisioni PASS in `decision-regression.log` |
| UI catalogo/ricerca/centratura/dettaglio struttura sanitaria | PASS | Verifica IAB sul Monitoraggio, nome originale OSM e geometria; immagini nel run locale |
| Workspace utente e caso FonteVetica, motori CIMA | PASS | Confronto prima/dopo audit;145pin invariati, nessun nuovo job fisico |
| Estrazione nazionale/planetaria completa, topologia di routing, aggiornamenti incrementali regionali | NOT RUN | Nessun bulk download; non confondere il catalogo con il censimento di un Paese |
| Capacità sanitaria operativa, disponibilità letti/mezzi/personale, validazione ufficiale | BLOCKED | OSM è contesto, richiede fonti qualificate e data di validità |
| Simulazioni sanitarie, nuovi benchmark p95/soak, nuovi run fisici e validazione scientifica | NOT RUN | Nessun nuovo hazard; gate completi M5–M7 ancora BLOCKED |

Gli oggetti con geometria che interseca l’area possono estendersi oltre la bbox: non viene inventata una porzione mancante. I conteggi della mappa cambiano con viewport e fonte riusata. Lo snapshot non è una ricognizione sanitaria odierna. Data precisa di disponibilità del raw non ricavabile dai soli metadati usati: resta `null`, non mezzanotte inventata.

## Ripetibilità

Nella VM, dalla directory `app`, con gli ambienti già installati:

```sh
PYTHONPATH=src PROJ_LIB=/usr/share/proj /home/hazardia/m0/reflex-env/bin/python -m unittest discover -s tests/decision -p test_territorial_context.py -v
PYTHONPATH=src PROJ_LIB=/usr/share/proj /home/hazardia/m0/reflex-env/bin/python scripts/import_territorial_osm.py --root /home/hazardia/hazardia-runtime --raw /home/hazardia/hazardia-runtime/runs/map-detail-20261015T204352Z/osm-map-final-raw.json --bounds 13.375 42.345 13.405 42.36 --source-url https://api.openstreetmap.org/api/0.6/map
PYTHONPATH=src PROJ_LIB=/usr/share/proj /home/hazardia/m0/reflex-env/bin/python tests/native/osm_catalog_audit.py --root /home/hazardia/hazardia-runtime --out /home/hazardia/hazardia-runtime/runs/osm-catalog-20261019/audit-new
```

Limiti conservati: bbox massima1°×1°,10richieste OSM/giorno condivise; risposte live2MiB/2.000oggetti e fallback API4MiB; import locali32MiB raw,20.000oggetti normalizzati,16MiB derivati,20snapshot letti. Acquisizione/cache/parser/HTTP nella stessaVM4vCPU/8GiB/19GiB. Nessuna installazione o aumento risorse. Download massivi ulteriori richiedono prima una stima e autorizzazione se superano i limiti concordati. Non usare tile o Nominatim come servizio di estrazione dati.

## Negativi conservati e limiti

- Primo controllo sintassi JS lanciato con modalitàCommonJS: FAIL di harness, corretto con `node --input-type=module --check`.
- Primo import aveva ricevuto da CLI una mezzanotte non verificata come disponibilità: FAIL di configurazione. Record conservato in `runs/osm-catalog-20261019/import-invalid-availability.json`, rimosso dagli import attivi tramite spostamento e rieseguito con disponibilità sconosciuta. Raw invariato.
- Primo auditAPI403 per header di ricerca mancante, secondo400 mentre i due worker territoriali erano occupati dai casi aperti: FAIL di harness/contesa, senza ridurre protezioni o limiti. Terzo audit9PASS. Un rifiuto per coda occupata resta esplicito.
- Restart iniziale non riuscito per PIDfile obsoleto: identificato il listener effettivo, verificata coda fisica vuota, arresto del solo processo HAZARDIA e un nuovo avvio; nessun sudo.
- Il caricamento dopo centratura richiudeva il popup: corretto mantenendo la selezione durante il ridisegno, senza attivare autopan.
- 197oggetti del raw non normalizzati: nessuna completezza inventata; relazioni arbitrarie, reti topologiche, restrizioni di svolta e temporalità richiedono consumer dedicati.

## Fonti e decisione

[OSM Healthcare](https://wiki.openstreetmap.org/wiki/Healthcare), [specialità sanitarie](https://wiki.openstreetmap.org/wiki/Key:healthcare:speciality), [ospedali e attributi](https://wiki.openstreetmap.org/wiki/Tag:healthcare%3Dhospital), [policy API OSMF](https://operations.osmfoundation.org/policies/api/), [licenza e attribuzione](https://www.openstreetmap.org/copyright).

Scelta: archivio sorgente + normalizzazione generica versionata + consumer espliciti per dominio. Alternativa scartata: aggiungere una whitelist per ogni futuro hazard, perdendo informazioni già acquisite. Alternativa rimandata: scaricare un interoPaese/planet o introdurre un serverOSM dedicato, non necessario per questo incremento e non validato entro le risorse. Risultato tecnico, non evidenza a favore di H1–H3 o capacità operativa sanitaria.
