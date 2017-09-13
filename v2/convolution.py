import numpy as np
from astropy.io import fits
from scipy.ndimage.interpolation import shift
#import pyfftw
import time
#import wisdom_parse
from scipy import signal

import warnings
warnings.filterwarnings("ignore")

def pad(arr1, shape):
	#Pad arr1 with zeros to reach the desired shape
	bck = np.zeros(shape)
	dx = abs(arr1.shape[0] - shape[0])/2
	dy = abs(arr1.shape[1] - shape[1])/2
	bck[dx:-dx, dy:-dy-1] = arr1
	return bck.flatten()

def unpad(arr1, shape):
	#remove zeroes from arr1 until it reaches the desired shape
	arr1 = np.reshape(arr1,(960,1280))
	dx = abs(arr1.shape[0] - shape[0])/2
	dy = abs(arr1.shape[1] - shape[1])/2
	return arr1[dx:-dx, dy:-dy]

def ew_mult(a1, a2):
	#Perform an element-wise explicitly of two arrays. Used to check numpy's result
	f = np.zeros(a1.shape)
	for k in range(len(a1)):
		f[k] = a1[k] * a2[k]
	return f

"""
Convolve the density array with the acceleration kernel to get gx, gy using the circular convolution theorem.
Two-Dim convolution to maintain shape without supressing information. 
Found that numpy is faster in this case than FFTW, problably due to python wrappers and the overhead of multi-core setup.
"""
def convolve2d(arr, x_kernel, y_kernel,method='np'):
	#Pad the arrays with zeros so they are the desired shape
	bck = np.zeros(x_kernel.shape)
	dx = abs(arr.shape[0] - x_kernel.shape[0])/2
	dy = abs(arr.shape[1] - x_kernel.shape[1])/2
	bck[dx:-dx, dy:-dy] = arr
	
	#Do the 2d convolution using FFTW, do not reccommend
	if method == 'fftw':
		a = pyfftw.empty_aligned(bck.shape, dtype='float32')
		transform = pyfftw.builders.fft2(a)
	
		a[:,:] = bck[:,:]
		tform1 = transform()
	
		gx = x_kernel*tform1
		gy = y_kernel*tform1

		b = pyfftw.empty_aligned(gx.shape, dtype='complex64')
		inverse = pyfftw.builders.ifft2(b)
	
		b[:,:] = gx[:,:]

		gx_wrapped = inverse()
	
		b[:,:] = gy[:,:]
	
		gy_wrapped = inverse()

		framework = np.zeros((gx_wrapped.shape[0]*2, gx_wrapped.shape[1]*2))
		framework[:gx_wrapped.shape[0], :gx_wrapped.shape[1]] = gx_wrapped
		framework[:gx_wrapped.shape[0], gx_wrapped.shape[1]:] = gx_wrapped
		framework[gx_wrapped.shape[0]:, :gx_wrapped.shape[1]] = gx_wrapped
		framework[gx_wrapped.shape[0]:, gx_wrapped.shape[1]:] = gx_wrapped
		wx = float(framework.shape[0]); wy = float(framework.shape[1])
		gx = framework[wx/2-240:wx/2+240, wy/2-320:wy/2+319]

		framework[:gy_wrapped.shape[0], :gy_wrapped.shape[1]] = gy_wrapped
		framework[:gy_wrapped.shape[0], gy_wrapped.shape[1]:] = gy_wrapped
		framework[gy_wrapped.shape[0]:, :gy_wrapped.shape[1]] = gy_wrapped
		framework[gy_wrapped.shape[0]:, gy_wrapped.shape[1]:] = gy_wrapped
		gy = framework[wx/2-240:wx/2+240, wy/2-320:wy/2+319]

		return gx, gy
	#Do the convolution using numpy -  faster than FFTW in this case
	elif method=='wrap':
		bck = np.zeros( (arr.shape[0]*3, arr.shape[1]*3) )
		wx = arr.shape[0]; wy =arr.shape[1]
		#the middle section is the array we care about
		bck[wx:2*wx, wy:2*wy] = arr

		#fill the other 8 sections with a value
		vals = np.copy(arr)
		#vals = np.zeros(arr.shape)
		#vals = np.ones(arr.shape)*np.mean(arr)

		bck[:wx, :wy] = vals
		bck[:wx, wy:2*wy] = vals
		bck[:wx, -wy:] = vals
		bck[wx:2*wx, :wy] = vals
		bck[wx:2*wx, -wy:] = vals
		bck[-wx:, :wy] = vals
		bck[-wx:, wy:2*wy] = vals
		bck[-wx:, -wy:] = vals

		tform1 = np.fft.fft2(bck)
		gx = tform1 * x_kernel
		gy = tform1 * y_kernel

		#get the padded inverse transforms for gx and gy
		gx_wrapped = np.fft.ifft2(gx)
		gy_wrapped = np.fft.ifft2(gy)

		xw = arr.shape[1]/2
		yw = arr.shape[0]/2
		
		#build a background framework to store the values temporarily
		framework = np.zeros((gx_wrapped.shape[0]*2, gx_wrapped.shape[1]*2))

		#fill the framework with the padded arrays then cut out the needed portion
		framework[:gx_wrapped.shape[0], :gx_wrapped.shape[1]] = gx_wrapped
		framework[:gx_wrapped.shape[0], gx_wrapped.shape[1]:] = gx_wrapped
		framework[gx_wrapped.shape[0]:, :gx_wrapped.shape[1]] = gx_wrapped
		framework[gx_wrapped.shape[0]:, gx_wrapped.shape[1]:] = gx_wrapped
		wx = float(framework.shape[0]); wy = float(framework.shape[1])
		gx = np.copy(framework[wx/2-yw:wx/2+yw, wy/2-xw:wy/2+xw])
		
		framework[:gy_wrapped.shape[0], :gy_wrapped.shape[1]] = gy_wrapped
		framework[:gy_wrapped.shape[0], gy_wrapped.shape[1]:] = gy_wrapped
		framework[gy_wrapped.shape[0]:, :gy_wrapped.shape[1]] = gy_wrapped
		framework[gy_wrapped.shape[0]:, gy_wrapped.shape[1]:] = gy_wrapped
		gy = framework[wx/2-yw:wx/2+yw, wy/2-xw:wy/2+xw]

		# --- scale the acceleration fields if necessary and make negative -------
		#gx = signal.convolve(arr,x_kernel,'same')
		#gy = signal.convolve(arr,y_kernel,'same') 
		gx = np.negative(gx)*.6
		gy = np.negative(gy)*.6

		# Get second order terms for a potential leapfrog improvement
		#---- d2x and d2y ---
		g2x, junk = np.gradient(gx)
		g2y, junk = np.gradient(gy)

		print gx.shape
		
		return gx, gy, g2x, g2x

	else:
		#do the fft of the density field and multiply with fft kernels
		tform1 = np.fft.fft2(bck)
		gx = tform1 * x_kernel
		gy = tform1 * y_kernel

		#get the padded inverse transforms for gx and gy
		gx_wrapped = np.fft.ifft2(gx)
		gy_wrapped = np.fft.ifft2(gy)

		xw = arr.shape[1]/2
		yw = arr.shape[0]/2
		
		#build a background framework to store the values temporarily
		framework = np.zeros((gx_wrapped.shape[0]*2, gx_wrapped.shape[1]*2))

		#fill the framework with the padded arrays then cut out the needed portion
		framework[:gx_wrapped.shape[0], :gx_wrapped.shape[1]] = gx_wrapped
		framework[:gx_wrapped.shape[0], gx_wrapped.shape[1]:] = gx_wrapped
		framework[gx_wrapped.shape[0]:, :gx_wrapped.shape[1]] = gx_wrapped
		framework[gx_wrapped.shape[0]:, gx_wrapped.shape[1]:] = gx_wrapped
		wx = float(framework.shape[0]); wy = float(framework.shape[1])
		gx = np.copy(framework[wx/2-yw:wx/2+yw, wy/2-xw:wy/2+xw])
		
		framework[:gy_wrapped.shape[0], :gy_wrapped.shape[1]] = gy_wrapped
		framework[:gy_wrapped.shape[0], gy_wrapped.shape[1]:] = gy_wrapped
		framework[gy_wrapped.shape[0]:, :gy_wrapped.shape[1]] = gy_wrapped
		framework[gy_wrapped.shape[0]:, gy_wrapped.shape[1]:] = gy_wrapped
		gy = framework[wx/2-yw:wx/2+yw, wy/2-xw:wy/2+xw]

		# --- scale the acceleration fields if necessary and make negative -------
		#gx = signal.convolve(arr,x_kernel,'same')
		#gy = signal.convolve(arr,y_kernel,'same') 
		gx = np.negative(gx)*.5
		gy = np.negative(gy)*.5

		# Get second order terms for a potential leapfrog improvement
		#---- d2x and d2y ---
		g2x, junk = np.gradient(gx)
		g2y, junk = np.gradient(gy)
		
		return gx, gy, g2x, g2x

	



