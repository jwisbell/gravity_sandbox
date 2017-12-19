import sys
import time
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
import subprocess
start = time.time()
end = time.time()
scaling = 16
YWIDTH = 600#480.
XWIDTH = 422#600#640.
y0 = 20
x0 = 35

def load_data():
    while True:
        try:
            x, y = np.load('algorithm_output.npy')
            # = 640-y-40
            #x = x
            x_scaled = x * YWIDTH #+ x0
            y_scaled = 600- (y * XWIDTH)
            num_pts = 1000
            step = int(len(x)/num_pts)
            x = x_scaled[::10] ; y = y_scaled[::10]
            bg = np.load('display_dem.npy') / scaling
            #bad = np.where(bg>2000)
            #bg[bad]=np.nan
            #bg = np.nan_to_num(bg)
            #bg = np.negative(bg)
            #bg = np.roll(bg,-28,axis=1) # x axis
            #bg = np.roll(bg,10,axis=0)
            #bg = bg[10:-10,:]
            #subprocess.call('rm algorithm_output.npy',shell=True)
            return x, y, bg	
        except:
            continue

x, y, bg = load_data()


cmap_viridis = np.array([(68,1,84,255), (72,21,103,255), (72,38,119,255),(69,55,124,255),(64,71,136,255),(57,86,140,255), (51,99,141,255),(45,112,142,255),(40,125,142,255),(35,138,141,255),(31,150,139,255),(32,163,135,255),(60,187,117,255),(85,198,103,255),(115,208,85,255),(149,216,64,255),(184,272,41,255),(220,227,25,255),(253,231,37,255),(0,0,0,255)])
cmap_jet = np.load('jet_cmap.npy')

#cmap_jet = np.array([(0,0,204,255),(0,0,255,255),(0,255,255,255),(0,255,0,255),(255,255,0,0),(255,128,0,255),(255,0,0,255),(153,0,0,255)])



