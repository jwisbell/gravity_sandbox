"""
Orbit Calculation for Gravbox, an Augmented Reality Gravitational Dynamics Simulation. 
Relies on Verlet ('leapfrog') integration to conserve energy throughout orbit and to accomplish relatively fast, accurate orbits.

This was developed at the University of Iowa by Jacob Isbell
    based on work in Dr. Fu's Introduction to Astrophysics class by Jacob Isbell, Sophie Deam, Jianbo Lu, and Tyler Stercula (beta version)
Version 1.0 - December 2017
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.mlab as mlab
from scipy.optimize import curve_fit
import time


"""Class to hold Particle object, holds position and velocity as well as acceleration field. 
Has functions to update particle parameters using leapfrog integration."""
class Particle():
    def __init__(self,pos,vel, accel,ggx, ggy):
        #set initial positions, velocities, and acceleration fields

        #x acceleration field
        self.dx = accel[0]
        # y acceleration field
        self.dy = accel[1]

        #2nd order accleration fields
	self.ggx = ggx
        self.ggy = ggy

        #box boundaries
	self.MAXX = self.dx.shape[1]-2
        self.MIN = 0
        self.MAXY = self.dy.shape[0]-2

        #initial position, velocity
        self.pos = pos
        self.prev_pos = np.copy(pos)
        self.vel = vel
        #make sure particle is in bounds [MINX:MAXX, MINY:MAXY]
        try:
            self.acc = [self.dx[int(self.pos[0]),int(self.pos[1])], self.dy[int(self.pos[0]),int(self.pos[1])]]
        except:
            self.acc = [0.,0.]

    def update_accel(self,pos):
        #update the accleration based on position within x,y acceleration fields
        self.acc = [self.dx[int(self.pos[0]),int(self.pos[1])], self.dy[int(self.pos[0]),int(self.pos[1])]]

    def a(self):
        #update the accleration based on position within x,y acceleration fields, if not in bounds return previous accel value
        try:
            acc = [self.dx[int(self.pos[0]),int(self.pos[1])], self.dy[int(self.pos[0]),int(self.pos[1])]]
            self.acc = np.copy(acc)
            return np.array(acc)
        except:
            return self.acc

    def v(self,pos, step):
        #update the velocity based on current acceleration and user-defined timestep
        temp_a = self.a()
        self.vel = [self.vel[0]+temp_a[0]*step, self.vel[1]+temp_a[1]*step]
        return self.vel
#--------------------------------------------------------------
#INTEGRATION METHODS
#--------------------------------------------------------------
    def leapfrog(self,step=0.01):
        # modified leapfrog based on integer steps
        new_pos = np.array(self.pos) + np.nan_to_num(np.array(self.vel)) * step + (0.5 * step**2 * np.nan_to_num(np.array(self.a())))
        try:
        	new_accel = np.nan_to_num(np.array([self.dx[int(new_pos[0]),int(new_pos[1])], self.dy[int(new_pos[0]),int(new_pos[1])]]))
        except:
            new_accel = np.nan_to_num(np.array(self.a()))
        new_vel = self.vel + 0.5*(np.nan_to_num(np.array(self.a())) + new_accel)*step
        self.pos = np.copy(new_pos)
        self.vel = np.copy(new_vel)
  
    def kick(self, step=0.01):
        #kick the particle for verlet integration offset by half-step  
        self.vel = self.vel+ .5 * step*np.array(self.acc)

    def leapfrog2(self, step=0.01):
        #'true' leapfrog based on offset steps
        #can be modified to use 2nd order acceleration
        new_pos = np.array(self.pos) + np.array(self.vel)*step
        #new_x = self.ggx[int(self.pos[0]),int(self.pos[1])] * (self.pos[0]-int(self.pos[0])) 
        #new_y = self.ggy[int(self.pos[0]),int(self.pos[1])] * (self.pos[1]-int(self.pos[1])) 
        try:
        	new_accel = np.array([self.dx[int(new_pos[0]),int(new_pos[1])], self.dy[int(new_pos[0]),int(new_pos[1])]])
        except:
            new_accel = np.array([self.dx[int(self.pos[0]),int(self.pos[1])], self.dy[int(self.pos[0]),int(self.pos[1])]])

        new_vel = self.vel + step * new_accel #+ np.array([new_x,new_y]) * step

        self.pos = np.copy(new_pos)
        self.vel = np.copy(new_vel)
	    return new_pos
  

    def energy(self):
        #return K + U energy
        return (0.5*(self.vel[0]**2 + self.vel[1]**2) + self.pot[self.pos[0], self.pos[1]]) 


    def update(self,step,kind='leapfrog2'): 
        #update the particle position using the selected integration method
        if kind == 'leapfrog':
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
        #check to see if the particle is in the boundaries, to prevent 'index out of bounds' errors
        #edge modes are 'reflect' which bounces off sides, returning True
        #               'pacman' which wraps the particle around to the other side, returning True
        #               'stop'    returns False if out of bounds, which ends simulation
        self.edge_mode = edge_mode

        if edge_mode == 'stop':
            return self.pos[0] < self.MAXX and self.pos[0] > self.MIN and self.pos[1] < self.MAXY and self.pos[1] > self.MIN

        if edge_mode == 'reflect':
            if self.pos[0] > self.MAXY: #bottom
                self.pos[0] = self.MAXY
                self.vel[0] = self.vel[0] * -1
            elif self.pos[0] <= 0: #top
                self.pos[0] = 1
                self.vel[0] = self.vel[0]* -1
            elif self.pos[1] > self.MAXX: #right
                self.pos[1] = self.MAXX
                self.vel[1] = self.vel[1] * -1
            elif self.pos[1] <= 0:#left
                self.pos[1] = 1
                self.vel[1] = self.vel[1] * -1
            return True

        if edge_mode == 'pacman':
            if self.pos[0] >= self.MAXY:
                self.pos[0] = self.MIN+1
            elif self.pos[0] <= self.MIN:
                self.pos[0] = self.MAXY-1
            elif self.pos[1] >= self.MAXX:
                self.pos[1] = self.MIN+1 
            elif self.pos[1] <= self.MIN:
                self.pos[1] = self.MAXX-1
            return True
      
#see if Kepler's 3rd Law holds  
#for debugging
def kepler_check(test_particle,potential, orbits=1,step=0.001,edge_mode='pacman',kind='leapfrog'):
	y_pos = np.linspace(230,250,10)
	x_pos = [300 for x in y_pos]
	vel = np.linspace(.5,1,5)
	periods = []; axis = []
	for y in y_pos:
		print 'Starting from ', [y,290]
		num_orbit = 0
		test_particle.pos = [y,290]
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
	plt.savefig('./debug/kepler3_gauss_leapfrog2.png')

#debugging code
#check to find optimal step size
def step_check(test_particle,potential,edge_mode='pacman',kind='leapfrog'):
    steps = [.0001, .0005, .001, .005, .01, .05, .1]#, .05, .1]
    steps = [50,10,5,1,.5,.1,.05,.01,.005,.001]#,.0005,.0001]
    #steps = [.01,.005,.001, .0005, .0001]
    periods = []; axis = []
    total_posx = []; total_posy = []; total_pot = []
    time = 5000
    max_loc = np.where(potential == np.max(potential))
    x0 = max_loc[0][0]; y0 = max_loc[1][0]
    print x0, y0
    for s in steps:
        print 'Starting from ', [230,290]
        num_steps = time/s
        i = 0
        test_particle.pos = [250,290]
        test_particle.vel = [0, 0.]
        test_particle.kick(s/2.)
        init_pos = np.copy(test_particle.pos)
        init_vel = np.copy(test_particle.vel)
        num_iter = 0
        near = True
        times = [0]
        posx = []; posy = []
        while i < num_steps:
            if test_particle.is_inbounds(edge_mode):
                    test_particle.update(s,'leapfrog2')
                    posx.append(test_particle.pos[0])
                    posy.append(test_particle.pos[1])
            else:
                break
            i+=1
        print 'Completed %i iter with step=%f'%(num_steps, s)
        '''fig = plt.figure()
        plt.imshow(test_particle.dx)
        plt.plot(posy, posx,c='w')
        plt.show()
        plt.close()
        return'''
        total_posx.append(np.array(posx))
        total_posy.append(np.array(posy))
        total_pot.append(np.max(potential)/ np.sqrt( np.power(np.array(posx)-x0,2.) + np.power(np.array(posy)-y0,2.))) #GM/r
    np.save('/media/gravbox/G/orbit test/leapfrog_stepx.npy', np.array(total_posx))
    np.save('/media/gravbox/G/orbit test/leapfrog_stepy.npy', np.array(total_posy))
    np.save('/media/gravbox/G/orbit test/leapfrog_steppot.npy', np.array(total_pot))

    #basisx = total_posx[0]; basisy = total_posy[0]

    
#calculate the potential energy
def pot_energy(pos1, pos2, mass):
    G = 1#28029.7740431#1#000
    dist = np.sqrt((pos1[0]-pos2[0])**2+ (pos1[1] - pos2[1])**2)
    if dist <= 1.:
        return np.nan
    return -G * float(mass) / (dist**2)

#debugging code to see if energy is conserved
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
    #plt.show()
    plt.savefig('/home/gravbox/Desktop/energy_leapfrog.png')
    print masses[0]*knrg[-1]/(1./rs[0] - 1./rs[-1])


