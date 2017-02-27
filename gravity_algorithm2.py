# Gravity Algorithm for AR Sandbox
# Fall 2016
# Jianbo Lu, Tyler Stercula, Sophie Deam

import numpy as np
from astropy.io import fits
from astropy.convolution import convolve, convolve_fft
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.mlab as mlab
import testing
# gdal (Geospatial Data Access Library) module allows DEM file manipulation
#import gdal
from time import time

start = time()

class Particle():
    def __init__(self,pos,vel):
        self.pos = pos
        self.vel = vel
        self.acc = [dx[int(self.pos[0]),int(self.pos[1])], dy[int(self.pos[0]),int(self.pos[1])]]
    def update_accel(self,pos):
        self.acc = [dx[int(self.pos[0]),int(self.pos[1])], dy[int(self.pos[0]),int(self.pos[1])]]
    def a(self):
        return [dx[int(self.pos[0]),int(self.pos[1])], dy[int(self.pos[0]),int(self.pos[1])]]
    def v(self,pos, step):
        temp_a = self.a()
        self.vel = [self.vel[0]+temp_a[0]*step, self.vel[1]+temp_a[1]*step]
        return self.vel
    """Function that updates (x,y,z,vx,vy,vz) by implementing the Runge-Kutta algorithm
        
        a = f(t,v0)
        b = f(t+dt/2, v+dt*a/2)
        c = f(t+dt/2, v+dt*b/2)
        d = f(t+dt, v+dt*c
        v1 = v0 + dt/6*(a + 2b + 2c + d)
    """
    def rk4(self, step, pos):
        p0 = pos
        k1 = self.v(pos,step/2)
        k1v = [p0[0]+step/2*k1[0],p0[1]+step/2*k1[1]]
        k2 = self.v(k1v, step/2)
        k2v = [p0[0]+step/2*k2[0],p0[1]+step/2*k2[1]]
        k3 = self.v(k2v, step/2)
        k3v = [p0[0]+step*k3[0],p0[1]+step*k3[1]]
        k4 = self.v(k3v,step/2)
        temp_pos = [pos[i] for i in range(len(pos))] #because otherwise it's a reference
        #temp_pos = [pos[i] for i in range(len(pos))]
        for i in range(len(temp_pos)):
            temp_pos[i] = pos[i] + step/6.0*(k1[i] + 2*k2[i] + 2*k3[i] + k4[i])
            #temp_pos[i] = pos[i] + temp_vel[i]*step #updates position using instantaneous velocity 
            #self.acc[i] = 1/6.0*(k1[i] + 2*k2[i] + 2*k3[i] + k4[i])
        return temp_pos#, temp_pos
    #-------------------------------------------------------------
    def update(self,step): 
        #p1 = [self.pos[i] + self.vel[i]*step for i in range(len(self.pos))]
        p1 = self.rk4(step/2., self.pos)
        #v1 = self.rk4(step, self.vel)
        #p2 = [self.pos[i] + self.vel[i]*(step/2.0) for i in range(len(self.pos))]
        if self.is_inbounds():
            self.update_accel(p1)
            p2 = self.rk4(step/2., self.pos)
            #v2 = self.rk4(step/2.0, self.vel)
            for i in range(2):
                self.pos[i] = p2[i]
        else:
            self.pos[i] = [x for x in p1]
    def is_inbounds(self):
        #print self.pos
        return self.pos[0] <= MAXX and self.pos[0] >= MIN and self.pos[1] <= MAXY and self.pos[1] >= MIN


dx,dy, potential = testing.make_acceleration_field(300,300,1)
'''from astropy.io import fits
hdu = fits.open('earth_moon_pot.fits')
potential = hdu[0].data'''
dx, dy = np.gradient(potential)
dx = np.negative(dx)
dy = np.negative(dy)
MAXX = dx.shape[1]-1
MIN = 0
MAXY = dy.shape[0]-1


# Sample values 
# NOTES: When the particle moves out of bounds of the density field, the calculation will stop and return an error. This will eventually be remedied so the particle either stops or reflects off of the boundary. 

# Calculate velocity from initial position
def acce(pos):
    return (dx[pos[0],pos[1]], dy[pos[0],pos[1]])

#needs exception handling

