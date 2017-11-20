import sys
import time
from pyqtgraph.Qt import QtCore, QtGui
#from pyqtgraph.Qt.QtCore import QThread, SIGNAL
import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
from subprocess import call
from skimage import measure
import gravity_algorithm
import convolution
import topogra as topo
from argparse import ArgumentParser


start = time.time()
end = time.time()
scaling = 40 * 10
YWIDTH = 580.#480.
XWIDTH = 410.#600#640.
y0 = 1.#-10#/2.
x0 = 1#15#2.
XWINDOW = 640.*2   
YWINDOW = 512.*2 
#xscale = 600.*2.055 ; yscale = 495.*2.045
xscale = 600.*2.008 ; yscale = 495.*2.003

# ----- INITIAL VALUES AND CONSTANTS -------------
X_KERNEL =  np.load('./aux/dx_dft.npy')#fits.getdata('./aux/dx_kernel.fits',0)  ##
Y_KERNEL = np.load('./aux/dy_dft.npy') #fits.getdata('./aux/dy_kernel.fits',0) #

TRACE_BOOL = False
TRACE_LENGTH = 0


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
            #bg = np.zeros(bg.shape)
            bg[0,0] = -40
            bg[0,1] = 1
            #subprocess.call('rm algorithm_output.npy',shell=True)
            return x, y, bg#, np.load('contours.npy')
        except:
            i += 1

x, y, bg = load_data()


#cmap_jet = np.load('./aux/jet_cmap.npy')
cmap_jet = np.load('./aux/jet_cmap.npy')
cmap_viridis = np.load('./aux/viridis_cmap.npy')
cmap_sauron = np.load('./aux/cmap_sauron.npy')

class AboutScreen(QtGui.QWidget):
     def __init__(self, parent=None):
        super(AboutScreen,self).__init__(parent)
        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        #self.setCentralWidget(self.mainbox)
        self.setLayout(QtGui.QGridLayout())

        self.setGeometry(1920/2.,1080/2.,500,500)

        self.bck = QtGui.QLabel()
        self.bck.setPixmap(QtGui.QPixmap('./aux/starfield.png'))
        self.bck.setGeometry(0,0,500,500)

        self.aboutText = QtGui.QLabel()
        self.aboutText.setText('GravBox is the interface application for the Augmented Reality (AR) Sandbox for gravitational dynamics simulations designed and built\nby Dr. Hai Fu\'s Introduction to Astrophysics class during the 2016-2017 academic year and beyond.\nGravBox itself was designed by Zachary Luppen, Erin Maier, and Mason Reed.\n\nAR Sandbox is the result of an NSF-funded project on informal science education for freshwater lake and watershed science developed by the\nUC Davis\' W.M. Keck Center for Active Visualization in the Earth Sciences (KeckCAVES),\ntogether with the UC Davis Tahoe Environmental Research Center, Lawrence Hall of Science, and ECHO Lake Aquarium and Science Center.')
        self.aboutText.move(0,30)

        self.exit_button = QtGui.QPushButton('Close', self)
        self.exit_button.clicked.connect(self.exit_about)
        self.exit_button.move(0,50)

    def exit_about():
        self.close()

class WelcomeScreen(QtGui.QWidget):
     def __init__(self, parent=None):
        super(WelcomeScreen,self).__init__(parent)
        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        #self.setCentralWidget(self.mainbox)
        self.setLayout(QtGui.QGridLayout())

        self.setGeometry(0,0,1920,1080)

        self.bck = QtGui.QLabel()
        self.bck.setPixmap(QtGui.QPixmap('./aux/starfield.png')) #change to welcome screen
        self.bck.setGeometry(0,0,1920,1080)

        self.aboutText = QtGui.QLabel()
        self.aboutText.setText('')
        self.aboutText.move(0,30)

        self.exit_button = QtGui.QPushButton('Start Your Journey', self)
        self.exit_button.clicked.connect(self.exit)
        self.exit_button.move(0,50)

    def exit():
        #self.close()
        self.lower()

class GravityThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.current_pos = [300,212]
        self.current_vel = [0,0]
        self.previous_pos = np.copy(self.current_pos)
        self.previous_vel = np.copy(self.current_vel)
        self.in_pos = np.copy(self.previous_pos)
        self.in_vel = np.copy(self.previous_vel)
        self.baseplane,self.bounds = topo.ar_calibrate()#topo.generate_baseplane()
        #self.prev_dem = np.load('display_dem.npy')
        self.prev_dem = topo.update_surface(self.baseplane,self.bounds, None)
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
                #scaled_dem_array = np.load('display_dem.npy')
                scaled_dem_array = topo.update_surface(self.baseplane,self.bounds, self.prev_dem, verbose=True) 
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
                to_send = gravity_algorithm.run_orbit(particle, 1500, loops=0,step=0.001,edge_mode='reflect',kind='leapfrog2') #run for 1000 iterations and save the array
                posx = [val[0] for val in to_send]
                posy = [val[1] for val in to_send]
                print 'Calculation took ', time.time()-calc_start

                input_pos, input_vel = self.in_pos, self.in_vel
                #check for inputs
                if not self.differ(input_pos, self.previous_pos) and not self.differ(input_vel, self.previous_vel):
                    x = np.asarray(posx)/scaled_dem_array.shape[1]
                    y = np.asarray(posy)/scaled_dem_array.shape[0]
                    x = x[::15]
                    y = y[::15]
                #print 'has it even gotten here?', x
                #sys.exit() 
                self.emit(QtCore.SIGNAL('stage_data'),[x, y, np.nan_to_num(scaled_dem_array)+2,self.idle])

                self.current_pos = [particle.pos[0], particle.pos[1]] 
                self.current_vel = [particle.vel[0], particle.vel[1]]
                

                print 'TRACE LENGTH', TRACE_LENGTH
                time.sleep(.87 + (.0002*TRACE_LENGTH) - (time.time() - start_loop))
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
                scaled_dem_array = topo.update_surface(self.baseplane, self.bounds,self.prev_dem,verbose=True)
                #scaled_dem_array = scaled_dem_array[40:-30, 30:-30] 
                #scaled_dem_array = np.load('display_dem.npy') 
                self.prev_dem = scaled_dem_array
                x = np.zeros(100)
                y = np.zeros(100)
                #np.save('../circles.npy',scaled_dem_array)
                #x,y = self.loading_circle()
                #bck = np.zeros((410,610))
                #bck[:,30:] = scaled_dem_array
                self.emit(QtCore.SIGNAL('stage_data'),[x/scaled_dem_array.shape[1], y/scaled_dem_array.shape[0], np.nan_to_num(scaled_dem_array)+2, self.idle])
                #add an idle message! or plot a loading circle...?
                time.sleep(1)

    def read_input(self,inputs, vel_scaling,x_factor=580, y_factor=410):
        x_i, y_i, x_f, y_f = inputs
        #pos = np.array([y_i * y_factor +10, x_i * x_factor-10]) 
        pos = np.array([y_i * y_factor +0, x_i * x_factor-0])    
        d_x = (x_f - x_i)*x_factor
        d_y = (y_f - y_i)*y_factor
        ang = np.arctan2(d_y,d_x)
        mag = np.sqrt(d_x**2 + d_y**2) * vel_scaling
        vel = np.array([np.sin(ang)*mag, np.cos(ang)*mag])
        print pos, vel, 'pos and vel'
    
        self.in_pos = pos
        self.in_vel = vel

