"""
GUI software for Gravbox, an Augmented Reality Gravitational Dynamics Simulation. 
This was developed at the University of Iowa by Jacob Isbell
    based on work in Dr. Fu's Introduction to Astrophysics class by Jacob Isbell, Sophie Deam, Jianbo Lu, and Tyler Stercula (beta version)
Version 1.0 - December 2017
"""
import sys
import time
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
from subprocess import call
from skimage import measure
from argparse import ArgumentParser

#custom scripts to import specific functions
import gravity_algorithm
import convolution
import topogra as topo
import mk_kernels


### --------- CONSTANTS --------- ###
scaling = 40 * 10 #scaling factor for representation of topography
YWIDTH = 580.# width of the plot for animation
XWIDTH = 410.# height of the plot for animation
y0 = 0# top boundary of plot
x0 = 186+18# left boundary of plot

#convolution kernels
X_KERNEL =  np.load('./aux/dx_dft.npy')
Y_KERNEL = np.load('./aux/dy_dft.npy') 
#toggles for tracing and contours
TRACE_BOOL = False
TRACE_LENGTH = 0
CONTOURS_ON = True
#colormaps
cmap_jet = np.load('./aux/cmap_jet.npy')
cmap_viridis = np.load('./aux/cmap_viridis.npy')
cmap_sauron = np.load('./aux/cmap_sauron.npy')
cmap_geo = np.load('./aux/cmap_geo.npy')


#I think this can be removed
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

"""Class containing the popup window with "about" information. Called from WelcomeScreen or Display. Not deleted on exit, just pushed to back. """
class AboutScreen(QtGui.QWidget):
     def __init__(self, parent=None):
        super(AboutScreen,self).__init__(parent)
        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        self.setLayout(QtGui.QGridLayout())

        self.setGeometry(0,0,900,700)

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

        self.uiowa_button = PicButton('UIowa',QtGui.QPixmap('./aux/assets/uiowa.png'),self)
        self.uiowa_button.setGeometry(0,0,125,50)
        self.uiowa_button.clicked.connect(self.open_uiowa)
        self.uiowa_button.move(425/2,600)

        self.aboutText.setAutoFillBackground(True)
        #set the font
        self.aboutText.setStyleSheet("background-color:  #1b1c1d;  color:#fcfcff;font-size:22px; QLabel {font-family:Droid Sans; font-size:22px; color: #fcfcff;} QPushbutton {font-family:Droid Sans; font-size:14px;}")

     def exit_about(self):
        #don't delete the element, hide it behind the others for fast loading and constant memory use
        self.lower()

     def open_uiowa(self):
        #open the uiowa popup window by placing it on top of this one. Send this window to the back.
        self.lower()
        self.parent().uiowa.raise_()

"""Class containing the popup window with information about the team. Called from WelcomeScreen or About. Not deleted on exit, just pushed to back. """
class UIowaScreen(QtGui.QWidget):
     def __init__(self, parent=None):
        super(UIowaScreen,self).__init__(parent)
        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
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

        self.uiowa_button = PicButton('UIowa',QtGui.QPixmap('./aux/assets/about.png'),self)
        self.uiowa_button.setGeometry(0,0,125,50)
        self.uiowa_button.clicked.connect(self.open_uiowa)
        self.uiowa_button.move(425/2,600)

        self.aboutText.setAutoFillBackground(True)

        #set the font
        self.aboutText.setStyleSheet("background-color:  #1b1c1d;  color:#fcfcff;font-size:22px; QLabel {font-family:Droid Sans; font-size:22px; color: #fcfcff;} QPushbutton {font-family:Droid Sans; font-size:14px;}")

     def exit_about(self):
        #don't delete the element, hide it behind the others for fast loading and constant memory use
        self.lower()

     def open_uiowa(self):
        #open the uiowa popup window by placing it on top of this one. Send this window to the back.
        self.lower()
        self.parent().about.raise_()

