import sys
import numpy as np
from subprocess import call
import time

one = True
"""
From whichever UI is in use, get the x0,y0,x1,y1 positions and scale for calculation.
"""
def read_from_app(vel_scaling=.1,x_factor=600, y_factor=424, mode='tablet'):
	if mode =='tablet':
		call('adb pull /sdcard/kivy/GravBox/algorithm_input.txt /home/gravbox/Desktop/gravbox/gravity_sandbox/v2/algorithm_input.txt',shell=True)
	x_i, y_i, x_f, y_f = np.loadtxt('./algorithm_input.txt', unpack=True,dtype='float')
	if mode == 'tablet':
		x_i /= 1600; x_f /= 1600
		y_i = 1 - y_i/1200; y_f = 1- y_f/1200
	pos = np.array([y_i * y_factor, x_i * x_factor])	
	d_x = (x_f - x_i)*x_factor
	d_y = (y_f - y_i)*y_factor
	ang = np.arctan2(d_y,d_x)
	mag = np.sqrt(d_x**2 + d_y**2) * .1
	vel = np.array([np.sin(ang)*mag, np.cos(ang)*mag])
	
	print pos, vel, 'pos and vel'
	c = 50
	if vel[0] > c:
		vel[0] = c	
	if vel[0] < -c:
		vel[0] = -c
	if vel[1] > c:
		vel[1] = c
	if vel[1] < -c:
		vel[1] = -c
	return pos, vel


def plot_orbit(data, potential_field):
	import matplotlib.pyplot as plt
	fig = plt.figure()
	plt.imshow(potential_field)
	xdata = [k[1] for k in data]
	ydata = [k[0] for k in data]
	plt.plot(xdata, ydata, c='r')
	plt.show()
	plt.close()

"""Save the topography file on the tablet. Doing two copies so that they can read without delay? """
def send_topo():
	global one
	if one:
		call('adb shell rm /sdcard/kivy/GravBox/color_field_%i.jpg'%(1), shell=True)
		call('adb push /home/gravbox/Desktop/gravbox/gravity_sandbox/v2/color_field.jpg /sdcard/kivy/GravBox/color_field_%i.jpg'%(1), shell=True)
		one= False
	else:
		one = True
		call('adb shell rm /sdcard/kivy/GravBox/color_field_%i.jpg'%(0), shell=True)
		call('adb push /home/gravbox/Desktop/gravbox/gravity_sandbox/v2/color_field.jpg /sdcard/kivy/GravBox/color_field_%i.jpg'%(0), shell=True)


def write_to_tablet():
	out_s = time.time()
	call('adb push algorithm_output.npy /sdcard/kivy/GravBox/algorithm_output.npy', shell=True)
	print 'sending output file took: ',time.time()-out_s


"""
	global IM
	f = open('aux/algorithm_output.csv','w')
	# ----- INTERPOLATE AND GIVE PTS2SEND VALS TO APP----------------
	mod = int(len(data)/PTS2SEND)
	for k in range(len(data)):
		if k%mod == 0.: #send 1/10 of all our data points
			f.write('\"%i\",\"%i\"\n'%(data[k][1]/FACTOR0, data[k][0]/FACTOR1))
	f.close()
	#use adb push
	try:
		out_s = time.time()
		call('adb shell rm /storage/emulated/0/sandbox/algorithm_output.csv',shell=True)
		call('adb push aux/algorithm_output.csv /storage/emulated/0/sandbox/algorithm_output_0.csv', shell=True)
		call('adb push aux/algorithm_output.csv /storage/emulated/0/sandbox/algorithm_output_1.csv', shell=True)
		print 'sending output file took: ',time.time()-out_s
		#pot_s = time.time()
		#call('adb shell rm /storage/emulated/0/sandbox/potential_field.png',shell=True)
		#call('adb push /home/gravity/Desktop/grav_sandbox/potential_field.png /storage/emulated/0/sandbox/potential_field.png', shell=True)
		#print 'sending pot map file took: ',time.time()-pot_s
		cont_s = time.time()
		idle_send()
		print 'sending contour file took: ',time.time()-cont_s
		return 1
	except:
		print 'Something went wrong! Could not push file to tablet... Writing a new file there and trying again.'
		try:
			# generate empty test file, then retry pushing file
			call('adb shell touch /home/gravity/Desktop/grav_sandbox/algorithm_output.txt', shell=True)
			call('adb push /home/gravity/Desktop/grav_sandbox/algorithm_output.txt /storage/emulated/0/sandbox/algorithm_output.csv', shell=True)
			return 1
		except:
			'Could not create a new file. Exiting...'
			return 0
"""
