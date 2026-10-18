# Contenuto del repository e significato delle prove

Il repository pubblico contiene tutti i sorgenti correnti di HAZARDIA, dashboard, contratti JSON, adapter/worker, decision engine e checker, coda, strumenti di test, bootstrap, configurazione UTM/cloud-init, patch REFlEx dichiarata e documentazione. Gli esperimenti storici e la documentazione locale rimangono distinti dalla verifica di una nuova installazione.

## Artefatti che si ricostruiscono

| Elemento | Dove / come |
|---|---|
| VM Ubuntu ARM64 | `infra/utm/vm.json`, preparatore ISO/immagine, script opzionale UTM e guida installazione |
| Dipendenze OS | `infra/guest/system-packages.txt`, installazione privilegiata esplicita nel guest |
| Motori originali | URL/commit/SHA-256 in `reproducibility/sources.lock.json`; scaricati e compilati localmente |
| Ambienti e solver | `requirements/`, bootstrap; inventari effettivi in `installation/` |
| DEM/Sentinel originali | URL/dimensioni/SHA in `reproducibility/snapshots/inputs.lock.json`; download o riuso verificato |
| Meteo e toponimi del fixture | Snapshot piccoli e licenze in `reproducibility/snapshots/ATTRIBUTION.md` |
| Prodotti e dashboard | `bootstrap.py demo`, `days`, `verify`; nessun output fisico inventato se manca un motore |
| Stato personale | Casi, annotazioni e viste creati nella propria VM; non pubblicati nel repository |

Il file di configurazione `runtime-v2.json` viene generato localmente: non copiare quello della macchina dello sviluppatore. Le chiavi SSH sono proprie dell’utente; non servono token GitHub per leggere il repository pubblico o chiavi commerciali per gli esempi.

## Cosa non viene pubblicato

- Chiavi private, credenziali, `.env`, seed personali, host keys, dischi `.utm/.qcow2/.img/.iso`, ambienti Python installati, cache e database di lavoro.
- Raster originali di centinaia di MB e immagini delle ortofoto regionali. Per i primi sono fissati i download; per le seconde è disponibile la consultazione WMS nei limiti dichiarati.
- Intera cronologia privata degli esperimenti e fotografie della UI che includono ortofoto con diritti di redistribuzione non verificati. Il primo commit pubblico è una fotografia curata del sorgente completo; la storia locale originale è preservata. Non si tratta di una riscrittura o eliminazione delle prove originali.

File e prove locali citati nei rapporti possono quindi non essere scaricabili da GitHub. I rapporti riportano esiti e identificativi; le nuove installazioni producono propri log e manifest. Non aggiungere automaticamente tutti i file ignorati per risolvere un link a un artefatto locale.

## Livelli di verifica

1. **Preparazione VM:** controllo digest immagine, seed senza password/chiavi private, ISO generata; distinto dal boot di una VM nuova.
2. **Ricostruzione del runtime in prefisso nuovo:** nuovi ambienti, motori e addons sotto la propria directory, nessun riferimento necessario a `m0` o al Mac; dati riusati solo con hash verificato. Può essere eseguita nella stessa VM e non dimostra da sola un’installazione su un secondo OS.
3. **Esecuzioni reali:** nuovi prodotti PROPAGATOR/HMC→REFlEx e nuova coppia nativa su72h, con check indipendenti di forma, valori, tempo e hash. Ripetizione tecnica sul fixture, non campioni indipendenti di eventi reali.
4. **Qualificazione scientifica/operativa:** resta separata e incompleta; terreno reale e ripetibilità non dimostrano accuratezza o efficacia sul campo. Vecchi FAIL e BLOCKED restano nei registri.

Gli esiti effettivi di questa consegna sono nel rapporto [PUBBLICAZIONE-GITHUB](../reports/PUBBLICAZIONE-GITHUB.md) e nella checklist ufficiale. Qualunque fase non eseguita deve apparire NOT RUN o BLOCKED. Il bootstrap non rende M5–M7 scientificamente completate.

## Licenze

HAZARDIA non assume una nuova licenza di distribuzione del proprio codice: vedere [NOTICE](../NOTICE.md). La pubblicazione del sorgente non autorizza a rimuovere diritti o attribuzioni. CIMA e GRASS mantengono le licenze upstream; il bootstrap li acquisisce separatamente. La patch REFlEx segue gli obblighi upstream ed è esplicitamente visibile; non viene presentata come versione originale CIMA. I dati conservano licenze e attribuzioni per fonte.

## Aggiornare il repository pubblico

La checkout di sviluppo può contenere nella propria storia immagini o prove che non devono essere pubblicate. Non usare un force-push di quella storia sul repository pubblico. Preparare invece il sorgente da un commit completo:

```sh
python3 scripts/prepare_publication.py --ref HEAD --output /percorso/nuova-esportazione
```

Lo strumento legge soltanto file presenti nel commit, esclude stato locale/media e bozza editoriale, controlla pattern noti di chiavi/token e genera `PUBLICATION.json` con hash di ogni file e commit sorgente. Non esegue push. Per gli aggiornamenti, applicare la nuova esportazione a una checkout fresca del repository pubblico, revisionare il diff, committare e fare un normale push che conservi i commit pubblici precedenti. Non copiare `.git` dalla storia privata e non modificare la visibilità del repository implicitamente. Il controllo di pattern non è una garanzia universale di assenza di segreti: la revisione del contenuto resta necessaria.


## Terreni e forzanti dinamiche
Ogni nuovo dominio conserva grid/manifest, finestre COG con ETag e SHA, arrays/DEM, source raw e campo meteo normalizzato, piano e risorse. Il job fissa gli asset per hash. Una riacquisizione Open-Meteo successiva non è un replay esatto; per confronti controllati riusare il forcing_id del primo caso e identici inizio/terreno/seme. Il batch UI ricalcola gli scenari selezionati sullo stesso campo di base e tempo; i cambi ipotetici sono espliciti. Gli input scientifici e lo stato dell’utente rimangono nella VM, non nel repository pubblico. [Report](../reports/DOMINI-DINAMICI-E-FORZANTI.md) e [ADR-0014](../reports/ADR-0014-dynamic-terrain-and-forcing.md) documentano le assunzioni non calibrate e le prove reali; la nuova copertura tecnica non chiude M5–M7.
