# gravity_sandbox
==================

Orbit Integration and Acceleration Calculation for Gravitational Simulation Sandbox
Version 1.0  --  December 2017

Written by Jacob Isbell, Sophie Deam, Jianbo Lu, and Tyler Stercula at the University of Iowa
Graphics made by Jeremy Swanson

#What is GravBox?
While gravitational interactions are the most important processes in astronomy, it is difficult to show them in the classroom. GravBox aims to remedy this by creating an interactive Augmented Reality (AR) tool for use in high-school and undergraduate astronomy classes. 

GravBox uses a Kinect camera to read a real sand topography and convert it into an acceleration field. A number of test particles can then be orbited through this field in real time, responding to changes in the sand surface. This allows students to gain a better intuition for the complex gravitational fields and mass distributions that fill the Universe. 

See our website for more information: TODO

Requirements
------------
#Hardware
- Kinect Camera
- Debian-based Linux PC (everything was tested and developed in Mint)
- Projector
- Sandbox

#Software
Everything was coded in Python 2.7. Eventually we aim to make it Python 3 compatible.

Packages:
- numpy
- scipy
- scikit-image
- libfreenect
- pyqtgraph


