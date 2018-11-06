#!/usr/bin/python2

import writeToFile as wf
import resourceData as rd
import mn_distributed as mnd

class Mininet(object):
    def __init__(self, mininet, timeStamp, logFile, sleepTime, sleepTimeMem, clusterNodesLength, networkLength, \
            arrayNetworkLength, mclink):
        self.mininet = mininet
        self.timeStamp = timeStamp
        self.logFile = logFile
        self.sleepTime = sleepTime
        self.sleepTimeMem = sleepTimeMem
        self.clusterNodesLength = clusterNodesLength
        self.mclink = mclink
	
        object_array = CreateArray(self.logFile, self.clusterNodesLength, networkLength, arrayNetworkLength, self.mclink)
	self.coreSwitchList = object_array.coreSwitches(self.clusterNodesLength, arrayNetworkLength)
    	self.hostList, self.edgeSwitchList, self.aggregateSwitchList = object_array.hostEdgeAggregateSwitches(arrayNetworkLength)
    	self.controllerList = object_array.controller()
    	self.linksHostEdgeList, self.linksEdgeAggregateList, self.linksAggregateCoreList = \
                object_array.links(self.hostList, self.edgeSwitchList, self.aggregateSwitchList, self.coreSwitchList)
        
        wf.line('        -- switch_core_per_cluster_node:%s\n\
        \nLine structure:\n\
        - time: time spent on task execution (seconds)\n\
        - local memory: number of memory used to execute the task on local cluster node (bytes)\n\
        - remote memory: number of memory used to execute the task on remote cluster node (bytes)\n\
        - local processes: number of persistent processes created to execute the task on local cluster node\n\
        - remote processes: number of persistent processes created to execute the task on remote cluster node\n\
        - cluster node: the name of the cluster node on which the task is running\n\
        - amount: amount of elements created (hosts, switches, links) on the task\n\
        - description: a description that describe the what the task does\n'
        % (self.coreSwitchList), logFile)

        self.callMininet()

    def callMininet(self):
        for mininet in self.mininet:                    # Mininet Cluster and Maxinet
            if mininet == 'mc':
                for link in self.mclink:
                    self.distributedMininet(mininet, link)
            elif mininet == 'mn':
                self.distributedMininet(mininet, None)

    def distributedMininet(self, mininet, link):
        if mininet == 'mc':
            print('\n-<MininetCluster>-\n--<%s>--' % (link))
            wf.line('-<MininetCluster>-\n--<%s>--' %(link), self.logFile)
        elif mininet == 'mn':
            print('\n-<MaxiNet>-\n')
            wf.line('--<MaxiNet>--', self.logFile)
        """
            Initiating Mininet Cluster Topology
        """
        if mininet == 'mc':
            print('\nInitiating Mininet Cluster Topology...')
            mc = mnd.MininetCluster()
        elif mininet == 'mn':
            print('\nInitiating Maxinet Topology...')
            mn = mnd.MaxiNet()
            for i in range(self.clusterNodesLength):
                clusterNodeName = 'node%s' % (i +1)
                if clusterNodeName == 'node1':
                    lMem = rd.getMemLocal(self.sleepTimeMem)
                    pTime = rd.getTime(self.sleepTime)
                    mn.workers(clusterNodeName)
                    pTime = rd.getTime(self.sleepTime) - pTime
                    lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
                    wf.string(pTime, lMem, 0, 4, 0, clusterNodeName, 2, 'MaxiNetFrontendServer', self.logFile)
                else:
                    rMem = rd.getMemRemote(self.sleepTimeMem, clusterNodeName)
                    pTime = rd.getTime(self.sleepTime)
                    mn.workers(clusterNodeName)
                    pTime = rd.getTime(self.sleepTime) - pTime
                    rMem = rMem - rd.getMemRemote(self.sleepTimeMem, clusterNodeName)
                    wf.string(pTime, 0, rMem, 0, 3, clusterNodeName, 1, 'MaxiNetWorker', self.logFile)
        lMem = rd.getMemLocal(self.sleepTimeMem)
        pTime = rd.getTime(self.sleepTime)
        if mininet == 'mc':
            mc.topology(link)
        elif mininet == 'mn':
            mn.topology(self.clusterNodesLength)
        pTime = rd.getTime(self.sleepTime) - pTime
        lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
        wf.string(pTime, lMem, 0, 0, 0, 'node1', 0, 'topology', self.logFile)
        """
            Creating Controller
            self.controllerList[i][0] = controller name
        """
        print('\nController...')
        lMem = rd.getMemLocal(self.sleepTimeMem)
        pTime = rd.getTime(self.sleepTime)
        if mininet == 'mc':
            for i in range(len(self.controllerList)):
                mc.controller(self.controllerList[i][0])
            pTime = rd.getTime(self.sleepTime) - pTime
            lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
            wf.string(pTime, lMem, 0, 1, 0, 'node1', 0, 'controller', self.logFile)
        """
            Creating Core switches
            self.coreSwitchList[i][0] = Core switch name (ex.: s10)
            self.coreSwitchList[i][1] = node name (ex.: node1)
        """
        print('\nCore switches...')
        coreSwitchClusterNode = []
        for i in range(len(self.coreSwitchList)):
            exist = False
            for y in range(len(coreSwitchClusterNode)):
                if self.coreSwitchList[i][1] == coreSwitchClusterNode[y]:
                    exist = True
            if not exist:
                coreSwitchClusterNode.append(self.coreSwitchList[i][1])
        for i in range(len(coreSwitchClusterNode)):
            lMem = rd.getMemLocal(self.sleepTimeMem)
            rMem = rd.getMemRemote(self.sleepTimeMem, coreSwitchClusterNode[i])
            pTime = rd.getTime(self.sleepTime)
            amount = 0
            lProc = 0
            rProc = 0
            clusterNodeRemote = False
            for y in range(len(self.coreSwitchList)):
                if coreSwitchClusterNode[i] == self.coreSwitchList[y][1]:
                    if coreSwitchClusterNode[i] == 'node1':
                        amount += 1
                        lProc += 1
                        rProc = 0
                        rMem = 0
                    else:
                        amount += 1
                        lProc += 2
                        rProc += 4
                        clusterNodeRemote = True
                    if mininet == 'mc':
                        mc.switch(self.coreSwitchList[y][0], self.coreSwitchList[y][1])
                    elif mininet == 'mn':
                        mn.switch(self.coreSwitchList[y][0], self.coreSwitchList[y][2])
            pTime = rd.getTime(self.sleepTime) - pTime
            lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
            if clusterNodeRemote:
                rMem = rMem - rd.getMemRemote(self.sleepTimeMem, coreSwitchClusterNode[i])
            wf.string(pTime, lMem, rMem, lProc, rProc, coreSwitchClusterNode[i], amount, 'coreSwitch', self.logFile)
        """
            Creating Aggregate switches
            self.aggregateSwitchList[i][0] = Aggregate switch name (ex.: s200)
            self.aggregateSwitchList[i][1] = node name (ex.: node1)
        """
        print('\nAggregate switches...')
        aggregateSwitchClusterNode = []
        for i in range(len(self.aggregateSwitchList)):
            exist = False
            for y in range(len(aggregateSwitchClusterNode)):
                if self.aggregateSwitchList[i][1] == aggregateSwitchClusterNode[y]:
                    exist = True
            if not exist:
                aggregateSwitchClusterNode.append(self.aggregateSwitchList[i][1])
        for i in range(len(aggregateSwitchClusterNode)):
            lMem = rd.getMemLocal(self.sleepTimeMem)
            rMem = rd.getMemRemote(self.sleepTimeMem, aggregateSwitchClusterNode[i])
            pTime = rd.getTime(self.sleepTime)
            amount = 0
            lProc = 0
            rProc = 0
            clusterNodeRemote = False
            for y in range(len(self.aggregateSwitchList)):
                if aggregateSwitchClusterNode[i] == self.aggregateSwitchList[y][1]:
                    if aggregateSwitchClusterNode[i] == 'node1':
                        amount += 1
                        lProc += 1
                        rProc = 0
                        rMem = 0
                    else:
                        amount += 1
                        lProc += 2
                        rProc += 4
                        clusterNodeRemote = True
                    if mininet == 'mc':
                        mc.switch(self.aggregateSwitchList[y][0], self.aggregateSwitchList[y][1])
                    elif mininet == 'mn':
                        mn.switch(self.aggregateSwitchList[y][0], self.aggregateSwitchList[y][2])
            pTime = rd.getTime(self.sleepTime) - pTime
            lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
            if clusterNodeRemote:
                rMem = rMem - rd.getMemRemote(self.sleepTimeMem, aggregateSwitchClusterNode[i])
            wf.string(pTime, lMem, rMem, lProc, rProc, aggregateSwitchClusterNode[i], amount, 'aggregateSwitch', self.logFile)
        """
            Creating Edge switches
            self.edgeSwitchList[i][0] = Edge switch name (ex.: s300)
            self.edgeSwitchList[i][1] = node name (ex.: node1)
        """
        print('\nEdge switches...')
        edgeSwitchClusterNode = []
        for i in range(len(self.edgeSwitchList)):
            exist = False
            for y in range(len(edgeSwitchClusterNode)):
                if self.edgeSwitchList[i][1] == edgeSwitchClusterNode[y]:
                    exist = True
            if not exist:
                edgeSwitchClusterNode.append(self.edgeSwitchList[i][1])
        for i in range(len(edgeSwitchClusterNode)):
            lMem = rd.getMemLocal(self.sleepTimeMem)
            rMem = rd.getMemRemote(self.sleepTimeMem, edgeSwitchClusterNode[i])
            pTime = rd.getTime(self.sleepTime)
            amount = 0
            lProc = 0
            rProc = 0
            clusterNodeRemote = False
            for y in range(len(self.edgeSwitchList)):
                if edgeSwitchClusterNode[i] == self.edgeSwitchList[y][1]:
                    if edgeSwitchClusterNode[i] == 'node1':
                        amount += 1
                        lProc += 1
                        rProc = 0
                        rMem = 0
                    else:
                        amount += 1
                        lProc += 2
                        rProc += 4
                        clusterNodeRemote = True
                    if mininet == 'mc':
                        mc.switch(self.edgeSwitchList[y][0], self.edgeSwitchList[y][1])
                    elif mininet == 'mn':
                        mn.switch(self.edgeSwitchList[y][0], self.edgeSwitchList[y][3])
            pTime = rd.getTime(self.sleepTime) - pTime
            lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
            if clusterNodeRemote:
                rMem = rMem - rd.getMemRemote(self.sleepTimeMem, edgeSwitchClusterNode[i])
            wf.string(pTime, lMem, rMem, lProc, rProc, edgeSwitchClusterNode[i], amount, 'edgeSwitch', self.logFile)
        """
            Creating Hosts
            self.hostList[i][0] = Host name (ex.: h00)
            self.hostList[i][1] = node name (ex.: node1)
        """
        print('\nHost list...')
        hostClusterNode = []
        for i in range(len(self.hostList)):
            exist = False
            for y in range(len(hostClusterNode)):
                if self.hostList[i][1] == hostClusterNode[y]:
                    exist = True
            if not exist:
                hostClusterNode.append(self.hostList[i][1])
        for i in range(len(hostClusterNode)):
            lMem = rd.getMemLocal(self.sleepTimeMem)
            rMem = rd.getMemRemote(self.sleepTimeMem, hostClusterNode[i])
            pTime = rd.getTime(self.sleepTime)
            amount = 0
            lProc = 0
            rProc = 0
            clusterNodeRemote = False
            for y in range(len(self.hostList)):
                if hostClusterNode[i] == self.hostList[y][1]:
                    if hostClusterNode[i] == 'node1':
                        amount += 1
                        lProc += 1
                        rProc = 0
                        rMem = 0
                    else:
                        amount += 1
                        lProc += 2
                        rProc += 4
                        clusterNodeRemote = True
                    if mininet == 'mc':
                        mc.host(self.hostList[y][0], self.hostList[y][1])
                    elif mininet == 'mn':
                        mn.host(self.hostList[y][0], self.hostList[y][3])
            pTime = rd.getTime(self.sleepTime) - pTime
            lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
            if clusterNodeRemote:
                rMem = rMem - rd.getMemRemote(self.sleepTimeMem, hostClusterNode[i])
            wf.string(pTime, lMem, rMem, lProc, rProc, hostClusterNode[i], amount, 'host', self.logFile)
        """
            Link between Hosts and Edge switches
            self.linksHostEdgeList[i][0] = Host name (ex.: h00)
            self.linksHostEdgeList[i][1] = Edge switch name (ex.: s300)
        """
        print('\nlink: Host <-> Edge...')
        linksHostEdgeClusterNode = []
        for i in range(len(self.linksHostEdgeList)):
            exist = False
            for y in range(len(linksHostEdgeClusterNode)):
                if self.linksHostEdgeList[i][2] == linksHostEdgeClusterNode[y]:
                    exist = True
            if not exist:
                linksHostEdgeClusterNode.append(self.linksHostEdgeList[i][2])
        for i in range(len(linksHostEdgeClusterNode)):
            lMem = rd.getMemLocal(self.sleepTimeMem)
            rMem = rd.getMemRemote(self.sleepTimeMem, linksHostEdgeClusterNode[i])
            pTime = rd.getTime(self.sleepTime)
            amount = 0
            lProc = 0
            rProc = 0
            clusterNodeRemote = False
            for y in range(len(self.linksHostEdgeList)):
                if linksHostEdgeClusterNode[i] == self.linksHostEdgeList[y][2]:
                    if linksHostEdgeClusterNode[i] == 'node1':
                        amount += 1
                        rMem = 0
                    else:
                        lMem = 0
                        amount += 1
                        clusterNodeRemote = True
                    if mininet == 'mc':
                        mc.link(self.linksHostEdgeList[y][0], self.linksHostEdgeList[y][1])
                    elif mininet == 'mn':
                        mn.link(self.linksHostEdgeList[y][0], self.linksHostEdgeList[y][1])
            pTime = rd.getTime(self.sleepTime) - pTime
            if not clusterNodeRemote:
                lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
            if clusterNodeRemote:
                rMem = rMem - rd.getMemRemote(self.sleepTimeMem, linksHostEdgeClusterNode[i])
            wf.string(pTime, lMem, rMem, lProc, rProc, linksHostEdgeClusterNode[i], amount, 'linkHostEdge', self.logFile)
        """
            Link between Edge and Aggregate switches
            self.linksEdgeAggregateList[i][0] = Edge switch name (ex.: s300)
            self.linksEdgeAggregateList[i][1] = Aggregate switch name (ex.: s200)
        """
        print('\nlink: Edge <-> Aggregate...')
        linksEdgeAggregateClusterNode = []
        for i in range(len(self.linksEdgeAggregateList)):
            exist = False
            for y in range(len(linksEdgeAggregateClusterNode)):
                if self.linksEdgeAggregateList[i][2] == linksEdgeAggregateClusterNode[y]:
                    exist = True
            if not exist:
                linksEdgeAggregateClusterNode.append(self.linksEdgeAggregateList[i][2])
        for i in range(len(linksEdgeAggregateClusterNode)):
            lMem = rd.getMemLocal(self.sleepTimeMem)
            rMem = rd.getMemRemote(self.sleepTimeMem, linksEdgeAggregateClusterNode[i])
            pTime = rd.getTime(self.sleepTime)
            amount = 0
            lProc = 0
            rProc = 0
            clusterNodeRemote = False
            for y in range(len(self.linksEdgeAggregateList)):
                if linksEdgeAggregateClusterNode[i] == self.linksEdgeAggregateList[y][2]:
                    if linksEdgeAggregateClusterNode[i] == 'node1':
                        amount += 1
                        rMem = 0
                    else:
                        lMem = 0
                        amount += 1
                        clusterNodeRemote = True
                    if mininet == 'mc':
                        mc.link(self.linksEdgeAggregateList[y][0], self.linksEdgeAggregateList[y][1])
                    elif mininet == 'mn':
                        mn.link(self.linksEdgeAggregateList[y][0], self.linksEdgeAggregateList[y][1])
            pTime = rd.getTime(self.sleepTime) - pTime
            if not clusterNodeRemote:
                lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
            if clusterNodeRemote:
                rMem = rMem - rd.getMemRemote(self.sleepTimeMem, linksEdgeAggregateClusterNode[i])
            wf.string(pTime, lMem, rMem, lProc, rProc, linksEdgeAggregateClusterNode[i], amount, 'linkEdgeAggregate', self.logFile)
        """
            Link between Aggregate and Core switches
            self.linksAggregateCoreList[i][0] = Aggregate switch name (ex.: s200)
            self.linksAggregateCoreList[i][1] = Core switch name (ex.: s10)
        """
        print('\nlink: Aggregate <-> Core...')
        linksAggregateCoreClusterNodeSrc = []
        linksAggregateCoreClusterNodeDst = []
        for i in range(len(self.linksAggregateCoreList)):
            exist = False
            for y in range(len(linksAggregateCoreClusterNodeSrc)):
                if self.linksAggregateCoreList[i][2] == linksAggregateCoreClusterNodeSrc[y]:
                    exist = True
            if not exist:
                linksAggregateCoreClusterNodeSrc.append(self.linksAggregateCoreList[i][2])
        for i in range(len(self.linksAggregateCoreList)):
            exist = False
            for y in range(len(linksAggregateCoreClusterNodeDst)):
                if self.linksAggregateCoreList[i][3] == linksAggregateCoreClusterNodeDst[y]:
                    exist = True
            if not exist:
                linksAggregateCoreClusterNodeDst.append(self.linksAggregateCoreList[i][3])
        for i in range(len(linksAggregateCoreClusterNodeSrc)):
            for y in range(len(linksAggregateCoreClusterNodeDst)):
                lMem = 0
                rMem1 = 0
                rMem2 = 0
                lProc = 0
                rProc1 = 0
                rProc2 = 0
                cNode2 = 0
                amount = 0
                local_local = False
                local_remote = False
                remote_local = False
                remoteX_remoteX = False
                remoteX_remoteY = False
                """
                    local - local: (node1 - node1)
                    - local veth
                    - 0 local process - 0 remote process
                """
                lMem = rd.getMemLocal(self.sleepTimeMem)
                pTime = rd.getTime(self.sleepTime)
                for x in range(len(self.linksAggregateCoreList)):
                    if self.linksAggregateCoreList[x][2] == linksAggregateCoreClusterNodeSrc[i] and \
                            self.linksAggregateCoreList[x][3] == linksAggregateCoreClusterNodeDst[y] and \
                            linksAggregateCoreClusterNodeSrc[i] == 'node1' and linksAggregateCoreClusterNodeDst[y] == 'node1':
                        if mininet == 'mc':
                            mc.link(self.linksAggregateCoreList[x][0], self.linksAggregateCoreList[x][1])
                        elif mininet == 'mn':
                            mn.link(self.linksAggregateCoreList[x][0], self.linksAggregateCoreList[x][1])
                        amount += 1
                        local_local = True
                if local_local:
                    pTime = rd.getTime(self.sleepTime) - pTime
                    lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
                    wf.stringAggregateCoreRemote(pTime, lMem, rMem1, rMem2, lProc, rProc1, rProc2, \
                            linksAggregateCoreClusterNodeSrc[i], linksAggregateCoreClusterNodeDst[y], amount, \
                            'linkAggregateCore-local-local', self.logFile)
                    continue
                """
                    local - remote (node1 - nodeX)
                    - SSH tunnel
                    - 2 local process - 2 remote process
                """
                lMem = rd.getMemLocal(self.sleepTimeMem)
                rMem1 = rd.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeDst[y])
                pTime = rd.getTime(self.sleepTime)
                for x in range(len(self.linksAggregateCoreList)):
                    if self.linksAggregateCoreList[x][2] == linksAggregateCoreClusterNodeSrc[i] and \
                            self.linksAggregateCoreList[x][3] == linksAggregateCoreClusterNodeDst[y] and \
                            linksAggregateCoreClusterNodeSrc[i] == 'node1' and linksAggregateCoreClusterNodeDst[y] != 'node1':
                        if mininet == 'mc':
                            mc.link(self.linksAggregateCoreList[x][0], self.linksAggregateCoreList[x][1])
                        elif mininet == 'mn':
                            mn.link(self.linksAggregateCoreList[x][0], self.linksAggregateCoreList[x][1])
                        amount += 1
                        local_remote = True
                if local_remote:
                    pTime = rd.getTime(self.sleepTime) - pTime
                    lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
                    rMem1 = rMem1 - rd.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeDst[y])
                    lProc = 2 * amount
                    rProc1 = 2 * amount
                    wf.stringAggregateCoreRemote(pTime, lMem, rMem1, rMem2, lProc, rProc1, rProc2, \
                            linksAggregateCoreClusterNodeSrc[i], linksAggregateCoreClusterNodeDst[y], amount, \
                            'linkAggregateCore-local-remote', self.logFile)
                    continue
                """
                    remote - local (nodeX - node1)
                    - SSH tunnel
                    - 2 local process - 2 remote process
                """
                lMem = rd.getMemLocal(self.sleepTimeMem)
                rMem1 = rd.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeSrc[i])
                pTime = rd.getTime(self.sleepTime)
                for x in range(len(self.linksAggregateCoreList)):
                    if self.linksAggregateCoreList[x][3] == linksAggregateCoreClusterNodeDst[y] and \
                            self.linksAggregateCoreList[x][2] == linksAggregateCoreClusterNodeSrc[i] and \
                            linksAggregateCoreClusterNodeDst[y] == 'node1' and linksAggregateCoreClusterNodeSrc[i] != 'node1':
                        if mininet == 'mc':
                            mc.link(self.linksAggregateCoreList[x][0], self.linksAggregateCoreList[x][1])
                        elif mininet == 'mn':
                            mn.link(self.linksAggregateCoreList[x][0], self.linksAggregateCoreList[x][1])
                        amount += 1
                        remote_local = True
                if remote_local:
                    pTime = rd.getTime(self.sleepTime) - pTime
                    lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
                    rMem1 = rMem1 - rd.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeSrc[i])
                    lProc = 2 * amount
                    rProc1 = 2 * amount
                    wf.stringAggregateCoreRemote(pTime, lMem, rMem1, rMem2, lProc, rProc1, rProc2, \
                            linksAggregateCoreClusterNodeSrc[i], linksAggregateCoreClusterNodeDst[y], amount, \
                            'linkAggregateCore-remote-local', self.logFile)
                    continue
                """
                    remote - remote (nodeX - nodeX)
                    - remote veth
                    - 0 local process - 0 remote process
                """
                rMem1 = rd.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeSrc[i])
                rMem2 = rd.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeDst[y])
                pTime = rd.getTime(self.sleepTime)
                for x in range(len(self.linksAggregateCoreList)):
                    if self.linksAggregateCoreList[x][2] == linksAggregateCoreClusterNodeSrc[i] and \
                            self.linksAggregateCoreList[x][3] == linksAggregateCoreClusterNodeDst[y] and \
                            linksAggregateCoreClusterNodeSrc[i] != 'node1' and linksAggregateCoreClusterNodeDst[y] != 'node1' and \
                            self.linksAggregateCoreList[x][2] == self.linksAggregateCoreList[x][3]:
                        if mininet == 'mc':
                            mc.link(self.linksAggregateCoreList[x][0], self.linksAggregateCoreList[x][1])
                        elif mininet == 'mn':
                            mn.link(self.linksAggregateCoreList[x][0], self.linksAggregateCoreList[x][1])
                        amount += 1
                        remoteX_remoteX = True
                if remoteX_remoteX:
                    pTime = rd.getTime(self.sleepTime) - pTime
                    rMem1 = rMem1 - rd.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeSrc[i])
                    rMem2 = rMem2 - rd.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeDst[y])
                    wf.stringAggregateCoreRemote(pTime, lMem, rMem1, rMem2, lProc, rProc1, rProc2, \
                            linksAggregateCoreClusterNodeSrc[i], linksAggregateCoreClusterNodeSrc[y], amount, \
                            'linkAggregateCore-remoteX-remoteX', self.logFile)
                    continue
                """
                    remote - remote (nodeX - nodeY)
                    - SSH tunnel to send command (2 local process - 2 remote process)
                    - 2 local process - 2 remote process (nodeX) - 2 remote process (nodeY)
                """
                lMem = rd.getMemLocal(self.sleepTimeMem)
                rMem1 = rd.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeSrc[i])
                rMem2 = rd.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeDst[y])
                pTime = rd.getTime(self.sleepTime)
                for x in range(len(self.linksAggregateCoreList)):
                    if self.linksAggregateCoreList[x][2] == linksAggregateCoreClusterNodeSrc[i] and \
                            self.linksAggregateCoreList[x][3] == linksAggregateCoreClusterNodeDst[y] and \
                            linksAggregateCoreClusterNodeSrc[i] != 'node1' and linksAggregateCoreClusterNodeDst[y] != 'node1' and \
                            self.linksAggregateCoreList[x][2] != self.linksAggregateCoreList[x][3]:
                        if mininet == 'mc':
                            mc.link(self.linksAggregateCoreList[x][0], self.linksAggregateCoreList[x][1])
                        elif mininet == 'mn':
                            mn.link(self.linksAggregateCoreList[x][0], self.linksAggregateCoreList[x][1])
                        amount += 1
                        remoteX_remoteY = True
                if remoteX_remoteY:
                    pTime = rd.getTime(self.sleepTime) - pTime
                    lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
                    rMem1 = rMem1 - rd.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeSrc[i])
                    rMem2 = rMem2 - rd.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeDst[y])
                    lProc = 2 * amount
                    rProc1 = 2 * amount
                    rProc2 = 2 * amount
                    wf.stringAggregateCoreRemote(pTime, lMem, rMem1, rMem2, lProc, rProc1, rProc2, \
                            linksAggregateCoreClusterNodeSrc[i], linksAggregateCoreClusterNodeSrc[y], amount, \
                            'linkAggregateCore-remoteX-remoteY', self.logFile)
                    continue
        if mininet == 'mc':
            mc.controllerPox()
        elif mininet == 'mn':
            mn.controllerPox()
        lMem = rd.getMemLocal(self.sleepTimeMem)
        pTime = rd.getTime(self.sleepTime)
        if mininet == 'mc':
            mc._start()
        pTime = rd.getTime(self.sleepTime) - pTime
        lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
        wf.string(pTime, lMem, 0, 0, 0, 'node1', 1, 'start', self.logFile)
        if mininet == 'mc':
            mc._stop()
        elif mininet == 'mn':
            mn._stop()
            for i in range(self.clusterNodesLength):
                clusterNodeName = 'node%s' % (i +1)
                mn._workers(clusterNodeName)


