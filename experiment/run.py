#!/usr/bin/python2

from mininet.log import setLogLevel
import build.dCell as DCell
import build.fatTree as FatTree
import os
import logging
import sys
import time

def experiment():
    print('\nChoose the option:\n\n\
            (1)  MaxiNet and Mininet Cluster (SSH and GRE Remote link) - FatTree and DCell (ALL)\n\
            (2)  MaxiNet - FatTree and DCell\n\
            (3)  MaxiNet - FatTree\n\
            (4)  MaxiNet - DCell\n\
            (5)  Mininet Cluster (SSH and GRE Remote link) - FatTree and DCell\n\
            (6)  Mininet Cluster (SSH Remote link) - FatTree\n\
            (7)  Mininet Cluster (GRE Remote link) - FatTree\n\
            (8)  Mininet Cluster (SSH Remote link) - DCell\n\
            (9)  Mininet Cluster (GRE Remote link) - DCell\n\
            (10) Mininet Cluster (SSH and GRE Remote link) - FatTree\n\
            (11) Mininet Cluster (SSH and GRE Remote link) - DCell\n\
            (12) Exit\n')
    experiment = False
    while not experiment:
        try:
            experiment = int(raw_input('Input experiment option: '))
            if experiment < 1 or experiment > 12:
                logging.error('Invalid input option')
                experiment = False
        except ValueError:
            logging.error('Not a number')
    return(experiment)

def clusterNodesLength():
    """
        Input the number of cluster nodes
    """
    nodesLength = False
    while not nodesLength:
        try:
            nodesLength = int(raw_input('Input the number of cluster nodes : '))
            if nodesLength < 1:
                logging.error(' Cluster must have 1 or more nodes')
                nodesLength = False
        except ValueError:
            logging.error(' Not a number')
    return(nodesLength)

def networkLength():
    """
        - DCell - number of cell switches
        - FatTree - number of pods
    """
    networkLength = False
    while not networkLength:
        try:
            networkLength = int(raw_input('Input network length (DCell - cell switches | FatTree - PODs) : '))
            if networkLength < 1 or networkLength % 2 != 0:
                logging.error(' Network length must be greater than 0 and even')
                networkLength = False
        except ValueError:
            logging.error(' Not a number')
    return(networkLength)

def arrayNetworkLength(networkLength, clusterNodesLength):
    """
        Define how many cell switches (DCell) and PODs (FatTree) wil be created on each cluster node or worker
    """
    arrayNetworkLength = [networkLength / clusterNodesLength] * clusterNodesLength
    restNetworkLength = networkLength % clusterNodesLength
    for i in range(restNetworkLength):
        arrayNetworkLength[i] = arrayNetworkLength[i] + 1
    return(arrayNetworkLength)

def getTime(Sleep):
    time.sleep(Sleep)
    Time = time.time() - Sleep
    return(Time)

