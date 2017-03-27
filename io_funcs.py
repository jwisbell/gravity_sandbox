import sys
import subprocess

def read_from_app(fname):
	#copy file using adb pull
	subprocess()
	f = open(fname)
	l = f.readline()
	data = l.split(',')
	f.close()
	to_send = [float(d) for d in data]
	return to_send

def write_to_tablet(fname):
	#use adb push
	try:
		subprocess()
		return 1
	except:
		print 'Something went wrong! Could not push file to tablet... Writing a new file there and trying again.'
		try:
			#adb shell touch fname
			#adb push our file
			subprocess()
			return 1
		except:
			'Could not create a new file. Exiting...'
			return 0