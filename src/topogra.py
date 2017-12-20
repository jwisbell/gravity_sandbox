"""
Software to interface with Kinect to read in surface topography for Gravbox, an Augmented Reality Gravitational Dynamics Simulation. 
Calibrates plane of data based on SARndbox calibration files (BoxLayout.txt).

This was developed at the University of Iowa by Jacob Isbell
    based on work in Dr. Fu's Introduction to Astrophysics class by Jacob Isbell, Sophie Deam, Jianbo Lu, and Tyler Stercula (beta version)
Version 1.0 - December 2017
"""
from freenect import sync_get_depth as get_depth
import numpy as np
import scipy.linalg
import functools
import scipy.optimize



PLANE_PARAMS = [0.01,-0.001, 730.] #to be modified slightly for a specific system
SCALE_FACTOR = 1./50

#roughly 4.5 units per cm


def plane(x, y, params):
    #plane equation for slope subtraction
    a = params[0]
    b = params[1]
    c = params[2]
    z = a*x + b*y + c
    return z

"""Error function for fitting the planar parameters"""
def error(params, points):
    result = 0
    for (x,y,z) in points:
        plane_z = plane(x, y, params)
        diff = abs(plane_z - z)
        result += diff**2
    return result

"""Read in the AR Sandbox Calibration File"""
def ar_calibration(fname='./aux/BoxLayout.txt'):
    f = open(fname,'r')
    lines = f.readlines()
    plane = lines[0].split('(')[1].split(')')[0].split(',')
    plane = np.array(plane,dtype=float)
    factor = 730./float(lines[0].split(')')[1].split(',')[1])
    vertices = []
    for k in range(1,len(lines)-1):
        l = lines[k]
        if len(l)>1:
            print l.strip('(')
            d = l.strip('(')
            d = d.strip(')')[:-2]
            data = d.strip().split(',')
            print data[0], 'here'
            x = float(data[0])
            y = float(data[1])
            z = float(data[2])*factor
            vertices.append((x,y,z))
    f.close()

    #return the vertices of the 'good' boundary

    a = plane[0]#factor
    b = plane[1]#*factor
    c = 730.
    #Z = a*X + b*Y + c
    print vertices[0][0]

    print 'COPY PLANAR_PARAMS to the constant value at the start of this script'
    print 'PLANAR_PARAMS =  [%f, %f, %f]'%(a,b,c)
    print 'BOUNDARIES = [%f,%f],[%f,%f]'%(vertices[0][0],vertices[1][1],vertices[2][0],vertices[2][1])
    print 'COPY SHAPE to gravbox.py XWIDTH YWIDTH'
    shp = np.zeros( (480,640) )
    bounds = [vertices[1][0],vertices[0][0],vertices[2][1],vertices[1][1]]
    bounds = [40,-30,30,-30]
    print bounds
    print 'SHAPE: ', shp[bounds[0]:bounds[1], bounds[2]:bounds[3]].shape


    return generate_baseplane((a,b,c),shp[bounds[0]:bounds[1], bounds[2]:bounds[3]].shape), bounds


def calibrate(surface,baseplane,bounds):
    """Do calibration here - scaling, setting zero point, removing dead pixels, and trimming edges."""
    surface = surface.astype('float32')
    
    #need to remove planar slope
    surface = surface[bounds[0]:bounds[1], bounds[2]:bounds[3]] - baseplane
    BAD_PIX = []#np.where(surface>=200)
    surface *= .1#SCALE_FACTOR
    #scale exponentially
    x =  np.power(np.e,np.absolute(surface))
    surface = x * np.absolute(surface) / surface * 10
   
    surface[BAD_PIX] = 0.#np.nan

    return np.nan_to_num(surface), BAD_PIX

def generate_baseplane(params,shape=(580,410)):
    """Run on startup to get quick baseplane for calibration using PLANE_PARAMS"""
    X,Y = np.meshgrid(np.arange(0,shape[1]), np.arange(0,shape[0]))
    XX = X.flatten()
    YY = Y.flatten()
    Z = params[0]*X + params[1]*Y + params[2]
    return Z


def update_surface(baseplane,bounds,prev=None,FLOOR=-600,verbose=False):
    """Read updated topography and calibrate for use"""
    #(depth,_)= get_depth()
    d = []
    for i in range(10):
        (depth,_)= get_depth()
        d.append(depth)
        #time.sleep()
    #time average the readings to reduce noise
    #currently taking mean, maybe switch to median
    depth = np.sum(d[::],axis=0)/10.
    topo,pix = calibrate(depth,baseplane,bounds)
    if verbose:
        print 'SURFACE STATS'
        print np.mean(topo), np.max(topo),np.min(topo), np.median(topo)
    #if there are enough pixels above a threshold, ignore and show previous topo
    #this is useful when hands are in the sandbox
    if len(np.where(topo<FLOOR)[0]) + len(np.where(topo<FLOOR)[1]) > 20:
        if prev == None:
            return topo #- np.nanmedian(topo)
        else:
            return prev
    return topo #- np.nanmedian(topo)




"""Run the calibration scripts and output a plot showing how well the plane subtraction worked."""
if __name__ == "__main__":
    from sys import argv
    script, fname = argv
    import matplotlib.pyplot as plt
    

    baseplane, bounds = ar_calibration()
    test = update_surface(baseplane,bounds,None)

    stretch_vals = np.ones(test.shape[0])
    stretch_vals[:test.shape[0]/8] = 2
    test = np.repeat(test,stretch_vals.astype(int), axis=0)

    fig = plt.figure()
    plt.imshow(test)
    plt.show()

