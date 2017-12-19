from PyQt4 import QtGui as QtWidgets
import matplotlib.pyplot as plt
from subprocess import call
import time
import numpy as np

class Animate():
	def __init__(self, dem_array):
		#self.fig = plt.figure()#figsize=(10,8))
		self.fig,self.ax=plt.subplots(1)
		self.graph = plt.plot(0,0,lw=3,c='white')[0]
		self.img = self.ax.imshow(dem_array,vmax=10, vmin=-.1,cmap='jet_r')
		plt.ion()
		self.win = self.fig.canvas.manager.window
		self.toolbar = self.win.findChild(QtWidgets.QToolBar)
		self.toolbar.setVisible(False)
		self.ax.axis('tight')
		self.ax.axis('off')
		self.fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
		plt.draw()
		plt.pause(0.01)
		#call("xdotool search Figure windowmove 1500 0", shell=True)	
		#call("xdotool search Figure windowsize 1280 1024", shell=True)
	"""
	def update_fig(self, scaled_dem_array, SCALE_FACTOR):
		self.img.set_data(scaled_dem_array*SCALE_FACTOR/2)	
		self.posx,self.posy = np.loadtxt('aux/algorithm_output.csv', delimiter='"',usecols=(1,3), unpack=True)
		self.graph.set_xdata(self.posy[0:len(self.posy)/2])
		self.graph.set_ydata(self.posx[0:len(self.posy)/2])
		plt.draw()
		plt.pause(0.01)
		self.graph.set_xdata(self.posy[len(self.posy)/2:len(self.posy)])
		self.graph.set_ydata(self.posx[len(self.posy)/2:len(self.posy)])

	"""
	def update_fig(self, scaled_dem_array, posy, posx, SCALE_FACTOR):
		self.img.set_data(scaled_dem_array*SCALE_FACTOR/2)
		self.graph.set_xdata(posy)
		self.graph.set_ydata(posx)
		plt.draw()
		plt.savefig('/home/gravbox/Desktop/app/GravBox-master/app_test.jpg')
		plt.pause(0.01)		
		#plt.pause(0.01)
		#call("xdotool search Figure windowmove 1250 0", shell=True)	
	

FACTOR0 = 639./360
FACTOR1 = 480./270
PTS2SEND = 250

def read_from_file():
	posx,posy = np.loadtxt('aux/algorithm_output.csv', delimiter='"',usecols=(1,3), unpack=True)

def write_to_file(data):
	global IM
	f = open('aux/algorithm_output.csv','w')
	# ----- INTERPOLATE AND GIVE PTS2SEND VALS TO APP----------------
	mod = int(len(data)/PTS2SEND)
	for k in range(len(data)):
		if k%mod == 0.: #send 1/10 of all our data points
			f.write('\"%i\",\"%i\"\n'%(data[k][1]/FACTOR0, data[k][0]/FACTOR1))
	f.close()

def read_array(data):
	x, y = np.load(test.npy)
	print x



# Maybe test necessity of this later?
"""
	#try:
	#	win = fig.canvas.manager.window
	#except:
	#	win= fig.canvas.window()
"""