if __name__ == '__main__':
    """
        Verify if root
        Welcome message
        set cluster node length
        set network length (cell switch number (DCell) and POD number (FatTree))
    """
    setLogLevel('info')
    if os.getuid() != 0:
        logging.warning(' You are NOT root')
    elif os.getuid() == 0:
        option = experiment()
        if option == 12:
            sys.exit(0)
        clusterNodesLength = clusterNodesLength()
        networkLength = networkLength()
        arrayNetworkLength = arrayNetworkLength(networkLength, clusterNodesLength)
        timeStamp = getTime(0)
        logFile = './log/experiment_' + str(timeStamp) + '.log'
        sleepTime = 0
        sleepTimeMem = 0
        """
            mininet - mc = MininetCluster | mn = MaxiNet
        """
        # (1)  MaxiNet and Mininet Cluster (SSH and GRE Remote link) - FatTree and DCell (ALL)
        if option == 1: 
            mininet = ['mc','mn']
            mclink = ['RemoteSSHLink','RemoteGRELink']
            FatTree.Mininet(mininet, timeStamp, logFile, sleepTime, sleepTimeMem, clusterNodesLength, \
                    networkLength, arrayNetworkLength, mclink)
            DCell.Mininet(mininet, timeStamp, logFile, sleepTime, sleepTimeMem, clusterNodesLength, \
                    networkLength, arrayNetworkLength, mclink)

        # (2)  MaxiNet - FatTree and DCell
        elif option == 2:
            mininet = ['mn']
            FatTree.Mininet(mininet, timeStamp, logFile, sleepTime, sleepTimeMem, clusterNodesLength, \
                    networkLength, arrayNetworkLength, None)
            DCell.Mininet(mininet, timeStamp, logFile, sleepTime, sleepTimeMem, clusterNodesLength, \
                    networkLength, arrayNetworkLength, None)

        # (3)  MaxiNet - FatTree
        elif option == 3:
            mininet = ['mn']
            FatTree.Mininet(mininet, timeStamp, logFile, sleepTime, sleepTimeMem, clusterNodesLength, \
                    networkLength, arrayNetworkLength, None)

        # (4)  MaxiNet - DCell
        elif option == 4:
            mininet = ['mn']
            DCell.Mininet(mininet, timeStamp, logFile, sleepTime, sleepTimeMem, clusterNodesLength, \
                    networkLength, arrayNetworkLength, None)

        # (5)  Mininet Cluster (SSH and GRE Remote link) - FatTree and DCell
        elif option == 5:
            mininet = ['mc']
            mclink = ['RemoteSSHLink','RemoteGRELink']
            FatTree.Mininet(mininet, timeStamp, logFile, sleepTime, sleepTimeMem, clusterNodesLength, \
                    networkLength, arrayNetworkLength, mclink)
            DCell.Mininet(mininet, timeStamp, logFile, sleepTime, sleepTimeMem, clusterNodesLength, \
                    networkLength, arrayNetworkLength, mclink)

        # (6)  Mininet Cluster (SSH Remote link) - FatTree
        elif option == 6: 
            mininet = ['mc']
            mclink = ['RemoteSSHLink']
            FatTree.Mininet(mininet, timeStamp, logFile, sleepTime, sleepTimeMem, clusterNodesLength, \
                    networkLength, arrayNetworkLength, mclink)

        # (7)  Mininet Cluster (GRE Remote link) - FatTree
        elif option == 7:    
            mininet = ['mc']
            mclink = ['RemoteGRELink']
            FatTree.Mininet(mininet, timeStamp, logFile, sleepTime, sleepTimeMem, clusterNodesLength, \
                    networkLength, arrayNetworkLength, mclink)
        
        # (8)  Mininet Cluster (SSH Remote link) - DCell
        elif option == 8: 
            mininet = ['mc']
            mclink = ['RemoteSSHLink']
            DCell.Mininet(mininet, timeStamp, logFile, sleepTime, sleepTimeMem, clusterNodesLength, \
                    networkLength, arrayNetworkLength, mclink)

        # (9)  Mininet Cluster (GRE Remote link) - DCell
        elif option == 9:
            mininet = ['mc']
            mclink = ['RemoteGRELink']
            DCell.Mininet(mininet, timeStamp, logFile, sleepTime, sleepTimeMem, clusterNodesLength, \
                    networkLength, arrayNetworkLength, mclink)

        # (10) Mininet Cluster (SSH and GRE Remote link) - FatTree
        elif option == 10:
            mininet = ['mc']
            mclink = ['RemoteSSHLink', 'RemoteGRELink']
            FatTree.Mininet(mininet, timeStamp, logFile, sleepTime, sleepTimeMem, clusterNodesLength, \
                    networkLength, arrayNetworkLength, mclink)

        # (11) Mininet Cluster (SSH and GRE Remote link) - DCell
        elif option == 11:
            mininet = ['mc']
            mclink = ['RemoteSSHLink', 'RemoteGRELink']
            DCell.Mininet(mininet, timeStamp, logFile, sleepTime, sleepTimeMem, clusterNodesLength, \
                    networkLength, arrayNetworkLength, mclink)