"""Upon initialization of Display element, place this 'splash' image on top. Approximate buttons by screen regions. 
If 'start your journey' region is clicked, simply hide this element in the back. If 'About' is clicked, hide this and raise the AboutScreen widget.
If 'UIowa' is clicked, hide this and raise UIowaScreen widget. Finally, when the program goes to idle mode place this back on top. """
class WelcomeScreen(QtGui.QWidget):
    def __init__(self, parent=None):
        super(WelcomeScreen,self).__init__(parent)
        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        self.setLayout(QtGui.QGridLayout())

        self.setGeometry(0,0,1920,1080)

        ###LAYOUT THE DSIPLAY ###
        self.bck=QtGui.QLabel(self)
        self.bck.setPixmap(QtGui.QPixmap('./aux/assets/homescreen.png')) #Created by Jeremy Swanson
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
        #define the regions that approximate buttons
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
        
                
""" 'Powerhouse' thread that handles updating topography and calls gravity_algorithm to calculate orbits using Verlet Integration. """
class GravityThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        #initial values
        self.current_pos = [0,0]
        self.current_vel = [0,0]
        self.previous_pos = np.copy(self.current_pos)
        self.previous_vel = np.copy(self.current_vel)
        self.in_pos = np.copy(self.previous_pos)
        self.in_vel = np.copy(self.previous_vel)
        self.baseplane,self.bounds = topo.ar_calibration()

        #update the kernel size for calibration settings, only if calibration flag is called
        if args.calibrate == True:
            print 'baseplane shape', self.baseplane.shape 
            mk_kernels.make(self.baseplane.shape[0],self.baseplane.shape[1])
        #save the previous topography in case there's too large a change in the values, then revert to previous topgraphy
        self.prev_dem = topo.update_surface(self.baseplane,self.bounds, None)
        #initially not doing calculation, this is 'idle' mode
        self.idle = True

    def __del__(self):
        self.wait()

    def differ(self,arr1, arr2):
        #function to see if input parameters vary from previous values
        #if return True, start a new orbit
        #if return False, continue old orbit
        for k in range(len(arr1)):
            if arr1[k] != arr2[k]:
                return True
        return False
    
    def run(self):
        #computation loop. Called immediately after __init__() to start thread

        last_idle = time.time() #time that idle mode ended, for use in checking elapsed time
        while True:
            start_loop = time.time()
            if not self.idle:
                # Load in surface
                scaled_dem_array = topo.update_surface(self.baseplane,self.bounds, self.prev_dem, verbose=True) 
                self.prev_dem = scaled_dem_array
                
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
                
                #normalize topography [0,1]
                scaled_dem_array = self.normalize_bg(scaled_dem_array)
                if CONTOURS_ON:
                    #contours are defined as negative values
                    scaled_dem_array = self.make_contours(scaled_dem_array)

                #send orbit data and topography to main thread for display and animation
                self.emit(QtCore.SIGNAL('stage_data'),[x, y, scaled_dem_array,self.idle])

                #update positions for next iteration, used to see if new orbit is necessary
                self.current_pos = [particle.pos[0], particle.pos[1]] 
                self.current_vel = [particle.vel[0], particle.vel[1]]
                
                try:
                    time.sleep(.93  - (time.time() - start_loop)) #sleep the amount of time to make each loop take 0.93 seconds
                except:
                    print ''

                dt = time.time()-start_loop
                print 'LOOP TOOK: ', dt

                #if idle_time has passed since last new input, start idle mode and raise welcome screen to top
                if time.time() - last_idle >= args.idle_time:
                    self.idle=True
                    #self.parent().WelcomeScreen.raise_()
            else:
                #IDLE MODE - only update topography 

                #check if there are new inputs from main thread
                input_pos, input_vel = self.in_pos, self.in_vel
                if self.differ(input_pos, self.previous_pos) or self.differ(input_vel, self.previous_vel):
                    self.idle = False
                    last_idle = time.time()
                    continue

                #update surface
                scaled_dem_array = topo.update_surface(self.baseplane, self.bounds,self.prev_dem,verbose=True)
                self.prev_dem = scaled_dem_array
                scaled_dem_array = self.normalize_bg(scaled_dem_array)

                if CONTOURS_ON:
                    scaled_dem_array = self.make_contours(scaled_dem_array)
                x = np.zeros(100)
                y = np.zeros(100)
                
                #send 'orbit' and surface to main thread for display
                self.emit(QtCore.SIGNAL('stage_data'),[x/scaled_dem_array.shape[1], y/scaled_dem_array.shape[0], scaled_dem_array, self.idle])
                
                time.sleep(0.93 - (time.time()-start_loop) ) #for consistent loop timing with calculation mode

    def read_input(self,inputs, vel_scaling,x_factor=580, y_factor=410):
        #convert the mouse positions from the main thread to (x,y) and (vx,vy)
        x_i, y_i, x_f, y_f = inputs #unpack 
        
        pos = np.array([y_i * y_factor, x_i * x_factor])    
        d_x = (x_f - x_i)*x_factor
        d_y = (y_f - y_i)*y_factor
        ang = np.arctan2(d_y,d_x)
        mag = np.sqrt(d_x**2 + d_y**2) * vel_scaling
        vel = np.array([np.sin(ang)*mag, np.cos(ang)*mag])
       
        self.in_pos = pos
        self.in_vel = vel

    def normalize_bg(self, bg):
        #set a consistent contrast range, sacrificing two pixels
        bg[0,0] = -600
        bg[0,1] = 15

        bg = (bg + 600) / 615. #normalize and make [0,1]
        return np.nan_to_num(bg)

    def make_contours(self, im, num_contours=7):
        #Function to add contour lines to surface plot

        #set the levels at which to calculate contours
        contour_levels = np.linspace(np.min(im)*.7, np.max(im)*.9,num_contours)
        contour_levels = np.append(contour_levels, np.median(im))

        #use scikit-image measurement tool to find pixel locations for contours
        for v in contour_levels:
            c = measure.find_contours(im, v)
            for n, contour in enumerate(c):
                contour = np.nan_to_num(contour).astype(int)
                im[contour[:,0], contour[:,1]] = -.5 #set to a negative value because colormaps define negative as contour lines
        return im



