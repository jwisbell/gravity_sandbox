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
import mk_kernels


start = time.time()
end = time.time()
scaling = 40 * 10
YWIDTH = 580.#480.
XWIDTH = 410.#600#640.
y0 = 0#60.+40#-10#/2.
x0 = 186+18#15#2.
XWINDOW = 640.*2   
YWINDOW = 512.*2 
#xscale = 600.*2.055 ; yscale = 495.*2.045
xscale = 600.*2.008 ; yscale = 495.*2.003

# ----- INITIAL VALUES AND CONSTANTS -------------
X_KERNEL =  np.load('./aux/dx_dft.npy')#fits.getdata('./aux/dx_kernel.fits',0)  ##
Y_KERNEL = np.load('./aux/dy_dft.npy') #fits.getdata('./aux/dy_kernel.fits',0) #

TRACE_BOOL = False
TRACE_LENGTH = 0
CONTOURS_ON = True


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
cmap_jet = np.load('./aux/cmap_jet.npy')#np.load('./aux/jet_cmap.npy')
cmap_viridis = np.load('./aux/cmap_viridis.npy')
cmap_sauron = np.load('./aux/cmap_sauron.npy')
cmap_geo = np.load('./aux/cmap_geo.npy')


#fonts
#droid_sans = QtGui.QFontDatabase.addApplicationFont('./aux/droid_font/DroidSans.ttf')
#lato_reg = QtGui.QFontDatabase.addApplicationFont('./aux/lato_font/Lato-Regular.ttf')
#lato_reg = QtGui.QFontDatabase.addApplicationFont('./aux/lato_font/Lato-Regular.ttf')

class AboutScreen(QtGui.QWidget):
     def __init__(self, parent=None):
        super(AboutScreen,self).__init__(parent)
        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        #self.setCentralWidget(self.mainbox)
        self.setLayout(QtGui.QGridLayout())

        self.setGeometry(0,0,900,700)


        '''self.bck = QtGui.QLabel(self)
        self.bck.setGeometry(0,0,900,800)
        self.bck.setPixmap(QtGui.QPixmap('./aux/assets/starfield.png'))
        self.bck.move(0,0)
        self.bck.setScaledContents(True)'''

        self.aboutText = QtGui.QLabel(self)
        self.rawtext = "\tGravBox is the Augmented Reality (AR) Sandbox for gravitational \n\tdynamics simulations designed and built by Dr. Hai Fu's Introd-\n\tuction to Astrophysics class during the 2016-2017 academic year \n\tand beyond.\n\n\tAR Sandbox is the result of an NSF-funded project on informal \n\tscience education for freshwater lake and watershed science \n\tdeveloped by the UC Davis' W.M. Keck Center for Active Visual-\n\tization in the Earth Sciences (KeckCAVES), together with the UC \n\tDavis Tahoe Environmental Research Center, Lawrence Hall of \n\tScience, and ECHO Lake Aquarium and Science Center."
        self.aboutText.setText(self.rawtext)
        self.aboutText.setGeometry(0,0,850,800)
        self.aboutText.move(75,0)

        self.logo = QtGui.QLabel(self)
        self.logo.setPixmap(QtGui.QPixmap('./aux/assets/icon.png'))
        self.logo.setGeometry(0,0,100,100)
        self.logo.move(440,100)
        self.logo.setScaledContents(True)

        self.exit_button = PicButton('Close', QtGui.QPixmap('./aux/assets/back.png'),self)
        self.exit_button.setGeometry(0,0,125,50)
        self.exit_button.clicked.connect(self.exit_about)
        self.exit_button.move(425 + 425/2,600)

        self.uiowa_button = QtGui.QPushButton('UIowa',self)
        self.uiowa_button.setGeometry(0,0,125,50)
        self.uiowa_button.clicked.connect(self.open_uiowa)
        self.uiowa_button.move(425/2,600)

        self.aboutText.setAutoFillBackground(True)


        #set the font
        self.aboutText.setStyleSheet("background-color:  #1b1c1d;  color:#fcfcff;font-size:22px; QLabel {font-family:Droid Sans; font-size:22px; color: #fcfcff;} QPushbutton {font-family:Droid Sans; font-size:14px;}")

     def exit_about(self):
        self.lower()

     def open_uiowa(self):
        self.lower()
        self.parent().uiowa.raise_()


