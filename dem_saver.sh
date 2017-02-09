#! /bin/bash

# Create a function to call the BathymetrySaverTool
function Save {
            while true; do
            #        wmctrl finds running window with the name SARndbox
            wmctrl -a SARndbox;
            #        xdotool calls keystroke "B" in the SARndbox window,
            #        where B is the shortcut assigned to execute BathymetrySaverTool
            xdotool key “B”’;
            #        Wait 1 second before repeating
            sleep 1.0;
        done
}

# Call the Save function
Save
