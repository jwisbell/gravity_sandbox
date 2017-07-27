import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation

x, y = np.load('algorithm_output.npy')
bg = np.load('display_dem.npy')
scaling = 8

fig,ax = plt.subplots(1)
img = ax.imshow(bg*scaling, vmax=.1, vmin=-.1)
ax.axis('tight')
ax.axis('off')
line, = ax.plot([],[],c='white',lw=2)


def init():
	line.set_data([],[])
	return line, 

def animate(i):
	global x, y
	for i in range(len(x)):
		line.set_data(x[i],y[i])
		print x[i]
		img.set_array(bg*scaling)
		return line, img

anim = animation.FuncAnimation(fig, animate, init_func=init, interval=50, blit=True)

plt.show()