"""Widget for displaying the topography with or without contours and for animating the orbit of the test particle.
Called from Display. There are two of these widgets, one on the monitor display and one on the sand surface. """
class Surface(QtGui.QWidget):
    def __init__(self, parent=None, aspectLock=True, lmargin=0,rmargin=0, tmargin=20, bmargin=20, xstart=0,ystart=0,xspan=1160*4/3.,yspan=1160):
        super(Surface,self).__init__(parent)
        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        self.setLayout(QtGui.QGridLayout())
        self.setCursor(QtCore.Qt.CrossCursor)
        
        #create the plotting canvas and define its size
        self.canvas = pg.GraphicsLayoutWidget()
        self.layout().addWidget(self.canvas)
        self.view = self.canvas.addViewBox()
        self.view.setAspectLocked(aspectLock)
        self.view.setRange(xRange=[0,580],yRange=[0,410],padding=-1)
        self.view.setMouseEnabled(x=False,y=False)
        self.view.setBackgroundColor((.5,.5,.5,1.))
        self.xsize = float(xspan); self.ysize = float(yspan)

        #define the geometry of the entire widget
        self.setGeometry(0+xstart,0+ystart, xspan, yspan)  
        self.canvas.nextRow()
        self.setContentsMargins(lmargin,tmargin,rmargin,bmargin)

        #define all the colormaps. lut(N)c is the map without a contour
        r = cmap_jet[::-1]
        pos = np.linspace(0.,1.5,len(r)-1)
        pos= np.append(pos, np.array([-.00125]))
        self.cmap = pg.ColorMap(pos, r)
        self.lut = self.cmap.getLookupTable(-.001,1.6,512)
        self.lutc = self.cmap.getLookupTable(0.1,1.72,512)

        r2 = cmap_viridis[::-1]
        pos2 = np.linspace(-0.005,.9,len(r2)-1)
        pos2= np.append(pos2, np.array([-1]))
        self.cmap2 = pg.ColorMap(pos2, r2)
        self.lut2 = self.cmap2.getLookupTable(0,.85,512)
        self.lut2c = self.cmap2.getLookupTable(0.1,.95,512)

        r4 = cmap_sauron
        pos4 = np.linspace(0.05,.9,len(r4)-1)
        pos4= np.append(pos4, np.array([-1]))
        self.cmap4 = pg.ColorMap(pos4, r4)
        self.lut4 = self.cmap4.getLookupTable(0,.95)
        self.lut4c = self.cmap4.getLookupTable(0.2,.95)

        #same as sarndbox
        r5 = cmap_geo[::-1]
        pos5 = np.linspace(.0,1.08,len(r5)-1)+.15
        pos5 = np.append(pos5,np.array([-1]))
        self.cmap5 = pg.ColorMap(pos5,r5)
        self.lut5 = self.cmap5.getLookupTable()
        self.lut5c = self.cmap5.getLookupTable(.05,1.05)

        #black
        r3 = np.array([[0,0,0,256],[255,255,255,178]])
        pos3 = [-1,0.]
        self.cmap3 = pg.ColorMap(pos3, r3)
        self.lut3 = self.cmap3.getLookupTable(-1,0,2)

        self.luts = [self.lut, self.lut2, self.lut4, self.lut3,self.lut5]
        self.luts_base = [self.lutc, self.lut2c, self.lut4c, self.lut3,self.lut5c]
        self.imap = 0 #index of colormap for use in synching colors when contours are toggled

        #### Set  Initial Data  #####################
        self.start = time.time()
        self.y = []
        self.x = []
        self.newx = np.copy(self.x)
        self.newy = np.copy(self.y)
        self.j = 0
        self.tracex = [0]; self.tracey = [0]
        self.pressed =False; self.moved = False
        self.xlow = 0; self.ylow = 0
        self.xhigh = 0; self.yhigh = 0
        #  surface plot
        self.data = np.rot90(bg)
        self.newbg = np.copy(self.data)
        self.img = pg.ImageItem(border=None)
        self.img.setZValue(-100) #set image below animating scatter plot
        self.img.setLookupTable(self.lut)
        self.img.setImage(self.data)
        self.current_conts = []
        self.pdi_list = []

        #define the number of colors for animating trail gradient
        n_colors = 5
        grad = np.linspace(64,255,n_colors)
        for x in grad:
            self.pdi_list.append(pg.PlotDataItem([], [], pen={'color':(255, 255, 255,x),'width':3})) #pen={'color':(230, 0, 230,x)
        
        self.view.addItem(self.img)
        for v in self.pdi_list:
            self.view.addItem(v)

        #recursively enable mouse tracking across the plotting widgets
        self.view.mouseClickEvent = self.new_MouseClickEvent 
        self.setMouseTracking(True)

    def _update_pos(self, x,y, color='w'):
        #update the position of the animating particle

        #if there are no data, plot nothing
        if len(x) < 1 and color != 'r':
            for i in range(len(self.pdi_list)):
                v = self.pdi_list[i]
                v.setData([], [])
        else:    #otherwise plot the values evenly distributed among the trail gradient
            self.x = x; self.y = y
            num_vals = 50 / len(self.pdi_list) #define number of points per color
            self.pdi_list[0].setPen(color=(255, 255, 255,32),width=3)
            for i in range(len(self.pdi_list)):
                v = self.pdi_list[i]
                v.setData(x[i*num_vals:(i+1)*num_vals], y[i*num_vals:(i+1)*num_vals])
            #if trace is enabled, add the previous trail to existing trace (keeping only every 5th value)
            if TRACE_BOOL and not self.parent().gravity_thread.idle:
                i=1
                self.tracex = np.append(x[i*num_vals:(i+1)*num_vals:5],self.tracex)[::]#np.append(x,self.tracex)[::5]
                self.tracey = np.append(y[i*num_vals:(i+1)*num_vals:5],self.tracey)[::]#np.append(y,self.tracey)[::5]
                if len(self.tracex) > 10000:
                    self.tracex = self.tracex[:10000]
                    self.tracey = self.tracey[:10000]
            else: #if idle or trace turned off, clear the trace
                self.tracex = []
                self.tracey = []
        if color=='r': #color is defined as red when the mouse is clicked
            v = self.pdi_list[0]
            v.setPen(color='r',width=3)
            for i in range(len(self.pdi_list)):
                v = self.pdi_list[i]
                v.setData(x[i*num_vals:(i+1)*num_vals], y[i*num_vals:(i+1)*num_vals])
        
    def _update_bg(self, bg, stretch=False):
        #function to update the surface plot
        self.data = np.rot90(bg,1)

        #if the color is black, define all bg values as -1 because why complicate things
        if self.imap == 3:
            self.data = np.zeros(bg.shape)-1.
            self.data = np.rot90(self.data)
 
        if TRACE_BOOL:
            #if trace enabled (and trace values exist), set those pixels on the surface to a constant value
            if len(self.tracex) > 1:
                try:
                    self.data[np.nan_to_num(self.tracex).astype(int),np.nan_to_num(self.tracey).astype(int)] = 0.
                except:
                    print ''

        #once all modifications are done, set the plot data as the surface
        self.img.setImage(self.data)

    def set_cmap(self, imap):
        #function to set the colormap to a different value, imap is the index
        #0=default (jet), 1=viridis, 2=sauron, 3=black, 4=geology
        self.imap = imap
        #use the specific lookuptable for either contours on or off
        if CONTOURS_ON:
            self.img.setLookupTable(self.luts[imap])
        else:
            self.img.setLookupTable(self.luts_base[imap])

    def mouseMoveEvent(self, e):
        #if there has been a click inside the boundaries, track the mouse position
        pos = e.pos()

        if self.pressed:
            self.moved = True
            pos= e.pos()
            self.current_pos = [(pos.x())/(self.xsize),(pos.y())/self.ysize]


    def mousePressEvent(self, QMouseEvent):
        #track mouse clicks for user-input initial vectors
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
            pos = QMouseEvent.pos()

            if not self.pressed:
                #if there hasn't been a first click, set pressed to true and keep start position
                self.pressed =True
                self.parent().pressed = True
                self.start_pos = [(pos.x()-22)/1500., (pos.y()-10)/1140.]
                self.parent().start_pos = self.start_pos
                self.parent().toggle_trace()
                self.emit(QtCore.SIGNAL('clear data')) #clear the data so that only the mouse position, rather than the orbit, is displayed

            elif self.pressed:
                #if there's been a click, then this is the second click so keep the final position and start a new computation
                self.pressed=False
                self.end_pos = [(pos.x()-22)/1500., (pos.y()-10)/1140.]
                self.tracex= []; self.tracey=[]
                self.emit(QtCore.SIGNAL('clear data'),self.start_pos)
                #send a signal to parent with start and end positions
                self.emit(QtCore.SIGNAL('start_computation'), [self.start_pos, self.end_pos])
                
    def new_MouseClickEvent(self, e):
        if e.button() == QtCore.Qt.RightButton:
            e.accept()

