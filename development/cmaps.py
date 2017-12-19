import numpy as np
import matplotlib.cm as cm

def rainbow():
    array = np.empty((256, 4))
    abytes = np.arange(0, 1, 0.00390625)
    array[:, 0] = np.abs(2 * abytes - 0.5) * 255
    array[:, 1] = np.sin(abytes * np.pi) * 255
    array[:, 2] = np.cos(abytes * np.pi / 2) * 255
    array[:, 3] = 1
    #print array
    return array
def cubehelix(gamma=1.0, s=0.5, r=-1.5, h=1.0):
    def get_color_function(p0, p1):
        def color(x):
            xg = x ** gamma
            a = h * xg * (1 - xg) / 2
            phi = 2 * np.pi * (s / 3 + r * x)
            return xg + a * (p0 * np.cos(phi) + p1 * np.sin(phi))
        return color

    array = np.empty((256, 4))
    abytes = np.arange(0, 1, 1/256.)
    array[:, 0] = get_color_function(-0.14861, 1.78277)(abytes) * 255
    array[:, 1] = get_color_function(-0.29227, -0.90649)(abytes) * 255
    array[:, 2] = get_color_function(1.97294, 0.0)(abytes) * 255
    array[:, 3] = 50
    return array

def jet():
    jetcmap = cm.get_cmap('jet', 20)
    jet_vals = jetcmap(np.arange(20))
    np.save('jet_cmap_2.npy', jet_vals)
