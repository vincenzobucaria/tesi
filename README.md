<b>UPDATE</b>

Lo script <b>network-generator.py</b> permette di automatizzare il processo di costruzione della rete,
mediante il file di testo network.txt è possibile definire la topologia della rete, il file properties.txt permette di definire
le proprietà di connessione tra i vari router di frontiera.


<b>La sintassi di ogni riga del file network.txt deve essere la seguente:</b>

NODENAME LAN SUBNET_TYPE

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

<b>La sintassi di ogni riga del file properties.txt deve essere la seguente:</b>

LAN1 LAN2 RITARDO BANDA

<b>LAN1</b> specifica la prima LAN target<br>
<b>LAN2</b> specifica la seconda LAN target<br>
<b>RITARDO</b> specifica la latenza che sussiste tra i router di frontiera delle due LAN target. Il valore è in millisecondi (ms).
<b>BANDA</b> specifica la massima larghezza di banda disponibile nell'arco che collega le due LAN target.

   
________________________________________________________________________







<b>nat-network.py</b>


La rete è composta da 3 sottoreti, due di queste sono sottoreti che utilizzano IP privati della classe 10.0.0.x, la restante sottorete ospita due server muniti di IP pubblici (9.0.0.2 e 9.0.0.3), questi potranno essere contattati.


