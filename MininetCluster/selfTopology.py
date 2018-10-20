#!/usr/bin/python

from mininet.examples.cluster import RemoteHost, RemoteLink, RemoteOVSSwitch
from mininet.net import Mininet
#import os
from mininet.net import CLI

def topology():
  
    print('Creating Mininet Topology...\n')
    net = Mininet( host=RemoteHost, link=RemoteLink, switch=RemoteOVSSwitch )

    print('Creating hosts h1 (20.0.0.1) and h2 (20.0.0.2)...\nObs.: h1 is in node1 and h2 is in node2\n')
    h1 = net.addHost( 'h1', ip='20.0.0.1' )
    h2 = net.addHost( 'h2', ip='20.0.0.2', server='node2' )

    print('Creating a link between h1 and h2...\n')
    net.addLink( h1, h2 )

    print('\n----------------------------------------------\n\n')

    print('Creating hosts h3, h4, h5 and h6\nObs.: h3 and h4 is in node1. h5 and h6 is in node2\n')
    h3 = net.addHost( 'h3', ip='20.0.0.3' )
    h4 = net.addHost( 'h4', ip='20.0.0.4' )
    h5 = net.addHost( 'h5', ip='20.0.0.5', server='node2' )
    h6 = net.addHost( 'h6', ip='20.0.0.6', server='node2' )
    
    print('Creating OVS switches s0, s1 and s2.\nObs.: s0 and s1 is in node1. s2 is in node2\n')
    s0 = net.addSwitch( 's0' )
    s1 = net.addSwitch( 's1' )
    s2 = net.addSwitch( 's2', server='node2' )

    print('Creating links between:\n . s0 - s1\n . . s1 - h3\n . . s1 - h4\n . s0 - s2\n . . s2 - h5\n . . s2 - h6\n')
    net.addLink( s0, s1 )
    net.addLink( s0, s2 )
    net.addLink( h3, s1 )
    net.addLink( h4, s1 )
    net.addLink( h5, s2 )
    net.addLink( h6, s2 )

    #print('Adding permit all rule in s0, s1 and s2')
    #os.system('sh ovs-ofctl add-flow s0 action=normal') 
    #os.system('sh ovs-ofctl add-flow s1 action=normal')
    #os.system('sh ovs-ofctl add-flow s2 action=normal')

    net.start()

    CLI( net) 
    
    net.stop()

if __name__ == '__main__':
    topology()
