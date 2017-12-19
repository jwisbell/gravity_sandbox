# Gravity Algorithm for AR Sandbox
# Fall 2016
# Jianbo Lu, Tyler Stercula, Sophie Deam

import numpy as np
#from astropy.io import fits
#from astropy.convolution import convolve, convolve_fft
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.mlab as mlab
from scipy.optimize import curve_fit

import time



class Particle():
    def __init__(self,pos,vel, accel,ggx, ggy):
       
        self.dx = accel[0]
        self.dy = accel[1]
	self.ggx = ggx
        self.ggy = ggy
	self.MAXX = self.dx.shape[1]-2
        self.MIN = 0
        self.MAXY = self.dy.shape[0]-2
        #print self.MAXX, self.MAXY, 'SHAPE'
        self.pos = pos
        self.prev_pos = np.copy(pos)
        self.vel = vel
        try:
            self.acc = [self.dx[int(self.pos[0]),int(self.pos[1])], self.dy[int(self.pos[0]),int(self.pos[1])]]
        except:
            self.acc = [0.,0.]
    def update_accel(self,pos):
        self.acc = [self.dx[int(self.pos[1]),int(self.pos[0])], self.dy[int(self.pos[1]),int(self.pos[0])]]
    def a(self):
        try:
            acc = [self.dx[int(self.pos[0]),int(self.pos[1])], self.dy[int(self.pos[0]),int(self.pos[1])]]
            self.acc = np.copy(acc)
            return np.array(acc)
        except:
            return self.acc#[self.dx[int(self.prev_pos[0]),int(self.prev_pos[1])], self.dy[int(self.prev_pos[0]),int(self.prev_pos[1])]]
    def v(self,pos, step):
        temp_a = self.a()
        self.vel = [self.vel[0]+temp_a[0]*step, self.vel[1]+temp_a[1]*step]
	speed_lim = 25
        if self.vel[1]>=speed_lim:
            self.vel[1] = speed_lim
        if self.vel[0]>=speed_lim:
            self.vel[0] =speed_lim
        return self.vel