## Leapstep Definition ##
dtime = 0.1
acceleration = []
velocity_arr = []
pos_arr = []
energy = []
def leap(pos,vel):
    posi = np.rint(pos)         # Interpolate between pixels using np.rint in x direction
    #print posi
    acc = acce(posi)
    acceleration.append(acc)
    #print acc
    vel = vel + 0.5*dtime*np.array(acc)
    velocity_arr.append(vel)
    pos = pos + 0.5*dtime*vel
    pos_arr.append(pos[0])
    energy.append(e(pos, vel))
    posv = np.rint(pos)         # Interpolate between pixels using np.rint in y direction
    #if pos[0]<460 and pos[1]<640:
    acc = acce(posv)
    acceleration.append(acc)
    vel = vel + 0.5*dtime*np.array(acc)
    velocity_arr.append(vel)
    pos = pos + 0.5*dtime*vel
    pos_arr.append(pos[0])
    energy.append(e(pos, vel))
    return pos,vel      

## Energy Conservation: K+U; K is 0.5v^2 and U is index on the potential.
def e(pos,vel):
    return (0.5*np.sum(np.square(vel)) + potential[np.rint(pos[0]).astype(int)][np.rint(pos[1]).astype(int)])
# Needs further calibration: energy conservation violation becomes a problem as step size increases


## Orbit Calculation ##
posxtot = []
posytot = []
step = 0.01
times = 5000000                # Set the number of steps to be calculated
velocity = -np.sqrt(1./(320-300))
test_particle = Particle([320,300],[0,0])
print test_particle.pos


acceleration = []
velocity_arr = []
pos_arr = []
energy = []
def run_orbit(test_particle):
    num_steps = 0
    for n in xrange(1, times):
        #if pos[0]<460 and pos[1]<640:
        if test_particle.is_inbounds():
            test_particle.update(step)
            posxtot.append(test_particle.pos[0])
            posytot.append(test_particle.pos[1])
            acceleration.append(test_particle.acc[0])
            velocity_arr.append(test_particle.vel[0])
            pos_arr.append(test_particle.pos[0])
            #if test_particle.pos[0] <= 300:
            #num_steps = n
            #return num_steps
        else:
            break
    return num_steps
'''start_pos = np.linspace(1, 150,10)
masses = np.linspace(0.1, 1, 10)
f = open('timescale.txt','w')
ts= []
for x in masses:
    dx,dy, potential = testing.make_acceleration_field(300,300,x)
    #global potential = potential
    dx, dy = np.gradient(potential)
    dx = np.negative(dx)
    dy = np.negative(dy)
    part = Particle([300+50,300],[0,0])
    t = run_orbit(part)
    ts.append(t)
    f.write('%i\n'%(t))
f.close()
fig = plt.figure()
print len(start_pos), len(ts)
plt.plot(masses, ts)
plt.plot(masses, [1./np.sqrt(i)*1000 for i in masses],'g--')
plt.xlabel('Distance from central pixel')
plt.ylabel('Number of iterations to reach central pixel')
plt.title('Free-fall Timescale')
plt.savefig('free_fall_timescale.png',bbinches='tight')
plt.close()
'''
posxtot = []
posytot = []
velocity = -np.sqrt(1./(350-300))
test_particle = Particle([350,300],[0,-.28])
x= run_orbit(test_particle)


fig, (ax1,ax2, ax3) = plt.subplots(3)
ax1.plot(range(len(acceleration)), acceleration)
ax1.set_ylabel('Accleration')
ax2.plot(range(len(velocity_arr)), velocity_arr)
ax2.set_ylabel('Velocity')
ax3.plot(range(len(pos_arr)), pos_arr)
ax3.set_ylabel('Position')
#ax4.plot(range(len(energy)), energy)
#ax4.set_ylabel('Energy')
plt.savefig('rk4_freefall2.png', bbinches='tight')
plt.close()

# Plotting orbits for troubleshooting #
accel_im = np.zeros(dx.shape)
for i in range(dx.shape[0]):
    for j in range(dx.shape[1]):
        accel_im[i,j]=np.sqrt(dx[i,j]**2 + dy[i,j]**2)
fig = plt.figure()
plt.imshow(potential)
plt.plot(posxtot, posytot)
plt.suptitle('Orbit for Potential file with 1 pt')
plt.xlabel('X component of position')
plt.xlim((0,dx.shape[1]))
plt.ylim((0, dy.shape[0]))
plt.ylabel('Y component of position')
plt.savefig('freefall_test2.png',bbinches='tight')


time = time() - start
print time                # Benchmark time
plt.show()

#### FINAL NOTES: There still needs to be code written to replace the "Sample Values" with an IMPORTED .txt file from the interface team to define intial positions and velocities. Also, there needs to be code written to OUTPUT a .txt file of x and y position and time for the interface team. 
