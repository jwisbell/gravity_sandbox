"""
Software to load FFTW wisdoms for Gravbox, an Augmented Reality Gravitational Dynamics Simulation. 
Currently NOT IN USE, but leaving in case user wants to enable FFTW mode in convolution.py
I DO NOT GUARANTEE THE EFFICACY OF THIS SCRIPT -- DEPRECATED

This was developed at the University of Iowa by Jacob Isbell
    based on work in Dr. Fu's Introduction to Astrophysics class by Jacob Isbell, Sophie Deam, Jianbo Lu, and Tyler Stercula (beta version)
Version 1.0 - December 2017
"""

import string

#load the fftw plan
def load_wisdom():
    f = open('forward_plan.txt','r')
    plan = ''
    for l in f.readlines():
        plan = plan+l
    return plan

#parse the fftw plan and return 
def read_wisdom(fname):
    f = open(fname+'_0.txt')
    lines = f.readlines()
    part1 = '' 
    for l in lines:
        part1 = part1+l
    f.close()
    
    f = open(fname+'_1.txt')
    lines = f.readlines()
    part2 ='' 
    for l in lines:
        part2 = part2+l
    f.close()
   
    f = open(fname+'_2.txt')
    lines = f.readlines()
    part3 = '' 
    for l in lines:
        part3 = part3+l
    f.close()

    return [part1,part2,part3]


