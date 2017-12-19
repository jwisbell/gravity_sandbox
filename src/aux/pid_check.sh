#!/bin/bash
#if the plotting function stops, kill the calculation script
if ! pgrep -f 'python animate.py' > /dev/null
then 
	pgrep -f 'python gravbox.py' | xargs kill
fi