class App(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)

        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QVBoxLayout())
        self.mainbox.setCursor(QtCore.Qt.CrossCursor)
        self.mainbox.setMouseTracking(True)

        self.canvas = pg.GraphicsLayoutWidget()
        self.canvas.setMouseTracking(True)
        self.mainbox.layout().addWidget(self.canvas)
        self.pressed=False		
        #self.label = QtGui.QLabel()
        #self.mainbox.layout().addWidget(self.label)

        self.view = self.canvas.addViewBox()
        self.view.setAspectLocked(False)
        self.view.setRange(xRange=[0,600],yRange=[0,422],padding=-1)
        self.view.setMouseEnabled(x=False,y=False)
        #self.mainbox.setContentsMargins(-150,10,-0,-10)#(-40,10,-130,-10)
        self.mainbox.setContentsMargins(-80,0,-50,-80)#-100,-90,-70,-40)
        #self.mainbox.setContentsMargins(-0,0,0,0)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        
        self.setGeometry(1280,0, 1216, 972.8)
        #self.setGeometry(1280,0, 1280, 1024)
        #self.setGeometry(0,0, 640, 512)#,1280,1024) #JUST IN CASE, CTRL-ALT-ESC
        #self.mainbox.selectAll()
        self.canvas.mouseMoveEvent = self.mainbox.mouseMoveEvent
        self.mainbox.setFocus()


        #self.view.setRange(QtCore.QRectF(0,0, 1280, 480))
	

        self.canvas.nextRow()


        #r = cmap_viridis
        r = cmap_jet
        global bg
        #print np.max(bg), np.min(bg)
        pos = np.linspace(1.1,-.4,len(r)-1)#[0., 1., 0.5, 0.25, 0.75])
        pos= np.append(pos, np.array([np.nan]))
        color = np.array([(0,0,255,255),(0,255,0,255),(255,128,0,255),(255,0,0,255)])
        #color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, r)
        lut = cmap.getLookupTable(.5,1.0,256)#(-.009,1.05, 256)

        
        #### Set Data  #####################
        self.y = x#[0:20]
        self.x = y#[0:20]

        #  image plot
        self.data = np.rot90(bg)
        self.img = pg.ImageItem(border=None)
        self.img.setZValue(-100)
        self.img.setLookupTable(lut)
        self.img.setImage(self.data)
		
        self.pdi = pg.PlotDataItem(self.x, self.y, pen={'color':'w','width':3})
        self.pdi = pg.PlotDataItem(self.x, self.y, pen={'color':'w','width':3})
        self.view.addItem(self.img)
        self.view.addItem(self.pdi)

        self.counter = 0
        self.fps = 0. 
        self.lastupdate = time.time()
        
        #### Start  #####################
        self.view.mouseClickEvent = self.new_MouseClickEvent
        #self.view.mouseMoveEvent = self.new_mouseMoveEvent
        self.setMouseTracking(True)
        self._update()


    def paintEvent(self, event):
        self.painter = QtGui.QPainter()
        self.painter.begin(self)


    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def mouseMoveEvent(self, e):
        #print 'here'
        if self.pressed:
            pos= e.pos()
            self.current_pos = [pos.x(),pos.y()]

    def setMouseTracking(self, flag):
        def recursive_set(parent):
            for child in parent.findChildren(QtCore.QObject):
                try:
                    child.setMouseTracking(flag)
                except:
                    pass
                recursive_set(child)
        QtGui.QWidget.setMouseTracking(self, flag)
        recursive_set(self)
            


    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
                #make points transparent
                if self.pressed:
                    pos= QMouseEvent.pos()
                    self.end_pos = [pos.x(),pos.y()]
                    print '!!!! Final pos', self.end_pos
                    #save data to file
                    '''f = open('algorithm_input.txt','w')
                    f.write('%f,%f,%f,%f'%((self.start_pos[0] - y0)/YWIDTH,(self.start_pos[1] - x0)/XWIDTH,(self.end_pos[0] - y0)/YWIDTH,(self.end_pos[1] - x0)/XWIDTH))
                    f.close()'''
                    self.mainbox.setCursor(QtCore.Qt.WaitCursor)
                    time.sleep(.5)
                    self.counter = 0
                    global x
                    global y
                    global end
                    global start
                    x,y,bg = load_data() #/ scaling
                    #keep = bg[:28,:]
                    #self.x = x - 28
                    #self.y = y + 20
                    self.data = np.rot90(bg)
                    self.img.setImage(self.data)
                    self.mainbox.setCursor(QtCore.Qt.CrossCursor)
                    self.pressed=False
                    self.pdi.setPen(color='w',width=3)
                else:
                    pos = QMouseEvent.pos()
                    self.pressed = True
                    self.start_pos = [pos.x(),pos.y()]
                    self.current_pos = [pos.x(),pos.y()]
                    print '!!!! Starting Pos', self.start_pos
                    self.pdi.setPen(color='r',width=3)

                     
    def new_MouseClickEvent(self, e):
        if e.button() == QtCore.Qt.RightButton:
            e.accept()
            #print 'final pos', QMouseEvent.pos()



    """
    def mousePressEvent(self, e):
        self.pressed = True
        self.x = e.x()
        self.y = e.y()
        mousePressEvent(self, e)
    
    
    def mousePressEvent(self, e):
        self.onMousePressed.emit()
        print "DOWN"
    def mouseReleaseEvent(self, event):
      self.onMouseReleased.emit()
      print "UP"
    """

    def _update(self):

          #bad = bg.where()
          self.x = x #- 28
          self.y = y #+ 20
          self.x = self.x[self.counter:self.counter + 50]
          self.y = self.y[self.counter:self.counter + 50]
          #print self.x
          #self.y = [300,300, .25*600, .25*600, .75*600, .75*600]#x#[0:20]
          #self.x = [0,.5*XWIDTH, .25*XWIDTH, 0.25*XWIDTH, 0.75*XWIDTH, 0.75*XWIDTH]
          self.pdi.setData(self.y, self.x)

          if self.pressed:
            self.pdi.setData([600-self.start_pos[0],600-self.current_pos[0]],[self.start_pos[1],self.current_pos[1]])

          now = time.time()
          dt = (now-self.lastupdate)
          if dt <= 0:
            dt = 0.000000000001
          fps2 = 1.0 / dt
          self.lastupdate = now
          self.fps = self.fps * 0.9 + fps2 * 0.1
          tx = 'Mean Frame Rate:  {fps:.3f} FPS'.format(fps=self.fps )
          #self.label.setText(tx)
          QtCore.QTimer.singleShot(5, self._update)
          self.counter += 1
          #print self.counter
          if self.counter == len(x):
            end = time.time()
            self.counter = 0
            global x
            global y
            global end
            global start
            x,y,bg = load_data() #/ scaling
            #keep = bg[:28,:]
            #self.x = x - 28
            #self.y = y + 20
            self.data = np.rot90(bg,1)
            self.img.setImage(self.data)
            self.c = pg.IsocurveItem()#level=v, pen=(i, len(levels)*1.5))
            self.c.setParentItem(self.img)            
            exporter = pg.exporters.ImageExporter(self.img)
            exporter.export('color_field.jpg')


            print 'It took %f to read %i pts'%(start-end, len(x))
            start = time.time()
          #self.painter.drawLine(10, 150, 50, 150)


           


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    thisapp = App()
    thisapp.show()
    sys.exit(app.exec_())