class UIowaScreen(QtGui.QWidget):
     def __init__(self, parent=None):
        super(UIowaScreen,self).__init__(parent)
        #### Create Gui Elements ###########
        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        #self.setCentralWidget(self.mainbox)
        self.setLayout(QtGui.QGridLayout())

        self.setGeometry(0,0,900,700)

        self.aboutText = QtGui.QLabel(self)
        self.rawtext = "\tGravBox was developed at the University of Iowa, and \n\twas supported by NSF-Grant ASTR-1614326 (PI: Hai Fu).\n\n    -Engineering Team: Wyatt Bettis, Sadie Moore, and Ross McCurty \n\n    -Interface Team: Zachary Luppen, Erin Maier, and Mason Reed \n\n    -Algorithm Team: Sophie Deam, Jacob Isbell, Jianbo Lu \n\n\tFollow the QR Code for more information about the University. "
        self.aboutText.setText(self.rawtext)
        self.aboutText.setGeometry(0,0,850,800)
        self.aboutText.move(75,0)

        self.logo = QtGui.QLabel(self)
        self.logo.setPixmap(QtGui.QPixmap('./aux/assets/icon.png'))
        self.logo.setGeometry(0,0,100,100)
        self.logo.move(440,100)
        self.logo.setScaledContents(True)

        self.tiger = QtGui.QLabel(self)
        self.tiger.setPixmap(QtGui.QPixmap('./aux/assets/herkylogo.png'))
        self.tiger.setGeometry(0,0,150,100)
        self.tiger.move(440/2-25,100)
        self.tiger.setScaledContents(True)

        self.qr = QtGui.QLabel(self)
        self.qr.setPixmap(QtGui.QPixmap('./aux/assets/qrcode.png'))
        self.qr.setGeometry(0,0,100,100)
        self.qr.move(440+440/2,100)
        self.qr.setScaledContents(True)

        self.exit_button = PicButton('Close', QtGui.QPixmap('./aux/assets/back.png'),self)
        self.exit_button.setGeometry(0,0,125,50)
        self.exit_button.clicked.connect(self.exit_about)
        self.exit_button.move(425+425/2,600)

        self.uiowa_button = QtGui.QPushButton('About',self)
        self.uiowa_button.setGeometry(0,0,125,50)
        self.uiowa_button.clicked.connect(self.open_uiowa)
        self.uiowa_button.move(425/2,600)

        self.aboutText.setAutoFillBackground(True)


        #set the font
        self.aboutText.setStyleSheet("background-color:  #1b1c1d;  color:#fcfcff;font-size:22px; QLabel {font-family:Droid Sans; font-size:22px; color: #fcfcff;} QPushbutton {font-family:Droid Sans; font-size:14px;}")

     def exit_about(self):
        self.lower()

     def open_uiowa(self):
        self.lower()
        self.parent().about.raise_()


class WelcomeScreen(QtGui.QWidget):
    def __init__(self, parent=None):
        super(WelcomeScreen,self).__init__(parent)
        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        #self.setCentralWidget(self.mainbox)
        self.setLayout(QtGui.QGridLayout())

        self.setGeometry(0,0,1920,1080)

        ###LAYOUT THE DSIPLAY ###
        self.bck=QtGui.QLabel(self)
        self.bck.setPixmap(QtGui.QPixmap('./aux/assets/homescreen.png')) #get higher resolution image
        self.bck.setGeometry(0,0,1920,1080)
        self.bck.setScaledContents(True)
        self.bck.setMinimumSize(1,1)
        self.bck.move(0,0)

        self.sxl = 760; self.sxh = 1160
        self.syl = 720; self.syh = 820

        self.axl = 1190; self.axh = 1340
        self.ayl = 980; self.ayh = 1080

        self.ixl = 1340; self.ixh = 1500
        self.iyl = 980; self.iyh = 1080


    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
            pos = QMouseEvent.pos()

            if pos.x() > self.sxl and pos.x() < self.sxh and pos.y() > self.syl and pos.y() < self.syh:
                #inside the start boundaries
                self.lower()

            if pos.x() > self.axl and pos.x() < self.axh and pos.y() > self.ayl and pos.y() < self.ayh:
                #inside the about boundaries
                self.parent().about.raise_()
                self.lower()

            if pos.x() > self.ixl and pos.x() < self.ixh and pos.y() > self.iyl and pos.y() < self.iyh:
                #inside the UIowa boundaries
                self.parent().uiowa.raise_()
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
        self.baseplane,self.bounds = topo.ar_calibration()#topo.generate_baseplane()
        #update the kernel size for calibration settings
        print 'baseplane shape', self.baseplane.shape
        if args.calibrate == True: 
            mk_kernels.make(self.baseplane.shape[0],self.baseplane.shape[1])
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
                scaled_dem_array = self.normalize_bg(scaled_dem_array)
                if CONTOURS_ON:
                    scaled_dem_array = self.make_contours(scaled_dem_array) 
                self.emit(QtCore.SIGNAL('stage_data'),[x, y, scaled_dem_array,self.idle])

                self.current_pos = [particle.pos[0], particle.pos[1]] 
                self.current_vel = [particle.vel[0], particle.vel[1]]
                
                try:
                    #time.sleep(.93 + (.00025*TRACE_LENGTH) - (time.time() - start_loop))
                    time.sleep(.93  - (time.time() - start_loop))
                except:
                    print ''#time.sleep(.95 + (.00025*TRACE_LENGTH) - (time.time() - start_loop))

                dt = time.time()-start_loop
                print 'LOOP TOOK: ', dt
                if time.time() - last_idle >= args.idle_time:
                    self.idle=True
                    self.parent().WelcomeScreen.raise_()
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
                scaled_dem_array = self.normalize_bg(scaled_dem_array)

                if CONTOURS_ON:
                    scaled_dem_array = self.make_contours(scaled_dem_array)
                x = np.zeros(100)
                y = np.zeros(100)
                #np.save('../circles.npy',scaled_dem_array)
                #x,y = self.loading_circle()
                #bck = np.zeros((410,610))
                #bck[:,30:] = scaled_dem_array
                self.emit(QtCore.SIGNAL('stage_data'),[x/scaled_dem_array.shape[1], y/scaled_dem_array.shape[0], scaled_dem_array, self.idle])
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
        #print pos, vel, 'pos and vel'
    
        self.in_pos = pos
        self.in_vel = vel

    def normalize_bg(self, bg):
        #force range of values
        bg[0,0] = -600
        bg[0,1] = 15

        bg = (bg + 600) / 615. #normalize and make [0,1]
        return np.nan_to_num(bg)

    def make_contours(self, im, num_contours=7):
        contour_levels = np.linspace(np.min(im)*.7, np.max(im)*.9,num_contours)
        contour_levels = np.append(contour_levels, np.median(im))

        for v in contour_levels:
            c = measure.find_contours(im, v)
            for n, contour in enumerate(c):
                contour = np.nan_to_num(contour).astype(int)
                im[contour[:,0], contour[:,1]] = -.5 #-600

        return im




