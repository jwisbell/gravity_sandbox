import sys
import numpy as np
from subprocess import call
import time

FACTOR0 = 639./360
FACTOR1 = 480./270
VEL_FACTOR = 1.1
PTS2SEND = 250



def read_from_app(vel_scaling=1.):
	#copy file using adb pull
	call('adb pull /storage/emulated/0/sandbox/algorithm_input.txt /home/gravity/Desktop/grav_sandbox/algorithm_input.txt', shell=True)
	f = open('/home/gravity/Desktop/grav_sandbox/algorithm_input.txt','r')
	data = f.readline().strip('(').replace(')', '').split()
	for j in range(len(data)):
		data[j] = float(data[j])
	pos = np.array([data[1]*FACTOR0,data[0]*FACTOR1])

	deltax = data[4]
	deltay = data[5]
	angle = np.arctan2(deltay,deltax) #+ np.pi/2

	mag = data[3]*VEL_FACTOR*vel_scaling
	vel = np.array([np.cos(angle)*mag, np.sin(angle)*mag])
	#obj = data[4]
	f.close()
	print pos, vel#, obj
	return pos, vel#, obj


	#to_send = [float(d) for d in data]
	#return to_send

#read_from_app()

def plot_orbit(data, potential_field):
	import matplotlib.pyplot as plt
	fig = plt.figure()
	plt.imshow(potential_field)
	xdata = [k[1] for k in data]
	ydata = [k[0] for k in data]
	plt.plot(xdata, ydata, c='r')
	plt.show()
	plt.close()

def send_screenshot():
	call('adb shell rm /storage/emulated/0/sandbox/color_field.jpg', shell=True)
	call('adb push /home/gravity/Desktop/color_field.jpg /storage/emulated/0/sandbox/color_field.jpg', shell=True)
	return
def send_pot_field():
	call('adb shell rm /storage/emulated/0/sandbox/potential_field.png',shell=True)
	call('adb push /home/gravity/Desktop/grav_sandbox/potential_field.png /storage/emulated/0/sandbox/potential_field.png', shell=True)
	return
def save_screenshot():
	call("xwd -name SARndbox | convert xwd:- '/home/gravity/Desktop/color_field.jpg' ;", shell=True)
	return	

def idle_send():
	call('adb shell rm /storage/emulated/0/sandbox/color_field_%i.jpg'%(1), shell=True)
	call('adb shell rm /storage/emulated/0/sandbox/color_field_%i.jpg'%(0), shell=True)
	call('convert /home/gravity/Desktop/color_field.jpg -rotate 180 /home/gravity/Desktop/color_field.jpg',shell=True)
	call('adb push /home/gravity/Desktop/color_field.jpg /storage/emulated/0/sandbox/color_field_%i.jpg'%(0), shell=True)
	call('adb push /home/gravity/Desktop/color_field.jpg /storage/emulated/0/sandbox/color_field_%i.jpg'%(1), shell=True)


def write_to_tablet(data):
	global IM
	f = open('/home/gravity/Desktop/grav_sandbox/algorithm_output.csv','w')
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
		call('adb push /home/gravity/Desktop/grav_sandbox/algorithm_output.csv /storage/emulated/0/sandbox/algorithm_output_0.csv', shell=True)
		call('adb push /home/gravity/Desktop/grav_sandbox/algorithm_output.csv /storage/emulated/0/sandbox/algorithm_output_1.csv', shell=True)
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


#write_to_tablet()
