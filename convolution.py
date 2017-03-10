import numpy as np
from astropy.io import fits
from scipy.ndimage.interpolation import shift
import pyfftw
import time
import wisdom_parse



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
	    transform = pyfftw.FFTW(inp, output, threads=4,flags='FFTW_WISDOM_ONLY')
	except:
	    print 'No previous FFT plan found, proceeding and saving one for later.'
	    transform = pyfftw.FFTW(inp, output,threads=4)
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
	output=pyfftw.empty_aligned(len(oned)*2 + 1,dtype='float32',n=16)
	inp=pyfftw.empty_aligned(len(oned), dtype='complex64',n=16)#np.zeros(oned.shape)
	for i in range(len(inp)):
		inp[i]=oned[i] 
	output[:] = np.ones(len(output))
	try:
	    wis = wisdom_parse.read_wisdom('backward_plan')
	    pyfftw.import_wisdom(wis)
	    transform = pyfftw.FFTW(inp, output, threads=4,direction:='FFTW_BACKWARD',flags='FFTW_WISDOM_ONLY')
	except:
	    print 'No previous FFT plan found, proceeding and saving one for later.'
	    transform = pyfftw.FFTW(inp, output,threads=4,direction:='FFTW_BACKWARD')
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
	tform2 = fft_forward(arr2)
	to_tform = tform1*tform2
	tform3 = fft_backward(to_tform)
	return tform3