class Surface(QtGui.QWidget):
    def __init__(self, parent=None, aspectLock=True, lmargin=0,rmargin=0, tmargin=20, bmargin=20, xstart=0,ystart=0,xspan=1160*4/3.,yspan=1160):
        super(Surface,self).__init__(parent)
        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        #self.setCentralWidget(self.mainbox)
        self.setLayout(QtGui.QGridLayout())
        self.setCursor(QtCore.Qt.CrossCursor)
        
        self.canvas = pg.GraphicsLayoutWidget()
        self.layout().addWidget(self.canvas)
        self.view = self.canvas.addViewBox()
        self.view.setAspectLocked(aspectLock)
        self.view.setRange(xRange=[0,580],yRange=[0,410],padding=-1)
        self.view.setMouseEnabled(x=False,y=False)
        self.view.setBackgroundColor((.5,.5,.5,1.))
        self.xsize = float(xspan); self.ysize = float(yspan)

        self.setGeometry(0+xstart,0+ystart, xspan, yspan) # JUST IN CASE, CTRL-ALT-ESC    
        self.canvas.nextRow()
        self.setContentsMargins(lmargin,tmargin,rmargin,bmargin)

        #r = cmap_viridis
        r = cmap_jet[::-1]
        pos = np.linspace(0.,1.5,len(r)-1)
        pos= np.append(pos, np.array([-.00125]))
        self.cmap = pg.ColorMap(pos, r)
        self.lut = self.cmap.getLookupTable(-.001,1.6,512)#.1,-1.8,512)#(-.009,1.05, 256)
        self.lutc = self.cmap.getLookupTable(0.1,1.72,512)

        r2 = cmap_viridis[::-1]
        pos2 = np.linspace(-0.005,.9,len(r2)-1)
        pos2= np.append(pos2, np.array([-1]))
        #pos2 = np.linspace(1.4,-.7,len(r2)-1)
        #pos2= np.append(pos2, np.array([np.nan]))
        self.cmap2 = pg.ColorMap(pos2, r2)
        self.lut2 = self.cmap2.getLookupTable(0,.85,512)#-5,1.4,256)
        self.lut2c = self.cmap2.getLookupTable(0.1,.95,512)

        r4 = cmap_sauron#[::-1]
        pos4 = np.linspace(0.05,.9,len(r4)-1)#np.array([0.]+[.05*np.power(2,k) for k in range(len(r4)-2)])/2.+.3 #np.linspace(0.2,.95,len(r4)-1)
        pos4= np.append(pos4, np.array([-1]))
        #pos4 = np.linspace(.8,-.3,len(r4)-1)
        #pos4= np.append(pos4, np.array([np.nan]))
        self.cmap4 = pg.ColorMap(pos4, r4)
        self.lut4 = self.cmap4.getLookupTable(0,.95)#.0,2,512)#-6.25,.8,256)
        self.lut4c = self.cmap4.getLookupTable(0.2,.95)

        #same as sarndbox
        r5 = cmap_geo[::-1]
        pos5 = np.linspace(.0,1.08,len(r5)-1)+.15#(np.array([-40,-30,-20,-12.5,-.75,-.25,-.05,0,.05,.25,.75,12.5,20,30,40])+40) /80.
        pos5 = np.append(pos5,np.array([-1]))
        self.cmap5 = pg.ColorMap(pos5,r5)
        self.lut5 = self.cmap5.getLookupTable()
        self.lut5c = self.cmap5.getLookupTable(.05,1.05)


        #black
        r3 = np.array([[0,0,0,256],[255,255,255,178]])
        pos3 = [-1,0.]
        #pos3= np.append(pos3, np.array([np.nan]))
        self.cmap3 = pg.ColorMap(pos3, r3)
        self.lut3 = self.cmap3.getLookupTable(-1,0,2)

        self.luts = [self.lut, self.lut2, self.lut4, self.lut3,self.lut5]
        self.luts_base = [self.lutc, self.lut2c, self.lut4c, self.lut3,self.lut5c]
        self.imap = 0

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
            self.pdi_list.append(pg.PlotDataItem([], [], pen={'color':(255, 255, 255,x),'width':3})) #pen={'color':(230, 0, 230,x)
        
        self.view.addItem(self.img)
        for v in self.pdi_list:
            self.view.addItem(v)

        self.tracex = [0]; self.tracey = [0]
        self.pressed =False; self.moved = False
        self.xlow = 0; self.ylow = 0
        self.xhigh = 0; self.yhigh = 0
        self.view.mouseClickEvent = self.new_MouseClickEvent
        self.setMouseTracking(True)

    def _update_pos(self, x,y, color='w'):

        if len(x) < 1 and color != 'r':
            for i in range(len(self.pdi_list)):
                v = self.pdi_list[i]
                v.setData([], [])
        else:    
            self.x = x; self.y = y
            num_vals = 50 / len(self.pdi_list)
            self.pdi_list[0].setPen(color=(255, 255, 255,32),width=3)
            for i in range(len(self.pdi_list)):
                v = self.pdi_list[i]
                v.setData(x[i*num_vals:(i+1)*num_vals], y[i*num_vals:(i+1)*num_vals])
            if TRACE_BOOL and not self.parent().gravity_thread.idle:
                i=1
                self.tracex = np.append(x[i*num_vals:(i+1)*num_vals:5],self.tracex)[::]#np.append(x,self.tracex)[::5]
                self.tracey = np.append(y[i*num_vals:(i+1)*num_vals:5],self.tracey)[::]#np.append(y,self.tracey)[::5]
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
        
    def _update_bg(self, bg, stretch=False):
        self.data = np.rot90(bg,1)
        if self.imap == 3:
            self.data = np.zeros(bg.shape)-1.
            self.data = np.rot90(self.data)
 
        if TRACE_BOOL:
            if len(self.tracex) > 1:
                self.data[np.nan_to_num(self.tracex).astype(int),np.nan_to_num(self.tracey).astype(int)] = 0.


        self.img.setImage(self.data)

        if args.cont_on:
            self.mk_contours_thread.update_bg(bg)

    def set_cmap(self, imap):
        self.imap = imap
        if CONTOURS_ON:
            self.img.setLookupTable(self.luts[imap])
        else:
            self.img.setLookupTable(self.luts_base[imap])

    def mouseMoveEvent(self, e):
        #constrain the mouse cursor?
        pos = e.pos()
        print pos, 'cursor position, child'

        if self.pressed:
            self.moved = True
            pos= e.pos()
            self.current_pos = [(pos.x())/(self.xsize),(pos.y())/self.ysize]


    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
            pos = QMouseEvent.pos()

            if not self.pressed:
                self.pressed =True
                self.parent().pressed = True
                #print pos.x(), pos.y()
                self.start_pos = [(pos.x()-22)/1500., (pos.y()-10)/1140.]
                self.parent().start_pos = self.start_pos
                print pos.x(), pos.y(), 'click click mfer'
                self.parent().toggle_trace()
                self.emit(QtCore.SIGNAL('clear data'))

            elif self.pressed:
                self.pressed=False
                self.end_pos = [(pos.x()-22)/1500., (pos.y()-10)/1140.]
                print 'Trace bool value', TRACE_BOOL
                self.tracex= []; self.tracey=[]
                self.emit(QtCore.SIGNAL('clear data'),self.start_pos)
                #send a signal to parent with start and end positions
                self.emit(QtCore.SIGNAL('start_computation'), [self.start_pos, self.end_pos])
                
    def new_MouseClickEvent(self, e):
        if e.button() == QtCore.Qt.RightButton:
            e.accept()
    
