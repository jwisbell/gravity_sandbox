import matplotlib.pyplot as plt
import numpy as np
from subprocess import call
import imageio
import glob
import re

def makeplots(posy, posx, gy, gx, loops):
	fig,ax = plt.subplots(2)
   	ax[0].imshow(gy,vmax=.2, vmin=-.2)
	ax[0].scatter(posy,posx, c='white',edgecolors='none',s=2)
	ax[1].imshow(gx,vmax=.2, vmin=-.2)
	ax[1].scatter(posy,posx, c='white',edgecolors='none',s=2)
    #plt.arrow(init_pos[1], init_pos[0], init_pos[1]+step*init_vel[1], init_pos[0]+step*init_vel[0], head_width=0.05, head_length=0.1, fc='k', ec='k')
	plt.title(r'Test Orbit using $\Delta t = %.3f$'%(.01))
	plt.xlim([0,640])
	plt.ylim([0,480])
    #plt.show()
	plt.savefig('./debug/images/test_orbit%i.png'%(loops))
	plt.close()

def keyFunc(afilename):
	nondigits = re.compile('\D')
	return int(nondigits.sub("", afilename))

def makegif(posy, posx, gy, gx, loops):
	if loops == 0:
		call('rm ./debug/images/test_orbit*', shell=True)
	makeplots(posy,posx, gy, gx, loops)
	filenames=glob.glob('./debug/images/test_orbit*png')
	filenames = sorted(filenames, key=keyFunc)
	images=[]
	if len(filenames) > 25:
		for filename in filenames:
			images.append(imageio.imread(filename))
		imageio.mimsave('./debug/orbit_%i.gif'%(loops/25),images)
		call('rm ./debug/images/test_orbit*', shell=True)







	
