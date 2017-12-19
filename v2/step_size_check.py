import numpy as np
import matplotlib.pyplot as plt

lfx = np.load('/media/gravbox/G/orbit test/leapfrog_stepx.npy')
lfy = np.load('/media/gravbox/G/orbit test/leapfrog_stepy.npy')
lf_pot = np.load('/media/gravbox/G/orbit test/leapfrog_steppot.npy')


gx = np.load('/media/gravbox/G/orbit test/leapfrogG_stepx.npy')
gy = np.load('/media/gravbox/G/orbit test/leapfrogG_stepy.npy')
g_pot = np.load('/media/gravbox/G/orbit test/leapfrogG_steppot.npy')

'''times = [50,10,5,1,.5,.1,.05,.01,.005,.001]#[10,5,1,.5,.1,.05,.01,.005,.001,.0005,.0001]

for i in range(len(times)):
    t = times[i]
    fig, ax = plt.subplots(4,2)

    xvals = np.arange(len(lfx[i]))*t
    #print lf_pot[i]

    #left side is without gradient
    ax[0,0].plot(xvals, lfx[i])
    ax[1,0].plot(xvals, lfy[i])
    ax[2,0].plot(lfx[i],lfy[i])
    ax[3,0].plot(xvals,lf_pot[i]/np.max(lf_pot[i]))

    #right side is with gradient
    ax[0,1].plot(xvals, gx[i])
    ax[1,1].plot(xvals, gy[i])
    ax[2,1].plot(gx[i], gy[i])
    ax[3,1].plot(xvals,g_pot[i]/np.max(g_pot[i]))

    plt.suptitle('Step Size: %f, w/o gradient (left), w/ gradient (right)'%(t))

    plt.savefig('/media/gravbox/G/orbit test/step_check%i.png'%(i), bbinches='tight')
    plt.close()

'''
lfx = np.load('/media/gravbox/G/orbit test/long_stepx.npy')
lfy = np.load('/media/gravbox/G/orbit test/long_stepy.npy')
lf_pot = np.load('/media/gravbox/G/orbit test/long_steppot.npy')

times = [1,.5,.1,.05]
for i in range(len(times)):
    t = times[i]
    fig, ax = plt.subplots(4,1)

    xvals = np.arange(len(lfx[i]))*t
    #print lf_pot[i]

    #left side is without gradient
    ax[0].plot(xvals, lfx[i])
    ax[1].plot(xvals, lfy[i])
    ax[2].plot(lfx[i],lfy[i])
    ax[3].plot(xvals,lf_pot[i]/np.max(lf_pot[i]))

    plt.suptitle('Step Size: %f, w/o gradient'%(t))

    plt.savefig('/media/gravbox/G/orbit test/long_check%i.png'%(i), bbinches='tight')
    plt.close()