# Gravity Algorithm for AR Sandbox
# Fall 2016
# Jianbo Lu, Tyler Stercula, Sophie Deam

### Calculating Discrete Plummer Kernel ###
import numpy as np
from astropy.io import fits
from scipy.ndimage.interpolation import shift
import pyfftw
import time
import wisdom_parse
a = 0.5         # Plummer Radius
G = 1           # Setting Gravitational constant to 1 for simplification
y = 1           
u = []
for x in range(-640,640):
    y = -800
    plu = G/np.sqrt(x**2+y**2+a**2)
    u.append(plu)           # Create x array
 
for y in range(-460,460):
    p = []
    for x in range(-640,640):
        plu = G/np.sqrt(x**2+y**2+a**2)
        p.append(plu)           # Create y array
    u = np.vstack((p,u))        # Combine x and y array
    
#perform DFT on entire kernel
oned = np.reshape(u,-1)
inp=pyfftw.empty_aligned(len(oned),dtype='float32',n=16)
for i in range(len(inp)):
	inp[i]=oned[i] 
output=pyfftw.empty_aligned(len(oned)//2+1, dtype='complex64',n=16)#np.zeros(oned.shape)
output[:] = np.ones(len(output))
print output.shape
try:
    wis = wisdom_parse.read_wisdom()
    #wis = (pl for pl in plan)
    print wis
    print pyfftw.import_wisdom(wis)
    #w = input()
    transform = pyfftw.FFTW(inp, output, threads=4,flags='FFTW_WISDOM_ONLY')
except:
    print 'No previous FFT plan found, proceeding and saving one for later.'
    transform = pyfftw.FFTW(inp, output,threads=4)
    plan = pyfftw.export_wisdom()
    for i in range(len(plan)):
        f = open('forward_plan_%i.txt'%(i),'w')
        f.write(plan[i])
        f.close()
    print plan
    #w = input()

for i in range(len(inp)):
	inp[i]=oned[i] 
start = time.time()
DFT = transform()
end = time.time()
print end-start
#print DFT*1000
#write Plummer Kernel to FITS Image
Plum = fits.PrimaryHDU(u)       # Assign HDU
Plumlist = fits.HDUList([Plum])
Plumlist.writeto('DiscPlumFITS.fits', clobber = True)   # Save kernel as .FITS file

#write DFT of Plummer Kernel to FITS table
column = fits.Column(name='PlummerDFT',format='M',array=DFT)
cols = fits.ColDefs([column])
tbhdu = fits.BinTableHDU.from_columns(cols)
tbhdu.writeto('PlummerDFT.fits',clobber=True)

