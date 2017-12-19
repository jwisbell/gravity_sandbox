# ------- Import Basic Functionality ------
import time
import sys
from subprocess import call
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from multiprocessing import Process
from optparse import OptionParser
from argparse import ArgumentParser
from scipy import signal
from PyQt4 import QtGui as QtWidgets
from skimage import measure


#------- Import our files ---------
import gravity_algorithm
import convolution
import io_funcs
import mpl_animate as mpl
import topogra as topo

# --------- Constants -----------
ADB_FILEPATH = ''
NORMALIZATION = 1.
REFRESH_RATE = 1 #hz
SLEEP_TIME = 1 #seconds
POTENTIAL_NORM = 5000#7500.
INT_SECONDS = 3.5
#verbose = 0
SCALE_FACTOR = 16 # for DEM smoothing

parser = ArgumentParser()
parser.add_argument("-i", "--idle", dest="idle_time", default=60., type=float, help="Set the amount of time (in seconds) until idle mode begins (default 600)")
parser.add_argument("-t", "--timing", dest="INT_SECONDS", default=3.5, type=float, help="Set the number of seconds per iteration you would like (default 3.5)")
parser.add_argument("-s", "--speed", dest="vel_scaling", type=float, default=.05, help="Set a scaling factor for the input velocities (default 1.0)")
parser.add_argument("-m", "--mode", dest="mode", type=str, default='tablet', help="Input mode. Default is 'tablet'. Type 'mouse' for mouse input.")
parser.add_argument("-d", "--debug", dest="debug", type=int, default=0, help="Use a pre-made density field for testing purposes. Disables tablet I/O. 1 for on, 0 for off.")
parser.add_argument("-v", "--verbose", dest="verbose", type=bool, default=False, help="Save a plot displaying the potential field. (default False)")
parser.add_argument("-a", "--audio", dest="music", type=bool, default=False, help="Play appropriate music. (default False)")

args = parser.parse_args()

waiting = time.time()
ITER = 10000#int(11000 * (args.INT_SECONDS - 2.2))

def mk_gauss(sigx=1.8, sigy=1.8, xshape=480, yshape=640):
    #sigx, sigy in FWHM arcsec
    sigma_x = sigx #/ px_factor / fwhm_factor #-> to sigma
    sigma_y = sigy #/ px_factor / fwhm_factor #-> to sigma
    pa = 0.#np.pi/2.#np.radians(45.)

    parms1 = [24., yshape/2,xshape/2,sigma_x,sigma_y,np.degrees(pa)]
    model1 = n_gaussians(1,parms1)

    X = np.arange(0,xshape,1); Y = np.arange(0,yshape,1)
    xv,yv = np.meshgrid(X,Y)

    synth1 = model1(yv,xv) +0 #+ np.random.randn(yshape,xshape)*5
    #make the measurement mask
    return synth1

def n_gaussians(n,params):
    '''Given parameters, it returns a function of n summed gaussians in 2D space.
        That function can then be fed a point or an array of data to fill the 2D distribution.'''
    offset = 0.#params[-1]
    indiv_params = [params[6*i:i*6+6] for i in range(n)]
    gauss_n = [gauss_2d(*indiv_params[i]) for i in range(n)]
    
    def n_gauss(x,y):
        tot = offset
        for i in range(len(gauss_n)):
            tot += gauss_n[i](x,y)
        return tot
    return n_gauss

