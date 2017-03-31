import sys
import numpy as np
from subprocess import call



def read_from_app():
	#copy file using adb pull
	call('adb pull /storage/emulated/0/sandbox/algorithm_input.txt /home/gravity/Desktop/grav_sandbox/algorithm_input.txt', shell=True)
	f = open('/home/gravity/Desktop/grav_sandbox/algorithm_input.txt','r')
   	#f.seek(0)
	data = f.readline().strip('(').replace(')', '').split()
	for j in range(len(data)):
		data[j] = float(data[j])
	pos = np.array([data[0],data[1]])
	vel = np.array([data[2],data[3]])
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
		f.write('%i, %i \n'%(data[k][0], data[k][1]))
	f.close()
	#use adb push
	try:
		call('adb push /home/gravity/Desktop/grav_sandbox/algorithm_output.csv /storage/emulated/0/sandbox/algorithm_output.csv', shell=True)
		return 1
	except:
		print 'Something went wrong! Could not push file to tablet... Writing a new file there and trying again.'
		try:
			# generate empty test file, then retry pushing file
			call('adb shell touch /home/gravity/Desktop/grav_sandbox/algorithm_output.txt', shell=True)
			call('adb push /home/gravity/Desktop/grav_sandbox/algorithm_output.txt /storage/emulated/0/sandbox/algorithm_output.txt', shell=True)
			return 1
		except:
			'Could not create a new file. Exiting...'
			return 0


#write_to_tablet()
