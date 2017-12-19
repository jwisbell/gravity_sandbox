# Gravity Algorithm for AR Sandbox
# Fall 2016
# Jianbo Lu, Tyler Stercula, Sophie Deam

### Calculating Discrete Plummer Kernel ###
import numpy as np
from astropy.io import fits
from scipy.ndimage.interpolation import shift
import pyfftw
import time
import matplotlib.pyplot as plt


def make(xw=410,yw=580,xname='./aux/dx_dft.npy',yname='./aux/dy_dft.npy'):
	a = 2.       # Plummer Radius
	G = 1.           # Setting Gravitational constant to 1 for simplification           
	u = []

	#xw = int(410); yw =int(580)
	dx = np.zeros((len(range(-xw,xw)),len(range(-yw,yw))))
	dy = np.copy(dx)
	for y in range(-yw,yw):
		for x in range(-xw,xw):
			try:
			    dx[x+xw,y+yw] = G/(x**2 + y**2 + a**2) * (x/np.sqrt(x**2. + y**2. + a**2)) #G/r^2 * dx/r 
			except:
				dx[x+xw,y+yw] = 1
			try:
			    dy[x+xw,y+yw] = G/(x**2 + y**2 + a**2) * (y/np.sqrt(x**2. + y**2. + a**2))
			except:
			    dy[x+xw,y+yw] = 1

	dx_dft =  np.fft.fft2(dx)
	dy_dft = np.fft.fft2(dy)


	np.save(xname,dx_dft)
	np.save(yname,dy_dft)
