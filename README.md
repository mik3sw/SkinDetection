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

<img src="docs/imgs/img1.jpg", align = "right",width="300" height="200">
Prendiamo come esempio la foto a destra: <br>le operazioni di processing possiamo suddividerle in 4 macro-categorie:

* Creazione pre-maschera
* Preprocessing
* Processing
* Postprocessing

### Creazione pre-maschera
In molti test abbiamo notato che la maschera fatta attraverso il classificatore rileva anche una parte di pixel "falsi positivi" (quindi rileva pixel non di pelle come pelle) nello sfondo. Questo è causato da ombre, rumore e simili che in fase di preprocessing non riescono a venire eliminati.
Abbiamo quindi pensato di aggiungere una funzione (prima del preprocessing) che prima di creare la maschera, fa una grossolana individuazione dei pixel "nuovi" rispetto allo sfondo (attraverso una dilate lasciamo molto margine di errore per evitare di non selezionare tutto il foreground). 
Quello che otteniamo è una pre-maschera, che scontorna (lasciando una sorta di aura intorno) tutto il foreground. 

**Vantaggi**: abbiamo verificato la quasi totale eliminazione degli "artefatti" che si creano nello sfondo dei video processati.

**Contro**: Non sempre la maschera è perfetta e capita che alcuni pixel di pelle ne restino esclusi.

**Decisione finale**: Abbiamo deciso usare questa funzione dato che in molti test il risultato è abbastanza preciso ed elimina gli artefatti nello sfondo.

### Preprocessing
Il preprocessing del frame comprende le seguenti operazioni (eseguite iterativamente):

**Adaptive gamma correction**

Original             |  Gamma correction
:-------------------------:|:-------------------------:
![](docs/imgs/img1.jpg)  |  ![](docs/imgs/gamma_correction.jpg)


**White balance**

Gamma correction             |  White balance
:-------------------------:|:-------------------------:
![](docs/imgs/gamma_correction.jpg)  |  ![](docs/imgs/white_balance.jpg)


**Erase colors**

White balance             |  Erase colors
:-------------------------:|:-------------------------:
![](docs/imgs/white_balance.jpg)  |  ![](docs/imgs/erase_colors.jpg)




### Processing
Il processing del frame è svolto principalemente attraverso il classificatore [...]

Original                   |  Processed
:-------------------------:|:-------------------------:
![](docs/imgs/img1.jpg)  |  ![](docs/imgs/skin_detected_nopost.jpg)

### Postprocessing
Il postprocessing consiste nel [...] perchè [...]

Processed                  |  Postprocessing
:-------------------------:|:-------------------------:
![](docs/imgs/skin_detected_nopost.jpg)  |  ![](docs/imgs/skin_detected.jpg)



## 🔸 Risultati

I risultati sono visualizzabili qui: [Video](docs/final.m4v)

## 🔸 Codice ed installazione

Consultare [INSTALL.md](docs/INSTALL.md)