class Settings(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Settings,self).__init__(parent)

        self.mainbox = QtGui.QWidget()
        #self.setCentralWidget(self.mainbox)
        self.setLayout(QtGui.QGridLayout())
        self.setCursor(QtCore.Qt.CrossCursor)
        #self.setMouseTracking(True)
        self.setGeometry(0,0,250,450)
        self.setFocus()

        self.boxes = []


        self.update_btn = QtGui.QPushButton('Update',self)
        self.update_btn.clicked.connect(self._update)
        self.update_btn.move(0,10)

        #             [lmargin, rmargin, tmargin, bmargin, x0,y0, xstretch, ystretch]
        self.params = [0,0,0,0,0,0,1280,960]

        self.lmargin_lbl = QtGui.QLabel(self)
        self.lmargin_lbl.setText('Left Margin (0)')
        self.lmargin_box = QtGui.QLineEdit(self)
        self.lmargin_lbl.move(0,50)
        self.lmargin_box.move(100,50)
        self.lmargin_box.setText(str(self.parent().lmargin))
        self.boxes.append(self.lmargin_box)

        self.rmargin_lbl = QtGui.QLabel(self)
        self.rmargin_lbl.setText('Right Margin (0)')
        self.rmargin_box = QtGui.QLineEdit(self)
        self.rmargin_lbl.move(0,50*2)
        self.rmargin_box.move(100,50*2)
        self.rmargin_box.setText(str(self.parent().rmargin))
        self.boxes.append(self.rmargin_box)

        self.tmargin_lbl = QtGui.QLabel(self)
        self.tmargin_lbl.setText('Top Margin (0)')
        self.tmargin_box = QtGui.QLineEdit(self)
        self.tmargin_lbl.move(0,50*3)
        self.tmargin_box.move(100,50*3)
        self.tmargin_box.setText(str(self.parent().tmargin))
        self.boxes.append(self.tmargin_box)

        self.bmargin_lbl = QtGui.QLabel(self)
        self.bmargin_lbl.setText('Bot. Margin (0)')
        self.bmargin_box = QtGui.QLineEdit(self)
        self.bmargin_lbl.move(0,50*4)
        self.bmargin_box.move(100,50*4)
        self.bmargin_box.setText(str(self.parent().bmargin))
        self.boxes.append(self.bmargin_box)

        self.xstart_lbl = QtGui.QLabel(self)
        self.xstart_lbl.setText('X Start (0)')
        self.xstart_box = QtGui.QLineEdit(self)
        self.xstart_lbl.move(0,50*5)
        self.xstart_box.move(100,50*5)
        self.xstart_box.setText(str(self.parent().xstart))
        self.boxes.append(self.xstart_box)

        self.ystart_lbl = QtGui.QLabel(self)
        self.ystart_lbl.setText('Y Start (0)')
        self.ystart_box = QtGui.QLineEdit(self)
        self.ystart_lbl.move(0,50*6)
        self.ystart_box.move(100,50*6)
        self.ystart_box.setText(str(self.parent().ystart))
        self.boxes.append(self.ystart_box)

        self.xspan_lbl = QtGui.QLabel(self)
        self.xspan_lbl.setText('X Span (0)')
        self.xspan_box = QtGui.QLineEdit(self)
        self.xspan_lbl.move(0,50*7)
        self.xspan_box.move(100,50*7)
        self.xspan_box.setText(str(self.parent().xspan))
        self.boxes.append(self.xspan_box)

        self.yspan_lbl = QtGui.QLabel(self)
        self.yspan_lbl.setText('Y Span (0)')
        self.yspan_box = QtGui.QLineEdit(self)
        self.yspan_lbl.move(0,50*8)
        self.yspan_box.move(100,50*8)
        self.yspan_box.setText(str(self.parent().yspan))
        self.boxes.append(self.yspan_box)

        self.setAutoFillBackground(True)

    def _update(self):
        for i in range(len(self.boxes)):
            b = self.boxes[i]
            t = b.text().toFloat()
            #print t
            self.params[i] = t[0]

        self.parent().lmargin,self.parent().rmargin,self.parent().tmargin,self.parent().bmargin,self.parent().xstart,self.parent().ystart,self.parent().xspan,self.parent().yspan = self.params
        self.parent().need_new =True


