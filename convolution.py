import numpy as np
from astropy.io import fits
from scipy.ndimage.interpolation import shift
import pyfftw
import time
import wisdom_parse

def pad(arr1, shape):
	delta = shape-len(arr1)
	w = delta/2
	return np.concatenate((np.zeros(w), arr1, np.zeros(w)))

def unpad(arr1, shape):
	delta = abs(shape-len(arr1))
	w = delta/2
	return arr1[w:-w]

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
	    wis = wisdom_parse.read_wisdom('forward_plan')
	    pyfftw.import_wisdom(wis)
	    transform = pyfftw.FFTW(inp, output, threads=8,flags='FFTW_WISDOM_ONLY')
	except:
	    print 'No previous FFT Forward plan found, proceeding and saving one for later.'
	    transform = pyfftw.FFTW(inp, output,threads=8)
	    plan = pyfftw.export_wisdom()
	    for i in range(len(plan)):
	        f = open('forward_plan_%i.txt'%(i),'w')
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
	    wis = wisdom_parse.read_wisdom('backward_plan')
	    pyfftw.import_wisdom(wis)
	    transform = pyfftw.FFTW(inp, output, threads=8,direction='FFTW_BACKWARD',flags='FFTW_WISDOM_ONLY')
	except:
	    print 'No previous FFT Backward plan found, proceeding and saving one for later.'
	    transform = pyfftw.FFTW(inp, output,threads=8,direction='FFTW_BACKWARD')
	    plan = pyfftw.export_wisdom()
	    for i in range(len(plan)):
	        f = open('backward_plan_%i.txt'%(i),'w')
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

def convolve(arr1, tform1, arr_type):
	arr1 = arr1.flatten() 
	orig_len = len(arr1)
	if len(arr1) != len(tform1):
		arr1 = pad(arr1, len(tform1))
	tform2 = fft_forward(arr1)
	#print tform2, tform1[0]	
	to_tform = np.array(tform1[0])*tform2
	#print to_tform, to_tform.shape
	tform3 = fft_backward(to_tform)
	print tform3
	tform4 = unpad(tform3, orig_len)
	print tform4.shape
	return tform4


