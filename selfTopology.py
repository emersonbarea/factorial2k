#!/usr/bin/python

from mininet.examples.cluster import RemoteHost, RemoteLink
# RemoteLink = no Mininet 2.2.2 ha somente RemoteLink (tunnel SSH). Nao ha RemoteSSHLink e RemoteGRELink (esses existem apenas a partir do Mininet versao 2.3.0d3, mas ha bug)
from mininet.net import Mininet
from mininet.net import CLI

def topology():
  
    net = Mininet( host=RemoteHost, link=RemoteLink )

    h1 = net.addHost( 'h1', ip='20.0.0.1' )
    h2 = net.addHost( 'h2', ip='20.0.0.2', server='node2' )

    net.addLink( h1, h2 )
    
    net.start()

    CLI( net) 
    
    net.stop()

if __name__ == '__main__':
    topology()
