# Gravity Algorithm for AR Sandbox
# Fall 2016
# Jianbo Lu, Tyler Stercula, Sophie Deam

### Calculating Discrete Plummer Kernel ###
import numpy as np
from astropy.io import fits
from scipy.ndimage.interpolation import shift
import pyfftw
import time
#import wisdom_parse
import matplotlib.pyplot as plt
a = 1.       # Plummer Radius
G = 10.           # Setting Gravitational constant to 1 for simplification
y = 1           
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

dx = np.zeros((len(range(-480,480)),len(range(-640,640))))
dy = np.copy(dx)
for y in range(-640,640):
	for x in range(-480,480):
		try:
			dx[x+480,y+640] = G/(x**2 + y**2 + a**2) * (x/np.sqrt(x**2. + y**2. + a**2))
		except:
			dx[x+480,y+640] = 0
		try:
			dy[x+480,y+640] = G/(x**2 + y**2 + a**2) * (y/np.sqrt(x**2. + y**2. + a**2))
		except:
			dy[x+480,y+640] = 0
'''fig,ax = plt.subplots(2)
ax[0].imshow(dx)
ax[1].imshow(dy)
plt.show()'''

#write Plummer Kernel to FITS Image
Plum = fits.PrimaryHDU(dx)       # Assign HDU
Plumlist = fits.HDUList([Plum])
Plumlist.writeto('dx_kernel.fits', clobber = True)   # Save kernel as .FITS file
#write Plummer Kernel to FITS Image
Plum = fits.PrimaryHDU(dy)       # Assign HDU
Plumlist = fits.HDUList([Plum])
Plumlist.writeto('dy_kernel.fits', clobber = True)   # Save kernel as .FITS file
    
#perform DFT on entire kernel
oned = np.reshape(dx,-1)
'''inp=pyfftw.empty_aligned(len(oned),dtype='float32',n=16)
for i in range(len(inp)):
	inp[i]=oned[i] 
output=pyfftw.empty_aligned(len(oned)//2+1, dtype='complex64',n=16)#np.zeros(oned.shape)
output[:] = np.ones(len(output))
print output.shape
try:
    #wis = wisdom_parse.read_wisdom()
    #wis = (pl for pl in plan)
    #print wis
    #print pyfftw.import_wisdom(wis)
    #w = input()
    transform = pyfftw.FFTW(inp, output, threads=4,flags='FFTW_MEASURE')
except:
    print 'No previous FFT plan found, proceeding and saving one for later.'
    transform = pyfftw.FFTW(inp, output,threads=4)
    plan = pyfftw.export_wisdom()
    for i in range(len(plan)):
        f = open('forward_plan_%i.txt'%(i),'w')
        f.write(plan[i])
        f.close()
    #print plan
    #w = input()

for i in range(len(inp)):
	inp[i]=oned[i] 
output[:] = np.ones(len(output)) 
start = time.time()
DFT = transform()'''
start = time.time()
a = pyfftw.empty_aligned(dx.shape, dtype='float32')
transform = pyfftw.builders.fft2(a)
'''for x in range(a.shape[0]):
	for y in range(a.shape[1]):
		a[x,y] = arr[x,y]'''
a[:,:] = dx[:,:]
np.nan_to_num(a)
tform1 = transform()
print np.max(tform1)


a[:,:] = dy[:,:]
tform2 = transform()



#print DFT
end = time.time()
print end-start
np.save('dxDFT.npy', np.fft.fft2(dx))
np.save('dyDFT.npy', np.fft.fft2(dy))

#write DFT of Plummer Kernel to FITS table
#column = fits.Column(name='dyDFT',format='M',array=DFT)
#cols = fits.ColDefs([column])
#tbhdu = fits.BinTableHDU.from_columns(cols)
#tbhdu.writeto('dxDFT.fits',clobber=True)