class CreateArray(object):
    """
        Host name = 'h' + <edgeSwitchId> + <hostId>
        Edge switches name = 's3' + <podId> + <edgeSwitchId>
        Aggregate switches name = 's2' + <podId> + <aggregateSwitchId>
        Core switches name = 's1' + <coreSwitchId>
        Controller name = 'c0'
    """
    def __init__(self, logFile, clusterNodesLength, networkLength, arrayNetworkLength, mclink):
        self.pod = networkLength                                                # Total number of PODs
        self.densityPod = (networkLength / 2) ** 2                              # Number of Hosts per POD
        self.coreSwitch = (networkLength / 2) ** 2                              # Total number of Core switches
        self.aggregateSwitch = networkLength*networkLength / 2                  # Total number of Aggregate switches
        self.edgeSwitch = networkLength * networkLength / 2                     # Total number of Edge switches
        self.hosts = self.densityPod * self.pod                                 # Total number of Hosts
        self.edgeSwitchPerPod = self.edgeSwitch / self.pod                      # Number of Edge switches per POD
        self.aggregateSwitchPerPod = self.aggregateSwitch / self.pod            # Number of Aggregate switches per POD
        self.hostsPerEdgeSwitch = self.densityPod / self.edgeSwitchPerPod       # Number of Hosts per Edge switch

        print('\n-- FATTREE --\n')
        print('\nPODs: %s\nCore Switches: %s\nAggregate Switches: %s\nEdge Switches: %s\nHosts: %s\n' \
                % (self.pod, self.coreSwitch, self.aggregateSwitch, self.edgeSwitch, self.hosts))
        print('\nNumber of ... per POD:\nAggregate Switches: %s\nEdge Switches: %s\nHosts: %s' \
                % (self.edgeSwitchPerPod, self.aggregateSwitchPerPod, self.densityPod))

        wf.line('-- FATTREE --\n\
        -- cluster_nodes:%s\n\
        -- array_cluster_nodes:%s\n\
        -- total_pod:%s\n\
        -- total_switch_core:%s\n\
        -- total_switch_aggregate:%s\n\
        -- total_switch_edge:%s\n\
        -- total_host:%s\n\
        -- switch_aggregate_per_pod:%s\n\
        -- switch_edge_per_pod:%s\n\
        -- host_per_pod:%s'
        % (clusterNodesLength, arrayNetworkLength, self.pod, self.coreSwitch, self.aggregateSwitch, self.edgeSwitch, \
        self.hosts, self.aggregateSwitchPerPod, self.edgeSwitchPerPod, self.densityPod), logFile)

    def coreSwitches(self, clusterNodesLength, arrayNetworkLength):
        """ 
            Core switches
        """
        coreSwitchList = []
        arrayCoreLength = [self.coreSwitch / clusterNodesLength] * clusterNodesLength
        restCoreLength = self.coreSwitch % clusterNodesLength
        for i in range(restCoreLength):
            arrayCoreLength[i] = arrayCoreLength[i] + 1                         # Number of core switches per cluster node
        count = 0
        for i in range(len(arrayNetworkLength)):                                # Take nodeId
            for j in range(arrayCoreLength[i]):                                 # how many times repeat on each node
                coreSwitchList.append (['s1' + str(count), 'node' + str(i + 1), i])
                count += 1
        return(coreSwitchList)

    def hostEdgeAggregateSwitches(self, arrayNetworkLength):
        """
            Aggregate switches, Edge switches  and Host
        """
        aggregateSwitchList = []
        edgeSwitchList = []
        hostList = []
        countSw = 0
        countHt = 0
        countPod = 0
        for i in range(len(arrayNetworkLength)):                                # Take nodeId
            for j in range(arrayNetworkLength[i]):                              # how many times repeat on each node
                for x in range(self.aggregateSwitchPerPod):                     # how many times repeat on each POD (for switches)
                    aggregateSwitchList.append (['s2' + str(countPod) + str(countSw), 'node' + str(i + 1), i])
                    edgeSwitchList.append (['s3' + str(countPod) + str(countSw), 'node' + str(i + 1), countSw, i])
                    for y in range(self.hostsPerEdgeSwitch):                    # how many times repeat on each Switch (for hosts)
                        hostList.append (['h' + str(countSw) + str(countHt), 'node' + str(i + 1), countSw, i])
                        countHt += 1
                    countSw += 1
                countPod += 1
        return(hostList, edgeSwitchList, aggregateSwitchList)

    def controller(self):
        """
            Controller
        """
        controllerList = []
        controllerList.append (['c0'])
        return(controllerList)

    def links(self, hostList, edgeSwitchList, aggregateSwitchList, coreSwitchList):
        """
            Links
        """
        """
            Host <-> Edge Switches
        """
        linksHostEdgeList = []
        for i in range(len(hostList)):
            for y in range(len(edgeSwitchList)):
                if hostList[i][2] == edgeSwitchList[y][2]:
                    linksHostEdgeList.append ([hostList[i][0], edgeSwitchList[y][0], hostList[i][1]])
        """
            Edge <-> Aggregate
        """
        linksEdgeAggregateList = []
        podRangeNumber = 0
        countLink = 0
        for i in range(len(edgeSwitchList)):
            if i >= (podRangeNumber + self.edgeSwitchPerPod):
                podRangeNumber = podRangeNumber + self.edgeSwitchPerPod
            for y in range(self.edgeSwitchPerPod):
                linksEdgeAggregateList.append ([edgeSwitchList[i][0], 's2' + \
                        str(edgeSwitchList[i][0][2:-len(str(edgeSwitchList[i][2]))]) + str(podRangeNumber + y), \
                        edgeSwitchList[i][1]])
                countLink += 1
        """
            Aggregate <--> Core
        """
        linksAggregateCoreList = []
        forBegin = 0
        forEnd = self.pod / 2
        countLink = 0
        for i in range(len(aggregateSwitchList)):
            for y in xrange(forBegin, forEnd):
                for x in range(len(coreSwitchList)):
                    if coreSwitchList[x][0] == 's1' + str(y):
                        corePlace = coreSwitchList[x][1]
                linksAggregateCoreList.append ([aggregateSwitchList[i][0], 's1' + str(y), \
                        aggregateSwitchList[i][1], corePlace])
                countLink += 1
            if forEnd == self.coreSwitch:
                forBegin = 0
                forEnd = self.pod / 2
            else:
                forBegin = forEnd
                forEnd = forEnd + (self.pod / 2)
        return(linksHostEdgeList, linksEdgeAggregateList, linksAggregateCoreList)
