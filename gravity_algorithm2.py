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
from scipy.optimize import curve_fit

# gdal (Geospatial Data Access Library) module allows DEM file manipulation
#import gdal
from time import time

start = time()

class Particle():
    def __init__(self,pos,vel, potential):
        self.pot = potential
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
    def dynamic_timestep(self, step=0.1):
        p1 = self.rk4(step/2., self.pos)
        temp_pos = p1
        if self.is_inbounds(self.edge_mode):
            p2 = self.rk4(step/2., p1)
            temp_pos = p2
        p3 = self.rk4(step, self.pos)
        max_allowable_dif = 1
        if np.sqrt((p3[0]-temp_pos[0])**2 + (p3[1]-temp_pos[1])**2) > max_allowable_dif and step >= 0.01:#p3 and p1+p2 are very unalike
            step = self.dynamic_timestep(self, step/2)
        else:
            self.pos = [c for c in temp_pos]
        return step
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
        return temp_pos#, temp_pos
    #-------------------------------------------------------------
    def get_time_step(self):
        val = abs(self.pot[self.pos[0],self.pos[1]])
        #print 'potential value is ', val
        mx = 0.01*abs(np.min(self.pot))
        #print mx
        #return 0.01
        if val < 0.125*mx:
            return 0.1
        elif val >= 0.125*mx:
            return 0.0875
        elif val >= 0.25*mx:
            return 0.075
        elif val >= 0.375*mx:
            return 0.0625
        elif val >= 0.5*mx:
            return 0.05
        elif val >= 0.625*mx:
            return 0.0375
        elif val >= 0.75*mx:
            return 0.025
        elif val >= 0.75*mx:
            return 0.0125
        elif val > .95*mx:
            return 0.01
        else:
            return 0.01
    def update(self,step): 
        #p1 = [self.pos[i] + self.vel[i]*step for i in range(len(self.pos))]
        p1 = self.rk4(step/2., self.pos)
        #v1 = self.rk4(step, self.vel)
        #p2 = [self.pos[i] + self.vel[i]*(step/2.0) for i in range(len(self.pos))]
        if self.is_inbounds(self.edge_mode):
            self.update_accel(p1)
            p2 = self.rk4(step/2., p1)
            #v2 = self.rk4(step/2.0, self.vel)
            for i in range(2):
                self.pos[i] = p2[i]
        else:
            self.pos[i] = [x for x in p1]
    def is_inbounds(self, edge_mode):
        self.edge_mode = edge_mode
        if edge_mode == 'stop':
            return self.pos[0] < MAXX and self.pos[0] > MIN and self.pos[1] < MAXY and self.pos[1] > MIN
        if edge_mode == 'reflect':
            if self.pos[1] >= MAXX:
                self.pos[1] = MAXX-1
                self.vel[1] = self.vel[1] * -1
                print 'BOUNCE'
            elif self.pos[1] <= MIN:
                self.pos[1] = MIN+1
                self.vel[1] = self.vel[1] * -1
                print 'BOUNCE'
            elif self.pos[0] >= MAXY:
                self.pos[0] = MAXY-1
                self.vel[0] = self.vel[0] * -1
                print 'BOUNCE'
            elif self.pos[0] <= MIN:
                self.pos[0] = MIN+1
                self.vel[0] = self.vel[0] * -1
                print 'BOUNCE'
            return True
        if edge_mode == 'pacman':
            if self.pos[1] >= MAXX:
                self.pos[1] = MIN+1
            elif self.pos[1] <= MIN:
                self.pos[1] = MAXX-1
            elif self.pos[0] >= MAXY:
                self.pos[0] = MIN+1 
            elif self.pos[0] <= MIN:
                self.pos[0] = MAXY-1
            return True
        


dx,dy, potential = testing.make_acceleration_field(300,300,1)
'''from astropy.io import fits
hdu = fits.open('earth_moon_pot.fits')
potential = hdu[0].data'''
#potential = potential/np.sum(potential)*2 #normalize with ln
dx, dy = np.gradient(potential)
#dx = np.negative(dx)
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
times = 250000                # Set the number of steps to be calculated
velocity = -np.sqrt(1./(320-300))
#test_particle = Particle([320,300],[0,0])
#print test_particle.pos


acceleration = []
velocity_arr = []
pos_arr = []
energy = []
posxtot = []
posytot = []
interp_points = np.array([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.])
test_positionsx = []; test_positionsy = []
def run_orbit2(test_particle):
    num_steps = 0
    for n in xrange(1, times):
        #if pos[0]<460 and pos[1]<640:
        if test_particle.is_inbounds('reflect'):
            test_particle.update(0.01)
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


