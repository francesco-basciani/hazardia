# Installare HAZARDIA e ricreare la macchina virtuale

Percorso di riferimento: Mac Apple Silicon → UTM 4.6.4 → Ubuntu Server 22.04 ARM64. Tutti i simulatori, l’acquisizione/preparazione dei dati, il solver, l’archivio e il server della dashboard eseguono nella **stessa VM**. Il Mac prepara i file della VM e visualizza la dashboard. Non occorrono servizi commerciali o chiavi API.

Questa guida riguarda il prototipo di ricerca: terreno e immagini reali, inneschi/piogge/popolazione/risorse ipotetici, modelli non calibrati. Non usare per operazioni reali. Lo stato delle verifiche è in [CHECKLIST](../CHECKLIST.md); la distinzione fra ricostruzione in una nuova directory e avvio su una seconda VM è riportata in [RIPRODUCIBILITA](RIPRODUCIBILITA.md).

## 1. Prerequisiti e risorse

Sul Mac: UTM dal [sito ufficiale gratuito](https://mac.getutm.app/), Git, SSH, Python 3.10 o successivo e `hdiutil` (incluso in macOS). Lo script non installa software sul Mac. Il bootstrap scientifico rifiuta l’esecuzione su macOS.

VM di riferimento: 4 vCPU, 8192 MiB RAM, disco 19 GiB, UEFI, rete QEMU emulata/NAT, nessuna cartella condivisa. Solo `127.0.0.1:22227 → guest:22`. Server web nel guest solo su `127.0.0.1:8080`, accessibile dal Mac tramite tunnel SSH. Parametri in [infra/utm/vm.json](../infra/utm/vm.json).

Budget originariamente autorizzato: 5 GiB complessivi di download, 20 GiB di disco, 8 GiB RAM, 4 vCPU. Il download iniziale comprende immagine OS, pacchetti di sistema, ambienti Python e circa 369 MiB di raster. I fetch dei sorgenti/dati sono limitati e verificati; APT/pip e i trasferimenti vanno conteggiati separatamente nel budget complessivo. Il bootstrap richiede almeno 3 GiB liberi prima di iniziare. Non è un installer universale certificato: il riferimento verificato è Linux ARM64/Ubuntu 22.04; altre architetture richiedono lock/binari appropriati e nuove prove.

Non eseguire questo percorso sopra la VM in uso o nella sua directory runtime. Non avviare una seconda VM se questo supera le risorse disponibili. Non riutilizzare una porta host già occupata.

## 2. Preparare immagine e seed sul Mac

```sh
git clone https://github.com/francesco-basciani/hazardia.git
cd hazardia
ssh-keygen -t ed25519 -f "$HOME/.ssh/hazardia-vm"
bash infra/utm/prepare.sh \
  --output "$HOME/HAZARDIA-VM-assets" \
  --public-key "$HOME/.ssh/hazardia-vm.pub" \
  --download
```

Scegli personalmente la passphrase della nuova chiave. **Non inserire la chiave privata nel repository, nel seed o nella VM.** Il seed include solo la chiave pubblica, disabilita autenticazione SSH con password e accesso root diretto. L’utente guest `hazardia` può usare sudo; i pacchetti privilegiati vengono installati da un comando esplicito successivo, non dal seed.

Per riusare un’immagine già scaricata, sostituisci `--download` con `--image-file /percorso/jammy-server-cloudimg-arm64.img`. Immagine fissata: Ubuntu Jammy `20261004`, URL e SHA-256 in `vm.json`; il checksum differente interrompe la preparazione. Il confronto usa il digest ufficiale via HTTPS; non è stata eseguita una verifica GPG indipendente. Non disabilitare TLS se un certificato fallisce.

Il comando produce `ubuntu-arm64.img`, `seed/` e `seed.iso`. Prepara soltanto file: non crea o avvia una VM.

## 3. Creare la VM in UTM

Metodo opzionale tramite API ufficiale di UTM, eseguito dall’utente:

```sh
osascript infra/utm/create.applescript \
  "$HOME/HAZARDIA-VM-assets/ubuntu-arm64.img" \
  "$HOME/HAZARDIA-VM-assets/seed.iso" \
  "HAZARDIA-ARM64"
```

Lo script rifiuta un nome già esistente; crea una VM QEMU ARM64 con virtualizzazione hardware, 4 core, 8192 MiB, disco 19456 MiB (19 GiB), UEFI e seed rimovibile. Imposta il forwarding SSH solo su loopback e nessuna directory condivisa. Non avvia, cancella o modifica altre VM. Il consenso macOS all’automazione di UTM, se richiesto, va gestito dall’utente. Variante parametrizzata del percorso usato per la VM originaria; il nuovo avvio completo non è automaticamente considerato verificato.

In alternativa crea la VM dall’interfaccia UTM con gli stessi parametri, importa l’immagine cloud come disco di sistema e collega `seed.iso` come unità CD rimovibile. Usa QEMU/HVF, non cambiare backend silenziosamente. Controlla dimensione disco, rete e risorse prima dell’avvio. Riferimento: [API UTM](https://docs.getutm.app/scripting/reference/).

Avvia la VM da UTM e attendi il completamento di cloud-init. La console non accetta password dell’utente; usa SSH:

```sh
ssh -i "$HOME/.ssh/hazardia-vm" -p 22227 hazardia@127.0.0.1
cloud-init status --wait
uname -m
cat /etc/os-release
```

Risultato atteso: `aarch64`, Ubuntu 22.04. Verifica la nuova host key della VM prima di accettarla; non disabilitare il controllo delle chiavi SSH. Terminato il primo avvio, il seed può essere scollegato a VM spenta. Non eliminare il disco della VM per ricreare il seed.

## 4. Installare i prerequisiti nel guest

**Da qui tutti i comandi sono nella VM**, come utente `hazardia`:

```sh
sudo apt-get update
sudo apt-get install -y --no-install-recommends git ca-certificates
mkdir -p "$HOME/hazardia-runtime"
git clone https://github.com/francesco-basciani/hazardia.git "$HOME/hazardia-runtime/app"
cd "$HOME/hazardia-runtime/app"
cat infra/guest/system-packages.txt
sudo bash infra/guest/install-system.sh
```

Questi sono i passaggi che richiedono privilegi, tutti nel guest: installa compilatori, librerie NetCDF/GDAL/GRASS e pacchetti scientifici Ubuntu. Leggilo prima di eseguirlo. Non modifica/disabilita servizi di sistema o protezioni. Se i pacchetti cambiano con gli aggiornamenti Ubuntu, conserva il nuovo inventario e ripeti le verifiche; le versioni dei pacchetti APT non costituiscono un’immagine OS immutabile.

## 5. Ricostruire motori e ambienti separati

```sh
python3 scripts/bootstrap.py preflight --runtime "$HOME/hazardia-runtime"
python3 scripts/bootstrap.py install --runtime "$HOME/hazardia-runtime"
```

Il secondo comando, senza sudo:

- scarica gli archivi ufficiali fissati di PROPAGATOR, HMC, REFlEx, GRASS addons e Python 3.12, verificandone SHA-256;
- crea `core-env`, `decision-env`, gli ambienti separati incendio/geografia sotto `engines/upstream`, e compila HMC;
- compila quattro addons GRASS in un prefisso privato del runtime, senza dipendere da `~/.grass7/addons`;
- conserva REFlEx originale e applica la patch dichiarata a una copia isolata;
- genera `runtime-v2.json`, hash dei motori e inventari in `installation/`.

Nessuna dipendenza da `/home/hazardia/m0`, percorsi del Mac o ambienti del precedente esperimento. La distribuzione Python standalone contiene collegamenti terminfo non accettati dall’estrazione sicura: il bootstrap omette soltanto quella banca dati terminale opzionale e conserva il filtro di sicurezza; usa terminfo Ubuntu. I sorgenti CIMA non vengono modificati.

`requirements/` contiene versioni Python fissate per i tre ambienti. L’ambiente geografico usa anche i pacchetti Ubuntu: non installare l’intero vecchio `pip freeze` come se fosse un lock pip portabile.

## 6. Rigenerare gli esempi Abruzzo

```sh
python3 scripts/bootstrap.py demo --runtime "$HOME/hazardia-runtime"
python3 scripts/bootstrap.py days --runtime "$HOME/hazardia-runtime"
python3 scripts/bootstrap.py verify --runtime "$HOME/hazardia-runtime"
```

`demo` acquisisce i raster originali dagli URL pubblici con hash fissati, prepara gli input, esegue davvero PROPAGATOR (60 minuti) e HMC→REFlEx (6 ore, massimo di allagamento), quindi crea catalogo, immagini e vendor Leaflet locali. I nomi delle sottocartelle M1/M3 sono identificativi di compatibilità del fixture; i nuovi comandi registrano la data effettiva di esecuzione.

`days` ricostruisce la griglia 1024² e riesegue le due simulazioni native su 72 ore: controllo no-op e fascia tagliafuoco ideale con stesso calendario. Crea 144 immagini orarie con hash. È un esperimento di ricerca a due realizzazioni e combustibile/umidità ipotetici; non dimostra efficacia sul campo. Richiede coda vuota; eseguilo prima di avviare il server ed evita altri job contemporanei. La sensibilità al calendario degli eventi rimane una limitazione esplicita.

`verify` verifica percorsi autonomi, hash, prodotti reali, frame pubblicati e test unitari/dominio/decisione/web. Senza `days`, la verifica del confronto 72h è **NOT RUN**, non PASS. Mancanza di dati, hash diversi o output parziali interrompono il percorso; non vengono sostituiti con risultati fittizi.

Per riusare download già presenti: `install --archive-cache DIR` cerca `PROPAGATOR.tar.gz`, `HMC.tar.gz`, `REFLEX.tar.gz`, `GRASS_ADDONS.tar.gz`, `PYTHON312.tar.gz`; `demo --input-cache DIR` cerca i tre file raster e `leaflet/{leaflet.js,leaflet.css,LICENSE}`. Anche il riuso verifica gli hash. Sono opzioni, non dipendenze nascoste dalla VM originaria.

I record sono immutabili. Uno stadio completato non si reinstalla automaticamente; un fallimento parziale conserva log e input. Prima di rimuovere una directory incompleta, conservarne le evidenze; usare un nuovo prefisso per una ricostruzione indipendente. Non rilanciare alla cieca dentro un runtime con lavori dell’utente.

## 7. Avviare e aprire la dashboard

Nel guest:

```sh
cd "$HOME/hazardia-runtime/app"
../core-env/bin/python scripts/web_service.py start --runtime "$HOME/hazardia-runtime"
```

In un altro terminale **sul Mac**, mantieni aperto il tunnel:

```sh
ssh -i "$HOME/.ssh/hazardia-vm" -p 22227 \
  -N -L 127.0.0.1:8080:127.0.0.1:8080 hazardia@127.0.0.1
```

Apri [dashboard](http://127.0.0.1:8080/) e [confronto incendio 1–3 giorni](http://127.0.0.1:8080/physical-fire.html). Verifica connessione VM, due pericoli nel catalogo e raster della pagina incendio. Le ortofoto dettagliate vengono consultate tramite proxy WMS limitato della Regione Abruzzo; non sono distribuite nel repository. In caso di indisponibilità del servizio scegli Sentinel offline: copertura limitata al ritaglio dichiarato, non una mappa offline di tutta Italia.

Per arrestare il servizio, prima aspetta che non ci siano job attivi:

```sh
../core-env/bin/python scripts/web_service.py stop --runtime "$HOME/hazardia-runtime"
```

Non esporre il server su `0.0.0.0`, non aprire porte del router e non abilitare dispatch reali. Questa installazione è locale di ricerca.

## 8. Test opzionali del browser

La piattaforma non richiede Node. Per QA del client di visualizzazione, in una checkout sul client:

```sh
npm install
npx playwright install chromium
npm run test:ui
node tests/browser/physical-fire.cjs qa-results/physical node_modules/axe-core/axe.min.js
```

Il backend deve essere già in esecuzione nella VM e raggiungibile attraverso il tunnel. Se usi un browser/runtime già installati imposta `HAZARDIA_PLAYWRIGHT_PATH`, `HAZARDIA_BROWSER_EXECUTABLE`, `HAZARDIA_BASE_URL` e, se necessario, `HAZARDIA_AXE_PATH`; non occorrono percorsi del precedente Mac. Le prove usano casi/annotazioni chiaramente di test, conservano i contenuti precedenti e rifiutano la pulizia se rilevano revisioni concorrenti.

Gli altri script browser storici documentano prove di precedenti incrementi; alcuni selettori si riferiscono a quelle UI. I punti d’ingresso della UI attuale sono `control-room.cjs` e `physical-fire.cjs`. Non interpretarli tutti come una suite corrente già passata.

## Problemi frequenti

| Problema | Azione |
|---|---|
| SSH non disponibile | Attendere cloud-init, verificare VM accesa, forward22227→22 e chiave pubblica nel seed; nessuna password predefinita |
| Porta8080 occupata | Riutilizzare il tunnel/servizio esistente o chiuderlo esplicitamente; non terminare processi sconosciuti |
| Errore certificato HTTPS | Sistemare CA/orologio; non usare `curl -k` o SSL senza verifica |
| Checksum sorgente/dato diverso | Conservare il fallimento; verificare URL/snapshot, creare una nuova versione con evidenza; non aggiornare automaticamente il digest |
| `GRASS` o import scientifico mancante | Ricontrollare prerequisiti Ubuntu; non mescolare gli ambienti incendio/geografia |
| Ortofoto non disponibili | Stato degradato esplicito e Sentinel locale; il risultato fisico non cambia |
| Alluvione dinamica/argini/pompe assenti | Limite attuale del prototipo, non problema d’installazione; vedere piano e checklist |
| Installazione su x86/altro OS | Percorso non ancora verificato; usare i lock ARM64 di riferimento solo su ARM64 |

## Previsioni Open-Meteo nella VM

Nessun pacchetto o chiave aggiuntiva. Avvia la dashboard come sopra: il browser legge solo `/api/weather` locale e il backend acquisisce il punto L’Aquila dal solo endpoint gratuito. Le schede condividono cache/contatore SQLite in `web-state/weather`,30min/minimo tra tentativi,48tentativi/giornoUTC. Non copiare cache personali o quote inGit. Eseguire solo usi noncommerciali consentiti dai termini. Un’installazione nuova acquisisce un nuovo snapshot alla prima apertura; nessuna stessa-condizione atmosferica implicita.

Nella mappa **Meteo → ora → Simula con queste previsioni** apre il nuovo calcolo con fonteFORECAST. Scegli ora futura e modello, poi avvia. Incendio10/30/60min; alluvione6h. Eventi/combustibile/soil/Q0 non calibrati; un caso asciutto può legittimamente non mappare acqua. [Guida dettagliata](../reports/METEO-REALE.md), [contratti/tempi](../reports/ADR-0010-openmeteo-forecast.md). Per verifiche extra nella VM: `../core-env/bin/python -m unittest discover -s tests/unit -p test_forecast.py -v`. Il browserQA opzionale `tests/browser/weather.cjs` usa le variabiliQA già documentate e deve puntare a un runtime di collaudo.


## Vento regionale con particelle

Nessun pacchetto aggiuntivo. Dopo l’aggiornamento del sorgente e il riavvio del servizio nellaVM, la dashboard acquisisce/cache il campo tramite `/api/weather/wind`, con refresh POST dedicato a griglia fissa e nessuna chiave.315punti/4giorni/2variabili, nearest, elevation=nan per ogni coordinata,8tentativi/giorno/3h;64MiBcache. La cache è `web-state/regional-wind`, da preservare con ricevute/quote per il replay; non cancellare il database per aggirare i limiti. Quando piena, ulteriori download sono bloccati prima di superare il budget.

Richiesti HTTPS in uscita dallaVM a `api.open-meteo.com` e, per lo sfondo regionale opzionale, `tiles.maps.eox.at`. Uso gratuito non commerciale, attribuzioni già presenti; nessun endpoint cliente commerciale. EOX2024:CC-BY-NC-SA4.0, RAM8MiB/downloadcumulativo16MiB, zoom8–11; ortofoto regionali per il dettaglio. Le immagini sono consultate, non incluse nella distribuzioneGit. Il browser contatta solo laVM.

Usa Monitoraggio → Vento sull’Abruzzo → Inquadra Abruzzo; cambia ora o pausa. Il movimento ridotto produce frecce statiche. I dati non sostituiscono le forzanti dei job fisici. [Dati,comandi,prove e limiti](../reports/VENTO-REGIONALE.md), [ADR](../reports/ADR-0011-regional-wind-display.md). Test nellaVM: `../core-env/bin/python -m unittest discover -s tests/unit -p test_regional_wind.py -v`; checker congelato `scripts/verify_regional_wind.py`. QAclient opzionale `tests/browser/regional-wind.cjs`, con le stesse variabiliPlaywright/Chrome/axe delle suite precedenti.


**Orario dopo sospensioneVM:** verificare `date -u` nel guest contro il computer di controllo: il solo indicatore “System clock synchronized: yes” può essere rimasto vecchio. Se necessario, a coda vuota l’amministratore può riavviare il servizio già presente con `sudo systemctl restart systemd-timesyncd`. Non cambia fuso orario o configurazione e non installa pacchetti. L’interfaccia segnala cacheSTALE se l’età dichiarata dallaVM e l’orologio del browser divergono oltre120s; API/CLI richiedono comunque OS correttamente sincronizzato. La ripresa da sospensione va inclusa nei controlli di ambiente.

### Meteo su tutta la vista
Nel **Monitoraggio → Meteo sulla mappa** scegli ora e vento, poi **Colore trasparente sulla mappa → Temperatura / Precipitazione**. Il primo accesso acquisisce nellaVM un contesto81punti ICON Global e riusa il vento regionale più fitto. Pan/zoom riutilizzano la cache; nuove aree/contesti richiedono copertura reale e rispettano i limiti. Clicca un punto/cella per leggere valori e fonti. Nessuna dipendenza aggiuntiva: urllib/sqlite della libreria standard. Nuovo cache `web-state/map-weather`, endpoint locali `/api/weather/map` e `/api/weather/map/refresh` (POST con solo bounds WGS84 e header di ricerca); non modificare raw/receipt. Limiti48tentativi/giorno,65s,TTL3h,1MiB/risposta,64MiBcache. Totale conservativo con gli endpoint precedenti≤6456località-equivalenti/giorno. Le tinte sono campi di consultazione interpolati, con campionamento dichiarato, separati dai nuovi job CIMA. [Report e limiti](../reports/METEO-SULLA-MAPPA.md).
