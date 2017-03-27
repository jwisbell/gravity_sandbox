import numpy as np
import time
from astropy.io import fits
import re
#from pyadb import ADB

import subprocess



## Read input file and assign values ##
#fileBytePos = 0
def get_particle_params():
		# pull file 
	subprocess('adb pull /storage/emulated/0/field.jpg /home/gravity/sandbox_scripts')

    f = open('/home/gravity/sandbox_scripts/algorithm_input.txt','r')
	#f.seek(fileBytePos)
    f.seek(0)
    data = f.readline().strip('(').replace(')', '').split()
    for j in range(len(data)):
        data[j] = float(data[j])
    pos = np.array([data[0],data[1]])
    vel = np.array([data[2],data[3]])
    obj = data[4]
    f.close()
    print pos, vel, obj
    return pos, vel, obj


subprocess('adb push /home/gravity/Desktop/color_field.jpg /storage/emulated/0/field.jpg')
