#! /bin/bash

# Start Sandbox
#./bin/SARndbox -uhm -fpv -rer 20 100

# Make Sandbox active window
wmctrl -a SARndbox;

# Make Sandbox window fullscreen
xdotool key "F11";
					

function Get_images {
			   #while true; do
						# Make Sandbox active window
               		wmctrl -a SARndbox;

						# Take screenshot 
					xwd -name SARndbox | convert xwd:- '/home/gravity/Desktop/color_field.jpg' ;

						# Remove the original color map file from tablet in order to send updated image (doesn't update automatically)
						# Note: this loop will continue to run even if the tablet is not connected, i.e. even if there is 'device not found' error
					adb shell rm /storage/emulated/0/field.jpg

						# Push color map to tablet
					adb push /home/gravity/Desktop/color_field.jpg /storage/emulated/0/field.jpg;

						# Save dem file
               		xdotool key "B";

						# Wait 2 seconds before repeating
					#sleep 2.0;


						# If Sandbox stops running, break out of loop
					#if ! pgrep -x "SARndbox" > /dev/null
					#then 
						#break
					#fi;

			   done
}

Get_images
