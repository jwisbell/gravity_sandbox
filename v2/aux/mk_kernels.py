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
a = 2.       # Plummer Radius
G = 1.           # Setting Gravitational constant to 1 for simplification           
u = []
'''for x in range(-640,640):
    y = -800
    plu = G/np.sqrt(x**2+y**2+a**2)
    u.append(plu)           # Create x array
 
for y in range(-460,460):
    p = []
    for x in range(-640,640):
        plu = G/np.sqrt(x**2+y**2+a**2)
        p.append(plu)           # Create y array
    u = np.vstack((p,u))        # Combine x and y array'''

#dx = np.zeros((len(range(-480,480)),len(range(-640,640))))
xw = int(410); yw =int(580)
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
'''fig,ax = plt.subplots(2)
ax[0].imshow(dx)
ax[1].imshow(dy)
plt.show()
'''
dx_dft =  np.fft.fft2(dx)
dy_dft = np.fft.fft2(dy)

'''fig,ax = plt.subplots(2)
ax[0].imshow(np.real(dx_dft))
ax[1].imshow(np.real(dy_dft))
plt.show()'''

np.save('dx_dft.npy',dx_dft)
np.save('dy_dft.npy',dy_dft)

from scipy.signal import convolve
dem = np.load('../display_dem.npy')
test = convolve(dem, dx,'same')
fig = plt.figure()
plt.imshow(test)
plt.show()