class Surface(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Surface,self).__init__(parent)
        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        #self.setCentralWidget(self.mainbox)
        self.setLayout(QtGui.QGridLayout())
        self.setCursor(QtCore.Qt.CrossCursor)
        #self.setMouseTracking(True)


        self.canvas = pg.GraphicsLayoutWidget()
        self.layout().addWidget(self.canvas)
        self.view = self.canvas.addViewBox()
        self.view.setAspectLocked(True)
        self.view.setRange(xRange=[0,580],yRange=[0,410],padding=-1)
        self.view.setMouseEnabled(x=False,y=False)
        self.view.setBackgroundColor((.5,.5,.5,1.))

        self.setGeometry(0,0, 1280, 960) # JUST IN CASE, CTRL-ALT-ESC    
        self.canvas.nextRow()

        #r = cmap_viridis
        r = cmap_jet
        pos = np.linspace(1.9,-.9,len(r)-1)
        pos= np.append(pos, np.array([np.nan]))
        self.cmap = pg.ColorMap(pos, r)
        self.lut = self.cmap.getLookupTable(-5.25,1.9,256)#(-.009,1.05, 256)

        r2 = cmap_viridis
        pos2 = np.linspace(1.9,-.9,len(r2)-1)
        pos2= np.append(pos2, np.array([np.nan]))
        self.cmap2 = pg.ColorMap(pos2, r2)
        self.lut2 = self.cmap2.getLookupTable(-5.25,1.9,256)

        r4 = cmap_sauron
        pos4 = np.linspace(1.9,-.9,len(r2)-1)
        pos4= np.append(pos4, np.array([np.nan]))
        self.cmap4 = pg.ColorMap(pos4, r4)
        self.lut4 = self.cmap4.getLookupTable(-5.25,1.9,256)

        #black
        r3 = np.array([[0,0,0,256],[0,0,0,256],[0,0,0,256]])
        pos3 = np.linspace(1.9,-.9,len(r3)-1)
        pos3= np.append(pos3, np.array([np.nan]))
        self.cmap3 = pg.ColorMap(pos3, r3)
        self.lut3 = self.cmap3.getLookupTable(-5.25,1.9,256)

        self.luts = [self.lut, self.lut2, self.lut4, self.lut3]

        #### Set Data  #####################
        self.start = time.time()
        self.y = []#[0:20]
        self.x = []#[0:20]
        self.newx = np.copy(self.x)
        self.newy = np.copy(self.y)
        self.j = 0
        #  image plot
        self.data = np.rot90(bg)#np.zeros((580,410)))
        self.newbg = np.copy(self.data)
        self.img = pg.ImageItem(border=None)
        self.img.setZValue(-100)
        self.img.setLookupTable(self.lut)
        self.img.setImage(self.data)
        self.current_conts = []
        self.pdi_list = []
        n_colors = 5
        grad = np.linspace(64,255,n_colors)
        for x in grad:
            self.pdi_list.append(pg.PlotDataItem([], [], pen={'color':(230, 0, 230,x),'width':3})) #
        
        self.view.addItem(self.img)
        for v in self.pdi_list:
            self.view.addItem(v)

        self.tracex = []; self.tracey = []

    def _update_pos(self, x,y, color='w'):
        self.x = x; self.y = y
        num_vals = 50 / len(self.pdi_list)
        self.pdi_list[0].setPen(color=(255,255,255,32),width=3)
        for i in range(len(self.pdi_list)):
            v = self.pdi_list[i]
            v.setData(x[i*num_vals:(i+1)*num_vals], y[i*num_vals:(i+1)*num_vals])
        if TRACE_BOOL:
            v = self.pdi_list[0]
            i=1
            v.setData(np.append(x[i*num_vals:(i+1)*num_vals],self.tracex), np.append(y[i*num_vals:(i+1)*num_vals],self.tracey))
            self.tracex = np.append(x[i*num_vals:(i+1)*num_vals],self.tracex)[::]#np.append(x,self.tracex)[::5]
            self.tracey = np.append(y[i*num_vals:(i+1)*num_vals],self.tracey)[::]#np.append(y,self.tracey)[::5]
            if len(self.tracex) > 10000:
                self.tracex = self.tracex[:10000]
                self.tracey = self.tracey[:10000]
        else:
            self.tracex = []
            self.tracey = []
        if color=='r':
            v = self.pdi_list[0]
            v.setPen(color='r',width=3)
            for i in range(len(self.pdi_list)):
                v = self.pdi_list[i]
                v.setData(x[i*num_vals:(i+1)*num_vals], y[i*num_vals:(i+1)*num_vals])
        
    def _update_bg(self, bg, lutval):
        bg[0,0] = 600
        bg[0,1] = -5
        self.data = np.rot90(bg,1)
        self.img.setImage(self.data)
        if lutval != self.lutval:
            self.lutval = lutval
            if self.lutval == 1:
                self.img.setLookupTable(self.lut2)
            elif self.lutval == 2:
                self.img.setLookupTable(self.lut3)

        if args.cont_on:
            self.mk_contours_thread.update_bg(bg)

    def set_cmap(self, imap):
        self.img.setLookupTable(self.luts[imap])