#--------------------------------------------------------------
    def leapfrog(self,step=0.01):
        new_pos = np.array(self.pos) + np.nan_to_num(np.array(self.vel)) * step + (0.5 * step**2 * np.nan_to_num(np.array(self.a())))
	try:
       		new_accel = np.nan_to_num(np.array([self.dx[int(new_pos[0]),int(new_pos[1])], self.dy[int(new_pos[0]),int(new_pos[1])]]))
	except:
		new_accel = np.nan_to_num(np.array(self.a()))
        new_vel = self.vel + 0.5*(np.nan_to_num(np.array(self.a())) + new_accel)*step
        self.pos = np.copy(new_pos)
        self.vel = np.copy(new_vel)
    def kick(self, step=0.01):
        self.vel = self.vel+ .5 * step*np.array(self.acc)

    def leapfrog2(self, step=0.01):
        new_pos = np.array(self.pos) + np.array(self.vel)*step
        #add gradient stuff?
        #print new_pos
        new_x = self.ggx[int(self.pos[0]),int(self.pos[1])] * (self.pos[0]-int(self.pos[0])) 
        #print self.ggx[int(new_pos[0]),int(new_pos[1])] * (new_pos[0]-int(new_pos[0]))
        new_y = self.ggy[int(self.pos[0]),int(self.pos[1])] * (self.pos[1]-int(self.pos[1])) 
        #new_pos = [new_x,new_y]#[self.pos[0]+np.array(self.ggx[int(self.pos[0]),int(self.pos[1])])*(self.pos[0]-int(self.pos[0])), self.pos[1]+np.array(self.ggy[int(self.pos[0]),int(self.pos[1])])*(self.pos[1]-int(self.pos[1])]
        #print new_pos
	#i = input()
	try:
        	new_accel = np.array([self.dx[int(new_pos[0]),int(new_pos[1])], self.dy[int(new_pos[0]),int(new_pos[1])]])
	except:
		new_accel = np.array([self.dx[int(self.pos[0]),int(self.pos[1])], self.dy[int(self.pos[0]),int(self.pos[1])]])

        new_vel = self.vel + step * new_accel + np.array([new_x,new_y]) * step

        self.pos = np.copy(new_pos)
        self.vel = np.copy(new_vel)
	return new_pos
  
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
            if self.is_inbounds(self.edge_mode):
                self.prev_pos = np.copy(self.pos)
                self.leapfrog(step)
            else:
                self.pos = np.copy(self.pos)
        elif kind == 'leapfrog2':
		p1=(0,0)
		if self.is_inbounds(self.edge_mode):
            		self.prev_pos = np.copy(self.pos)
            		p1=self.leapfrog2(step)
		else:
                	self.pos[i] = [x for x in p1]
           	self.prev_pos = np.copy(self.pos)
    def is_inbounds(self, edge_mode):
        self.edge_mode = edge_mode
        if edge_mode == 'stop':
            return self.pos[0] < self.MAXX and self.pos[0] > self.MIN and self.pos[1] < self.MAXY and self.pos[1] > self.MIN
        if edge_mode == 'reflect':
            if self.pos[0] >= 479:#self.MAXY:
                self.pos[0] = 478#self.MAXY-1
                self.vel[0] = self.vel[0] * -1
                print 'BOUNCE'
		#print self.pos, self.vel, '1 index'
		#wait = input()
            elif self.pos[0] <= 1:
                print 'old pos,vel',self.pos, self.vel
                self.pos[0] = 5
                self.vel[0] = self.vel[0]* -1
                print 'BOUNCE'
                print 'new pos,vel',self.pos, self.vel
		#print self.pos, self.vel, '1 index'
		#wait = input()
            elif self.pos[1] >= 639:#self.MAXX:
                self.pos[1] = 638#self.MAXX-1
                self.vel[1] = self.vel[1] * -1
		print 'BOUNCE'
		#print self.pos, self.vel, '0 index'
		#wait = input()
            elif self.pos[1] <= 1:
                #print 'old pos,vel',self.pos, self.vel
                self.pos[1] = 5
                self.vel[1] = self.vel[1] * -1
                print 'BOUNCE'
                #print 'new pos,vel',self.pos, self.vel
		#print self.pos, self.vel, '0 index'
		#wait = input()
		#print self.pos, self.vel
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
        
def kepler_check(test_particle,potential, orbits=1,step=0.001,edge_mode='pacman',kind='leapfrog'):
	y_pos = np.linspace(215,230,10)
	x_pos = [300 for x in y_pos]
	vel = np.linspace(.5,1,5)
    	#mx = np.where(potential==np.max(potential))
    	#print mx
	periods = []; axis = []
	for y in y_pos:
		print 'Starting from ', [y,320]
		num_orbit = 0
		test_particle.pos = [y,300]
		#vel = -np.sqrt(10.*abs(240 - x))
		test_particle.vel = [0, 0]
		init_pos = np.copy(test_particle.pos)
   		init_vel = np.copy(test_particle.vel)
		num_iter = 0
		near = True
		times = [0]
		posx = []; posy = []
		start = time.time()
		while num_orbit < orbits:
			if test_particle.is_inbounds(edge_mode):
	            		test_particle.update(step,kind)
				posx.append(test_particle.pos[0])
            			posy.append(test_particle.pos[1])
                        	#print test_particle.pos
    	        		if abs(test_particle.pos[0] - init_pos[0]) < 2  and abs(test_particle.pos[1] - init_pos[1]) < 2:
					if near == False:
						num_orbit += 1
						print 'Completed an orbit'
						near = True
						times.append(num_iter - times[num_orbit-1])
				else:
					near = False	
        		else:
            			break
			num_iter += 1
		print 'orbit took', time.time()-start
		fig = plt.figure()
    		plt.imshow(test_particle.dx)
    		plt.scatter(posy, posx, c='purple',edgecolors='none',s=2)
    		#plt.arrow(init_pos[1], init_pos[0], init_pos[1]+step*init_vel[1], init_pos[0]+step*init_vel[0], head_width=0.05, head_length=0.1, fc='k', ec='k')
    		plt.title(r'Test Orbit using %s with $\Delta t = %.3f$'%(kind, step))
    		plt.xlim([0,480])
    		plt.ylim([0,640])
    		#plt.show()
    		plt.savefig('./debug/test_orbit%i.png'%(y))
    		plt.close()
		periods.append(np.mean(times))
		axis.append((np.max(posx)-np.min(posx))/2.)

	fig = plt.figure()
	plt.scatter(np.power(np.array(axis),3.), np.power(np.array(periods),2.))
	
	line = lambda x, a, b: a*x + b
	from scipy.optimize import curve_fit
	xdata = np.power(np.array(axis),3.)
	ydata = np.power(np.array(periods),2.)
	fit = curve_fit(line,xdata,ydata,p0=[(np.max(ydata)-np.min(ydata))/2.,ydata[0]])
	print fit
	plt.plot(xdata, line(xdata, *fit[0]), 'r--')
	plt.xlabel(r'$a^3$')
	plt.ylabel(r'$P^2$')
	plt.title('Kepler 3 Check')
	plt.savefig('./debug/kepler3.png')


