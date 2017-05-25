# Gravity Algorithm for AR Sandbox
# Fall 2016
# Jianbo Lu, Tyler Stercula, Sophie Deam

import numpy as np
from astropy.io import fits
from astropy.convolution import convolve, convolve_fft
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.mlab as mlab
#import testing
from scipy.optimize import curve_fit

# gdal (Geospatial Data Access Library) module allows DEM file manipulation
#import gdal
import time



class Particle():
    def __init__(self,pos,vel, accel,smoothness=4):
        #self.pot = potential
        #dx, dy = np.gradient(potential,smoothness)
        self.dx = accel[0]
        self.dy = accel[1]
	'''rmsx = np.std(self.dx)
	rmsy = np.std(self.dy)
	inds = np.where(self.dx > 10*rmsx)
	for k in range(len(inds[0])):
		self.dx[inds[0][k],inds[1][k]] = 10*rmsx
		self.dy[inds[0][k],inds[1][k]] = 10*rmsy
	inds = np.where(self.dx < -10*rmsx)
	for k in range(len(inds[0])):
		self.dx[inds[0][k],inds[1][k]] = -10*rmsx
		self.dy[inds[0][k],inds[1][k]] = -10*rmsy
       '''
	self.MAXX = self.dx.shape[0]-2
        self.MIN = 0
        self.MAXY = self.dy.shape[1]-2
        self.pos = pos
        self.prev_pos = np.copy(pos)
        self.vel = vel
        self.acc = [self.dx[int(self.pos[0]),int(self.pos[1])], self.dy[int(self.pos[0]),int(self.pos[1])]]
    def update_accel(self,pos):
        self.acc = [self.dx[int(self.pos[0]),int(self.pos[1])], self.dy[int(self.pos[0]),int(self.pos[1])]]
    def a(self):
        try:
            return [self.dx[int(self.pos[0]),int(self.pos[1])], self.dy[int(self.pos[0]),int(self.pos[1])]]
        except:
            print 'OUT OF BOUNDS WITH POSITIONS (%i,%i)'%(self.pos[0], self.pos[1])
            return [self.dx[int(self.prev_pos[0]),int(self.prev_pos[1])], self.dy[int(self.prev_pos[0]),int(self.prev_pos[1])]]
    def v(self,pos, step):
        temp_a = self.a()
        self.vel = [self.vel[0]+temp_a[0]*step, self.vel[1]+temp_a[1]*step]
	speed_lim = 25
        if self.vel[1]>=speed_lim:
            self.vel[1] = speed_lim
        if self.vel[0]>=speed_lim:
            self.vel[0] =speed_lim
        return self.vel
    def leapfrog(self,step=0.01):
        new_pos = np.array(self.pos) + np.array(self.vel) * step + (0.5 * step**2 * np.array(self.a()))
	try:
       		new_accel = np.array([self.dx[int(new_pos[0]),int(new_pos[1])], self.dy[int(new_pos[0]),int(new_pos[1])]])
	except:
		new_accel = np.array(self.a())
        new_vel = self.vel + 0.5*(np.array(self.a()) + new_accel)*step
        self.pos = np.copy(new_pos)
        self.vel = np.copy(new_vel)

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
        mx = .125*abs(np.min(self.pot))
        #print mx
        #print val
        #return 0.01
        if val <= 0.125*mx:
            return 0.01
        elif val <= 0.25*mx:
            return 0.00875
        elif val <= 0.375*mx:
            return 0.0075
        elif val <= 0.5*mx:
            return 0.005
        elif val <= 0.625*mx:
            return 0.00325
        elif val <= 0.75*mx:
            return 0.0025
        elif val <= 0.875*mx:
            return 0.00125
        else:
            return 0.001
    def energy(self):
        return (0.5*(self.vel[0]**2 + self.vel[1]**2) + self.pot[self.pos[0], self.pos[1]])
    def update(self,step,kind='rk4'): 
        if kind == 'rk4':
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
            self.prev_pos = np.copy(self.pos)
        elif kind == 'leapfrog':
            self.prev_pos = np.copy(self.pos)
            self.leapfrog(step)
    def is_inbounds(self, edge_mode):
        self.edge_mode = edge_mode
        if edge_mode == 'stop':
            return self.pos[0] < self.MAXX and self.pos[0] > self.MIN and self.pos[1] < self.MAXY and self.pos[1] > self.MIN
        if edge_mode == 'reflect':
            if self.pos[0] >= 479:#self.MAXY:
                self.pos[0] = 478#self.MAXY-1
                self.vel[0] = self.vel[0] * -1
                print 'BOUNCE'
		print self.pos, self.vel, '1 index'
		#wait = input()
            elif self.pos[0] <= 1:
                print 'old pos,vel',self.pos, self.vel
                self.pos[0] = 5
                self.vel[0] = self.vel[0]* -1
                print 'BOUNCE'
                print 'new pos,vel',self.pos, self.vel
		print self.pos, self.vel, '1 index'
		#wait = input()
            elif self.pos[1] >= 639:#self.MAXX:
                self.pos[1] = 638#self.MAXX-1
                self.vel[1] = self.vel[1] * -1
		print 'BOUNCE'
		print self.pos, self.vel, '0 index'
		#wait = input()
            elif self.pos[1] <= 1:
                print 'old pos,vel',self.pos, self.vel
                self.pos[1] = 5
                self.vel[1] = self.vel[1] * -1
                print 'BOUNCE'
                print 'new pos,vel',self.pos, self.vel
		print self.pos, self.vel, '0 index'
		#wait = input()
		print self.pos, self.vel
            return True
        if edge_mode == 'pacman':
            if self.pos[1] >= self.MAXY:
                self.pos[1] = self.MIN+1
            elif self.pos[1] <= self.MIN:
                self.pos[1] = self.MAXY-1
            elif self.pos[0] >= self.MAXX:
                self.pos[0] = self.MIN+1 
            elif self.pos[0] <= self.MIN:
                self.pos[0] = self.MAXX-1
            return True
        



