# SDN Load Balancing

## Note: Project is no longer being maintained. Have pushed a recent fix to fix the parsing issues. The script will work as long as the environment is setup correctly. The script is not at all optimized and was written to get a proof of concept.

**Goal**: To perform load balancing on any fat tree topology using SDN Controller i.e. Floodlight and OpenDaylight.

*Note: The goal is to perform load balancing but at the same time ensure that the latency is minimum. We are using dijkstra's algorithm to find multiple paths of same length which enables us to reduce the search to a small region in the fat tree topology. It is also important to note that OpenDaylight by default forwards traffic to all ports. So specific rules might need to be pushed to get a proper load balancing output. Currently the program simply finds the path with least load and forwards traffic on that path.*

**Code is be a bit un-optimized, especially for the flow rules being pushed in ODL.**

## System Details

1. SDN Controller - [Floodlight v1.2](http://www.projectfloodlight.org/floodlight/) or [OpenDaylight Beryllium SR1](http://www.opendaylight.org/)
2. Virtual Network Topology - [Mininet](http://mininet.org)
3. Evaluation & Analysis - [Wireshark](http://wireshark.org), [iPerf](http://iperf.fr)
5. OS - [Ubuntu 14.04 LTS](http://ubuntu.com)

## Implementation Approach

**Base Idea**: Make use of REST APIs to collect operational information of the topology and its devices.

1. Enable statistics collection in case of Floodlight (TX i.e. Transmission Rate, RX  i.e. Receiving Rate, etc). This step is not applicable for OpenDaylight
2. Find information about hosts connected such as their IP, Switch to which they are connected, MAC Addresses, Port mapping, etc
3. Obtain path/route information (using Dijkstra thereby limiting search to shortest paths and only one segment of fat tree topology) from Host 1 to Host 2 i.e. the hosts between load balancing has to be performed.
4. Find total link cost for all these paths between Host 1 and Host 2. In case of Floodlight it is the TX and RX but for OpenDaylight it gives only transmitted data. So subsequent REST requests are made to compute this. This adds latency to the application (when using OpenDaylight).
5. The flows are created depending on the minimum transmission cost of the links at the given time. 
6. Based on the cost, the best path is decided and static flows are pushed into each switch in the current best path. Information such as In-Port, Out-Port, Source IP, Destination IP, Source MAC, Destination MAC is fed to the flows.
7. The program continues to update this information every minute thereby making it dynamic.

## Results We Achieved


| Transfer (Gbytes) - BLB |	B/W(Gbits) - BLB  | Transfer (Gbytes) - ALB |	B/W(Gbits) - ALB |
|:-------------------:|:------------:|:------------------:|:-----------:|
|15.7 |	13.5|38.2 | 32.8|
|21.9 |	18.8|27.6 | 32.3|
|24.6 |	21.1|40.5 | 34.8|
|22.3 |	19.1|40.8 | 35.1|
|39.8 | 34.2 |16.5 | 14.2| 
| **Average = 24.86** |	**Average = 21.34**|**Average = 32.72** |	**Average = 29.84**|

*iPerf H1 to H3 Before Load Balancing (BLB) and After Load Balancing (ALB)*

| Transfer (Gbytes) - BLB |	B/W(Gbits) - BLB  | Transfer (Gbytes) - ALB |	B/W(Gbits) - ALB |
|:-------------------:|:------------:|:------------------:|:-----------:|
|18.5 |	15.9|37.2 |	31.9|	
|18.1 |	15.5|39.9 |	34.3|	
|23.8 |	20.2|40.2 |	34.5|
|17.8 |	15.3|40.3 |	34.6 |
|38.4 | 32.9|18.4 | 15.8 |
| **Average = 23.32** |	**Average = 19.96** | **Average = 35.2** |	**Average = 30.22**|


*iPerf H1 to H4 Before Load Balancing (BLB) and After Load Balancing (ALB)*

|Min |Avg |Max|Mdev|
|:----:|:----:|:---:|:-----:|
|0.049 | 0.245 | 4.407 | 0.807 |
|0.050 | 0.155 | 4.523 | 0.575 |
|0.041 | 0.068 | 0.112 | 0.019 |
|0.041 | 0.086 | 0.416 | 0.066 |
|0.018 | 0.231 | 4.093 | 0.759 |
|**Avg:0.0398**|**Avg:0.157**|**Avg:2.7102**|**Avg:0.4452**|

*Ping from H1 to H4 Before Load Balancing*

|Min |Avg |Max|Mdev|
|:----:|:----:|:---:|:-----:|
|0.039 | 0.075 | 0.407 | 0.068|
|0.048 | 0.078 | 0.471 | 0.091|
|0.04 | 0.072 | 0.064 | 0.199 |
|0.038 | 0.074 | 0.283 | 0.039|
|0.048 | 0.099 | 0.509 | 0.108 |
|**Avg:0.0426**|**Avg:0.0796**|**Avg:0.3468**|**Avg:0.101**|

*Ping from H1 to H4 After Load Balancing*

## How To Use It?

### Video Demo

<a href="http://www.youtube.com/watch?v=3C1Du32FNLo" target="_blank"><img src="http://img.youtube.com/vi/3C1Du32FNLo/0.jpg" 
alt="Video Demo" width="240" height="180" border="10" /></a>

### Requirements

1. Download Floodlight (v1.2) / OpenDaylight (Beryllium SR1)
2. Install Mininet (v2.2.1)
3. Install OpenVSwitch

### Running The Program (OpenDaylight)

1. Download the distribution package from [OpenDaylight](http://opendaylight.org/downloads). Next unzip the folder. 
2. In Terminal, change directory to the distribution folder and run ```./bin/karaf```. 
3. Run Mininet ```sudo mn --custom topology.py --topo mytopo --controller=remote,ip=127.0.0.1,port=6633```
4. Perform ```pingall``` a couple of times till no packet loss occurs. 
5. Next run the odl.py script and specify the input. Read the Floodlight instructions to get better insight on what is happening and what input to feed in.

### Running The Program (Floodlight)

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

5. Type the following command in Mininet

	```
	xterm h1 h1
	```
	
6. In first console of h1 type, ``` ping 10.0.0.3 ```
7. In second console of h1 type, ``` ping 10.0.0.4 ```
8. On Terminal open a new tab ``` Ctrl + Shift + T ``` and type ``` sudo wireshark ```
9. In wireshark, go to Capture->Interfaces and select ``` s1-eth4 ``` and start the capture.
10. In filters section in wireshark type ``` ip.addr==10.0.0.3 ``` and check if you are receiving packets for h1 -> h3. Do same thing for h1->h4. Once you see packets, you can figure that this is the best path.
11. But to confirm it is, repeat the above two steps for ``` s1-eth3 ``` and you will find that no packets are transmitted to this port. Only packets it will receive will be broadcast and multicast. Ignore them.
12. Now in the second console of xterm of h1, stop pinging h4. Our goal is to create congestion on the best path of h1->h3, h1->h4 and vice versa and h1 pinging h3 is enough for that
13. Go to your Terminal and open a new tab and run the **loadbalancer.py** script
14. Provide input arguments such as host 1, host 2 and host 2's neighbor in integer format like for example *1,4,3* where 1 is host 1, 4 is host 2 and 3 is host 2's neighbor. Look at the topology above and you will find that these hosts are nothing but h1, h4 and h3 respectively.
15. The loadbalancer.py performs REST requests, so initially the link costs will be 0. Re-run the script few times. This may range from 1-10 times. This is because statistics need to be enabled. After enabling statistics, it takes some time to gather information. Once it starts updating the transmission rates, you will get the best path and the flows for best path will be statically pushed to all the switches in the new best route. Here the best route is for h1->h4 and vice versa
16. To check the flows, perform a REST GET request to http://127.0.0.1:8080/wm/core/switch/all/flow/json
17. Now on second console of h1 type ``` ping 10.0.0.4 ```
18. Go to wireshark and monitor interface ``` s1-eth4 ``` with the filter ``` ip.addr==10.0.0.x ``` where x is 3 and 4. You will find 10.0.0.3 packets but no 10.0.0.4 packets
19. Stop the above capture and now do the capture on ``` s1-eth3, s21-eth1, s21-eth2, s2-eth3 ``` with the filter ``` ip.addr==10.0.0.x ``` where x is 3 and 4. You will find 10.0.0.4 packets but no 10.0.0.3 packets


*Load Balancing Works!*


