from PyQt4 import QtGui as QtWidgets
import matplotlib.pyplot as plt
from subprocess import call
import time
import numpy as np
scaling = 8

def load_data(filename):
	x, y = np.load(filename)#'algorithm_output.npy')
	x = x[::5000] ; y = y[::5000]
	bg = np.load('display_dem.npy') * scaling
	return x, y, bg	


class Animate():
	def __init__(self, height_map):
		#self.fig = plt.figure()#figsize=(10,8))
		self.fig,self.ax=plt.subplots(1,figsize=(16,15))
		self.graph = plt.plot(0,0,lw=3,c='white', solid_capstyle='round')[0]
		self.img = self.ax.imshow(height_map*scaling,vmax=3, vmin=-.1,cmap='jet_r')
		plt.ion()
		self.win = self.fig.canvas.manager.window
		self.toolbar = self.win.findChild(QtWidgets.QToolBar)
		self.toolbar.setVisible(False)
		#self.manager = plt.get_current_fig_manager() # IF USING THESE FUNCTIONS,
		#self.manager.full_screen_toggle()			 # CLOSE WINDOW WITH CTRL-W
		self.ax.axis('tight')
		self.ax.axis('off')
		self.fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
		plt.draw()
		plt.pause(0.01)
		#call("xdotool search Figure windowmove 1500 0", shell=True)	
		#call("xdotool search Figure windowsize 1280 1024", shell=True)

	def update_fig(self, height_map):#, y, x):
		#x, y, bg = load_data('algorithm_output.npy')
		restart = True
		while restart:
			self.img.set_data(height_map*scaling)#scaled_dem_array*SCALE_FACTOR/2)
			self.ax.draw_artist(self.img)
			x, y, bg = load_data('algorithm_output.npy')
			start = time.time()
			for i in range(len(x)):	
				#                                      plot [0:i] [i-10:]
				x_pos = x[i:i+20] 
				y_pos = y[i:i+20]

				self.graph.set_xdata(y_pos)
				self.graph.set_ydata(x_pos)
				self.ax.draw_artist(self.graph)
				#plt.savefig('/home/gravbox/Desktop/app/GravBox-master/app_test.jpg')
				plt.pause(0.001)
				if i == len(x):
					break
				else:
					print i
			print 'ANIM TOOK: ', time.time() - start 
	
			
bg = load_data('algorithm_output.npy')[2]
#print len(x)
#print x, y, bg
figure = Animate(bg)
figure.update_fig(bg)













