# Sample values 
# NOTES: When the particle moves out of bounds of the density field, the calculation will stop and return an error. This will eventually be remedied so the particle either stops or reflects off of the boundary. 

# Calculate velocity from initial position
def acce(pos):
    return (dx[pos[0],pos[1]], dy[pos[0],pos[1]])

#needs exception handling


def leap(pos,vel):
    ## Leapstep Definition ##
    dtime = 0.1
    acceleration = []
    velocity_arr = []
    pos_arr = []
    energy = []
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
    return (0.5*np.sum(np.square(vel)) - potential[np.rint(pos[0]).astype(int)][np.rint(pos[1]).astype(int)])
# Needs further calibration: energy conservation violation becomes a problem as step size increases


## Orbit Calculation ##
#posxtot = []
#posytot = []
#step = 0.01
#times = 500000                # Set the number of steps to be calculated
#velocity = -np.sqrt(1./(320-300))
#test_particle = Particle([320,300],[0,0])
#print test_particle.pos



def run_orbit2(test_particle):
    acceleration = []
    velocity_arr = []
    pos_arr = []
    energy = []
    posxtot = []
    posytot = []
    interp_points = np.array([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.])
    test_positionsx = []; test_positionsy = []
    num_steps = 0
    #for n in xrange(1, times):
    total_time = 0
    s = time.time()
    while total_time < 20.:
        if test_particle.is_inbounds('reflect'):
            test_particle.update(0.001)
            posxtot.append(test_particle.pos[0])
            posytot.append(test_particle.pos[1])
            acceleration.append(test_particle.acc[0])
            velocity_arr.append(test_particle.vel[0])
            pos_arr.append(test_particle.pos[0])
            total_time = (time.time() -s)
        else:
            break
    return num_steps


def run_orbit(test_particle, times = 1000,loops=0,step=0.001,edge_mode='pacman',kind='rk4'):
    #step = 0.001
    num_steps = 0
    posx = []; posy = []; fmatted = []; energy = []
    init_pos = np.copy(test_particle.pos)
    init_vel = np.copy(test_particle.vel)
    for n in xrange(1, times):
        if test_particle.is_inbounds(edge_mode):
            test_particle.update(step,kind)
            #energy.append(test_particle.energy())
            fmatted.append((test_particle.pos[0], test_particle.pos[1]))
            posx.append(test_particle.pos[0])
            posy.append(test_particle.pos[1])
            '''if np.sum(time) >= 1:
                to_sendx = np.interp(interp_points,time,posx)
                to_sendy = np.interp(interp_points,time,posy)
                for i in range(len(to_sendx)):
                    test_positionsx.append(to_sendx[i])
                    test_positionsy.append(to_sendy[i])
                time = []
                posx = []
                posy = []'''
        else:
            break

    '''fig = plt.figure()
    plt.imshow(test_particle.pot)
    #plt.scatter(posy, posx, c='purple',edgecolors='none',s=2)
    #plt.arrow(init_pos[1], init_pos[0], init_pos[1]+step*init_vel[1], init_pos[0]+step*init_vel[0], head_width=0.05, head_length=0.1, fc='k', ec='k')
    plt.title(r'Test Orbit using %s with $\Delta t = %.3f$'%(kind, step))
    plt.xlim([0,480])
    plt.ylim([0,640])
    plt.show()
    plt.savefig('test_orbit%s.png'%(kind))
    plt.close()'''

    ''' fig = plt.figure()
    distance = [np.sqrt((posx[k]-340)**2 + (posy[k] - 200)**2) for k in range(len(posy))]
    plt.plot(xrange(1, times),distance)
    plt.savefig('../timevdist.png',bbinches='tight')
    plt.close()'''
    '''from scipy.signal import argrelextrema	
    y = argrelextrema(np.array(distance),np.greater)
    u = argrelextrema(np.array(distance),np.less)
    print y
    print 'max and min of distance',(np.max(distance)+np.min(distance))/2
    delta = []
    for i in range(len(y)-1):
	delta.append(y[i+1]-y[i])
    print 'a, period'
    print '%f,%f'%((np.max(distance[:len(distance)/2])+np.min(distance[:len(distance)/2]))/2, np.gradient(y[0])[0])'''
