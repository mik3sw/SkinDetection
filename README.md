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

Siamo passati quindi a



## 🔸 Classificatore e features

## 🔸 Processing del frame

## 🔸 Risultati

## 🔸 Codice ed installazione

Per prima cosa clonate la repo GitHub con:

```
git clone https://github.com/mik3sw/SkinDetection.git
```

Installate le dipendenze necessarie con:

```
cd SkinDetection

pip install -r requirements.txt
```

Eseguite il file <code>setup.py</code> per scaricare il Dataset (operazione automatica). A seconda dell'harware che avete questa operazione può richiedere qualche minuto: il processo di unzipping del dataset (~500 MB) richiede tempo.

```
python3 setup.py
```

Infine eseguite il programma attraverso il file <code>main.py</code>, ecco gli argomenti accettati:

```
usage: main.py [-h] [-f FILE] [--ffmpeg] [-i]

== PROGETTO ELABORAZIONE DELLE IMMAGINI ==

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  video file to process
  --ffmpeg              use ffmpeg library to speed up the processing
  -i, --info            show info

Sample usage:
main.py                         | launch interactive cam session
main.py -f filename             | process given file
main.py -f filename --ffmpeg    | process given file using ffmpeg
```
### ⚠️ Attenzione! ⚠️
L'argomento **--ffmpeg è sperimentale**: utilizza la libreria ffmpeg che dovrete installare attraverso un package manager, tuttavia non tutti i sistemi sembrano supportare bene la nostra funzione, infatti **funziona solo su Linux** (testato su Arch e derivati), pertanto potete provare ad usarla ma non è garantino che funzioni. Il resto è funzionante, la lasciamo solo perchè il guadagno in performance è sostanziale.