class Display(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Display,self).__init__(parent)
        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        #self.setCentralWidget(self.mainbox)
        self.setLayout(QtGui.QGridLayout())
        self.setCursor(QtCore.Qt.CrossCursor)
        self.setMouseTracking(True)
        self.setGeometry(0,0,1920+1280,1080)

        ###LAYOUT THE DSIPLAY ###
        self.bck=QtGui.QLabel(self)
        self.bck.setPixmap(QtGui.QPixmap('./aux/starfield.png'))
        self.bck.setGeometry(0,0,1920,1080)
        self.bck.setScaledContents(True)
        self.bck.setMinimumSize(1,1)
        self.bck.move(0,0)

        ### HELPER WIDGETS ####
        self.home = WelcomeScreen()
        self.home.move(0,0)

        ### PLOTTING WIDGET(S) ####
        self.surface1 = Surface()
        self.surface2 = Surface()#surface1
        self.surface1.move(100,100)
        self.surface2.move(100+1280,100)
    

        #### BUTTONS ######
        self.trail_button = QtGui.QPushButton('Trail', self)
        #self.button = PicButton('grav_button.png','grav_hover.png','grav_click.png')
        self.trail_button.clicked.connect(self.start_trace)
        self.trail_button.move(1280+480,270)

        self.cmap_button = QtGui.QPushButton('ColorMap', self)
        self.menu = QtGui.QMenu()
        #self.menu.addAction('Contours',self.set_cont)
        self.menu.addAction('Default', self.set_nocont)
        self.menu.addAction('Sauron', self.set_saruon)
        self.menu.addAction('Viridis', self.set_viridis)
        self.menu.addAction('Black', self.set_black)
        self.cmap_button.setMenu(self.menu)
        #self.button = PicButton('grav_button.png','grav_hover.png','grav_click.png')
        self.cmap_button.clicked.connect(self.handleButton)
        self.cmap_button.move(1280+480,540)

        self.clear_button = QtGui.QPushButton('Clear', self)
        #self.button = PicButton('grav_button.png','grav_hover.png','grav_click.png')
        self.clear_button.clicked.connect(self.end_trace)
        self.clear_button.move(1280+480,540+270)

        self.about_button = QtGui.QPushButton('About', self)
        #self.button = PicButton('grav_button.png','grav_hover.png','grav_click.png')
        self.about_button.clicked.connect(self.open_about)
        self.about_button.move(70,360)

        self.sarndbox_button = QtGui.QPushButton('SARndbox', self)
        #self.button = PicButton('grav_button.png','grav_hover.png','grav_click.png')
        self.sarndbox_button.clicked.connect(self.start_sarndbox)
        self.sarndbox_button.move(70,720)

        #aboutText = QtGui.QLabel()
        

        self.pressed=False; self.moved=False  

        """
        Adjust margins to align stuff.
        Order is left, top, right, bottom. 
        """ 
        self.leftmargin = 240 ; self.topmargin = 20; self.rightmargin =240; self.bottommargin = 20
        self.setContentsMargins(self.leftmargin, self.topmargin, self.rightmargin, self.bottommargin)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        
        
        #start the computation thread
        self.gravity_thread = GravityThread()
        self.connect(self.gravity_thread, QtCore.SIGNAL('stage_data'), self.stage_data)
        self.gravity_thread.start()
        self.calc_idle = True       

        self.counter = 0
        self.fps = 0. 
        self.lastupdate = time.time()
        
        #### Start  #####################
        self.setMouseTracking(True)
        self.home.raise_()
        self._update()



    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            sys.exit()
    def handleButton(self):
        print ('Hello World')
        if self.lutval == 1:
            self.img.setLookupTable(self.lut2)
            self.lutval = 2
        else:
            self.img.setLookupTable(self.lut)
            self.lutval = 1

    def set_black(self):
        self.surface1.set_cmap(2)
    def set_nocont(self):
        self.surface1.set_cmap(0)
    def set_sauron(self):
        self.surface1.set_cmap(1)
    def set_viridis(self):
        self.surface1.set_cmap(3)

    def open_about(self):
        about = AboutScreen()
        about.move(1920/2,1080/2)
        about.raise_()

        
    def start_sarndbox(self):
        print 'call whatever starts the sarndbox'
        call('/home/gravbox/src/SARndbox-2.3/bin/SARndbox -uhm -fpv -rs 0.0&', shell=True)

    def start_trace(self):
        global TRACE_BOOL
        TRACE_BOOL = True
        self.tracex = []; self.tracey = []

    def end_trace(self):
        global TRACE_BOOL
        TRACE_BOOL = False
        self.tracex = []; self.tracey = []


    def mouseMoveEvent(self, e):
        #constrain the mouse cursor?
        pos = e.pos()
        if pos.x() > 1920:
            print 'WUBDOW'
            cursor = self.getCursor()
            cursor.setPos((1920,pos.y()))

