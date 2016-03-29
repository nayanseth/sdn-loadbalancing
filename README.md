# SDN Load Balancing

**Goal**: To perform load balancing on any topology using SDN Controller i.e. Floodlight.

## System Details

1. SDN Controller - Floodlight
2. Mininet
3. iPef
4. Wireshark
5. OS - Ubuntu 14.04 LTS

## Implementation Approach

**Base**: Make use of REST APIs to collect operational information of the topology and its devices.

1. Enable statistics collection (TX i.e. Transmission Rate, RX  i.e. Receiving Rate, etc)
2. Find information about hosts connected such as their IP, Switch to which they are connected, MAC Addresses, Port mapping, etc
3. Obtain path/route information from Host 1 to Host 2 i.e. the hosts between load balancing has to be performed.
4. Find total link cost for all these paths between Host 1 and Host 2.
5. The flows are created depending on the minimum transmission cost of the links at the given time. 
6. Based on the cost, the best path is decided and static flows are pushed into each switch in the current best path. Information such as in-port, out-port, src ip, dst ip, src mac, dst mac is fed to the flows.
7. The program continues to update this information every minute thereby making it dynamic.

##How To Use It?

###Requirements

1. Download [Floodlight](http://floodlight.org/)
2. Install Mininet
3. Install OpenVSwitch

###Running The Program

1. Remove the official Floodlight Load Balancer
2. Run the floodlight.sh shell script
3. Run Floodlight
4. Run the fat tree topology i.e. topology.py using Mininet

![alt tag](https://raw.githubusercontent.com/nayanseth/sdn-floodlight-loadbalancing/master/assets/topologies/fat-tree-topology.png)

5\. Type the following command in Mininet

```
xterm h1 h1
```

6\. In first console of h1 type, ```ping 10.0.0.3```
7\. In second console of h1 type, ```ping 10.0.0.4```
