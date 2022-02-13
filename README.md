# Elaborazione Delle Immagini 

## 👥 Partecipanti 
* [852239] **Mattia Napoli**
* [851905] **Michele Angelo Marcucci**
* [851649] **Eleonora Cicalla**


## 🔹 Table of content

* Approccio teorico
* Scelta del classificatore e delle features
* Processing del frame
* Risultati
* Codice ed installazione

## 🔸 Approccio teorico

**Obiettivo**: rilevare e segmentare le regioni di pelle umana

Siamo partiti dal capire come "trovare" la pelle in un'immagine cercandola tra gli spazi colore. Tuttavia si è dimostrato essere un metodo poco preciso e abbastanza deludente nei risultati.

Siamo passati quindi a valutare l'idea di usare un classificatore [...]



## 🔸 Classificatore e features

[...]

## 🔸 Processing del frame
Prendiamo come esempio questo frame:
![](docs/init.png)

Le operazioni possiamo suddividerle in 3 macro-categorie:

* Preprocessing
* Processing
* Postprocessing

### Preprocessing
Il preprocessing del frame comprende le seguenti operazioni:

- Adaptive gamma correction:
- White balance: 
- Erase colors: 

### Processing
Il processing del frame è svolto principalemente attraverso il classificatore [...]

### Postprocessing
Il postprocessing consiste nel [...] perchè [...]

![](docs/processing.png)

### Prove e correzioni
Dato che la maschera e il postprocessing rilevano anche una parte di pixel non-skin come skin nello sfondo (causate da ombre, rumore e simili)
abbiamo pensato di aggiungere una funzione che prima di creare la maschera, fa una grossolana individuazione dei pixel "nuovi" rispetto allo sfondo (attraverso una dilate lasciamo molto margine di errore per evitare di non selezionare tutto il foreground). 

**Vantaggi**: abbiamo verificato la quasi totale eliminazione degli "artefatti" che si creano nello sfondo dei video processati.

Ecco un esempio di pre-maschera
![](docs/differences.png)

**Contro**: Non sempre la maschera è perfetta e capita che molti pixel di pelle ne restino esclusi.

**Decisione finale**: Abbiamo deciso di non usare questa funzione dato che in molti test il risultato, pur senza artefatti nello sfondo, è risultato impreciso nella segmentazione della pelle.


## 🔸 Risultati

I risultati sono visualizzabili qui: [Video](docs/final.m4v)

## 🔸 Codice ed installazione

Consultare [INSTALL.md](docs/INSTALL.md)
