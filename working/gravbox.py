# ------- Import Basic Functionality ------
import time
import sys
from subprocess import call
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from multiprocessing import Process
from optparse import OptionParser

#------- Import our files ---------
import gravity_algorithm2
#import DiscretePlummerKernel
import convolution
import gdal
import io_funcs

#convolution.here()

# --------- Constants -----------
ADB_FILEPATH = ''
NORMALIZATION = 1.
REFRESH_RATE = 1 #hz
SLEEP_TIME = 1 #seconds
#ITER = 15000 #number of iteration to orbit over
POTENTIAL_NORM = 5000#7500.
INT_SECONDS = 3.5
ITER = int(11000 * (INT_SECONDS - 2.2))
vel_scaling = 1.
verbose = 1
SF = 4
idle_time = 1*60; waiting = time.time()
debug=0

parser = OptionParser()
parser.add_option("-i", "--idle", dest="idle_time", type='float', help="Set the amount of time (in seconds) until idle mode begins (default 600)")
parser.add_option("-t", "--timing", dest="INT_SECONDS", type='float', help="Set the number of seconds per iteration you would like (default 3.5)")
parser.add_option("-s", "--speed", dest="vel_scaling", type='float', help="Set a scaling factor for the input velocities (default 1.0)")
#parser.add_option("-v", "--verbose", dest="verbose", type='int',help="If this flag is set to true, save the potential field as a .png image")
parser.add_option("-m", "--smoothness", dest="SF", type='int', help="Smoothness factor for gradient calculation. Lower values make particle more sensitive to noise. Default is 4")
parser.add_option("-d", "--debug", dest="debug", type='int', help="Use a pre-made density field for testing purposes. Disables tablet I/O. 1 for on, 0 for off.")
(options, args) = parser.parse_args()

#if verbose == 1:
#verbose=True
#else:
#verbose=False
def differ(arr1, arr2):
	for k in range(len(arr1)):
		if arr1[k] != arr2[k]:
			return True
	return False

