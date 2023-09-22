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

## Avvio dello script

A setup terminato, è possibile avviare lo script mediante il seguente comando da eseguire sulla shell
```bash
$ sudo python3 network-generator.py
```

In caso di errore da parte di Mininet può essere utile un reset mediante
```bash
$ sudo mn -c
$ sudo fuser -k 6653/tcp

```

