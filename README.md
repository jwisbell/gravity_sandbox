# gravity_sandbox

Augmented Reality Gravitational Dynamics Sandbox - GravBox - Version 1.0  (December 2017)

Created at the University of Iowa

- Written by Jacob Isbell, Sophie Deam, Jianbo Lu, and Tyler Stercula 

- Graphics made by Jeremy Swanson and Jacob Isbell

- Hardware by Mason Reed, Ross McCurty, Sadie Moore, and Wyatt Bettis

- Supervised by Hai Fu

# What is GravBox?

While gravitational interactions are the most important processes in astronomy, it is difficult to show them in the classroom. GravBox aims to remedy this by creating an interactive Augmented Reality (AR) tool for use in high-school and undergraduate astronomy classes. 

GravBox uses a Kinect camera to read a real sand topography and convert it into an acceleration field. A number of test particles can then be orbited through this field in real time, responding to changes in the sand surface. This allows students to gain a better intuition for the complex gravitational fields and mass distributions that fill the Universe. 

See our website for more information: http://astro.physics.uiowa.edu/gravbox/

Requirements
------------
# Hardware
- Kinect Camera
- Debian-based Linux PC (everything was tested and developed in Mint)
- Projector
- Sandbox

# Software

Everything was coded in Python 2.7. Eventually we aim to make it Python 3 compatible.

Packages:
- numpy
- scipy
- scikit-image
- libfreenect
- pyqtgraph
- pyfftw (Optional)
- libusb

It may be useful (and FUN!) to install the AR Sandbox created at UC Davis (https://arsandbox.ucdavis.edu/)


