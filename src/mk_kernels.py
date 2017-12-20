"""
Convolution kernel calculation for Gravbox, an Augmented Reality Gravitational Dynamics Simulation. 
Saves the DFT of the convolution kernels to reduce run-time calculations.

This was developed at the University of Iowa by Jacob Isbell
    based on work in Dr. Fu's Introduction to Astrophysics class by Jacob Isbell, Sophie Deam, Jianbo Lu, and Tyler Stercula (beta version)
Version 1.0 - December 2017
"""

import numpy as np
from scipy.ndimage.interpolation import shift
#import pyfftw
import time
import matplotlib.pyplot as plt


def make(xw=410,yw=580,xname='./aux/dx_dft.npy',yname='./aux/dy_dft.npy'):
	#function to make the kernels and save to xname, yname
	#xw and yw are the dimensions of the input topography 

	a = 2.       # Plummer offset to prevent singularities
	G = 1.       # Setting Gravitational constant to 1 for simplification           
	u = []

	#define kernel to be twice as large as the topography for wrapping of values
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

	#calculate the dft of the above kernel
	dx_dft =  np.fft.fft2(dx)
	dy_dft = np.fft.fft2(dy)

	#save the dfts
	np.save(xname,dx_dft)
	np.save(yname,dy_dft)
