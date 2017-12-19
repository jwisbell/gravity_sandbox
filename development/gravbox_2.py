# ------- Import Basic Functionality ------
import time
import sys
from animate_orbits import makegif
from subprocess import call
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from multiprocessing import Process
from optparse import OptionParser
from argparse import ArgumentParser
from scipy import signal
from PyQt4 import QtGui as QtWidgets

#------- Import our files ---------
import gravity_algorithm
import convolution
import io_funcs
import active_animating
import topogra as topo

# --------- Constants -----------
ADB_FILEPATH = ''
NORMALIZATION = 1.
REFRESH_RATE = 1 #hz
SLEEP_TIME = 1 #seconds
#ITER = 15000 #number of iteration to orbit over
POTENTIAL_NORM = 5000#7500.
INT_SECONDS = 3.5
vel_scaling = 1.
#verbose = 0
SF = 4
SCALE_FACTOR = 16 # for DEM smoothing

parser = ArgumentParser()
parser.add_argument("-i", "--idle", dest="idle_time", default=60., type=float, help="Set the amount of time (in seconds) until idle mode begins (default 600)")
parser.add_argument("-t", "--timing", dest="INT_SECONDS", default=3.5, type=float, help="Set the number of seconds per iteration you would like (default 3.5)")
parser.add_argument("-s", "--speed", dest="vel_scaling", type=float, default=1.0, help="Set a scaling factor for the input velocities (default 1.0)")
parser.add_argument("-m", "--smoothness", dest="SF", type=int, default=4, help="Smoothness factor for gradient calculation. Lower values make particle more sensitive to noise. Default is 4")
parser.add_argument("-d", "--debug", dest="debug", type=int, default=0, help="Use a pre-made density field for testing purposes. Disables tablet I/O. 1 for on, 0 for off.")
parser.add_argument("-v", "--verbose", dest="verbose", type=bool, default=False, help="Save a plot displaying the potential field. (default False)")

args = parser.parse_args()

waiting = time.time()
ITER = 10000#int(11000 * (args.INT_SECONDS - 2.2))

def differ(arr1, arr2):
	for k in range(len(arr1)):
		if arr1[k] != arr2[k]:
			return True
	return False

