import sys
import time
from pyqtgraph.Qt import QtCore, QtGui
#from pyqtgraph.Qt.QtCore import QThread, SIGNAL
import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
import subprocess
from skimage import measure
import gravity_algorithm
import convolution
import topogra as topo
from argparse import ArgumentParser


start = time.time()
end = time.time()
scaling = 16
YWIDTH = 600.#480.
XWIDTH = 422.#600#640.
y0 = 10#/2.
x0 = 40#2.
XWINDOW = 640.*2/2
YWINDOW = 512.*2/2
xscale = 600.*2.05/2; yscale = 495.*2.05/2

# ----- INITIAL VALUES AND CONSTANTS -------------
X_KERNEL =  np.load('./aux/dx_dft.npy')#fits.getdata('./aux/dx_kernel.fits',0)  ##
Y_KERNEL = np.load('./aux/dy_dft.npy') #fits.getdata('./aux/dy_kernel.fits',0) #



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
            #subprocess.call('rm algorithm_output.npy',shell=True)
            return x, y, bg#, np.load('contours.npy')
        except:
            i += 1

x, y, bg = load_data()


cmap_jet = np.load('./aux/jet_cmap.npy')
cmap_viridis = np.load('./aux/viridis_cmap.npy')


class GravityThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.current_pos = [300,212]
        self.current_vel = [0,0]
        self.previous_pos = np.copy(self.current_pos)
        self.previous_vel = np.copy(self.current_vel)
        self.in_pos = np.copy(self.previous_pos)
        self.in_vel = np.copy(self.previous_vel)
        #self.baseplane = topo.generate_baseplane()
        self.prev_dem = np.load('display_dem.npy')
        #self.prev_dem = topo.update_surface(self.baseplane, None)
        self.idle = True
    def __del__(self):
        self.wait()
    def differ(self,arr1, arr2):
        for k in range(len(arr1)):
            if arr1[k] != arr2[k]:
                return True
        return False
    def loading_circle(self):
        t = np.linspace(0,np.pi*2, 200)
        r = 10
        x = r * np.cos(t) + 410/2
        y = r * np.sin(t) + 580/2
        return x,y
    def run(self):
        last_idle = time.time()
        while True:
            if not self.idle:
                # Load in surface
                start_loop = time.time()
                scaled_dem_array = np.load('display_dem.npy')#
                #scaled_dem_array = topo.update_surface(self.baseplane, self.prev_dem) 
                self.prev_dem = scaled_dem_array
                #scaled_dem_array = scaled_dem_array[40:-30, 30:-30] 
                xw = scaled_dem_array.shape[1]; yw = scaled_dem_array.shape[0]
                
                """CONVOLVE THE DEM-DENSITY FIELD WITH THE PLUMMER KERNEL"""
                shp = scaled_dem_array.shape
                conv_start = time.time()
                gx,gy, g2x, g2y = convolution.convolve2d(scaled_dem_array, X_KERNEL,Y_KERNEL,method='wrap')
                print 'Convolution took ', time.time()-conv_start
                
                #Create the particle
                particle = gravity_algorithm.Particle(self.current_pos, np.array(self.current_vel), (gx,gy),g2x,g2y)

                """Read input positions from UI. If they are new, use in a new particle. """
                #get from the signal
                input_pos = self.in_pos; input_vel= self.in_vel#io_funcs.read_from_app(args.vel_scaling,x_factor=shp[1],y_factor=shp[0], mode=args.mode)
                if self.differ(input_pos, self.previous_pos) or self.differ(input_vel, self.previous_vel):
                    particle = gravity_algorithm.Particle(input_pos, np.array(input_vel), (gx,gy),g2x,g2y)
                    particle.kick(0.001/2)
                    self.previous_pos = np.copy(input_pos); self.previous_vel = np.copy(input_vel)
                    last_idle = time.time()
                
                """INTEGRATE FOR A WHILE"""
                calc_start = time.time()
                to_send = gravity_algorithm.run_orbit(particle, 2000, loops=0,step=0.001,edge_mode='reflect',kind='leapfrog2') #run for 1000 iterations and save the array
                posx = [val[0] for val in to_send]
                posy = [val[1] for val in to_send]
                print 'Calculation took ', time.time()-calc_start

                input_pos, input_vel = self.in_pos, self.in_vel
                #check for inputs
                if not self.differ(input_pos, self.previous_pos) and not self.differ(input_vel, self.previous_vel):
                    x = np.asarray(posx)/scaled_dem_array.shape[1]
                    y = np.asarray(posy)/scaled_dem_array.shape[0]
                    x = x[::10]
                    y = y[::10]
                #print 'has it even gotten here?', x
                #sys.exit() 
                self.emit(QtCore.SIGNAL('stage_data'),[x, y, np.nan_to_num(scaled_dem_array)+2,self.idle])

                self.current_pos = [particle.pos[0], particle.pos[1]] 
                self.current_vel = [particle.vel[0], particle.vel[1]]
                print self.current_pos
                time.sleep(1.32 - (time.time() - start_loop))
                dt = time.time()-start_loop
                print 'LOOP TOOK: ', dt
                if time.time() - last_idle >= args.idle_time:
                    self.idle=True
            else:
                input_pos, input_vel = self.in_pos, self.in_vel
                if self.differ(input_pos, self.previous_pos) or self.differ(input_vel, self.previous_vel):
                    self.idle = False
                    last_idle = time.time()
                    continue
                #scaled_dem_array = topo.update_surface(self.baseplane, self.prev_dem)
                #scaled_dem_array = scaled_dem_array[40:-30, 30:-30] 
                scaled_dem_array = np.load('display_dem.npy') 
                self.prev_dem = scaled_dem_array
                x = np.zeros(200)
                y = np.zeros(200)
                #x,y = self.loading_circle()
                self.emit(QtCore.SIGNAL('stage_data'),[x/scaled_dem_array.shape[1], y/scaled_dem_array.shape[0], np.nan_to_num(scaled_dem_array)+2, self.idle])
                #add an idle message! or plot a loading circle...?
                time.sleep(1)

    def read_input(self,inputs, vel_scaling=1,x_factor=580, y_factor=410):
        x_i, y_i, x_f, y_f = inputs
        pos = np.array([y_i * y_factor, x_i * x_factor])    
        d_x = (x_f - x_i)*x_factor
        d_y = (y_f - y_i)*y_factor
        ang = np.arctan2(d_y,d_x)
        mag = np.sqrt(d_x**2 + d_y**2) * vel_scaling
        vel = np.array([np.sin(ang)*mag, np.cos(ang)*mag])
        print pos, vel, 'pos and vel'
        c = 50
        if vel[0] > c:
            vel[0] = c  
        if vel[0] < -c:
            vel[0] = -c
        if vel[1] > c:
            vel[1] = c
        if vel[1] < -c:
            vel[1] = -c
        self.in_pos = pos
        self.in_vel = vel

