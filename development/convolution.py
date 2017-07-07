import numpy as np
from astropy.io import fits
from scipy.ndimage.interpolation import shift
import pyfftw
import time
import wisdom_parse
from scipy import signal

def pad(arr1, shape):
	'''delta = shape-len(arr1)
	w = delta/2
	return np.concatenate((np.zeros(w), arr1, np.zeros(w)))'''
	bck = np.zeros(shape)
	dx = abs(arr1.shape[0] - shape[0])/2
	dy = abs(arr1.shape[1] - shape[1])/2
	bck[dx:-dx, dy:-dy-1] = arr1
	return bck.flatten()

def unpad(arr1, shape):
	'''delta = abs(shape-len(arr1))
	w = delta/2
	return arr1[w:-w]'''
	arr1 = np.reshape(arr1,(960,1280))
	dx = abs(arr1.shape[0] - shape[0])/2
	dy = abs(arr1.shape[1] - shape[1])/2
	return arr1[dx:-dx, dy:-dy]

def ew_mult(a1, a2):
	f = np.zeros(a1.shape)
	for k in range(len(a1)):
		f[k] = a1[k] * a2[k]
	return f

def fft_forward(arr):
	#perform DFT on entire kernel
	oned = np.reshape(arr,-1)
	inp=pyfftw.empty_aligned(len(oned),dtype='float32',n=16)
	for i in range(len(inp)):
		inp[i]=oned[i] 
	output=pyfftw.empty_aligned(len(oned)//2+1, dtype='complex64',n=16)#np.zeros(oned.shape)
	output[:] = np.ones(len(output))
	try:
	    wis = wisdom_parse.read_wisdom('./aux/forward_plan')
	    pyfftw.import_wisdom(wis)
	    transform = pyfftw.FFTW(inp, output, threads=8,flags='FFTW_WISDOM_ONLY')
	except:
	    print 'No previous FFT Forward plan found, proceeding and saving one for later.'
	    transform = pyfftw.FFTW(inp, output,threads=8)
	    plan = pyfftw.export_wisdom()
	    for i in range(len(plan)):
	        f = open('./aux/forward_plan_%i.txt'%(i),'w')
	        f.write(plan[i])
	        f.close()
	for i in range(len(inp)):
		inp[i]=oned[i] 
	DFT = transform()
	return DFT

def fft_backward(arr):
	oned = np.reshape(arr,-1)
	output=pyfftw.empty_aligned((len(oned)-1)*2,dtype='float32',n=16)
	inp=pyfftw.empty_aligned(len(oned), dtype='complex64',n=16)#np.zeros(oned.shape)
	for i in range(len(inp)):
		inp[i]=oned[i] 
	output[:] = np.ones(len(output))
	try:
	    wis = wisdom_parse.read_wisdom('./aux/backward_plan')
	    pyfftw.import_wisdom(wis)
	    transform = pyfftw.FFTW(inp, output, threads=8,direction='FFTW_BACKWARD',flags='FFTW_WISDOM_ONLY')
	except:
	    print 'No previous FFT Backward plan found, proceeding and saving one for later.'
	    transform = pyfftw.FFTW(inp, output,threads=8,direction='FFTW_BACKWARD')
	    plan = pyfftw.export_wisdom()
	    for i in range(len(plan)):
	        f = open('./aux/backward_plan_%i.txt'%(i),'w')
	        f.write(plan[i])
	        f.close()
	for i in range(len(inp)):
		inp[i]=oned[i] 
	DFT = transform()
	return DFT


def convolve(arr1, arr2):
	tform1 = fft_forward(arr1)
	tform2 = fft_forward(arr2)
	to_tform = tform1*tform2
	tform3 = fft_backward(to_tform)
	return tform3

def convolve(arr1, x_kernel,y_kernel, arr_type):
	#arr1 = arr1.flatten() 
	#print len(arr1)
	orig_shp = arr1.shape
	#if len(arr1) != len(x_kernel):
		#arr1 = pad(arr1, (960,1280))
	#tform2 = fft_forward(arr1)
	#temp = [x[0] for x in tform2]
	#print x_kernel[0]
	#print tform2, tform1[0]
	#print len(tform2), len(arr1), len(x_kernel)	
	#gx = x_kernel*tform2
	#gy = y_kernel*tform2
	#print to_tform, to_tform.shape
	#gx = fft_backward(gx)
	#gy = fft_backward(gy)
	#print tform3
	
	#print len(gx)
	gx = signal.fftconvolve(arr1, x_kernel,mode='same')
	gy = signal.fftconvolve(arr1, y_kernel,mode='same')
	#gx = unpad(gx, orig_shp)
	#gy = unpad(gy, orig_shp)
	#print tform4.shape
	return gx,gy

def convolve2d(arr, x_kernel, y_kernel,method='np'):
	#need to zero pad
	bck = np.zeros(x_kernel.shape)
	dx = abs(arr.shape[0] - x_kernel.shape[0])/2
	dy = abs(arr.shape[1] - x_kernel.shape[1])/2
	bck[dx:-dx, dy:-dy-1] = arr
	
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
	else:
		tform1 = np.fft.fft2(bck)
		gx = tform1 * x_kernel
		gy = tform1 * y_kernel

		gx_wrapped = np.fft.ifft2(gx)
		gy_wrapped = np.fft.ifft2(gy)
		
		framework = np.zeros((gx_wrapped.shape[0]*2, gx_wrapped.shape[1]*2))
		framework[:gx_wrapped.shape[0], :gx_wrapped.shape[1]] = gx_wrapped
		framework[:gx_wrapped.shape[0], gx_wrapped.shape[1]:] = gx_wrapped
		framework[gx_wrapped.shape[0]:, :gx_wrapped.shape[1]] = gx_wrapped
		framework[gx_wrapped.shape[0]:, gx_wrapped.shape[1]:] = gx_wrapped
		wx = float(framework.shape[0]); wy = float(framework.shape[1])
		gx = np.copy(framework[wx/2-240:wx/2+240, wy/2-320:wy/2+319])
		'''import matplotlib.pyplot as plt
		fig = plt.figure()
		plt.imshow(framework, vmin=0.5*np.min(framework), vmax=.5*np.max(framework))
		plt.show()
		'''
		framework[:gy_wrapped.shape[0], :gy_wrapped.shape[1]] = gy_wrapped
		framework[:gy_wrapped.shape[0], gy_wrapped.shape[1]:] = gy_wrapped
		framework[gy_wrapped.shape[0]:, :gy_wrapped.shape[1]] = gy_wrapped
		framework[gy_wrapped.shape[0]:, gy_wrapped.shape[1]:] = gy_wrapped
		gy = framework[wx/2-240:wx/2+240, wy/2-320:wy/2+319]

		print np.where(gy == np.max(gy))
		print np.where(gy == np.min(gy))

		print np.where(gx == np.max(gx))
		print np.where(gx == np.min(gx))

		#---- d2x and d2y ---
		g2x = np.gradient(gx)
		g2y = np.gradient(gy)
		
		return gx, gy

	