#------- begin main program ---------
if __name__ == '__main__':
	#------------ START THE SANDBOX ------------
	previous_pos = [0,0.]
	previous_vel = [0.,0.]
	#------ Initial Sandbox Calibration -------
	"""
	Kinect drivers not working for some reason??
	"""
	baseplane = topo.generate_baseplane()
	prev_dem = topo.update_surface(baseplane, None)

	# Initialize figure for animation
	#figure = active_animating.Animate(prev_dem)

	# ----- INITIAL VALUES AND CONSTANTS -------------
	PLUMMER = fits.getdata('./aux/PlummerDFT.fits',0)
	X_KERNEL =  np.load('./aux/dxDFT.npy')#fits.getdata('./aux/dx_kernel.fits',0)  ##
	Y_KERNEL = np.load('./aux/dyDFT.npy') #fits.getdata('./aux/dy_kernel.fits',0) #
	
	current_pos = [336,226]
	current_vel = [0,0]
	exit = 0
	loops = 0
	idle = False#True
	first = False
	if args.debug > 0:
		first = True

	while exit == 0:
		if args.debug ==1:
			call('./pid_check.sh', shell=True)
			start_loop = time.time()

			scaled_dem_array = topo.update_surface(baseplane, prev_dem)
			
			
			#scaled_dem_array = np.zeros((480,640))
			#scaled_dem_array[235:245,315:325] = 50
			#scaled_dem_array[150:160,200:210] = 40

			#plotted = np.copy(scaled_dem_array)
			prev_dem = scaled_dem_array

			'''EDGE = 10
			scaled_dem_array[:EDGE,:] = 0
			scaled_dem_array[-7:,:] = 0
			scaled_dem_array[:,:EDGE] = 0
			scaled_dem_array[:,-14:] = 0'''

			scaled_dem_array = scaled_dem_array[36:-20, 20:-20]
			xw = scaled_dem_array.shape[1]; yw = scaled_dem_array.shape[0]
			'''scaled_dem_array[yw*.25-5:yw*.25+5,xw*.25-5:xw*.25+5] = 50
			scaled_dem_array[yw*.5-5:yw*.5+5,xw*.5-5:xw*.5+5] = 50
			scaled_dem_array[yw*.75-5:yw*.75+5,xw*.75-5:xw*.75+5] = 50
			scaled_dem_array[yw*.25-5:yw*.25+5,xw*.75-5:xw*.75+5] = 50
			scaled_dem_array[yw*.75-5:yw*.75+5,xw*.25-5:xw*.25+5] = 50'''
			print scaled_dem_array.shape
			

			np.save('display_dem.npy',np.nan_to_num(scaled_dem_array)+2)

			
			"""
			CONVOLVE THE DEM-DENSITY FIELD WITH THE PLUMMER KERNEL
			"""
			shp = scaled_dem_array.shape
			print shp

			conv_start = time.time()
			gx,gy, g2x, g2y = convolution.convolve2d(scaled_dem_array, X_KERNEL,Y_KERNEL)
			gx = np.negative(gx)*.1
			gy = np.negative(gy)*.1

			#print 'Convolution took ', time.time()-conv_start
			#current_pos = [212,300]
			#current_vel = [10,0]
			particle = gravity_algorithm.Particle(current_pos, np.array(current_vel), (gx,gy),g2x,g2y)
			first = False
			input_pos, input_vel = io_funcs.read_from_app_2(vel_scaling)
			#print 'input vals',input_pos, input_vel 
			if differ(input_pos, previous_pos) or differ(input_vel, previous_vel):
				particle = gravity_algorithm.Particle(input_pos, np.array(input_vel), (gx,gy),g2x,g2y)
				particle.kick(0.001)
				previous_pos = np.copy(input_pos); previous_vel = np.copy(input_vel)
				waiting = time.time()
			
			
			"""
			INTEGRATE FOR A WHILE
			"""
			to_send = gravity_algorithm.run_orbit(particle, 5000, loops=loops,step=0.001,edge_mode='reflect',kind='leapfrog') #run for 1000 iterations and save the array
			posx = [val[0] for val in to_send]
			posy = [val[1] for val in to_send]
			topo_time = time.time()
			io_funcs.send_topo()
			print 'sent topo'
			topo_end = time.time() - topo_time
			print 'topo_time =', topo_end

			x = np.asarray(posx)/scaled_dem_array.shape[1]
			y = np.asarray(posy)/scaled_dem_array.shape[0]
			np.save('algorithm_output.npy', (x,y))
			#figure.update_fig(scaled_dem_array/1000, posy, posx, SCALE_FACTOR)

			####call("sleep 5.0",shell=True)

			loops +=1
			if loops > 100:
				loops=0

			current_pos = [particle.pos[0], particle.pos[1]] 
			current_vel = [particle.vel[0], particle.vel[1]]
			print 'CURRENT POSITION AND VELOCITY:', current_pos, current_vel
			dt = time.time()-start_loop
			print 'LOOP TOOK: ', dt
			if int(dt) < 1:
				time.sleep(1+1-dt)
			if int(dt)>=1:
				time.sleep(1+1-(dt-int(dt)))

		elif args.debug ==2:
			scaled_dem_array = np.zeros((480,640))
			#scaled_dem_array[235:245,315:325] = 50
			#scaled_dem_array[150:160,200:210] = 4

			scaled_dem_array = scaled_dem_array[36:-20, 20:-20]
			xw = scaled_dem_array.shape[1]; yw = scaled_dem_array.shape[0]
			'''scaled_dem_array[yw*.25-5:yw*.25+5,xw*.25-5:xw*.25+5] = 50
			scaled_dem_array[yw*.5-5:yw*.5+5,xw*.5-5:xw*.5+5] = 50
			scaled_dem_array[yw*.75-5:yw*.75+5,xw*.75-5:xw*.75+5] = 50
			scaled_dem_array[yw*.25-5:yw*.25+5,xw*.75-5:xw*.75+5] = 50
			scaled_dem_array[yw*.75-5:yw*.75+5,xw*.25-5:xw*.25+5] = 50'''
			scaled_dem_array[yw*.5,xw*.5]=20
			print scaled_dem_array.shape
		
			
			"""
			CONVOLVE THE DEM-DENSITY FIELD WITH THE PLUMMER KERNEL
			"""
			shp = scaled_dem_array.shape
			
			gx,gy, g2x, g2y = convolution.convolve2d(scaled_dem_array, X_KERNEL,Y_KERNEL)
			gx = np.negative(gx)*.1
			gy = np.negative(gy)*.1
			g2x = np.gradient(gx,4.)[0]
			g2y = np.gradient(gy,4.)[1]#np.negative(g2y)*.1
			current_pos = [yw*.4,xw*.5]
			current_vel = [0,.5]
			

			particle = gravity_algorithm.Particle(current_pos, np.array(current_vel), (gx,gy),g2x,g2y)
			particle.kick(.0005)
			#first = False

			#gravity_algorithm.kepler_check(particle,scaled_dem_array, step=.0001,kind='leapfrog')
			gravity_algorithm.energy_check(particle, pos=[(yw*.5,xw*.5)], masses=[50], step=0.0005, times=5000000, kind='leapfrog2')
			sys.exit()
