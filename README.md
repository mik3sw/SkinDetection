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
> Consigliamo di usare la flag --multi (o -m) per processare il video passato in input per un incremento sostanziale delle prestazioni.
> 
> Esempio: **python3 main.py -f file.mp4 --multi**
> 
> Esempio **python3 main.py -f file.mp4 -m**


```
usage: main.py [-h] [-f FILE] [--m] [-i]

== PROGETTO ELABORAZIONE DELLE IMMAGINI ==

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  video file to process
  -m, --multi           try multithread
  -i, --info            show info
  

Sample usage:
main.py                         | launch interactive cam session
main.py -f filename             | process given file
main.py -f filename --multi     | process given file using multithreading

```

