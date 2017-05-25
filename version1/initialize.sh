#! /bin/bash

# Start Sandbox
/home/gravity/src/SARndbox-2.2/bin/SARndbox -uhm -rs 0.0&
#/home/gravity/src/SARndbox-2.2/bin/SARndbox -uhm -fpv -rer 20 100 &

sleep 1.0;
# Make Sandbox active window
wmctrl -R SARndbox;

# Make Sandbox window fullscreen
xdotool key "F11";


xdotool keydown "B";
sleep 1;
xdotool mousemove_relative 0 140; #140;
xdotool mousemove_relative -- -32 0;
sleep 1;
#xdotool click 1;
xdotool keyup "B";

#-ws 0.0 0 
#-rer 20 100
