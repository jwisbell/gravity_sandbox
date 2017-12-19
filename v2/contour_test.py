from matplotlib import pyplot as plt
from matplotlib import _cntr as cntr
import numpy as np

z = np.array([[0.350087, 0.0590954, 0.002165],
              [0.144522,  0.885409, 0.378515],
              [0.027956,  0.777996, 0.602663],
              [0.138367,  0.182499, 0.460879], 
              [0.357434,  0.297271, 0.587715]])

x, y = np.mgrid[:z.shape[0], :z.shape[1]]
c = cntr.Cntr(x, y, z)

# trace a contour at z == 0.5
res = c.trace(0.5)

# result is a list of arrays of vertices and path codes
# (see docs for matplotlib.path.Path)
nseg = len(res) // 2
segments, codes = res[:nseg], res[nseg:]

fig, ax = plt.subplots(1, 1)
img = ax.imshow(z.T, origin='lower')
plt.colorbar(img)
ax.hold(True)
p = plt.Polygon(segments[0], fill=False, color='w')
ax.add_artist(p)
plt.show()