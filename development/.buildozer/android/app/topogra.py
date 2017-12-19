from freenect import sync_get_depth as get_depth
import numpy as np
import scipy.linalg
import functools
import scipy.optimize


PLANE_PARAMS = [0,0,-700]#[0.006452, -0.032609, 712.261579]
SCALE_FACTOR = 1./50


def plane(x, y, params):
    a = params[0]
    b = params[1]
    c = params[2]
    z = a*x + b*y + c
    return z

def error(params, points):
    result = 0
    for (x,y,z) in points:
        plane_z = plane(x, y, params)
        diff = abs(plane_z - z)
        result += diff**2
    return result


def do_calib(fname):
    data = np.load(fname)
    # best-fit linear plane
    # regular grid covering the domain of the data
    X,Y = np.meshgrid(np.arange(0,data.shape[1]), np.arange(0,data.shape[0]))
    
    points =     [(10,10,data[10,10]),
                (10,data.shape[0]-10,data[10,-10]),
                (data.shape[1]-10,10,data[-10,10]),
                (data.shape[1]-10,data.shape[0]-10,data[-10,-10])]

    fun = functools.partial(error, points=points)
    params0 = [0, 0, 0]
    res = scipy.optimize.minimize(fun, params0)

    badpx = np.where(data==2047)
    data = data.astype('float32')
    data[badpx] = np.nan

    #A = np.c_[data[:,0], data[:,1], np.ones(data.shape[0])]
    #C,_,_,_ = scipy.linalg.lstsq(A, data[:,2])    # coefficients
    
    # evaluate it on grid
    a = res.x[0]
    b = res.x[1]
    c = res.x[2]
    Z = a*X + b*Y + c

    surf = np.copy(data) - Z

    print 'PLANAR COEFFICIENTS: %f, %f, %f'%(a,b,c)
    print 'MEAN DEPTH: %f'%(np.nanmean(surf))



'''def calibrate(surface, baseplane):
    """Do calibration here - scaling, setting zero point, removing dead pixels, and trimming edges(?)."""
    BAD_PIX = np.where(surface==2047)
    surface = surface.astype('float32')
    #need to remove planar slope
    surface -= baseplane
    #scale
    surface *= SCALE_FACTOR
    #surface[BAD_PIX] = np.nan

    return surface'''
def calibrate(surface, baseplane):
    """Do calibration here - scaling, setting zero point, removing dead pixels, and trimming edges(?)."""
    BAD_PIX = np.where(surface==2047)
    surface = surface.astype('float32')
    #need to remove planar slope
    surface += baseplane
    #scale
    surface = np.power(surface,1.)
    surface *= 1.#SCALE_FACTOR
    #surface = np.negative(surface)
    surface[BAD_PIX] = 0.#np.nan

    return surface, BAD_PIX

def generate_baseplane(shape=(640,480)):
    """Run on startup to get quick baseplane for calibration """
    X,Y = np.meshgrid(np.arange(0,shape[0]), np.arange(0,shape[1]))
    XX = X.flatten()
    YY = Y.flatten()
    Z = PLANE_PARAMS[0]*X + PLANE_PARAMS[1]*Y + PLANE_PARAMS[2]
    return Z


def update_surface(baseplane,prev,CEILING=30):
    """Read updated topography and calibrate for use"""
    (depth,_)= get_depth()
    topo,pix = calibrate(depth,baseplane)
    if prev == None:
        return topo
    if len(np.where(topo>CEILING)[0]) + len(np.where(topo>CEILING)[1]) > 20:
        return topo
    return topo


#roughly 4.5 units per cm


if __name__ == "__main__":
    from sys import argv
    script, fname = argv
    import matplotlib.pyplot as plt
    do_calib(fname)
    baseplane = generate_baseplane()
    test = update_surface(baseplane)
    fig = plt.figure()
    plt.imshow(test)
    plt.show()

