import sys
import time
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg

scaling = 8
def load_data():
	x, y = np.load('algorithm_output.npy')
	x = x[::50] ; y = y[::50]
	bg = np.load('display_dem.npy') * scaling
	return x, y, bg	

x, y, bg = load_data()
cmap_vals = np.load('viridis.npy')
cmap_vals *= 2
cmap_vals[:, 3] = 50
print cmap_vals

def rainbow():
    array = np.empty((256, 4))
    abytes = np.arange(0, 1, 0.00390625)
    array[:, 0] = np.abs(2 * abytes - 0.5) * 255
    array[:, 1] = np.sin(abytes * np.pi) * 255
    array[:, 2] = np.cos(abytes * np.pi / 2) * 255
    array[:, 3] = 1
    print array
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

class App(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)

        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QVBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget()
        self.mainbox.layout().addWidget(self.canvas)
		
        #self.label = QtGui.QLabel()
        #self.mainbox.layout().addWidget(self.label)

        self.view = self.canvas.addViewBox()
        self.view.setAspectLocked(False)
        self.view.setRange(xRange=[0,640],yRange=[0,480],padding=-1)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        self.setGeometry(1280,0,1280,1024) #JUST IN CASE, CTRL-ALT-ESC


        #self.view.setRange(QtCore.QRectF(0,0, 1280, 480))
	

        self.canvas.nextRow()


		#bipolar colormap
        r = cmap_vals
        global bg
        bg = np.negative(bg)
        print np.max(bg), np.min(bg)
        bg = bg / np.max(np.absolute(bg))
        pos = np.linspace(0,1,4)#[0., 1., 0.5, 0.25, 0.75])
        color = np.array([(0,0,255,255),(0,255,0,255),(255,128,0,255),(255,0,0,255)])
        #color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)

        
        #### Set Data  #####################
        self.x = x[0:20]
        self.y = y[0:20]

        #  image plot
        self.data = np.rot90(bg,3)
        self.img = pg.ImageItem(border=None)
        self.img.setZValue(-100)
        self.img.setImage(self.data)
        self.img.setLookupTable(lut)
		
        self.pdi = pg.PlotDataItem(self.x, self.y, pen='w')
        self.view.addItem(self.img)
        self.view.addItem(self.pdi)

        self.counter = 0
        self.fps = 0. 
        self.lastupdate = time.time()
        
        #### Start  #####################
        self._update()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def _update(self):
        bg = np.load('display_dem.npy')
        bg = np.roll(bg,-28,axis=1)#bg[10:, 20:]
        bg = np.roll(bg,8,axis=0)
        self.data = np.rot90(bg)
        self.x = x[self.counter:self.counter + 20]
        self.y = y[self.counter:self.counter + 20]
        #self.ydata = np.sin(self.x/3.+ self.counter/9.)

        self.img.setImage(self.data)
        #self.img.setLookupTable(self.lut)
        #self.img.setLevels([0,1])
        self.pdi.setData(self.y, self.x)


        now = time.time()
        dt = (now-self.lastupdate)
        if dt <= 0:
            dt = 0.000000000001
        fps2 = 1.0 / dt
        self.lastupdate = now
        self.fps = self.fps * 0.9 + fps2 * 0.1
        tx = 'Mean Frame Rate:  {fps:.3f} FPS'.format(fps=self.fps )
        #self.label.setText(tx)
        QtCore.QTimer.singleShot(1, self._update)
        self.counter += 1


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    thisapp = App()
    thisapp.show()
    sys.exit(app.exec_())

