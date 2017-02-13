# Tyler Stercula, File open/edit test
import numpy as np
import time
from astropy.io import fits


## Read input file and assign values ##
fileBytePos = 0
def check(fileBytePos):
    f = open('algorithm_input.txt','r')
    f.seek(fileBytePos)
    data = f.readline().strip('(').strip(')').split()
    for j in range(len(data)):
        data[j] = float(data[j])
    pos = np.array([data[0],data[1]])
    vel = np.array([data[2],data[3]]) 
    obj = data[4]
    f.close()
    return pos, vel, obj
    print pos, vel, obj



## Calculate orbit and write to output file ##
posxtot = []
posytot = []

times = 10000                 # Set the number of steps to be calculated

outputfile = open('algorithm_output.csv','w')
for n in xrange(1, times):
    pos,vel = leap(pos,vel)
    posxtot.append(pos[0])
    posytot.append(pos[1])
    outputfile.write('(\"%i\",\"%i\")'%(pos[0],pos[1]))
outputfile.close()
