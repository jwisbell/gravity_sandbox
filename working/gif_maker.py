import imageio
import glob
import re

filenames =glob.glob('../test_images/*.png')

images = []
def keyFunc(afilename):
	nondigits = re.compile('\D')
	return int(nondigits.sub('',afilename))
filenames = sorted(filenames, key=keyFunc)

for filename in filenames:
	images.append(imageio.imread(filename))
imageio.mimsave('../OOOORRRBBBIIITTTT.gif',images)
