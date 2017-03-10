# ------- Import Basic Functionality ------
import time
import sys
import subprocess

#------- Import our files ---------
import gravity_algorithm2
import DiscretePlummerKernel
import convolve


# --------- Constants -----------
ADB_FILEPATH = ''
NORMALIZATION = 1.
REFRESH_RATE = 1 #hz
SLEEP_TIME = 1 #seconds


#------- begin main program ---------
if __namespace__ == 'main':
	PLUMMER = fits.getdata('PlummerDFT.fits',0)   
	particle = gravity_algorithm2.Particle(*input_params)
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
		potential_field = convolve.convolve(dem_array, PLUMMER, 'kernel')
		"""
		CHECK TO SEE IF WE ARE RUNNING ON NEW PARAMS
		"""

			"""
			READ IN INPUT PARAMS AND UPDATE PARTICLE
			"""
			particle = gravity_algorithm2.Particle(*input_params)
		"""
		INTEGRATE FOR A WHILE
		"""
		
		to_send = gravity_algorithm2.runorbit(particle, 1000, edge_mode='reflect')

		"""
		SEND IMAGE, ORBIT DATA TO APP
		"""
		#adb push
		"""
		CLEAN UP FOR MEMORY MANAGEMENT
		"""
		# delete any extra variables

