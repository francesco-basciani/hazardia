# Mappe di scenario contemporanee e verifica dell’intervento

Incremento `scenario-windows-20261017`, base privata `063f3f1f298b9eb4b061b3aba7b0c6ab81a60ff1`. Reviewer: Codex self-check. SPEC FR-26 / requisiti scenari e forzanti, piano M0–M7 e identità generica preservati. Runtime nell’esistente VM Linux; nessuna installazione o acquisizione aggiuntiva, nessun modello CIMA modificato.

## Risultato

Il separatore è sostituito da finestre cartografiche simultanee, con posizione, zoom e tempo comuni. Lo scenario selezionato è modificabile; gli altri hanno un pulsante Modifica. Scenari e livelli sceglie quali includere; Crea alternativa aggiunge una finestra. Opacità comune, raster originali senza deformazioni o riduzioni artificiali. Due colonne anche su telefono, con controlli esterni alle mappe; nuove finestre proseguono su ulteriori righe.

Inserimento, trascinamento, tempo e rimozione degli inneschi aggiornano tutte le configurazioni. Le risorse restano locali allo scenario. I vecchi casi con inneschi diversi non vengono riscritti al caricamento: un avviso spiega che la prima modifica di un innesco li allinea. Se un innesco ritardato supera la durata di un caso precedente, la durata viene estesa al primo valore supportato che lo comprende. I risultati immutabili e submitted_input precedenti sono conservati.

Il meteo è sopra le mappe: vento/provenienza, temperatura, umidità aria, pioggia, pressione, radiazione, ora e fonte; selettore fra meteo effettivamente usato nel risultato e previsione Open-Meteo aggiornata per consultazione. Tabella oraria aperta con evidenziazione del tempo. Assenze esplicite, previsione scaduta indicata, nessun passaggio silenzioso del vecchio inizio a una nuova data. Unità e mappe riportano modifiche non ancora calcolate. Pioggia/T/RH sono contesto: l’estimatore qualificato di umidità combustibile resta mancante.

## Prova reale della linea aggiunta dall’utente

Workspace revisione46, caso `three-days-e20b37eac6b2`, risultato `job-c25ae3f72783453b8a04c31bb7618122`. La linea Canadair `unit-69d4b7b6-80c` compare nella bozza, non nel submitted_input né nel piano del risultato visualizzato. Questa è una causa dell’assenza di aggiornamento grafico.

Verifica separata nella VM, senza modificare il workspace o i job precedenti: due esecuzioni native di72h,288frame ciascuna, stesso DEM/fuel/moisture15%, seme1729,2realizzazioni, singolo thread e identica previsione oraria congelata. Primo replay identico elemento per elemento nella probabilità finale; seconda esecuzione aggiunge la geometria dell’utente all’area già presente a+1h. Il motore consuma78celle di rimozione combustibile a0min e1506celle a60min. Superficie finale1,53ha in entrambi,0celle di probabilità diverse. Nessuna delle78celle della linea è raggiunta dal fuoco del caso di riferimento; distanza minima tra centri cella210m. La linea aggiunta non ha quindi un effetto supplementare osservabile in questo caso. Non inferire inefficacia generale né inventare una riduzione proporzionale al numero di unità.

Questa è rimozione ideale del combustibile, non una misura di efficacia realistica di Canadair, equipaggi, logistica o disponibilità. Le categorie continuano a condividere la medesima ipotesi ideale. La vecchia coppia senza/con area resta347,13/1,53ha, ma non è una validazione operativa.

Comandi riproducibili, dalla directory app della VM:

```sh
PYTHONPATH=src:/home/hazardia/m0/fire-src /home/hazardia/m0/fire-env/bin/python /home/hazardia/hazardia-runtime/native-check-windows.py
PYTHONPATH=src:/home/hazardia/m0/fire-src /home/hazardia/m0/fire-env/bin/python /home/hazardia/hazardia-runtime/spatial-check-windows.py
```

Gli script creano directory nuove: un replay richiede un nuovo run_id/destinazione, per non sovrascrivere l’evidenza. Script e output originali nella copia privata `experiments/runs/scenario-windows-20261017`; output nativi nella VM `runs/scenario-windows-20261017`. `native-verification.json` registra input SHA, Python3.12.15, eventi, tempi39,62/23,31s (due singole osservazioni, non benchmark), riscontri spaziali. Non pubblicare workspace personali/raster privati.

## Verifiche e limiti

- PASS:28verifiche browser delle finestre/zoom bidirezionale/centri/tempo/meteo/inneschi comuni/risorse locali/alternative/preservazione workspace;375/768/1440px,3axe componente senza violazioni. Suite `tests/browser/scenario-windows.cjs`; vecchio entrypoint studio-layout delega alla suite attuale, i test del separatore non sono più un requisito dello studio.
- PASS:19regressioni workflow, durata, payload giorno, clone e preservazione,3axe root senza violazioni. `tests/browser/fire-usability.cjs` aggiornato al confronto per finestre.
- PASS: replay nativo72h e consumo della nuova linea; l’ipotesi «la nuova linea deve cambiare necessariamente la propagazione» è smentita per questa geometria.
- PASS: nessuna scrittura del workspace reale da QA; asset statici distribuiti nella stessa VM senza riavvio del servizio.
- FAIL intermedio: nessun test finale fallito; osservata al controllo visuale una variazione del centro durante il ridimensionamento iniziale di Leaflet, corretta preservando il centro geografico al resize. Le catture precedenti sono conservate.
- BLOCKED: qualificazione fuel/moisture, efficacia differenziale/logistica e skill operativa; fullM5–M7 invariati.
- NOT RUN: nuove validazioni storiche, nuove prove su hardware fisico mobile/crossbrowser, benchmark p95/soak e scalabilità con molti scenari. Due colonne su telefono sono funzionalmente verificate, non un user study di usabilità.

Prossimo incremento scientifico invariato: fuel reale ed estimatore di umidità qualificati, poi capacità/logistica ed efficacia. L’implementazione del confronto non chiude questi gate.