class ContourThread(QtCore.QThread):
    def __init__(self,data):
        QtCore.QThread.__init__(self)
        self.new_bg = data
    def __del__(self):
        self.wait()
    def run(self):
        #might have to iterate through contours
        j = 0
        first = True
        self.cont_plots = []
        while True:
            scaled_dem_array = self.new_bg
            contours = []
            if first:
                #contour1 = measure.find_contours(scaled_dem_array,np.median(scaled_dem_array))
                contour2 = measure.find_contours(scaled_dem_array,.5*np.median(scaled_dem_array))
                contour3 = measure.find_contours(scaled_dem_array,2.5*np.median(scaled_dem_array))
                contour4 = measure.find_contours(scaled_dem_array,-1*np.median(scaled_dem_array))
                contours = [contour4,contour2,contour3]
            else:
                if j == 0:
                    contours[j] = measure.find_contours(scaled_dem_array,-1*np.median(scaled_dem_array))
                elif j==1:
                    contours[j] = measure.find_contours(scaled_dem_array,.5*np.median(scaled_dem_array))
                elif j==2:
                    contours[j] = measure.find_contours(scaled_dem_array,2.5*np.median(scaled_dem_array))
                #elif j==3:
                #    contours[j] = 
            #contours = np.load('contours.npy')
            colors = [(0,0,0,200),(128,128,128,200),(192,192,192,200)]#(102,102,153,200), (64,64,64,200),
            if first:
                first = False
                for i in range(len(contours)):
                    c = contours[i]
                    for n, contour in enumerate(c):
                        spi = pg.PlotDataItem(595-contour[::5,1]-12, contour[::5,0],pen={'color':colors[i],'width':3})
                        self.cont_plots.append(spi)
            else:
                c = contours[j]
                for n, contour in enumerate(c):
                    spi = pg.PlotDataItem(595-contour[::5,1]-12, contour[::5,0],pen={'color':colors[i],'width':3})
                    self.cont_plots[j] = spi #self.cont_plots.append(spi)
            self.emit(QtCore.SIGNAL('add_contours'), self.cont_plots)
            j += 1
            if j >= len(contours):
                j = 0
                #self.sleep(1)
            self.msleep(50)
    def update_bg(self, bg):
        self.new_bg = bg

