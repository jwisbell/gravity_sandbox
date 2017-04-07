import sys
import numpy as np
from subprocess import call

FACTORX = 360./639
FACTORY = 270./480.

def read_from_app():
	#copy file using adb pull
	call('adb pull /storage/emulated/0/sandbox/algorithm_input.txt /home/gravity/Desktop/grav_sandbox/algorithm_input.txt', shell=True)
	f = open('/home/gravity/Desktop/grav_sandbox/algorithm_input.txt','r')
	data = f.readline().strip('(').replace(')', '').split()
	for j in range(len(data)):
		data[j] = float(data[j])
	pos = np.array([data[0]/FACTORX,data[1]/FACTORY])
	vel = np.array([data[2]*10,data[3]*10])
	obj = data[4]
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


def write_to_tablet(data):
	f = open('/home/gravity/Desktop/grav_sandbox/algorithm_output.csv','w')
	for k in range(len(data)):
		f.write('\"%i\",\"%i\"\n'%(data[k][1]*FACTORX, data[k][0]*FACTORY))
	f.close()
	#use adb push
	try:
		call('adb shell rm /storage/emulated/0/sandbox/algorithm_output.csv',shell=True)
		call('adb push /home/gravity/Desktop/grav_sandbox/algorithm_output.csv /storage/emulated/0/sandbox/algorithm_output.csv', shell=True)
		call('adb shell rm /storage/emulated/0/sandbox/potential_field.jpg',shell=True)
		call('adb push /home/gravity/Desktop/grav_sandbox/potential_field.jpg /storage/emulated/0/sandbox/potential_field.jpg', shell=True)
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
