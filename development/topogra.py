from freenect import sync_get_depth as get_depth
import numpy as np
import scipy.linalg


PLANE_PARAMS = [0,0,0]
SCALE_FACTOR = 1.


def do_calib(fname):
	data = np.load(fname)
	# best-fit linear plane
	# regular grid covering the domain of the data
	X,Y = np.meshgrid(np.arange(0,data.shape[0]), np.arange(0,data.shape[1]))
	XX = X.flatten()
	YY = Y.flatten()

	badpx = np.where(data==2047)
	data = data.astype('float32')
	data[badpx] = np.nan

    A = np.c_[data[:,0], data[:,1], np.ones(data.shape[0])]
    C,_,_,_ = scipy.linalg.lstsq(A, data[:,2])    # coefficients
    
    # evaluate it on grid
	Z = C[0]*X + C[1]*Y + C[2]

	surf = np.copy(data) + Z

	print 'PLANAR COEFFICIENTS: A=%f, B=%f, C=%f'%(C[0],C[1],C[2])
	print 'MEAN DEPTH: %f'%(np.nanmean(surf))



def calibrate(surface, baseplane):
	"""Do calibration here - scaling, setting zero point, removing dead pixels, and trimming edges(?)."""
	BAD_PIX = np.where(surface==2047)
	surface = surface.astype('float32')
	#need to remove planar slope
	surface += baseplane
	#scale
	surface *= SCALE_FACTOR
	surface[BAD_PIX] = np.nan

	return surface

def generate_baseplane(shape):
	"""Run on startup to get quick baseplane for calibration """
	X,Y = np.meshgrid(np.arange(0,shape[0]), np.arange(0,shape[1]))
	XX = X.flatten()
	YY = Y.flatten()
	Z = PLANE_PARAMS[0]*X + PLANE_PARAMS[1]*Y + PLANE_PARAMS[2]
	return Z


def update_surface(baseplane):
	"""Read updated topography and calibrate for use"""
	(depth,_)= get_depth()
	topo = calibrate(depth,baseplane)
	return topo


#roughly 4.5 units per cm


if __name__ == "__main__":
	from sys import argv
	script, fname = argv
	do_calib(fname)
