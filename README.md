# Emulazione di Overlay Networks in ambiente IoT


## Premessa

Il software è stato testato su Ubuntu 20.04, qualsiasi versione superiore a quella di test può essere utilizzata.
Non sono garantiti invece i risultati per versioni inferiori o per distribuzioni Linux diverse da Ubuntu (Mininet necessita di Ubuntu).


## Setup

Il repository può essere clonato con il seguente comando da eseguire sulla shell
```bash
$ git clone https://github.com/vincenzobucaria/tesi.git
```
Successivamente è possibile avviare il setup con i seguenti comandi
```bash
$ cd tesi
$ chmod +x setup.sh
$ ./setup.sh
```
Il setup provvederà a installare l'ultima versione di mininet e il suo modulo per Python3,
verrà inoltre installato gradle ed i moduli necessari al funzionamento del tunnel-rtc.

Una seconda parte del setup verrà eseguita una volta avviato lo script in python.
Infatti, in caso di primo avvio dello script, questo provvederà ad installare il modulo del kernel che
permetterà a Mininet di emulare il comportamento di NAT definito in RFC 3489 (full cone nat, symmetric nat,
port restricted cone nat, restricted cone nat).


## Definizione della rete

E' possibile caratterizzare la rete andando a modificare il file di testo ```network.txt```.

La caratterizzazione permette di scegliere quanti nodi istanziare per ogni LAN,
così come il tipo di NAT che il router di confine della LAN applicherà, mentre la topologia adottata è full-mesh per
quanto riguarda i router che emulano internet. Questo tipo di topologia permette di definire valori di banda e latenza
per ciascun collegamento p2p.

  
Ciascuna LAN privata presenterà un certo numero di nodi (che è possibile definire per mezzo del file) collegati ad uno switch,
a suo volta collegato al router di confine della LAN cui comportamento è quello di un router domestico non applicante NAT.

Il router domestico sarà a sua volta connesso al router del suo ISP, questo applicherà il tipo di NAT definito nel file,
dunque si connetterà ad internet.


Le LAN definite come pubbliche presentano un certo numero di nodi (sempre definibile dal file di testo) collegati ad uno switch,
a sua volta collegato direttamente con un router di frontiera (NON è applicato alcun tipo di NAT).


Di seguito la rappresentazione grafica della rete definita di default nel file

![Testo alternativo](default_topo)




### Ciao






## Avvio della simulazione

A setup terminato, è possibile avviare lo script mediante il seguente comando da eseguire sulla shell
```bash
$ sudo python3 network-generator.py
```

In caso di errore da parte di Mininet può essere utile un reset mediante
```bash
$ sudo mn -c
$ sudo fuser -k 6653/tcp

```

