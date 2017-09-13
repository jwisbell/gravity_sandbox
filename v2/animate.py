import sys
import time
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
import subprocess
import io_funcs
from skimage import measure


start = time.time()
end = time.time()
scaling = 16
YWIDTH = 600.#480.
XWIDTH = 422.#600#640.
y0 = 10#/2.
x0 = 40#2.
XWINDOW = 640.*2
YWINDOW = 512.*2
xscale = 600.*2.05; yscale = 495.*2.05;

def load_data():
    """Load the output from the orbit calculation. If there is currently no file, wait indefinitely. """ 
    i = 0
    while i<1e6:
        try:
            x, y = np.load('algorithm_output.npy')
            x_scaled = x * YWIDTH - 7
            y_scaled = 600- (y * XWIDTH) - 12
            x = x_scaled ; y = y_scaled
            bg = np.load('display_dem.npy') / scaling
            bg[0,0] = -40
            bg[0,1] = 1
            '''contour1 = measure.find_contours(bg,np.median(bg))
            contour2 = measure.find_contours(bg,.5*np.median(bg))
            contour3 = measure.find_contours(bg,2*np.median(bg))
            contour4 = measure.find_contours(bg,-1*np.median(bg))'''
            #contour5 = measure.find_contours(bg, -.25*np.median(bg))
            #subprocess.call('rm algorithm_output.npy',shell=True)
            return x, y, bg, np.load('contours.npy')
        except:
            i += 1

x, y, bg,contours = load_data()


