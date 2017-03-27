# ------- Import Basic Functionality ------
import time
import sys
import subprocess

#------- Import our files ---------
import gravity_algorithm2
import DiscretePlummerKernel
import convolution
import gdal
import io_funcs


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
	PLUMMER = fits.getdata('PlummerDFT.fits',0)   
	#particle = gravity_algorithm2.Particle(*input_params)
	previous_vals = [0.,0.,0.,0.]
	exit = 0
	while exit == 0:
		"""
		REFRESH THE DEM FILE SAVED ON DISK
		"""
		subprocess('bash dem_saver.sh')
		"""
		READ IN THE DEM FILE AS NUMPY ARRAY
		"""
		dem_file = gdal.Open('BathymetrySaverTool.dem')
		# Converts dem_file to numpy array of shape (480, 639)
		dem_array = np.array(dem_file.GetRasterBand(1).ReadAsArray())
		# This is a temporary fix for an uncalibrated surface, i.e. we set a base level where any value is less than 3
		for x in np.nditer(dem_array, op_flags=['readwrite']):
		    if x[...] < 3.:
		        x[...] = 0.
		"""
		CONVOLVE THE DEM-DENSITY FIELD WITH THE PLUMMER KERNEL
		"""
		potential_field = convolution.convolve(dem_array, PLUMMER, 'kernel')
		"""
		CHECK TO SEE IF WE ARE RUNNING ON NEW PARAMS

		READ IN INPUT PARAMS AND UPDATE PARTICLE IF NEEDED
		"""
		input_params = io_funcs.read_from_app(ADB_FILEPATH)

		particle = gravity_algorithm2.Particle(*previous_vals, potential_field)
		if differ(input_params, previous_vals):
			particle = gravity_algorithm2.Particle(*input_params, potential_field)
		"""
		INTEGRATE FOR A WHILE
		"""
		to_send = gravity_algorithm2.runorbit(particle, ITER, edge_mode='reflect') #run for 1000 iterations and save the array
		previous_vals = [particle.pos[0], particle.pos[1], particle.vel[0], particle.vel[1]]
		"""
		SEND IMAGE, ORBIT DATA TO APP
		"""
		if not io_funcs.write_to_tablet(ADB_FILEPATH, to_send):
			exit = 1
		"""
		CLEAN UP FOR MEMORY MANAGEMENT
		"""
		del to_send
		del potential_field
		del particle

