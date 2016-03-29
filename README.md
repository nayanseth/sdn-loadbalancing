# SDN Load Balancing

**Goal**: To perform load balancing on any topology using SDN Controller i.e. Floodlight.

## System Details

1. SDN Controller - [Floodlight](http://www.projectfloodlight.org/floodlight/)
2. Virtual Network Topology - [Mininet](http://mininet.org)
3. Evaluation & Analysis - [Wireshark](http://wireshark.org), [iPerf](http://iperf.fr)
5. OS - [Ubuntu 14.04 LTS](http://ubuntu.com)

## Implementation Approach

**Base**: Make use of REST APIs to collect operational information of the topology and its devices.

1. Enable statistics collection (TX i.e. Transmission Rate, RX  i.e. Receiving Rate, etc)
2. Find information about hosts connected such as their IP, Switch to which they are connected, MAC Addresses, Port mapping, etc
3. Obtain path/route information from Host 1 to Host 2 i.e. the hosts between load balancing has to be performed.
4. Find total link cost for all these paths between Host 1 and Host 2.
5. The flows are created depending on the minimum transmission cost of the links at the given time. 
6. Based on the cost, the best path is decided and static flows are pushed into each switch in the current best path. Information such as in-port, out-port, src ip, dst ip, src mac, dst mac is fed to the flows.
7. The program continues to update this information every minute thereby making it dynamic.

##Results We Achieved

| Transfer (Gbytes) |	B/W(Gbits) |
|-------------------|------------:|
| 20 |	17.2 |
| 24.9 |	21.4 |
| 19.5 |	21.1 |
| 25 |	21.4  |
| 25 | 21.5  |
|**Average = 22.8 **|	**Average = 20.52**|
*iPerf H1 to H3 Before Load Balancing*

| Transfer (Gbytes) |	B/W(Gbits) |
|-------------------|------------:|
|25.3 |	21.7|
|24.1 |	20.7|
|24.5 |	21.1|
|21.5 |	18.5|
|19.9 | 17.1 |
|**Average = 23.06 **|	**Average = 19.82r**|
*iPerf H1 to H4 Before Load Balancing*


##How To Use It?

###Requirements

1. Download Floodlight
2. Install Mininet
3. Install OpenVSwitch

###Running The Program

*Note: We are performing load balancing between h1, h3 and h4 at the moment. The best path for both is via Switch 1 Port 4. This is the best path selected by OpenFlow protocol. Please see the topology and why is it Port 4.*

1. Remove the official Floodlight Load Balancer
2. Run the floodlight.sh shell script
3. Run Floodlight
4. Run the fat tree topology i.e. topology.py using Mininet

```
sudo mn --custom topology.py --topo mytopo --controller=remote,ip=127.0.0.1,port=6653
```

*Note: Provide correct path to topology.py in command*

![alt tag](https://raw.githubusercontent.com/nayanseth/sdn-floodlight-loadbalancing/master/assets/topologies/fat-tree-topology.png)

*Note: Switch ID have been added next to Switches. Numbers near the links are the port numbers. These port numbers may change when you run mininet. For us this is the port numbers. From now on all references in the code will be with respect to this topology*

<ol start=5>
<li>Type the following command in Mininet</li>

```
xterm h1 h1
```

<li>In first console of h1 type, ```ping 10.0.0.3```</li>
<li>In second console of h1 type, ```ping 10.0.0.4```</li>
<li>On Terminal open a new tab ```Ctrl + Shift + T``` and type ```sudo wireshark```</li>
<li>In wireshark, go to Capture->Interfaces and select ```s1-eth4``` and start the capture.</li>
<li>In filters section in wireshark type ```ip.addr==10.0.0.3``` and check if you are receiving packets for h1 -> h3. Do same thing for h1->h4. Once you see packets, you can figure that this is the best path.</li>
<li>But to confirm it is, repeat the above two steps for ```s1-eth3``` and you will find that no packets are transmitted to this port. Only packets it will receive will be broadcast and multicast. Ignore them.</li>
<li>Now in the second console of xterm of h1, stop pinging h4. Our goal is to create congestion on the best path of h1->h3, h1->h4 and vice versa and h1 pinging h3 is enough for that</li>
<li>Go to your Terminal and open a new tab and run the **loadbalancer.py** script</li>
<li>Provide input arguments such as host 1, host 2 and host 2's neighbor in integer format like for example *1,4,3* where 1 is host 1, 4 is host 2 and 3 is host 2's neighbor. Look at the topology above and you will find that these hosts are nothing but h1, h4 and h3 respectively.</li>
<li>The loadbalancer.py performs REST requests, so initially the link costs will be 0. Re-run the script few times. This may range from 1-10 times. This is because statistics need to be enabled. After enabling statistics, it takes some time to gather information. Once it starts updating the transmission rates, you will get the best path and the flows for best path will be statically pushed to all the switches in the new best route. Here the best route is for h1->h4 and vice versa</li>
<li>To check the flows, perform a REST GET request to http://127.0.0.1:8080/wm/core/switch/all/flow/json</li>
<li>Now on second console of h1 type ```ping 10.0.0.4```</li>
<li>Go to wireshark and monitor interface ```s1-eth4``` with the filter ```ip.addr==10.0.0.x``` where x is 3 and 4. You will find 10.0.0.3 packets but no 10.0.0.4 packets</li>
<li>Stop the above capture and now do the capture on ```s1-eth3, s21-eth1, s21-eth2, s2-eth3``` with the filter ```ip.addr==10.0.0.x``` where x is 3 and 4. You will find 10.0.0.4 packets but no 10.0.0.3 packets</li>


*Load Balancing Works!*