class PicButton(QtGui.QPushButton):
    def __init__(self,text, pixmap, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap
        self.text = text
        self.setText(self.text)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

class PicCheckButton(QtGui.QCheckBox):
    def __init__(self,text, pixmap0,pixmap1, parent=None):
        super(PicCheckButton, self).__init__(parent)
        self.pixmap0 = pixmap0
        self.pixmap1 = pixmap1
        self.text = text
        self.setText(self.text)
        self.setStyleSheet("QCheckBox::indicator:checked {image: url("+ self.pixmap1 +");}QCheckBox::indicator:unchecked{image: url(" +self.pixmap0 + ");}")
        self.pixmap = QtGui.QPixmap(self.pixmap0)


    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)


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
        self.setFocus()

        ###LAYOUT THE DSIPLAY ###
        self.bck=QtGui.QLabel(self)
        #self.bck.setPixmap(QtGui.QPixmap('./aux/starfield.png'))
        self.bck.setStyleSheet("background-color:  #1b1c1d ")
        self.bck.setGeometry(0,0,1920,1080)
        self.bck.setScaledContents(True)
        self.bck.setMinimumSize(1,1)
        self.bck.move(0,0)

        ### HELPER WIDGETS ####
        self.home = WelcomeScreen(self)
        self.home.move(0,0)
        self.about = AboutScreen(self)
        self.about.move(1920/2. -350,1080/2.-350)
        self.uiowa = UIowaScreen(self)
        self.uiowa.move(1920/2. -350,1080/2.-350)

        ### PLOTTING WIDGET(S) ####
        self.lmargin = 0; self.rmargin = 30; self.tmargin = -5; self.bmargin = 40;
        self.xstart = -40; self.ystart = -20; self.xspan = 1280; self.yspan = 860
        self.surface1 = Surface(self, aspectLock=False)#, lmargin=self.lmargin,rmargin=self.rmargin, tmargin=self.tmargin, bmargin=self.bmargin, xstart=self.xstart,ystart=self.ystart,xspan=self.xspan,yspan=self.yspan)#Surface(self)
        self.surface2 = Surface(self, aspectLock=False, lmargin=self.lmargin,rmargin=self.rmargin, tmargin=self.tmargin, bmargin=self.bmargin, xstart=self.xstart,ystart=self.ystart,xspan=self.xspan,yspan=self.yspan)#surface1
        self.surface1.move(390,-42)
        self.surface1.raise_()
        self.surface2.move(1920-30,-20)
        self.surface2.lower()
        self.need_new =False


        #### BUTTONS ######
        #self.trail_button = QtGui.QPushButton('Trail', self)
        #self.trail_button.setStyleSheet("background-image: url(" + './aux/assets' + "/trail_off.png);")
        self.trail_button = PicCheckButton('Trail', "./aux/assets/trail_off.png", "./aux/assets/trail_on.png",self)
        #self.trail_button.clicked.connect(self.start_trace)
        self.trail_button.stateChanged.connect(self.toggle_trace)
        #self.trail_button.setIcon(QtGui.QIcon("./aux/assets/trail_off.png"))
        #self.trail_button.setIconSize(QtCore.QSize(150,150))
        self.trail_button.setGeometry(0,0,250,100)
        self.trail_button.setStyleSheet('font-size:24px;')
        self.trail_button.move(80,360-50)

        #self.cmap_button = QtGui.QPushButton('ColorMap', self)
        self.cmap_button = PicButton('ColorMap', QtGui.QPixmap("./aux/assets/colormap.png"),self)
        self.menu = QtGui.QMenu()
        self.menu.addAction('Default', self.set_nocont)
        self.menu.addAction('Sauron', self.set_sauron)
        self.menu.addAction('Viridis', self.set_viridis)
        self.menu.addAction('Geology', self.set_geo)
        self.menu.addAction('Black', self.set_black)
        self.cmap_button.setMenu(self.menu)
        self.cmap_button.setStyleSheet('font-size:24px;')
        self.menu.setStyleSheet('font-size:24px;')
        self.cmap_button.setGeometry(0,0,250,100)
        self.cmap_button.move(80,180-50)

        #self.clear_button = QtGui.QPushButton('Reset', self)
        self.contour_toggle = PicCheckButton('Contour', "./aux/assets/contours_on.png", "./aux/assets/contours_off.png",self)
        #self.contour_toggle.clicked.connect(self.toggle_conts)
        self.contour_toggle.setChecked(True)
        self.contour_toggle.stateChanged.connect(self.toggle_conts)
        self.contour_toggle.setGeometry(0,0,250,100)
        self.contour_toggle.setStyleSheet('font-size:24px;')
        self.contour_toggle.move(80,360+180-50)

        #self.about_button = QtGui.QPushButton('About', self)
        self.about_button = PicButton('About', QtGui.QPixmap("./aux/assets/about.png"),self)
        self.about_button.clicked.connect(self.open_about)
        self.about_button.setGeometry(0,0,250,100)
        self.about_button.setStyleSheet('font-size:24px;')
        self.about_button.move(80,720-50)

        #self.sarndbox_button = QtGui.QPushButton('SARndbox', self)
        self.sarndbox_button = PicButton('Sarndbox', QtGui.QPixmap("./aux/assets/sarndbox.png"),self)
        self.sarndbox_button.clicked.connect(self.start_sarndbox)
        self.sarndbox_button.setGeometry(0,0,250,100)
        self.sarndbox_button.setStyleSheet('font-size:24px;')
        self.sarndbox_button.move(80,900-50)


        if args.calibrate:
            self.settings = Settings(self)
            self.settings.move(300,300)
            self.settings.raise_()
        

        self.pressed=False; self.moved=False  

        """
        Adjust margins to align stuff.
        Order is left, top, right, bottom. 
        """ 
        self.leftmargin = 240 ; self.topmargin = 30; self.rightmargin =240; self.bottommargin = 30
        self.setContentsMargins(self.leftmargin, self.topmargin, self.rightmargin, self.bottommargin)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        
        
        #start the computation thread
        self.gravity_thread = GravityThread()
        self.connect(self.gravity_thread, QtCore.SIGNAL('stage_data'), self.stage_data)
        self.gravity_thread.start()
        self.calc_idle = True

        self.connect(self.surface1, QtCore.SIGNAL('start_computation'), self.start_computation)
        self.connect(self.surface1, QtCore.SIGNAL('clear_data'), self.clear_data)       

        self.counter = 0
        self.fps = 0. 
        self.lastupdate = time.time()

        #initial values##
        self.x = []; self.y = []; self.data = []
        self.newx = []; self.newy = []; self.newbg = []
        self.xlow = 400; self.ylow = 100
        self.xhigh = 400+1280; self.yhigh = 100+960
        self.start_pos = []
        self.current_pos = []
        
        #### Start  #####################
        self.setMouseTracking(True)
        self.pp = QtGui.QCursor()
        self.start = time.time()
        self.home.raise_()
        self.about.lower()
        #self.home.close()
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
        self.surface1.set_cmap(3)
        self.surface2.set_cmap(3)
    def set_nocont(self):
        self.surface1.set_cmap(0)
        self.surface2.set_cmap(0)
    def set_sauron(self):
        self.surface1.set_cmap(2)
        self.surface2.set_cmap(2)
    def set_viridis(self):
        self.surface1.set_cmap(1)
        self.surface2.set_cmap(1)
    def set_geo(self):
        self.surface1.set_cmap(4)
        self.surface2.set_cmap(4)
    def toggle_conts(self):
        val = self.contour_toggle.isChecked()
        global CONTOURS_ON
        CONTOURS_ON = val
        self.surface1.set_cmap(self.surface1.imap)
        if CONTOURS_ON:
            self.contour_toggle.pixmap = QtGui.QPixmap(self.contour_toggle.pixmap0)
        else:
            self.contour_toggle.pixmap = QtGui.QPixmap(self.contour_toggle.pixmap1)

    def toggle_trace(self):
        val =self.trail_button.isChecked()
        global TRACE_BOOL
        TRACE_BOOL = val

        if TRACE_BOOL:
            self.tracex = []; self.tracey = []
            self.trail_button.pixmap = QtGui.QPixmap(self.trail_button.pixmap1)
        else:
            self.trail_button.pixmap = QtGui.QPixmap(self.trail_button.pixmap0)
            self.tracex = []; self.tracey = []
            global TRACE_LENGTH
            TRACE_LENGTH = 0

    def open_about(self):
        self.about.raise_()

        
    def start_sarndbox(self):
        print 'call whatever starts the sarndbox'
        #call('/home/gravbox/src/SARndbox-2.3/bin/SARndbox -uhm -fpv -rs 0.0&', shell=True)
        sys.exit(2)

    '''def start_trace(self):
                    global TRACE_BOOL
                    TRACE_BOOL = True
                    self.tracex = []; self.tracey = []
            
                def end_trace(self):
                    global TRACE_BOOL
                    TRACE_BOOL = False
                    self.tracex = []; self.tracey = []
                    self.gravity_thread.idle = True
                    self.surface1._update_pos([0],[0])
                    self.surface2._update_pos([0],[0])
                    self.x = []
                    self.y = []
                    global TRACE_LENGTH
                    TRACE_LENGTH = 0'''


    def mouseMoveEvent(self, e):
        #constrain the mouse cursor?
        pos = e.pos()
        if pos.x() > 1920:
            self.pp.setPos(1920,pos.y())