# ------------------------
    '''fig,ax = plt.subplots(2,sharex=True)
    ax[0].scatter(np.arange(len(energy)), energy,s=5)
    ax[0].set_ylabel('Energy of Particle')
    ax[0].set_xlabel('Time')
    #ax[1].imshow(test_particle.pot,vmax=0.5)
    #ax[1].scatter(posy, posx, c='purple',edgecolors='none')
    distance = [np.sqrt((posx[k]-300)**2 + (posy[k] - 300)**2) for k in range(len(posy))]
    ax[1].plot(np.arange(len(distance)),distance)
    ax[1].set_ylabel('Radial Distance from Point Mass')
    plt.suptitle(r'Energy and Radial Position for %s with $\Delta t = %.4f$'%(kind, step))
    plt.savefig('testing_'+kind+'_%.3f.png'%(step))'''
    return fmatted

def dynamic_orbit(test_particle, edge_mode='reflect'):
    time = []
    posx = []; posy = []
    for n in range(1, times):
        if test_particle.is_inbounds(edge_mode):
            dt = test_particle.dynamic_timestep()
            posxtot.append(test_particle.pos[0])
            posytot.append(test_particle.pos[1])
            acceleration.append(dy[test_particle.pos[0], test_particle.pos[1]])
            posx.append(test_particle.pos[0])
            posy.append(test_particle.pos[1])
            time.append(dt)
            '''if np.sum(time) >= 1.:
                to_sendx = np.interp(interp_points,time,posx)
                to_sendy = np.interp(interp_points,time,posy)
                for i in range(len(to_sendx)):
                    test_positionsx.append(to_sendx[i])
                    test_positionsy.append(to_sendy[i])
                time = []
                posx = []
                posy = []'''
        else:
            break
    print time
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
'''def functional(m, a, b):
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

'''
if __name__ == '__main__':
    dx,dy, potential = testing.make_acceleration_field(300,300,1)
    '''from astropy.io import fits
    hdu = fits.open('earth_moon_pot.fits')
    potential = hdu[0].data'''
    #potential = potential/np.sum(potential)*2 #normalize with ln
    dx, dy = np.gradient(potential)
    dx = np.negative(dx)
    dy = np.negative(dy)
    MAXX = dx.shape[1]-1
    MIN = 0
    MAXY = dy.shape[0]-1

    test_particle = Particle([300,330],[1/np.sqrt(30),0],potential)
    run_orbit(test_particle, 2*500000,step=0.01,kind='rk4')
    test_particle = Particle([300,330],[1/np.sqrt(30),0],potential)
    run_orbit(test_particle, 2*500000,step=0.01,kind='leapfrog')

    '''velocity = -np.sqrt(1./(350-300))
    test_particle = Particle([300,320],[.32,0.], potential)
    start_static = time.time()
    x = run_orbit2(test_particle)
    end_static = time.time()
    test_particle = Particle([300,320],[.32,0.], potential)
    start_d = time.time()
    x = run_orbit(test_particle)
    end_d = time.time()

    print 'Static took %f seconds'%(end_static-start_static)
    print 'Dynamic took %f seconds'%(end_d-start_d)

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
    plt.plot(posytot, posxtot, linewidth=2,c='blue')
    plt.plot(posytot2, posxtot2, linewidth=1, c='green')
    #plt.plot(test_positionsx, test_positionsy, linewidth=1)
    plt.suptitle('Orbit for Potential file with 1 pt')
    plt.xlabel('X component of position')
    plt.xlim((0,dx.shape[1]))
    plt.ylim((0, dy.shape[0]))
    plt.ylabel('Y component of position')
    plt.savefig('timing_test.png',bbinches='tight')


    time = time.time() - start
    print time                # Benchmark time
    plt.show()'''

