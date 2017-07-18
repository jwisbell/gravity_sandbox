from PyQt4 import QtGui as QtWidgets
import matplotlib.pyplot as plt
from subprocess import call


class Animate():
	def __init__(self, dem_array):
		self.fig = plt.figure(figsize=(24,24))
		self.graph = plt.plot(0,0,lw=3,c='white')[0]
		self.img = plt.imshow(dem_array,vmax=.1, vmin=-.1)
		plt.ion()
		plt.axis('off')	
		self.fig.tight_layout()
		self.win = self.fig.canvas.manager.window
		self.toolbar = self.win.findChild(QtWidgets.QToolBar)
		self.toolbar.setVisible(False)
		plt.draw()
		plt.pause(0.01)
		call("xdotool search Figure windowmove 1000 0", shell=True)	
	def update_fig(self, scaled_dem_array, posy, posx, SCALE_FACTOR):
		self.img.set_data(scaled_dem_array*SCALE_FACTOR/2)
		self.graph.set_xdata(posy)
		self.graph.set_ydata(posx)
		plt.draw()
		plt.pause(.01)
		#call("xdotool search Figure windowmove 1250 0", shell=True)	



# Maybe test this later?
"""
	#try:
	#	win = fig.canvas.manager.window
	#except:
	#	win= fig.canvas.window()
"""
