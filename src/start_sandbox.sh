#/bin/bash

LOOP=1

while [ $LOOP -gt 0 ]; do
    echo Starting GravBox...
    LOOP=0
    python gravbox.py #start with default settings
    rc=$?
    if [ $rc -eq 2 ]; then
        #start sarndbox
        echo Starting SARndbox...
        /home/gravbox/src/SARndbox-2.3/bin/SARndbox -uhm -fpv -rs 0.0
        LOOP=1
    fi
done