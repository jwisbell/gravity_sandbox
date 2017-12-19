#!/bin/bash

if ! pgrep -f 'python animating_4.py' > /dev/null
then 
	pgrep -f 'python gravbox_2.py' | xargs kill
	echo 'Not running'
fi