def pot_energy(pos1, pos2, mass):
    G = 1#28029.7740431#1#000
    dist = np.sqrt((pos1[0]-pos2[0])**2+ (pos1[1] - pos2[1])**2)
    if dist <= 1.:
        return np.nan
    return -G * float(mass) / (dist**2)

def energy_check(test_particle,pos=[],masses=[], step=0.001, times = 5000000, edge_mode='reflect',kind='leapfrog2'):
    nrg = []; knrg = []; pnrg = []; rs = []
    k = 0.5*(test_particle.vel[0]**2 + test_particle.vel[1]**2)
    knrg.append(k)
    u = 0
    it = 0
    for i in range(len(pos)):
        u += pot_energy(test_particle.pos, pos[i], masses[i])
    rs.append(np.sqrt((test_particle.pos[0]- pos[0][0])**2+ (test_particle.pos[1] - pos[0][1])**2))
    nrg.append(u+k)
    pnrg.append(u)
    posx = []; posy = []
    for n in range(times-1):
        if test_particle.is_inbounds(edge_mode):
            test_particle.update(step,kind)
            k = 0.5*(test_particle.vel[0]**2 + test_particle.vel[1]**2)
            u = 0
            for i in range(len(pos)):
                u += pot_energy(test_particle.pos, pos[i], masses[i])
            nrg.append(u+k)
            knrg.append(k)
            pnrg.append(u)
            rs.append(np.sqrt((test_particle.pos[0]- pos[0][0])**2+ (test_particle.pos[1] - pos[0][1])**2))
            posx.append(test_particle.pos[0])
            posy.append(test_particle.pos[1])
            '''print test_particle.pos[0]- pos[0][0]
            if abs(test_particle.pos[0]- pos[0][0]) <= 1 and abs(test_particle.pos[1]- pos[0][1]) <= 1:
            it = i
            break'''
    #print pnrg
    print 2*np.max(knrg)/pnrg[0]
    fig,ax = plt.subplots(3)
    ax[0].plot(range(len(nrg)), nrg)
    ax[0].set_xlabel('Num Iter')
    ax[0].set_ylabel('K')
    #ax[0].set_ylim([-300,-150])
    #ax[1].plot(range(len(knrg)), knrg)
    #ax[1].set_xlabel('Num Iter')
    #ax[1].set_ylabel('K')
    #ax[1].set_ylim([-1,5])
    ax[1].plot(range(len(posx)), posx)
    #ax[1].plot(range(len(posx)), posy)
    ax[1].set_xlabel('Num Iter')
    ax[1].set_ylabel('Location (pix)')
    #ax[2].set_ylim([-10,10])
    ax[2].imshow(test_particle.dx,origin='lower', vmin=-.1, vmax=.1)
    ax[2].plot(posy, posx, c='magenta')
    ax[2].set_ylim([0,422])
    ax[2].set_xlim([0,600])
    #plt.show()
    plt.savefig('/home/gravbox/Desktop/energy_leapfrogG_orbit.png')
    print masses[0]*knrg[-1]/(1./rs[0] - 1./rs[-1])



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