#cmap_viridis = np.array([(68,1,84,255), (72,21,103,255), (72,38,119,255),(69,55,124,255),(64,71,136,255),(57,86,140,255), (51,99,141,255),(45,112,142,255),(40,125,142,255),(35,138,141,255),(31,150,139,255),(32,163,135,255),(60,187,117,255),(85,198,103,255),(115,208,85,255),(149,216,64,255),(184,272,41,255),(220,227,25,255),(253,231,37,255),(0,0,0,255)])
#np.save('./aux/viridis_cmap.npy',cmap_viridis)
cmap_jet = np.load('./aux/jet_cmap.npy')
cmap_viridis = np.load('./aux/viridis_cmap.npy')

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
        self.pressed=False; self.moved=False		
        
        self.view = self.canvas.addViewBox()
        self.view.setAspectLocked(False)
        self.view.setRange(xRange=[0,600],yRange=[0,422],padding=-1)
        self.view.setMouseEnabled(x=False,y=False)

        """
        Adjust margins to better align the Kinect data with the projected image.
        Order is left, top, right, bottom. 
        """ 
        self.leftmargin = -60 ; self.topmargin = 0; self.rightmargin =70; self.bottommargin = -10
        self.mainbox.setContentsMargins(self.leftmargin, self.topmargin, self.rightmargin, self.bottommargin)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        
        self.setGeometry(0,0, XWINDOW, YWINDOW) # JUST IN CASE, CTRL-ALT-ESC
        self.canvas.mouseMoveEvent = self.mainbox.mouseMoveEvent
        self.mainbox.setFocus()


        #self.view.setRange(QtCore.QRectF(0,0, 1280, 480))
	
        self.canvas.nextRow()


        #r = cmap_viridis
        r = cmap_jet
        pos = np.linspace(1.1,-.4,len(r)-1)#[0., 1., 0.5, 0.25, 0.75])
        pos= np.append(pos, np.array([np.nan]))
        cmap = pg.ColorMap(pos, r)
        lut = cmap.getLookupTable(.5,1.0,256)#(-.009,1.05, 256)

        
        #### Set Data  #####################
        self.y = x#[0:20]
        self.x = y#[0:20]
        self.contours = contours
        self.j = 0
        #  image plot
        self.data = np.rot90(bg)
        self.img = pg.ImageItem(border=None)
        self.img.setZValue(-100)
        self.img.setLookupTable(lut)
        self.img.setImage(self.data)

        
        #make the contours
        self.cont_plots = []
        for c in self.contours:
            for n, contour in enumerate(c):
                spi = pg.PlotDataItem(595-contour[:,1]-12, contour[:,0],pen={'color':(102,102,153,127),'width':3})
                self.cont_plots.append(spi)
        for c in self.cont_plots:
            self.view.addItem(c)
        """
        LENGTH CONT_PLOTS != LENGTH SELF.CONTOURS
        """

        start= time.time()
        self.pdi = pg.PlotDataItem(self.x, self.y, pen={'color':'w','width':3})
        self.view.addItem(self.img)
        self.view.addItem(self.pdi)
       
        print 'creating contours takes', time.time()-start
        


        self.counter = 0
        self.fps = 0. 
        self.lastupdate = time.time()
        
        #### Start  #####################
        self.view.mouseClickEvent = self.new_MouseClickEvent
        #self.view.mouseMoveEvent = self.new_mouseMoveEvent
        self.setMouseTracking(True)
        self._update()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            '''try:
                subprocess.call('rm algorithm_input.txt', shell=True)
            except:
                print ""'''
            self.close()

    def mouseMoveEvent(self, e):
        #print 'here'
        if self.pressed:
            self.moved = True
            pos= e.pos()
            print [pos.x(),pos.y()]
            #self.current_pos = [pos.x()/XWINDOW,pos.y()/YWINDOW]
            self.pdi.setPen(color='r',width=3)
            self.current_pos = [(pos.x()+x0)/(xscale),(pos.y()-y0)/yscale]

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
                    self.end_pos = [(pos.x()+45)/(xscale),(pos.y()-15)/yscale]#[(pos.x()-self.leftmargin)/XWINDOW,(pos.y()-self.topmargin)/YWINDOW]
                    print self.end_pos, 'end pos'

                    #save data to file
                    f = open('algorithm_input.txt','w')
                    f.write('%f %f %f %f'%(self.start_pos[0],self.start_pos[1],self.end_pos[0],self.end_pos[1]))
                    f.close()
                    self.mainbox.setCursor(QtCore.Qt.WaitCursor)
                    #time.sleep(2.5)
                    self.counter = 0
                    global x
                    global y
                    global end
                    global start
                    x,y,bg,c = load_data() #/ scaling
                    self.contours = c
                    for c in self.cont_plots:
                        c.setData([],[])
                        self.view.removeItem(c)
                    self.cont_plots = []
                    for c in self.contours:
                        for n, contour in enumerate(c):
                            spi = pg.PlotDataItem(595-contour[:,1]-12, contour[:,0],pen={'color':(102,102,153,127),'width':3})
                            self.cont_plots.append(spi)
                    for c in self.cont_plots:
                        self.view.addItem(c)
                    self.view.removeItem(self.pdi)
                    self.view.addItem(self.pdi)
                    self.data = np.rot90(bg)
                    self.img.setImage(self.data)
                    self.mainbox.setCursor(QtCore.Qt.CrossCursor)
                    self.pressed = False; self.moved=False
                    self.pdi.setPen(color='w',width=3)
                else:
                    pos = QMouseEvent.pos()
                    self.pressed = True
                    self.start_pos = [(pos.x()+45)/(xscale),(pos.y()-15)/yscale]#[(pos.x()-self.leftmargin)/XWINDOW,(pos.y()-self.topmargin)/YWINDOW]
                    print self.start_pos, 'start'
                    #self.start_pos[0] = (self.start_pos[0]-x0)*XWIDTH; self.start_pos[1] = (self.start_pos[1]-y0)*YWIDTH
                    self.current_pos = [self.start_pos[0],self.start_pos[1]]
                    self.pdi.clear()
                    self.pdi.setPen(color=(0,0,0,0),width=3)
                    self.pdi.setData([0,0],[0,0])
                    self.mainbox.setCursor(QtCore.Qt.CrossCursor)

                     
    def new_MouseClickEvent(self, e):
        if e.button() == QtCore.Qt.RightButton:
            e.accept()
            #print 'final pos', QMouseEvent.pos()



    def _update(self):

          self.pdi.setData(self.y[self.counter:self.counter + 50], self.x[self.counter:self.counter + 50])

          if self.pressed and self.moved:
            self.pdi.setData([YWIDTH-self.start_pos[0]*YWIDTH,YWIDTH-self.current_pos[0]*YWIDTH],[self.start_pos[1]*XWIDTH,self.current_pos[1]*XWIDTH])

          QtCore.QTimer.singleShot(1, self._update)
          self.counter += 1
          
          #staggered contour plotting
          if self.counter == 25:
            i = self.j
            print i
            self.view.removeItem(self.cont_plots[i])
            c = self.contours[i]
            for n, contour in enumerate(c):
                spi = pg.PlotDataItem(595-contour[:,1]-12, contour[:,0],pen={'color':(102,102,153,127),'width':3})
                self.cont_plots[i] = spi           
            self.view.addItem(self.cont_plots[i])
            self.view.removeItem(self.pdi)
            self.view.addItem(self.pdi)
            self.j += 1
            if self.j >= 4:
                self.j = 0
          
          #staggered loading of data
          if self.counter == 100:
            x, y = np.load('algorithm_output.npy')
            x_scaled = x * YWIDTH - 7
            y_scaled = YWIDTH- (y * XWIDTH) - 12
            self.x = np.append(self.x, x_scaled)
            self.y = np.append(self.y, y_scaled)
          if self.counter == 150:
            self.c = np.load('contours.npy')
            bg = np.load('display_dem.npy') / scaling
            bg[0,0] = -40
            bg[0,1] = 1
            self.data = np.rot90(bg,1)
            self.img.setImage(self.data)
          if self.counter == 200:
            self.counter = 0
            self.x = self.x[200:]
            self.y = self.y[200:]
            
            i = self.j
            print i
            self.view.removeItem(self.cont_plots[i])
            c = self.contours[i]
            for n, contour in enumerate(c):
                spi = pg.PlotDataItem(595-contour[:,1]-12, contour[:,0],pen={'color':(102,102,153,127),'width':3})
                self.cont_plots[i] = spi           
            self.view.addItem(self.cont_plots[i])
            self.view.removeItem(self.pdi)
            self.view.addItem(self.pdi)
            self.j += 1
            if self.j >= 4:
                self.j = 0

          '''if self.counter == len(x)-50:
            end = time.time()
            self.counter = 0
            self.pdi.setData([],[])
            global x
            global y
            global end
            global start
            x,y,bg,c = load_data()
            self.contours = c
            for c in self.cont_plots:
                c.setData([],[])
                self.view.removeItem(c)
            self.cont_plots = []
            for c in self.contours:
                for n, contour in enumerate(c):
                    spi = pg.PlotDataItem(595-contour[:,1]-12, contour[:,0],pen={'color':(102,102,153,127),'width':3})
                    self.cont_plots.append(spi)
            for c in self.cont_plots:
                self.view.addItem(c)
                    
            self.view.removeItem(self.pdi)
            self.view.addItem(self.pdi)
            self.data = np.rot90(bg,1)
            #self.make_contours(1)
            """
            for c in self.curves:
                print c
                self.c.setData(self.data)
            """
            self.img.setImage(self.data)

            exporter = pg.exporters.ImageExporter(self.img)
            exporter.export('color_field.jpg')
            
            topo_time = time.time()
            io_funcs.send_topo()
            topo_end = time.time() - topo_time
            print 'topo_time =', topo_end


            print 'It took %f to read %i pts'%(start-end, len(x))
            start = time.time()
            '''

           


if __name__ == '__main__':

    #time.sleep(2)
    app = QtGui.QApplication(sys.argv)
    thisapp = App()
    thisapp.show()
    sys.exit(app.exec_())

