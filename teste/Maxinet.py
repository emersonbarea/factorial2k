#!/usr/bin/python2

from mininet.topo import Topo
from mininet.node import OVSSwitch

from MaxiNet.Frontend import maxinet
from MaxiNet.tools import Tools

# create topology
topo = Topo()

# start cluster
cluster = maxinet.Cluster(minWorkers=1, maxWorkers=1)

# start experiment on cluster
exp = maxinet.Experiment(cluster, topo, switch=OVSSwitch)
exp.setup()

print('****Setting up topology part 1')

print('Creating switches s1 (on worker1) and s2 (on worker2)...')
exp.addSwitch("s1", dpid="00:00:00:00:00:00:00:01", wid=0)
exp.addSwitch("s2", dpid="00:00:00:00:00:00:00:02", wid=0)

print('Adding hosts h1 in worker 1...')
exp.addHost('h1',ip=Tools.makeIP(1), max=Tools.makeMAC(1), pos='s1')

print('Adding hosts h2 in worker 2...')
exp.addHost('h2',ip=Tools.makeIP(2), max=Tools.makeMAC(2), pos='s2')

print('Connecting h1 with s1')
exp.addLink("h1", "s1", autoconf=True)

print('Connecting h2 with s2')
exp.addLink("h2", "s2", autoconf=True)

print('Connecting s1 and s2...')
exp.addLink("s1", "s2", autoconf=True)

raw_input('[Continue]')

print('****Setting up topoloty part 2')

print('Creating switches s3 (on worker1) and s4 (on worker2)...')
exp.addSwitch("s3", dpid="00:00:00:00:00:00:00:03", wid=0)
exp.addSwitch("s4", dpid="00:00:00:00:00:00:00:04", wid=0)

print('Adding hosts h3 in worker 1...')
exp.addHost('h3',ip=Tools.makeIP(3), max=Tools.makeMAC(3), pos='s3')

print('Adding hosts h4 in worker 2...')
exp.addHost('h4',ip=Tools.makeIP(4), max=Tools.makeMAC(4), pos='s4')

print('Connecting h3 with s3')
exp.addLink("h3", "s3", autoconf=True)

print('Connecting h4 with s4')
exp.addLink("h4", "s4", autoconf=True)

print('Connecting s3 and s4...')
exp.addLink("s3", "s4", autoconf=True)

maxinet.Experiment.CLI(exp, None, None)

#raw_input('[Continue]')

print('****Closing all')
exp.stop()