#will need to be rescaled
        if self.pressed:
            self.moved = True
            pos= e.pos()
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
            

    #TODO - redefine the click positions once things are placed    
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
                #make points transparent
                if self.pressed:
                    pos= QMouseEvent.pos()
                    if pos.x() >= self.xlow and pos.x() <= self.xhigh and pos.y() >= self.ylow and pos.y() <= self.yhigh:
                        #handle inside the plot boundaries
                        self.end_pos = [(pos.x()-self.xlow)/(xscale),(pos.y()-self.ylow)/yscale]
                    elif pos.x() >= self.xlow and pos.x() <= self.xhigh and pos.y() < self.ylow:
                        #within x but lower than y
                        self.end_pos = [(pos.x()-self.xlow)/(xscale),0.]
                    elif pos.x() >= self.xlow and pos.x() <= self.xhigh and pos.y() > self.yhigh:
                        #within x but higher than y
                        self.end_pos = [(pos.x()-self.xlow)/(xscale),1.]
                    elif pos.y() >= self.ylow and pos.y() <= self.yhigh and pos.x() < self.xlow:
                        #within y but lower than x
                        self.end_pos = [0.,(pos.y()-self.ylow)/yscale]
                    elif pos.y() >= self.ylow and pos.y() <= self.yhigh and pos.x() > self.xhigh:
                        #within y but higher than x
                        self.end_pos = [1.,(pos.y()-self.ylow)/yscale]
                    elif pos.x() < self.xlow and pos.y() < self.ylow:
                        #less than both
                        self.end_pos = [0.,0.]
                    else:
                        #greater than both
                        self.end_pos = [1.,1.]

                    self.gravity_thread.read_input([self.start_pos[0],self.start_pos[1],self.end_pos[0],self.end_pos[1]],args.vel_scaling)
                    self.mainbox.setCursor(QtCore.Qt.WaitCursor)
                    self._update_pos([],[])
                    x_scaled = self.newx* YWIDTH - 7
                    self.x =  np.log( np.zeros(len(x_scaled))-1)
                    self.y = np.copy(self.x)
                    self.newx = []; self.newy = []
                    self.counter = -1
                    self.start = time.time()
                    self.mainbox.setCursor(QtCore.Qt.CrossCursor)
                    self.pressed = False; self.moved=False
                    self.tracex = []
                    self.tracey = []
                    global TRACE_LENGTH
                    TRACE_LENGTH = 0
                   
                else:
                    pos = QMouseEvent.pos()
                    if pos.x() >= self.xlow and pos.x() <= self.xhigh and pos.y() >= self.ylow and pos.y() <= self.yhigh:
                        #inside the plot boundaries
                        self.pressed = True
                        self.start_pos = [(pos.x() - self.xlow)/(xscale),(pos.y()-self.ylow)/yscale]
                        self.current_pos = [self.start_pos[0],self.start_pos[1]]
                        self.mainbox.setCursor(QtCore.Qt.CrossCursor)
                        self.tracex = []
                        self.tracey = []
                        global TRACE_LENGTH
                        TRACE_LENGTH = 0
                     
    def new_MouseClickEvent(self, e):
        if e.button() == QtCore.Qt.RightButton:
            e.accept()


    def stage_data(self, data):
        if len(self.newx) <1:
            self.counter = 0
        self.newx, self.newy, self.newbg, self.calc_idle = data

    def _update(self):
        if self.counter >= 0:
          
          self.surface1._update_pos(self.y[self.counter:self.counter + 50], self.x[self.counter:self.counter + 50])
          self.surface2._update_pos(self.y[self.counter:self.counter + 50], self.x[self.counter:self.counter + 50])
          
          if self.pressed and self.moved:
            self.surface1._update_pos([YWIDTH-self.start_pos[0]*YWIDTH,YWIDTH-self.current_pos[0]*YWIDTH],[self.start_pos[1]*XWIDTH,self.current_pos[1]*XWIDTH],color='r')
            self.surface2._update_pos([YWIDTH-self.start_pos[0]*YWIDTH,YWIDTH-self.current_pos[0]*YWIDTH],[self.start_pos[1]*XWIDTH,self.current_pos[1]*XWIDTH],color='r')

          QtCore.QTimer.singleShot(6.5, self._update)
          self.counter += 1
          
          #staggered loading of data
          if self.counter == len(self.newx)-50:
            x_scaled = self.newx* YWIDTH #- 7
            y_scaled = YWIDTH- (self.newy * XWIDTH) #- 12
            self.x = np.append(self.x, x_scaled)
            self.y = np.append(self.y, y_scaled)
            print x_scaled[0], y_scaled[0]
            print 'updating'
          if self.counter == len(self.newx)-20:
            bg = self.newbg / scaling
            bg[0,0] = 600
            bg[0,1] = -5
            self.data = np.rot90(bg,1)
            self.surface1._update_bg(bg)
            self.surface2._update_bg(bg)
            
          if self.counter >= len(self.newx):
            if TRACE_BOOL == False:
                self.tracex = []
                self.tracey = []
                global TRACE_LENGTH
                TRACE_LENGTH = 0
            try:
                print time.time() - self.start,  'ANIMATING TOOK'
                time.sleep(.9 - (time.time() - self.start))
                self.counter = 0
                self.x = self.x[100:]
                self.y = self.y[100:]
                self.start = time.time()
            except:
                self.counter = 0
                print time.time() - self.start,  'ANIMATING TOOK'
                self.x = self.x[100:]
                self.y = self.y[100:]
                self.start = time.time()
        else:
            QtCore.QTimer.singleShot(1, self._update) 