def gauss_2d(amp, x_c, y_c, xwidth, ywidth, rot):
    '''Given parameters, returns a 2D Gaussian distribution function. This returned function can be fed data to fill the distribution space.'''
    rot = np.deg2rad(rot)
    try:
        a = (np.cos(rot)**2)/((2*xwidth)**2) + (np.sin(rot)**2)/((2*ywidth)**2)
    except:
        a = 0
    try:
        b = (-np.sin(2*rot))/((4*xwidth)**2) + np.sin(2*rot)/((4*ywidth)**2)
    except:
        b =0
    try:
        c = (np.sin(rot)**2)/((2*xwidth)**2) + (np.cos(rot)**2)/((2*ywidth)**2)
    except:
        c = 0
    
    def rotgauss(x,y):
        g = amp*np.exp(-1*(a*(x-x_c)**2 + 2*b*(x-x_c)*(y-y_c) + c*(y-y_c)**2))
        return g
    return rotgauss



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

	baseplane = topo.generate_baseplane()
	#prev_dem = topo.update_surface(baseplane, None)

	# Initialize figure for matplotlib animation
	#figure = mpl.Animate(prev_dem)

	# ----- INITIAL VALUES AND CONSTANTS -------------
	X_KERNEL =  np.load('./aux/dx_dft.npy')#fits.getdata('./aux/dx_kernel.fits',0)  ##
	Y_KERNEL = np.load('./aux/dy_dft.npy') #fits.getdata('./aux/dy_kernel.fits',0) #
	
	current_pos = [100,50]
	current_vel = [0,0]
	exit = 0
	loops = 0
	idle = False#True
	first = False
	if args.music == True:
		call('firefox https://www.youtube.com/watch?v=WgvRJRmsxjo &', shell=True)

	while exit == 0:
		if args.debug ==0:
			#call('./aux/pid_check.sh', shell=True) # Auxiliary bash script to check if the animation script has stopped running. If it has, gravbox will terminate
			start_loop = time.time()
			#scaled_dem_array = np.load('display_dem.npy')
			scaled_dem_array = topo.update_surface(baseplane, prev_dem) # Load in surface
			shp = scaled_dem_array.shape
			#scaled_dem_array = mk_gauss(5,5,xshape=shp[1], yshape=shp[0]) + 10
			#print np.max(scaled_dem_array), 'max value'
			#print np.median(scaled_dem_array), 'median value'
			
			#scaled_dem_array = np.zeros((480,640))
			#scaled_dem_array[235:245,315:325] = 50
			#scaled_dem_array[shp[0]/2, shp[1]/2] = 24

			#plotted = np.copy(scaled_dem_array)
			prev_dem = scaled_dem_array

			scaled_dem_array = scaled_dem_array[40:-30, 30:-30] 

			xw = scaled_dem_array.shape[1]; yw = scaled_dem_array.shape[0]
			'''scaled_dem_array[yw*.25-5:yw*.25+5,xw*.25-5:xw*.25+5] = 50
			scaled_dem_array[yw*.5-5:yw*.5+5,xw*.5-5:xw*.5+5] = 50
			scaled_dem_array[yw*.75-5:yw*.75+5,xw*.75-5:xw*.75+5] = 50
			scaled_dem_array[yw*.25-5:yw*.25+5,xw*.75-5:xw*.75+5] = 50
			scaled_dem_array[yw*.75-5:yw*.75+5,xw*.25-5:xw*.25+5] = 50'''
			print scaled_dem_array.shape
			

			#np.save('display_dem.npy',np.nan_to_num(scaled_dem_array)+2) 
			contour1 = measure.find_contours(scaled_dem_array,np.median(scaled_dem_array))
            		contour2 = measure.find_contours(scaled_dem_array,.5*np.median(scaled_dem_array))
            		contour3 = measure.find_contours(scaled_dem_array,2*np.median(scaled_dem_array))
            		contour4 = measure.find_contours(scaled_dem_array,-1*np.median(scaled_dem_array))
            		np.save('contours.npy',(contour1,contour2,contour3,contour4))

			
			"""
			CONVOLVE THE DEM-DENSITY FIELD WITH THE PLUMMER KERNEL
			"""
			shp = scaled_dem_array.shape
			print shp

			conv_start = time.time()
			gx,gy, g2x, g2y = convolution.convolve2d(scaled_dem_array, X_KERNEL,Y_KERNEL,method='wrap')
			print 'Convolution took ', time.time()-conv_start
			#np.save('display_dem.npy',np.nan_to_num(scaled_dem_array)+2)
			min_px = np.where(scaled_dem_array == np.nanmax(scaled_dem_array)) 
			#current_pos = [205,292]
			#current_vel = [0,0]	
			"""
			Create the particle
			"""
			particle = gravity_algorithm.Particle(current_pos, np.array(current_vel), (gx,gy),g2x,g2y)

			"""Read input positions from UI. If they are new, use in a new particle. """

			input_pos, input_vel = io_funcs.read_from_app(args.vel_scaling,x_factor=shp[1],y_factor=shp[0], mode=args.mode)
			if differ(input_pos, previous_pos) or differ(input_vel, previous_vel):
				particle = gravity_algorithm.Particle(input_pos, np.array(input_vel), (gx,gy),g2x,g2y)
				#particle.kick(0.001/2)
				previous_pos = np.copy(input_pos); previous_vel = np.copy(input_vel)
				waiting = time.time()
			
			
			"""
			INTEGRATE FOR A WHILE
			"""
			to_send = gravity_algorithm.run_orbit(particle, 5000, loops=loops,step=0.001,edge_mode='reflect',kind='leapfrog') #run for 1000 iterations and save the array
			posx = [val[0] for val in to_send]
			posy = [val[1] for val in to_send]
			#io_funcs.send_topo()
	



			input_pos, input_vel = io_funcs.read_from_app(args.vel_scaling,x_factor=shp[1],y_factor=shp[0], mode=args.mode)
			if not differ(input_pos, previous_pos) and not differ(input_vel, previous_vel):
				x = np.asarray(posx)/scaled_dem_array.shape[1]
				y = np.asarray(posy)/scaled_dem_array.shape[0]
				x = x[::10]
				y = y[::10]
				np.save('algorithm_output.npy', (x,y)) 

			loops +=1
			if loops > 100:
				loops=0

			current_pos = [particle.pos[0], particle.pos[1]] 
			current_vel = [particle.vel[0], particle.vel[1]]
			print 'CURRENT POSITION AND VELOCITY:', current_pos, current_vel
			dt = time.time()-start_loop
			print 'LOOP TOOK: ', dt
			time.sleep(.2)
			"""
			if int(dt) < 1:
				time.sleep(2+1-dt)
			if int(dt)>=1:
				time.sleep(2+1-(dt-int(dt)))
			"""

		elif args.debug ==1:
			scaled_dem_array = np.zeros((480,640))+2
			
			"""#scaled_dem_array[235:245,315:325] = 50
			#scaled_dem_array[150:160,200:210] = 4

			scaled_dem_array = scaled_dem_array[36:-20, 20:-20]
			xw = scaled_dem_array.shape[1]; yw = scaled_dem_array.shape[0]
			'''scaled_dem_array[yw*.25-5:yw*.25+5,xw*.25-5:xw*.25+5] = 50
			scaled_dem_array[yw*.5-5:yw*.5+5,xw*.5-5:xw*.5+5] = 50
			scaled_dem_array[yw*.75-5:yw*.75+5,xw*.75-5:xw*.75+5] = 50
			scaled_dem_array[yw*.25-5:yw*.25+5,xw*.75-5:xw*.75+5] = 50
			scaled_dem_array[yw*.75-5:yw*.75+5,xw*.25-5:xw*.25+5] = 50'''
			scaled_dem_array[yw*.5,xw*.5]=20
			print scaled_dem_array.shape"""
			shp = scaled_dem_array.shape
			#extended source 
			
			#point mass
			
			scaled_dem_array = scaled_dem_array[40:-30, 30:-30] 
			xw = scaled_dem_array.shape[1]; yw = scaled_dem_array.shape[0]
			scaled_dem_array[yw/2, xw/2] = 24.
			#scaled_dem_array = mk_gauss(5,5,xshape=xw, yshape=yw) +0
		
			
			"""
			CONVOLVE THE DEM-DENSITY FIELD WITH THE PLUMMER KERNEL
			"""
			
			
			gx,gy, g2x, g2y = convolution.convolve2d(scaled_dem_array, X_KERNEL,Y_KERNEL,'wrap')
			#gx = np.negative(gx)*.1
			#gy = np.negative(gy)*.1
			current_pos = [0,0]
			current_vel = [0,0.]
			

			particle = gravity_algorithm.Particle(current_pos, np.array(current_vel), (gx,gy),g2x,g2y)
			#particle.kick(.0001)
			

			#gravity_algorithm.kepler_check(particle,scaled_dem_array, step=.0001,kind='leapfrog2')
			gravity_algorithm.step_check(particle, scaled_dem_array)
			#gravity_algorithm.energy_check(particle, pos=[(yw*.5,xw*.5)], masses=[50], step=0.0005, times=5000000, kind='leapfrog')
			sys.exit()
		if idle:
			# In idle mode only update the topography to display on the UI
			scaled_dem_array = topo.update_surface(baseplane, prev_dem)
			prev_dem = scaled_dem_array
			scaled_dem_array = scaled_dem_array[36:-20, 20:-20]
			np.save('display_dem.npy',np.nan_to_num(scaled_dem_array)+2)
			# Check to see if there has been new input from the UI
			io_funcs.read_from_app(vel_scaling,args.mode)
			if differ(input_pos, previous_pos) or differ(input_vel, previous_vel):
				waiting = time.time()
				idle=False
			io_funcs.send_topo()
			sys.stdout.flush()
