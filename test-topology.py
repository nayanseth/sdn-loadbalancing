#!/usr/bin/python

from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch
from mininet.topo import Topo

class topology(Topo):

    def __init__(self):
        

        Topo.__init__(self)

        #Add hosts
        h1 = self.addHost('h1', cls=Host, ip='10.0.0.1')
        h2 = self.addHost('h2', cls=Host, ip='10.0.0.2')
	      h3 = self.addHost('h3', cls=Host, ip='10.0.0.3')
  	    h4 = self.addHost('h4', cls=Host, ip='10.0.0.4')
	      h5 = self.addHost('h5', cls=Host, ip='10.0.0.5')
	      h6 = self.addHost('h6', cls=Host, ip='10.0.0.6')
  
        #Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
	      s4 = self.addSwitch('s4')
	      s5 = self.addSwitch('s5')

        #Add links
	      self.addLink(h1,s2)
	      self.addLink(h2,s2)
	      self.addLink(h3,s3)
        self.addLink(h4,s3)
	      self.addLink(h5,s4)
	      self.addLink(h6,s4)
	      self.addLink(s1,s5)
	      self.addLink(s1,s2)
	      self.addLink(s1,s3)
        self.addLink(s5,s3)
	      self.addLink(s5,s4)
	
topos = { 'mytopo': (lambda: topology() ) }