parser = ArgumentParser()
parser.add_argument("-i", "--idle", dest="idle_time", default=180., type=float, help="Set the amount of time (in seconds) until idle mode begins (default 600)")
parser.add_argument("-t", "--timing", dest="INT_SECONDS", default=3.5, type=float, help="Set the number of seconds per iteration you would like (default 3.5)")
parser.add_argument("-s", "--speed", dest="vel_scaling", type=float, default=.5, help="Set a scaling factor for the input velocities (default 1.0)")
parser.add_argument("-c", "--contours", dest="cont_on", type=int, default=0, help="Turns the contours on (1) or off (0). Default is on.")
parser.add_argument("-d", "--debug", dest="debug", type=int, default=0, help="Use a pre-made density field for testing purposes. Disables tablet I/O. 1 for on, 0 for off.")
parser.add_argument("-v", "--verbose", dest="verbose", type=bool, default=False, help="Save a plot displaying the potential field. (default False)")
parser.add_argument("-a", "--audio", dest="music", type=bool, default=False, help="Play appropriate music. (default False)")
parser.add_argument("-m", "--colormap", dest="cmap_name", type=str, default='jet', help="Name of the colormap. Options are 'jet' and 'viridis'. Default is 'jet'.")
parser.add_argument("-q", "--second_display", dest="second_display", type=int, default=0,help="Display on a second monitor? Yes (1), No (0). Default no.")


if __name__ == '__main__':
    args = parser.parse_args()
    app = QtGui.QApplication(sys.argv)
    thisapp = Display()
    thisapp.show()
    sys.exit(app.exec_())