Per visualizzare la topologia di rete si può ricorrere al seguente [link](http://demo.spear.narmox.com/app/?apiurl=demo#!/mininet?data=%7B%22dump%22%3A%22%3CHost%20h0%3A%20h0-eth0%3A10.0.0.2%20pid%3D16790%3E%20%5Cn%3CHost%20h1%3A%20h1-eth0%3A10.0.0.3%20pid%3D16792%3E%20%5Cn%3CHost%20h2%3A%20h2-eth0%3A10.0.0.4%20pid%3D16794%3E%20%5Cn%3CHost%20h3%3A%20h3-eth0%3A10.0.0.5%20pid%3D16796%3E%20%5Cn%3CLinuxRouter%20r1%3A%20r1-eth0%3A10.0.0.1%2Cr1-eth1%3A5.0.1.1%20pid%3D16800%3E%20%5Cn%3CLinuxRouter%20r2%3A%20r2-eth0%3A10.0.0.1%2Cr2-eth1%3A5.0.1.3%20pid%3D16802%3E%20%5Cn%3CLinuxRouter%20r3%3A%20r3-eth1%3A9.0.0.1%2Cr3-eth2%3A5.0.1.2%20pid%3D16804%3E%20%5Cn%3CHost%20server1%3A%20server1-eth0%3A9.0.0.2%20pid%3D16806%3E%20%5Cn%3CHost%20server2%3A%20server2-eth0%3A9.0.0.3%20pid%3D16808%3E%20%5Cn%3CHost%20x0%3A%20x0-eth0%3A10.0.0.6%20pid%3D16810%3E%20%5Cn%3CHost%20x1%3A%20x1-eth0%3A10.0.0.7%20pid%3D16812%3E%20%5Cn%3CHost%20x2%3A%20x2-eth0%3A10.0.0.8%20pid%3D16814%3E%20%5Cn%3CHost%20x3%3A%20x3-eth0%3A10.0.0.9%20pid%3D16816%3E%20%5Cn%3COVSSwitch%20s1%3A%20lo%3A127.0.0.1%2Cs1-eth1%3ANone%2Cs1-eth2%3ANone%2Cs1-eth3%3ANone%2Cs1-eth4%3ANone%2Cs1-eth5%3ANone%20pid%3D16821%3E%20%5Cn%3COVSSwitch%20s2%3A%20lo%3A127.0.0.1%2Cs2-eth1%3ANone%2Cs2-eth2%3ANone%2Cs2-eth3%3ANone%2Cs2-eth4%3ANone%2Cs2-eth5%3ANone%20pid%3D16824%3E%20%5Cn%3COVSSwitch%20s3%3A%20lo%3A127.0.0.1%2Cs3-eth1%3ANone%2Cs3-eth2%3ANone%2Cs3-eth3%3ANone%20pid%3D16827%3E%20%5Cn%3COVSSwitch%20s4%3A%20lo%3A127.0.0.1%2Cs4-eth1%3ANone%2Cs4-eth2%3ANone%2Cs4-eth3%3ANone%20pid%3D16830%3E%20%5Cn%3COVSController%20c0%3A%20127.0.0.1%3A6653%20pid%3D16783%3E%22%2C%22links%22%3A%22h0-eth0%3C-%3Es1-eth1%20(OK%20OK)%20%5Cnh1-eth0%3C-%3Es1-eth2%20(OK%20OK)%20%5Cnh2-eth0%3C-%3Es1-eth3%20(OK%20OK)%20%5Cnh3-eth0%3C-%3Es1-eth4%20(OK%20OK)%20%5Cnr1-eth0%3C-%3Es1-eth5%20(OK%20OK)%20%5Cnr1-eth1%3C-%3Es3-eth1%20(OK%20OK)%20%5Cnr2-eth0%3C-%3Es2-eth5%20(OK%20OK)%20%5Cnr2-eth1%3C-%3Es3-eth2%20(OK%20OK)%20%5Cnr3-eth2%3C-%3Es3-eth3%20(OK%20OK)%20%5Cnr3-eth1%3C-%3Es4-eth3%20(OK%20OK)%20%5Cnserver1-eth0%3C-%3Es4-eth1%20(OK%20OK)%20%5Cnserver2-eth0%3C-%3Es4-eth2%20(OK%20OK)%20%5Cnx0-eth0%3C-%3Es2-eth1%20(OK%20OK)%20%5Cnx1-eth0%3C-%3Es2-eth2%20(OK%20OK)%20%5Cnx2-eth0%3C-%3Es2-eth3%20(OK%20OK)%20%5Cnx3-eth0%3C-%3Es2-eth4%20(OK%20OK)%22%2C%22positions%22%3A%22%7B%5C%22objects%5C%22%3A%5B%7B%5C%22type%5C%22%3A%5C%22switch%5C%22%2C%5C%22id%5C%22%3A%5C%22s1%5C%22%2C%5C%22x%5C%22%3A-10.235400199890137%2C%5C%22y%5C%22%3A323.36151123046875%7D%2C%7B%5C%22type%5C%22%3A%5C%22switch%5C%22%2C%5C%22id%5C%22%3A%5C%22s2%5C%22%2C%5C%22x%5C%22%3A191.40969848632812%2C%5C%22y%5C%22%3A57.402801513671875%7D%2C%7B%5C%22type%5C%22%3A%5C%22switch%5C%22%2C%5C%22id%5C%22%3A%5C%22s3%5C%22%2C%5C%22x%5C%22%3A-95.70130157470703%2C%5C%22y%5C%22%3A144.00909423828125%7D%2C%7B%5C%22type%5C%22%3A%5C%22switch%5C%22%2C%5C%22id%5C%22%3A%5C%22s4%5C%22%2C%5C%22x%5C%22%3A-378%2C%5C%22y%5C%22%3A106%7D%2C%7B%5C%22type%5C%22%3A%5C%22router%5C%22%2C%5C%22id%5C%22%3A%5C%22r1%5C%22%2C%5C%22x%5C%22%3A-131.25166873876435%2C%5C%22y%5C%22%3A273.50048828125%7D%2C%7B%5C%22type%5C%22%3A%5C%22router%5C%22%2C%5C%22id%5C%22%3A%5C%22r2%5C%22%2C%5C%22x%5C%22%3A63.19293041284699%2C%5C%22y%5C%22%3A111.79460144042969%7D%2C%7B%5C%22type%5C%22%3A%5C%22router%5C%22%2C%5C%22id%5C%22%3A%5C%22r3%5C%22%2C%5C%22x%5C%22%3A-195.9281671518503%2C%5C%22y%5C%22%3A125.62699890136719%7D%2C%7B%5C%22type%5C%22%3A%5C%22server%5C%22%2C%5C%22id%5C%22%3A%5C%22h0%5C%22%2C%5C%22x%5C%22%3A160.9925405384843%2C%5C%22y%5C%22%3A399%7D%2C%7B%5C%22type%5C%22%3A%5C%22server%5C%22%2C%5C%22id%5C%22%3A%5C%22h1%5C%22%2C%5C%22x%5C%22%3A189.9925405384843%2C%5C%22y%5C%22%3A353%7D%2C%7B%5C%22type%5C%22%3A%5C%22server%5C%22%2C%5C%22id%5C%22%3A%5C%22h2%5C%22%2C%5C%22x%5C%22%3A211.9925405384843%2C%5C%22y%5C%22%3A291%7D%2C%7B%5C%22type%5C%22%3A%5C%22server%5C%22%2C%5C%22id%5C%22%3A%5C%22h3%5C%22%2C%5C%22x%5C%22%3A179.63813990371867%2C%5C%22y%5C%22%3A239.31849670410156%7D%2C%7B%5C%22type%5C%22%3A%5C%22server%5C%22%2C%5C%22id%5C%22%3A%5C%22server1%5C%22%2C%5C%22x%5C%22%3A-468.00745946151574%2C%5C%22y%5C%22%3A13%7D%2C%7B%5C%22type%5C%22%3A%5C%22server%5C%22%2C%5C%22id%5C%22%3A%5C%22server2%5C%22%2C%5C%22x%5C%22%3A-544.0074594615157%2C%5C%22y%5C%22%3A93%7D%2C%7B%5C%22type%5C%22%3A%5C%22server%5C%22%2C%5C%22id%5C%22%3A%5C%22x0%5C%22%2C%5C%22x%5C%22%3A404.99254053848426%2C%5C%22y%5C%22%3A47%7D%2C%7B%5C%22type%5C%22%3A%5C%22server%5C%22%2C%5C%22id%5C%22%3A%5C%22x1%5C%22%2C%5C%22x%5C%22%3A431.99254053848426%2C%5C%22y%5C%22%3A96%7D%2C%7B%5C%22type%5C%22%3A%5C%22server%5C%22%2C%5C%22id%5C%22%3A%5C%22x2%5C%22%2C%5C%22x%5C%22%3A443.99254053848426%2C%5C%22y%5C%22%3A145%7D%2C%7B%5C%22type%5C%22%3A%5C%22server%5C%22%2C%5C%22id%5C%22%3A%5C%22x3%5C%22%2C%5C%22x%5C%22%3A474.99254053848426%2C%5C%22y%5C%22%3A197%7D%5D%7D%22%7D)

!!!!!!!!Attenzione, il tool online visualizza in maniera errata gli indirizzi IP sulle interfacce, è possibile verificarne la correttezza eseguendo il comando ifconfig sui router!!!!!!!!!!!!

Nelle LAN non è abilitato il traffic control di mininet, ciò vale a dire che i link tra i nodi costituenti le LAN sono ideali, i link WAN
invece simulano condizioni reali (banda limitata, delay e jitter realistici, non ho previsto invece un packet loss).

I due router delle due sottoreti che fanno uso di IP privati implementano il NAT a cono ristretto con restrizione sulle porte, ho scelto questa implementazione in quanto è la più restrittiva. E' possibile verificarne il funzionamento come quanto segue:

Sono presenti tre script python, quello denominato udp dev'essere eseguito da uno (o più) host di una delle due sottoreti private (o entrambe), semplicemente lo script manda dei datagrammi al server 9.0.0.2, che dovrà eseguire lo script udp2.py; questo si comporterà da server STUN, rispondendo ad ogni richiesta dell'host e indicandogli l'IP e la porta sorgente che il server ha rilevato, si potrà notare come la traduzione dell'indirizzo IP funziona correttamente. Successivamente, il server che esegue udp2.py invierà al server 9.0.0.3, che dovrà eseguire lo script udp3.py, un datagramma contenente i riferimenti all'host che ha contattato 9.0.0.2, quindi tenterà di rispondere direttamente all'host, tuttavia, poichè il NAT è a cono ristretto con restrizione sulle porte, non ci riuscirà. 


Di seguito i comandi che devono essere eseguiti sul terminale (indico con # i commenti), se GitHub dovesse rompere la formattazione, si prega di far riferimento al file istruzioni:

sudo python3 nat-network.py
h0 ping server1 									#è possibile verificare che h0 può raggiungere il server pubblico server1, può raggiungere anche 														server2
server1 ping h0										#il viceversa non è possibile, h0 non sarà ragguingibile dall'esterno della sua sottorete in quanto 													sotto NAT
h0 ping x0 											#x0 non sarà ovviamente ragguingibile da parte di h0 in quanto sotto NAT
xterm h0 server1 server2							#apre i terminali delle macchine h0, server1 e su server2

#Da eseguire in ordine

#Sul terminale di server1:
python3 udp2.py
#Sul terminale di server2:
python3 udp3.py
#Sul terminale di h0:
python3 udp.py

#Come si potrà notare, h0 riceve la risposta soltanto dal server1, poichè appunto il NAT implementato è a cono ristretto e con restrizione sulla porta.







