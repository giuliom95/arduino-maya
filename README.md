# Arduino-Maya communication suite

Software to make an Arduino board and a Maya session communicate.  
This can be particularly useful to create custom input devices.  

This repository contains:
* A Maya Python API/PyMEL plugin
    ([src/maya-plugin](tree/master/src/maya-plugin))
* A Python script to read the serial stream incoming from Arduino and feed it to Maya via socket connection
    ([src/driver](tree/master/src/driver))
* An Arduino test sketch
    ([src/arduino](tree/master/src/arduino))