class Display(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Display,self).__init__(parent)
        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        #self.setCentralWidget(self.mainbox)
        self.setLayout(QtGui.QVBoxLayout())
        self.setCursor(QtCore.Qt.CrossCursor)
        self.setMouseTracking(True)

        self.canvas = pg.GraphicsLayoutWidget()
        self.canvas.setMouseTracking(True)
        self.layout().addWidget(self.canvas)
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
        self.setContentsMargins(self.leftmargin, self.topmargin, self.rightmargin, self.bottommargin)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        
        self.setGeometry(640,30, XWINDOW, YWINDOW) # JUST IN CASE, CTRL-ALT-ESC    
        self.canvas.nextRow()

        #r = cmap_viridis
        r = cmap_jet
        pos = np.linspace(1.00,-.3,len(r)-1)
        pos= np.append(pos, np.array([np.nan]))
        cmap = pg.ColorMap(pos, r)
        lut = cmap.getLookupTable(.5,1.0,256)#(-.009,1.05, 256)
        if args.cmap_name == 'viridis':
            r = cmap_viridis
            pos = np.linspace(1,-.25,len(r)-1)
            pos= np.append(pos, np.array([np.nan]))
            cmap = pg.ColorMap(pos, r)
            lut = cmap.getLookupTable(-.01,.95, 256)
        
        #### Set Data  #####################
        self.start = time.time()
        self.y = x#[0:20]
        self.x = y#[0:20]
        self.newx = np.copy(self.x)
        self.newy = np.copy(self.y)
        self.j = 0
        #  image plot
        self.data = np.rot90(bg)
        self.newbg = np.copy(self.data)
        self.img = pg.ImageItem(border=None)
        self.img.setZValue(-100)
        self.img.setLookupTable(lut)
        self.img.setImage(self.data)
        self.current_conts = []
        self.pdi = pg.PlotDataItem([], [], pen={'color':'w','width':3})
        #self.ti = pg.TextItem("Click to draw a vector",color='r')
        self.view.addItem(self.img)
        self.view.addItem(self.pdi)

        #make the contours
        if args.cont_on == 1:
            self.mk_contours_thread = ContourThread(bg)
            self.connect(self.mk_contours_thread, QtCore.SIGNAL('add_contours'), self.add_contours)
            #self.connect(self.mk_contours_thread, SIGNAL('finished()'), self.done)
            self.current_conts = []
            self.mk_contours_thread.start()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            '''try:
                subprocess.call('rm algorithm_input.txt', shell=True)
            except:
                print ""'''
            #self.connect(mk_contours_thread.terminate)
            self.close()

    def _update_pos(self, x,y):
        self.pdi.setData(x,y)

    def _update_bg(self, bg):
        bg[0,0] = -40
        bg[0,1] = 1
        self.data = np.rot90(bg,1)
        self.img.setImage(self.data)
        if args.cont_on:
            self.mk_contours_thread.update_bg(bg)

    def _update_contours(self, cont_list):
        #need to remove old contours
        new_conts = []
        for c in self.current_conts:
            self.view.removeItem(c)
        for c in cont_list:
            new_conts.append(c)
            self.view.addItem(c)
        self.current_conts = np.copy(new_conts)
        self.view.removeItem(self.pdi)
        self.view.addItem(self.pdi)

    def add_contours(self, cont_list):
        #need to remove old contours
        new_conts = []
        for c in self.current_conts:
            self.view.removeItem(c)
        for c in cont_list:
            new_conts.append(c)
            self.view.addItem(c)
        self.current_conts = np.copy(new_conts)
        self.view.removeItem(self.pdi)
        self.view.addItem(self.pdi)
        #self.second_display._update_contours(cont_list)




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
        pos = np.linspace(1.00,-.3,len(r)-1)
        pos= np.append(pos, np.array([np.nan]))
        cmap = pg.ColorMap(pos, r)
        lut = cmap.getLookupTable(.5,1.0,256)#(-.009,1.05, 256)
        if args.cmap_name == 'viridis':
            r = cmap_viridis
            pos = np.linspace(1,-.25,len(r)-1)
            pos= np.append(pos, np.array([np.nan]))
            cmap = pg.ColorMap(pos, r)
            lut = cmap.getLookupTable(-.01,.95, 256)
        #[0., 1., 0.5, 0.25, 0.75])
        
        #### Set Data  #####################
        self.start = time.time()
        self.y = x#[0:20]
        self.x = y#[0:20]
        self.newx = np.copy(self.x)
        self.newy = np.copy(self.y)
        self.j = 0
        #  image plot
        self.data = np.rot90(bg)
        self.newbg = np.copy(self.data)
        self.img = pg.ImageItem(border=None)
        self.img.setZValue(-100)
        self.img.setLookupTable(lut)
        self.img.setImage(self.data)

        #start the computation thread
        self.gravity_thread = GravityThread()
        self.connect(self.gravity_thread, QtCore.SIGNAL('stage_data'), self.stage_data)
        self.gravity_thread.start()
        self.calc_idle = True        

        #make the contours
        if args.cont_on == 1:
            self.mk_contours_thread = ContourThread(bg)
            self.connect(self.mk_contours_thread, QtCore.SIGNAL('add_contours'), self.add_contours)
            #self.connect(self.mk_contours_thread, SIGNAL('finished()'), self.done)
            self.current_conts = []
            self.mk_contours_thread.start()

        #open the second window
        if args.second_display == 1:
            self.second_display = Display()
            self.second_display.show()


        start= time.time()
        self.pdi = pg.PlotDataItem(self.x, self.y, pen={'color':'w','width':3})
        #self.ti = pg.TextItem("Click to draw a vector",color='r')
        self.view.addItem(self.img)
        self.view.addItem(self.pdi)
        #self.view.addItem(self.ti)

       

        self.counter = 0
        self.fps = 0. 
        self.lastupdate = time.time()
        
        #### Start  #####################
        self.view.mouseClickEvent = self.new_MouseClickEvent
        self.setMouseTracking(True)
        self._update()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            '''try:
                subprocess.call('rm algorithm_input.txt', shell=True)
            except:
                print ""'''
            #self.connect(mk_contours_thread.terminate)
            if args.second_display:
                self.second_display.close()
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
                    #f = open('algorithm_input.txt','w')
                    #f.write('%f %f %f %f'%(self.start_pos[0],self.start_pos[1],self.end_pos[0],self.end_pos[1]))
                    #f.close()
                    self.gravity_thread.read_input([self.start_pos[0],self.start_pos[1],self.end_pos[0],self.end_pos[1]])
                    self.mainbox.setCursor(QtCore.Qt.WaitCursor)
                    #time.sleep(2.5)
                    self.counter = 0
                    #x,y,bg,c = load_data() #/ scaling
                    #get the new info from the computing thread
                    #time.sleep(1.5)
                    self.pdi.setData([],[])
                    x_scaled = self.newx* YWIDTH - 7
                    y_scaled = YWIDTH- (self.newy * XWIDTH) - 12
                    self.x =  np.copy(x_scaled)
                    self.y = np.copy(y_scaled)
                    self.start = time.time()
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

    def add_contours(self, cont_list):
        #need to remove old contours
        new_conts = []
        for c in self.current_conts:
            self.view.removeItem(c)
        for c in cont_list:
            new_conts.append(c)
            self.view.addItem(c)
        self.current_conts = np.copy(new_conts)
        self.view.removeItem(self.pdi)
        self.view.addItem(self.pdi)

    def stage_data(self, data):
        self.newx, self.newy, self.newbg, self.calc_idle = data

    def _update(self):
          #print self.x
          self.pdi.setData(self.y[self.counter:self.counter + 50], self.x[self.counter:self.counter + 50])
          if args.second_display:
            self.second_display._update_pos(self.y[self.counter:self.counter + 50], self.x[self.counter:self.counter + 50])
          #self.pdi.setData(self.y, self.x)

          if self.pressed and self.moved:
            self.pdi.setData([YWIDTH-self.start_pos[0]*YWIDTH,YWIDTH-self.current_pos[0]*YWIDTH],[self.start_pos[1]*XWIDTH,self.current_pos[1]*XWIDTH])

          QtCore.QTimer.singleShot(6.5, self._update)
          self.counter += 1
          
          #staggered loading of data
          if self.counter == len(self.newx)-50:
            #self.connect(self.gravity_thread, QtCore.SIGNAL('stage_data'), self.stage_data)
            #x, y = self.newx, self.newy#np.load('algorithm_output.npy')
            #print x
            x_scaled = self.newx* YWIDTH - 7
            y_scaled = YWIDTH- (self.newy * XWIDTH) - 12
            self.x = np.append(self.x, x_scaled)
            self.y = np.append(self.y, y_scaled)
            #self.newx = np.zeros(1); self.newy = np.zeros(1)
            print x_scaled[0], y_scaled[0]
            print 'updating'
            #waiting = input()
          if self.counter == len(self.newx)-20:
            bg = np.load('display_dem.npy')#self.newbg / scaling #
            bg[0,0] = -40
            bg[0,1] = 1
            self.data = np.rot90(bg,1)
            self.img.setImage(self.data)
            if args.second_display:
                self.second_display._update_bg(bg)
            if args.cont_on:
                self.mk_contours_thread.update_bg(bg)

          if self.counter >= len(self.newx):
            try:
                print time.time() - self.start,  'ANIMATING TOOK'
                time.sleep(1.25 - (time.time() - self.start))
                self.counter = 0
                self.x = self.x[200:]
                self.y = self.y[200:]
                self.start = time.time()
            except:
                self.counter = 0
                print time.time() - self.start,  'ANIMATING TOOK'
                self.x = self.x[200:]
                self.y = self.y[200:]
                self.start = time.time()            


