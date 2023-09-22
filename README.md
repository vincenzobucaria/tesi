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

### Caratteristiche generali della rete
E' possibile caratterizzare la rete andando a modificare il file di testo ```network.txt```.
Al momento è presente un limite di 255 nodi istanziabili.
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

![Testo alternativo](default_topo.png)


Il nome dei nodi è definibile a piacere, mentre il nome dei vari router e switch è generato automaticamente, i prefissi permettono di identificare la tipologia di router.   
 Con ```ri``` ci si riferisce a ```router domestici```,  
 ```r``` rappresenta il router dell'ISP  
 ```re``` rappresenta un router di frontiera  

### Struttura del file network.txt

<b>La sintassi di ogni riga del file network.txt deve essere la seguente (i parametri tra [] sono opzionali:</b>

NODENAME LAN SUBNET_TYPE [SERVER]

<b>NODENAME</b> specifica il nome del nodo <br>
<b>LAN</b> specifica la subnet di appartenenza del nodo <br>
<b>SUBNET_TYPE</b> è un parametro scelto tra [public, full_cone, port_restricted, restricted_cone, symmetric]. Questo parametro viene attribuito alla LAN specificata
alla prima dichiarazione, dichiarazioni incongruenti successive saranno ignorate.
<b>SUBNET_TYPE</b> può essere:
1) <b>public</b>, in questo caso a ogni nodo della sottorete è assegnato un IP pubblico, dunque ogni nodo è raggiungibile dall'esterno.
2) <b>symmetric</b>, ogni nodo ha un ip privato, il router di frontiera implementa il nat simmetrico
3) <b>full_cone</b>, ogni nodo ha un ip privato, il router di frontiera implementa il nat a cono pieno
4) <b>restricted_cone</b>, ogni nodo ha un ip privato, il router di frontiera implementa il nat a cono ristretto
5) <b>port_restricted</b>, ogni nodo ha un ip privato, il router di frontiera implementa il nat a cono ristretto con restrizione sulla porta
<b>SERVER</b> permette di flaggare uno specifico nodo come server



 
    






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