"""Settings widget for fine-tuning of surface plot on sand. Only created by Display if args.calib flag is set to true. """    
class Settings(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Settings,self).__init__(parent)
        #create the GUI elements
        self.mainbox = QtGui.QWidget()
        self.setLayout(QtGui.QGridLayout())
        self.setCursor(QtCore.Qt.CrossCursor)
        self.setGeometry(0,0,250,450)
        self.setFocus()

        #list to hold all text-edit widgets
        self.boxes = []

        self.update_btn = QtGui.QPushButton('Update',self)
        self.update_btn.clicked.connect(self._update)
        self.update_btn.move(0,10)

        #[lmargin, rmargin, tmargin, bmargin, x0,y0, xstretch, ystretch]
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
        #if the update button has been clicked, change the parameters of Surface widget in Display and re-draw it
        for i in range(len(self.boxes)):
            b = self.boxes[i]
            t = b.text().toFloat()
            self.params[i] = t[0]

        self.parent().lmargin,self.parent().rmargin,self.parent().tmargin,self.parent().bmargin,self.parent().xstart,self.parent().ystart,self.parent().xspan,self.parent().yspan = self.params
        self.parent().need_new =True


"""Custom version of PushButton that uses our own assets as pixmaps """
class PicButton(QtGui.QPushButton):
    def __init__(self,text, pixmap, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap
        self.text = text
        self.setText(self.text)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

"""Custom version of CheckBox that uses our own assets as pixmaps """
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

"""Main widget that holds and organizes all other widgets (Surface, AboutScreen, UIowaScreen, Settings, WelcomeScreen) and 
all other threads (GravityThread). Called at the start of the program."""
class Display(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Display,self).__init__(parent)
        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        self.setLayout(QtGui.QGridLayout())
        self.setCursor(QtCore.Qt.CrossCursor)
        self.setMouseTracking(True)
        self.setGeometry(0,0,1920+1280,1080)
        self.setFocus()

        ###LAYOUT THE DSIPLAY ###
        self.bck=QtGui.QLabel(self)
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
        self.trail_button = PicCheckButton('Trail', "./aux/assets/trail_off.png", "./aux/assets/trail_on.png",self)
        self.trail_button.stateChanged.connect(self.toggle_trace)
        self.trail_button.setGeometry(0,0,250,100)
        self.trail_button.setStyleSheet('font-size:24px;')
        self.trail_button.move(80,360-50)

        self.cmap_button = PicButton('ColorMap', QtGui.QPixmap("./aux/assets/colormap.png"),self)
        self.menu = QtGui.QMenu()
        self.menu.addAction('Default', self.set_jet)
        self.menu.addAction('Sauron', self.set_sauron)
        self.menu.addAction('Viridis', self.set_viridis)
        self.menu.addAction('Geology', self.set_geo)
        self.menu.addAction('Black', self.set_black)
        self.cmap_button.setMenu(self.menu)
        self.cmap_button.setStyleSheet('font-size:24px;')
        self.menu.setStyleSheet('font-size:24px;')
        self.cmap_button.setGeometry(0,0,250,100)
        self.cmap_button.move(80,180-50)

        self.contour_toggle = PicCheckButton('Contour', "./aux/assets/contours_on.png", "./aux/assets/contours_off.png",self)
        self.contour_toggle.setChecked(True)
        self.contour_toggle.stateChanged.connect(self.toggle_conts)
        self.contour_toggle.setGeometry(0,0,250,100)
        self.contour_toggle.setStyleSheet('font-size:24px;')
        self.contour_toggle.move(80,360+180-50)

        self.about_button = PicButton('About', QtGui.QPixmap("./aux/assets/about.png"),self)
        self.about_button.clicked.connect(self.open_about)
        self.about_button.setGeometry(0,0,250,100)
        self.about_button.setStyleSheet('font-size:24px;')
        self.about_button.move(80,720-50)

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
        self._update()


    def keyPressEvent(self, e):
        #if user presses ESC, exit the software
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            sys.exit()
    

    def set_black(self): #set colormap to black
        self.surface1.set_cmap(3)
        self.surface2.set_cmap(3)
    def set_jet(self): #set colormap to jet (default)
        self.surface1.set_cmap(0)
        self.surface2.set_cmap(0)
    def set_sauron(self): #set colormap to sauron
        self.surface1.set_cmap(2)
        self.surface2.set_cmap(2)
    def set_viridis(self): #set colormap to viridis
        self.surface1.set_cmap(1)
        self.surface2.set_cmap(1)
    def set_geo(self): #set colormap to geology
        self.surface1.set_cmap(4)
        self.surface2.set_cmap(4)

    def toggle_conts(self): 
        #toggle the contours by switching CONTOURS_ON value
        val = self.contour_toggle.isChecked() #value of check box
        global CONTOURS_ON
        CONTOURS_ON = val
        self.surface1.set_cmap(self.surface1.imap)
        if CONTOURS_ON:
            self.contour_toggle.pixmap = QtGui.QPixmap(self.contour_toggle.pixmap0) #update checkbox image to have x
        else:
            self.contour_toggle.pixmap = QtGui.QPixmap(self.contour_toggle.pixmap1) #update checkbox image to be unchecked

    def toggle_trace(self):
        #toggle the trace by switching TRACE_BOOL
        val =self.trail_button.isChecked()
        global TRACE_BOOL
        TRACE_BOOL = val

        #clear the traces and update the button's image 
        if TRACE_BOOL:
            self.tracex = []; self.tracey = []
            self.trail_button.pixmap = QtGui.QPixmap(self.trail_button.pixmap1) #checked
        else:
            self.trail_button.pixmap = QtGui.QPixmap(self.trail_button.pixmap0) #unchecked
            self.tracex = []; self.tracey = []
            global TRACE_LENGTH
            TRACE_LENGTH = 0

    def open_about(self):
        #open the about screen
        self.about.raise_()

        
    def start_sarndbox(self):
        #exit with status 2, which tells the start_sandbox script to open the AR Sandbox
        sys.exit(2)

    def mouseMoveEvent(self, e):
        #track mouse position and constrain to the monitor window
        pos = e.pos()
        if pos.x() > 1920:
            self.pp.setPos(1920,pos.y())

    def setMouseTracking(self, flag):
        #recursively set the mouse tracking in all child widgets
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
        #function to send click positions to the gravity thread
        self.start_pos = arr[0]; self.end_pos = arr[1]
        self.gravity_thread.read_input([self.start_pos[0],self.start_pos[1],self.end_pos[0],self.end_pos[1]],args.vel_scaling)
        #set cursor to loading wheel
        self.mainbox.setCursor(QtCore.Qt.WaitCursor)
        #clear orbit positions
        self.surface1._update_pos([],[])
        self.surface2._update_pos([],[])
        #reset all x and y values
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
        #clear the orbit position data in the Surface widgets
        self.surface1._update_pos([0],[0])
        self.surface2._update_pos([0],[0])
        self.surface1.tracex = []; self.surface1.tracey = []
        #time.sleep(.5)
        self.x = []
        self.y = []
        global TRACE_LENGTH
        TRACE_LENGTH = 0
        self.pressed = True


    def stage_data(self, data):
        #the gravity thread sends the x, y, and surface data to this function to be set in the Display class variables for later use
        #in animating on the Surface widgets
        if len(self.newx) <1:
            self.counter = 0
        self.newx, self.newy, self.newbg, self.calc_idle = data
        

    def _update(self):
        #update the positions and surface of the orbit data
        if self.counter >= 0:

          if self.need_new:
            #need_new is True if Settings widget changes parameters of Surface widget, this creates a new one
            self.surface2.setGeometry(1920+self.xstart,0+self.ystart, self.xspan, self.yspan)
            self.surface2.setContentsMargins(self.lmargin,self.tmargin, self.rmargin, self.bmargin)
            self.surface2.update()
            self.update()
            self.need_new= False
          
          if not self.pressed:
            #if the user has not clicked to input a new initial vector, update the particle positions[i:i+50]
            # so that there is a trail behind the head of the particle. 
            self.surface1._update_pos(self.y[self.counter:self.counter + 50], self.x[self.counter:self.counter + 50])
            self.surface2._update_pos(self.y[self.counter:self.counter + 50], self.x[self.counter:self.counter + 50])

          if self.pressed:
            #if the user is inputting a new initial vector, plot a red line from start_pos to the current cursor location
            self.current_pos = [(self.pp.pos().x()-409)/float(1508.), (self.pp.pos().y())/float(1080.)]
            self.surface1._update_pos([YWIDTH-self.start_pos[0]*YWIDTH,YWIDTH-self.current_pos[0]*YWIDTH],[self.start_pos[1]*XWIDTH,self.current_pos[1]*XWIDTH],color='r')
            self.surface2._update_pos([580*2-self.start_pos[0]*580*2,580-self.current_pos[0]*580],[self.start_pos[1]*410,self.current_pos[1]*410],color='r')

          #repeat this function call every 6.5 ms
          QtCore.QTimer.singleShot(6.5, self._update)
          #increment through orbit locations
          self.counter += 1
          
          #staggered loading of data

          #if 50 points from end, append the new orbit positions to the current track
          #this makes x,y go to length 400
          if self.counter == len(self.newx)-50:
            x_scaled = self.newx* YWIDTH #- 7
            y_scaled = YWIDTH- (self.newy * XWIDTH) #- 12
            self.x = np.append(self.x, x_scaled)
            self.y = np.append(self.y, y_scaled)
            
          #if 20 points from end, update the background
          if self.counter == len(self.newx)-20:
            bg = self.newbg / scaling
            self.data = np.rot90(bg,1)
            self.surface1._update_bg(bg)
            self.surface2._update_bg(bg,stretch=True)
          
          #if we've gone through all the points in one orbit calculation, move on to the next orbit
          #this shrinks the x,y vectors back to 200 
          if self.counter >= len(self.newx):
            if TRACE_BOOL == False:
                self.tracex = []
                self.tracey = []
                global TRACE_LENGTH
                TRACE_LENGTH = 0
            #wait an amount of time so that animating is smooth and consistent
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
        #if there is no data, keep looping until the counter is changed
        else:
            QtCore.QTimer.singleShot(1, self._update) 

#define command-line flags 
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

#boilerplate code, initialize the Display widget and start the program
if __name__ == '__main__':
    args = parser.parse_args()
    app = QtGui.QApplication(sys.argv)
    thisapp = Display()
    thisapp.show()
    sys.exit(app.exec_())
