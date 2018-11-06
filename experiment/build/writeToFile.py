#!/usr/bin/python

def line(line, logFileName):
    f = open(logFileName, 'a')
    f.write(str(line) + '\n')
    f.close()

def string(pTime, lMem, rMem, lProc, rProc, cNode, amount, description, logFileName):
    f = open(logFileName, 'a')
    line = (str(pTime) + ',' + \
            str(lMem) + ',' + \
            str(rMem) + ',' + \
            str(lProc) + ',' + \
            str(rProc) + ',' + \
            str(cNode) + ',' + \
            str(amount) + ',' + \
            description)
    f.write(str(line) + '\n')
    f.close()

def stringAggregateCoreRemote(pTime, lMem, rMem1, rMem2, lProc, rProc1, rProc2, cNode1, cNode2, amount, description, logFileName):
    f = open(logFileName, 'a')
    line = (str(pTime) + ',' + \
            str(lMem) + ',' + \
            str(rMem1) + ',' + \
            str(rMem2) + ',' + \
            str(lProc) + ',' + \
            str(rProc1) + ',' + \
            str(rProc2) + ',' + \
            str(cNode1) + ',' + \
            str(cNode2) + ',' + \
            str(amount) + ',' + \
            description)
    f.write(str(line) + '\n')
    f.close()    
