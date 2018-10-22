#!/usr/bin/python

import time

def executionTime():
   exTime = time.time()
   return(exTime)

def wtfLineFile( line, logFileName ):
    f = open( logFileName, 'a' )
    f.write( str(line) + '\n' )
    f.close()

def wtfExecutionTime( t1, t2, local, function, logFileName ):
    executionTime = t2 - t1
    f = open( logFileName, 'a' )
    line = ( str(executionTime) + ',' + local + ',' + function )
    f.write( str(line) + '\n' )
    f.close()