def run_orbit(test_particle, edge_mode='reflect'):
    num_steps = 0
    time = []
    posx = []; posy = []
    for n in xrange(1, times):
        print n
        if test_particle.is_inbounds(edge_mode):
            dt = test_particle.get_time_step()
            #print dt
            test_particle.update(step)
            posxtot.append(test_particle.pos[0])
            posytot.append(test_particle.pos[1])
            pos_arr.append(test_particle.pos[0])
            acceleration.append(dy[test_particle.pos[0], test_particle.pos[1]])
            posx.append(test_particle.pos[0])
            posy.append(test_particle.pos[1])
            time.append(dt)
            if np.sum(time) >= 1:
                to_sendx = np.interp(interp_points,time,posx)
                to_sendy = np.interp(interp_points,time,posy)
                for i in range(len(to_sendx)):
                    test_positionsx.append(to_sendx[i])
                    test_positionsy.append(to_sendy[i])
                time = []
                posx = []
                posy = []
        else:
            break
    return num_steps
def dynamic_orbit(test_particle, edge_mode='stop'):
    time = []
    posx = []; posy = []
    print test_particle.vel
    for n in range(1, times):
        if test_particle.is_inbounds(edge_mode):
            dt = test_particle.dynamic_timestep()
            posxtot.append(test_particle.pos[0])
            posytot.append(test_particle.pos[1])
            acceleration.append(dy[test_particle.pos[0], test_particle.pos[1]])
            posx.append(test_particle.pos[0])
            posy.append(test_particle.pos[1])
            time.append(dt)
            if np.sum(time) >= 1.:
                to_sendx = np.interp(interp_points,time,posx)
                to_sendy = np.interp(interp_points,time,posy)
                for i in range(len(to_sendx)):
                    test_positionsx.append(to_sendx[i])
                    test_positionsy.append(to_sendy[i])
                time = []
                posx = []
                posy = []
        else:
            break
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
'''
def functional(m, a, b):
    return a/np.sqrt(m) + b
f = open('timescale.txt','r')
lines = f.readlines()
f.close()
masses = np.linspace(0.1, 1, 10)
ts = []
for l in lines:
    data = l.split()
    ts.append(float(data[0]))
fig = plt.figure()
#print len(start_pos), len(ts)
plt.plot(masses, ts)
params,cov=curve_fit(functional,masses,np.array(ts),p0=[1.,0.])

plt.plot(masses, [functional(i,*params) for i in masses],'g--', linewidth=3)
print params
plt.xlabel('Distance from central pixel')
plt.ylabel('Number of iterations to reach central pixel')
plt.title('Free-fall Timescale')
plt.savefig('free_fall_timescale.png',bbinches='tight')
plt.close()


velocity = -np.sqrt(1./(350-300))
test_particle = Particle([300,320],[0,0], potential)
print 'HERE'
#x = run_orbit(test_particle)
#dynamic_orbit(test_particle)


fig, (ax1,ax2, ax3) = plt.subplots(3)
ax1.plot(range(len(acceleration)), acceleration)
ax1.set_ylabel('Accleration')
ax2.plot(range(len(velocity_arr)), velocity_arr)
ax2.set_ylabel('Velocity')
ax3.plot(range(len(posxtot)), posxtot)
ax3.set_ylabel('Position')
#ax4.plot(range(len(energy)), energy)
#ax4.set_ylabel('Energy')
#plt.savefig('rk4_freefall2.png', bbinches='tight')
plt.show()
plt.close()

# Plotting orbits for troubleshooting #
accel_im = np.zeros(dx.shape)
for i in range(dx.shape[0]):
    for j in range(dx.shape[1]):
        accel_im[i,j]=np.sqrt(dx[i,j]**2 + dy[i,j]**2)
fig = plt.figure()
plt.imshow(potential)
plt.plot(posytot, posxtot, linewidth=2)
#plt.plot(test_positionsx, test_positionsy, linewidth=1)
plt.suptitle('Orbit for Potential file with 1 pt')
plt.xlabel('X component of position')
plt.xlim((0,dx.shape[1]))
plt.ylim((0, dy.shape[0]))
plt.ylabel('Y component of position')
#plt.savefig('freefall_test2.png',bbinches='tight')


time = time() - start
print time                # Benchmark time
plt.show()

#### FINAL NOTES: There still needs to be code written to replace the "Sample Values" with an IMPORTED .txt file from the interface team to define intial positions and velocities. Also, there needs to be code written to OUTPUT a .txt file of x and y position and time for the interface team. 