#------- begin main program ---------
if __name__ == '__main__':
	#------------ START THE SANDBOX ------------
	call('bash initialize.sh', shell=True)
	# ----- INITIAL VALUES AND CONSTANTS -------------
	PLUMMER = fits.getdata('PlummerDFT.fits',0)   
	#previous_pos = [0.,0.]
	#previous_vel = [0.,0.]
	previous_pos, previous_vel = io_funcs.read_from_app()
	current_pos = [200.,316] #y, x
	vel = -np.sqrt(50/abs(340 - current_pos[1]))*.75
	current_vel = [vel,0] # vy, vx
	exit = 0
	loops = 0
	idle = False#True
	#call('/home/gravity/src/SARndbox-2.2/bin/SARndbox -uhm -fpv -rer 20 100 &', shell=True)
	while exit == 0:
		if not idle:
			start = time.time()
			"""
			REFRESH THE DEM FILE SAVED ON DISK
			"""
			call('xdotool keydown "b"', shell=True)		
			"""
			READ IN THE DEM FILE AS NUMPY ARRAY
			"""
			get_dem_start = time.time()
			call('xdotool mousemove_relative 0 350; ', shell=True) # move the mouse to get it out of screenshot
			call("xwd -name SARndbox | convert xwd:- '/home/gravity/Desktop/color_field.jpg' ;", shell=True)
			dem_file = gdal.Open('/home/gravity/Desktop/gravbox/BathymetrySaverTool.dem')#('/home/gravity/src/SARndbox-2.2/BathymetrySaverTool.dem')
			# Converts dem_file to numpy array of shape (480, 639)
			dem_array = np.array(dem_file.GetRasterBand(1).ReadAsArray())
			#dem_array = np.rot90(dem_array,2)
			get_dem_end = time.time()
			print "Getting DEM took: ",get_dem_end-get_dem_start

			
			"""
			CONVOLVE THE DEM-DENSITY FIELD WITH THE PLUMMER KERNEL
			"""
			shp = dem_array.shape
			call('xdotool keyup "b"', shell=True)
			convstart = time.time()
			potential_field = np.reshape(convolution.convolve(dem_array, PLUMMER, 'kernel'),shp)
			print 'it got here'
			potential_field = np.negative(potential_field/POTENTIAL_NORM)
			
			med = np.median(potential_field)/5.
			convend = time.time()
			print 'convolution took', convend-convstart

			if verbose:
				fig = plt.figure(figsize=(6.3,5))
				im1 = plt.imshow(potential_field,vmin=-10,vmax=20,origin='upper')
		            	im1.axes.get_xaxis().set_visible(False)
		        	im1.axes.get_yaxis().set_visible(False)
				extent = im1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
				plt.savefig('../potential_field.png',bbox_inches=extent,transparent=True, pad=0.)
				#plt.show()
				plt.close()

			field_edge = 10
			potential_field[:,0:field_edge] = med
			potential_field[:,(-1 * field_edge):] = med
			potential_field[0:field_edge,:] = med
			potential_field[(-1 * field_edge):,:] = med

			#----------- for testing only ------------------
			
			'''potential_field = np.zeros(shp)
			centerx = 340; centery=200
			for x in range(shp[1]):
				for y in range(shp[0]):
					potential_field[y,x] = - 50 /np.sqrt((x-centerx)**2 + (y-centery)**2)
			potential_field[centery-1:centery+1,centerx-1:centerx+1]=np.median(potential_field)
			#potential_field[potential_field.shape[0]-10:,potential_field.shape[1]-10] = med
			'''
			"""
			CHECK TO SEE IF WE ARE RUNNING ON NEW PARAMS?

			READ IN INPUT PARAMS AND UPDATE PARTICLE IF NEEDED
			"""
			get_inpt_s = time.time()
			input_pos, input_vel = io_funcs.read_from_app(vel_scaling)
			print input_pos
			particle = gravity_algorithm2.Particle(current_pos, np.array(current_vel), potential_field, smoothness=SF)
			if differ(input_pos, previous_pos) or differ(input_vel, previous_vel):
				particle = gravity_algorithm2.Particle(input_pos, np.array(input_vel), potential_field,smoothness=SF)
				previous_pos = np.copy(input_pos); previous_vel = np.copy(input_vel)
				waiting = time.time()
			print 'getting input takes: ', time.time()-get_inpt_s
			"""
			INTEGRATE FOR A WHILE
			"""
			int_time = time.time()
			to_send = gravity_algorithm2.run_orbit(particle, ITER, loops=loops,step=0.01,edge_mode='reflect',kind='leapfrog') #run for 1000 iterations and save the array
			int_end = time.time()
			print 'integration took', int_end-int_time		
			loops += 1
			if loops > 50:
				loops=0
			print loops

			current_pos = [particle.pos[0], particle.pos[1]] 
			current_vel = [particle.vel[0], particle.vel[1]]
			print 'CURRENT POSITION AND VELOCITY:', current_pos, current_vel

			#io_funcs.plot_orbit(to_send, potential_field)
			"""
			SEND IMAGE, ORBIT DATA TO APP
			"""
			sends = time.time()
			check_pos, check_vel = io_funcs.read_from_app()
			if differ(previous_pos,check_pos) or differ(previous_vel, check_vel):
				io_funcs.idle_send()
			else:
				io_funcs.write_to_tablet(to_send)

			#exit = call('pgrep -x "SARndbox" > /dev/null')
			sende = time.time()
			print 'sending info took', sende-sends 

			"""
			CLEAN UP FOR MEMORY MANAGEMENT
			"""
			del to_send
			del potential_field
			del particle
			end = time.time()
			print end-start, 'seconds have elapsed...'
			#maybe refresh after REFRESH_RATE - (end-start) seconds if positive number?
			time.sleep(1.5)
			if time.time() - waiting >= idle_time:
				idle=True
			sys.stdout.flush()
		if debug ==1:
			dem_array = np.zeros(480,639)
			dem_array[240,320] = 10
			#dem_array = np.rot90(dem_array,2)
			
			"""
			CONVOLVE THE DEM-DENSITY FIELD WITH THE PLUMMER KERNEL
			"""
			shp = dem_array.shape
			call('xdotool keyup "b"', shell=True)
			convstart = time.time()
			potential_field = np.reshape(convolution.convolve(dem_array, PLUMMER, 'kernel'),shp)
			print 'it got here'
			potential_field = np.negative(potential_field/POTENTIAL_NORM)
			
			med = np.median(potential_field)/5.
			convend = time.time()
			print 'convolution took', convend-convstart

			"""
			CHECK TO SEE IF WE ARE RUNNING ON NEW PARAMS?

			READ IN INPUT PARAMS AND UPDATE PARTICLE IF NEEDED
			"""
			
			particle = gravity_algorithm2.Particle(current_pos, np.array(current_vel), potential_field, smoothness=SF)
			
			"""
			INTEGRATE FOR A WHILE
			"""
			int_time = time.time()
			to_send = gravity_algorithm2.run_orbit(particle, ITER, loops=loops,step=0.01,edge_mode='reflect',kind='leapfrog') #run for 1000 iterations and save the array
			int_end = time.time()
			print 'integration took', int_end-int_time		
			loops += 1
			if loops > 50:
				loops=0

			current_pos = [particle.pos[0], particle.pos[1]] 
			current_vel = [particle.vel[0], particle.vel[1]]
			print 'CURRENT POSITION AND VELOCITY:', current_pos, current_vel


		else:
			call('xdotool mousemove_relative 0 350; ', shell=True) # move the mouse to get it out of screenshot
			call('xdotool keydown "b"', shell=True)	
			input_pos, input_vel = io_funcs.read_from_app()
			if differ(input_pos, previous_pos) or differ(input_vel, previous_vel):
				#previous_pos = np.copy(input_pos); previous_vel = np.copy(input_vel)
				waiting = time.time()
				idle=False
			call('xdotool keyup "b"', shell=True)
			call("xwd -name SARndbox | convert xwd:- '/home/gravity/Desktop/color_field.jpg' ;", shell=True)
			io_funcs.idle_send()
			sys.stdout.flush()