parser = ArgumentParser()
parser.add_argument("-i", "--idle", dest="idle_time", default=60., type=float, help="Set the amount of time (in seconds) until idle mode begins (default 600)")
parser.add_argument("-t", "--timing", dest="INT_SECONDS", default=3.5, type=float, help="Set the number of seconds per iteration you would like (default 3.5)")
parser.add_argument("-s", "--speed", dest="vel_scaling", type=float, default=.05, help="Set a scaling factor for the input velocities (default 1.0)")
parser.add_argument("-c", "--contours", dest="cont_on", type=int, default=1, help="Turns the contours on (1) or off (0). Default is on.")
parser.add_argument("-d", "--debug", dest="debug", type=int, default=0, help="Use a pre-made density field for testing purposes. Disables tablet I/O. 1 for on, 0 for off.")
parser.add_argument("-v", "--verbose", dest="verbose", type=bool, default=False, help="Save a plot displaying the potential field. (default False)")
parser.add_argument("-a", "--audio", dest="music", type=bool, default=False, help="Play appropriate music. (default False)")
parser.add_argument("-m", "--colormap", dest="cmap_name", type=str, default='jet', help="Name of the colormap. Options are 'jet' and 'viridis'. Default is 'jet'.")
parser.add_argument("-q", "--second_display", dest="second_display", type=int, default=0,help="Display on a second monitor? Yes (1), No (0). Default no.")


if __name__ == '__main__':
    args = parser.parse_args()
    app = QtGui.QApplication(sys.argv)
    thisapp = App()
    thisapp.show()
    sys.exit(app.exec_())

