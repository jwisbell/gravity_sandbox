# ------- Import Basic Functionality ------
import time
import sys
from subprocess import call
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt

#------- Import our files ---------
import gravity_algorithm2
#import DiscretePlummerKernel
import convolution
import gdal
import io_funcs
print 'shit'

#convolution.here()

# --------- Constants -----------
ADB_FILEPATH = ''
NORMALIZATION = 1.
REFRESH_RATE = 1 #hz
SLEEP_TIME = 1 #seconds
ITER = 1000 #number of iteration to orbit over

def differ(arr1, arr2):
	for k in range(len(arr1)):
		if arr1[k] != arr2[k]:
			return True
	return False

#------- begin main program ---------
if __name__ == '__main__':
	#call('rm BathymetrySaverTool.dem', shell=True)
	call('bash sandbox_start.sh', shell=True)
	#------------ START THE SANDBOX ------------
	'''call('/home/gravity/src/SARndbox-2.2/bin/SARndbox -uhm -fpv -rer 20 100 &', shell=True)
	call('sleep 1.0')
	call('wmctrl -R SARndbox; xdotool key "F11"; xdotool keydown "B";sleep 1; xdotool mousemove_relative 0 140; xdotool mousemove_relative -- -32 0; sleep 1; xdotool keyup "B";')'''
	


	PLUMMER = fits.getdata('PlummerDFT.fits',0)   
	previous_pos = [0.,0.]
	previous_vel = [0.,0.]
	current_pos = [400.,250.]
	current_vel = [0.,0.]
	exit = 0
	loops = 0
	#call('/home/gravity/src/SARndbox-2.2/bin/SARndbox -uhm -fpv -rer 20 100 &', shell=True)
	while exit == 0:
		call('xdotool keydown "b"', shell=True)
		start =time.time()
		"""
		REFRESH THE DEM FILE SAVED ON DISK
		"""
		
		#call('wmctrl -a SARndbox', shell=True)
		
		"""
		READ IN THE DEM FILE AS NUMPY ARRAY
		"""
		call('xdotool mousemove_relative 0 400; ', shell=True)
		call("xwd -name SARndbox | convert xwd:- '/home/gravity/Desktop/color_field.jpg' ;", shell=True)
		dem_file = gdal.Open('/home/gravity/Desktop/grav_sandbox/gravity_sandbox/BathymetrySaverTool.dem')#('/home/gravity/src/SARndbox-2.2/BathymetrySaverTool.dem')
		# Converts dem_file to numpy array of shape (480, 639)
		dem_array = np.negative(np.array(dem_file.GetRasterBand(1).ReadAsArray()))
		dem_array = dem_array - np.median(dem_array)
		# This is a temporary fix for an uncalibrated surface, i.e. we set a base level where any value is less than 3
		'''for x in np.nditer(dem_array, op_flags=['readwrite']):
		    if x[...] < 3.:
		        x[...] = 0.'''
		#dem_array = np.log(dem_array)#/np.max(np.absolute(dem_array))		
		'''fig = plt.figure()
		im1 = plt.imshow(dem_array, cmap='cool')
	        plt.axis('off')
        	im1.axes.get_xaxis().set_visible(False)
        	im1.axes.get_yaxis().set_visible(False)
        	#plt.savefig('/home/gravity/Desktop/color_field.jpg',bbinches='tight')
		plt.show()
		plt.close()'''
		call('adb shell rm /storage/emulated/0/sandbox/color_field.jpg', shell=True)
		call('adb push /home/gravity/Desktop/color_field.jpg /storage/emulated/0/sandbox/color_field.jpg', shell=True)
		"""
		CONVOLVE THE DEM-DENSITY FIELD WITH THE PLUMMER KERNEL
		"""
		shp = dem_array.shape
		call('xdotool keyup "b"', shell=True)
		convstart = time.time()
		potential_field = np.reshape(convolution.convolve(dem_array, PLUMMER, 'kernel'),shp)
		
		
		potential_field = potential_field/np.max(np.absolute(potential_field))*10000*2
		convend = time.time()
		print 'convolution took', convend-convstart
		
		fig = plt.figure()
		im1 = plt.imshow(potential_field,vmax=0.5)
            	im1.axes.get_xaxis().set_visible(False)
        	im1.axes.get_yaxis().set_visible(False)
		plt.savefig('../potential_field.jpg',bbinches='tight')
		#plt.show()
		plt.close()
		
		"""
		CHECK TO SEE IF WE ARE RUNNING ON NEW PARAMS?

		READ IN INPUT PARAMS AND UPDATE PARTICLE IF NEEDED
		"""
		input_pos, input_vel = io_funcs.read_from_app()
		print input_pos
		particle = gravity_algorithm2.Particle(current_pos, current_vel, potential_field)
		if differ(input_pos, previous_pos) or differ(input_vel, previous_vel):
			particle = gravity_algorithm2.Particle(input_pos, input_vel, potential_field)
			previous_pos = np.copy(input_pos); previous_vel = np.copy(input_vel)
		print particle.pos
		"""
		INTEGRATE FOR A WHILE
		"""
		int_time = time.time()
		to_send = gravity_algorithm2.run_orbit(particle, ITER, loops=loops,step=0.01,edge_mode='reflect') #run for 1000 iterations and save the array
		int_end = time.time()
		print 'integration took', int_end-int_time		
		loops += 1
		if loops > 100:
			loops = 0
		print loops

		current_pos = [particle.pos[0], particle.pos[1]] 
		current_vel = [particle.vel[0], particle.vel[1]]
		print current_pos, current_vel

		#io_funcs.plot_orbit(to_send, potential_field)
		"""
		SEND IMAGE, ORBIT DATA TO APP
		"""

		if not io_funcs.write_to_tablet(to_send):
			exit = 1
		#exit = call('pgrep -x "SARndbox" > /dev/null')

		"""
		CLEAN UP FOR MEMORY MANAGEMENT
		"""
		del to_send
		del potential_field
		del particle
		end = time.time()
		print end-start, 'seconds have elapsed...'
		#maybe refresh after REFRESH_RATE - (end-start) seconds if positive number?
		time.sleep(1.)