#will need to be rescaled

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
            

    def new_MouseClickEvent(self, e):
        if e.button() == QtCore.Qt.RightButton:
            e.accept()

    def start_computation(self, arr):
        self.start_pos = arr[0]; self.end_pos = arr[1]
        self.gravity_thread.read_input([self.start_pos[0],self.start_pos[1],self.end_pos[0],self.end_pos[1]],args.vel_scaling)
        self.mainbox.setCursor(QtCore.Qt.WaitCursor)
        self.surface1._update_pos([],[])
        self.surface2._update_pos([],[])
        x_scaled = self.newx* YWIDTH - 7
        self.x =  np.log( np.zeros(len(x_scaled))-1)
        self.y = np.copy(self.x)
        self.newx = []; self.newy = []
        self.counter = -1
        self.start = time.time()
        self.mainbox.setCursor(QtCore.Qt.CrossCursor)
        self.pressed = False; self.moved=False
        #self.tracex = []
        #self.tracey = []
        #global TRACE_LENGTH
        #TRACE_LENGTH = 0

    def clear_data(self):
        self.surface1._update_pos([0],[0])
        self.surface2._update_pos([0],[0])
        self.surface1.tracex = []; self.surface1.tracey = []
        #time.sleep(.5)
        self.x = []
        self.y = []
        global TRACE_LENGTH
        TRACE_LENGTH = 0
        self.pressed = True


        #self.surface1.close()
        #self.surface1 = Surface(self)
        #self.surface1.move(400,100)


    def stage_data(self, data):
        if len(self.newx) <1:
            self.counter = 0
        self.newx, self.newy, self.newbg, self.calc_idle = data
        #self.newy = self.newy+1

    def _update(self):
        if self.counter >= 0:

          if self.need_new:
            #self.surface1.close()
            self.surface2.setGeometry(1920+self.xstart,0+self.ystart, self.xspan, self.yspan)
            self.surface2.setContentsMargins(self.lmargin,self.tmargin, self.rmargin, self.bmargin)
            self.surface2.update()
            #self.surface1.raise_()
            self.update()
            self.need_new= False
          #print self.pp.pos().x()
          #print self.y; self.x
          if not self.pressed:
            self.surface1._update_pos(self.y[self.counter:self.counter + 50], self.x[self.counter:self.counter + 50])
            self.surface2._update_pos(self.y[self.counter:self.counter + 50], self.x[self.counter:self.counter + 50])

          if self.pressed:
            #print self.pp.pos(), 'this'
            #self.current_pos = [(self.pp.pos().x()-206)/float(1508.), (self.pp.pos().y())/float(1080.)]
            self.current_pos = [(self.pp.pos().x()-409)/float(1508.), (self.pp.pos().y())/float(1080.)]
            
            #print self.current_pos, self.start_pos

            self.surface1._update_pos([YWIDTH-self.start_pos[0]*YWIDTH,YWIDTH-self.current_pos[0]*YWIDTH],[self.start_pos[1]*XWIDTH,self.current_pos[1]*XWIDTH],color='r')
            self.surface2._update_pos([580*2-self.start_pos[0]*580*2,580-self.current_pos[0]*580],[self.start_pos[1]*410,self.current_pos[1]*410],color='r')

          QtCore.QTimer.singleShot(6.5, self._update)
          self.counter += 1
          
          #staggered loading of data
          if self.counter == len(self.newx)-50:
            x_scaled = self.newx* YWIDTH #- 7
            y_scaled = YWIDTH- (self.newy * XWIDTH) #- 12
            self.x = np.append(self.x, x_scaled)
            self.y = np.append(self.y, y_scaled)
            #print x_scaled[0], y_scaled[0]
            print 'updating'
          if self.counter == len(self.newx)-20:
            bg = self.newbg / scaling
            #bg[0,0] = 600
            #bg[0,1] = -5
            self.data = np.rot90(bg,1)
            self.surface1._update_bg(bg)
            self.surface2._update_bg(bg,stretch=True)
            
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
parser.add_argument("-b", "--calibrate", dest="calibrate", type=bool, default=False,help="Display calibration gui? Default False")


if __name__ == '__main__':
    args = parser.parse_args()
    app = QtGui.QApplication(sys.argv)
    thisapp = Display()
    thisapp.show()
    sys.exit(app.exec_())