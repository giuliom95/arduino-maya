# Arduino-Maya communication suite
Software to make an Arduino board and a Maya session communicate.  
This can be particularly useful to create custom input devices.  
It is programmed in Python and Arduino language. It uses pySerial ([https://github.com/pyserial/pyserial](https://github.com/pyserial/pyserial)).  
See it working on [my twitter](https://twitter.com/giuliom_95/status/918938709814398976)
and on my [July 2017 reel](https://vimeo.com/giuliom95/reeljul2017#t=17s).

## Directory structure
This repository contains:
* A Maya Python API/PyMEL plugin
    ([src/maya](https://github.com/giuliom95/arduino-maya/tree/master/src/maya))
* A Python script to read the serial stream incoming from Arduino and feed it to Maya via socket connection
    ([src/driver](https://github.com/giuliom95/arduino-maya/tree/master/src/driver))
* An Arduino test firmware
    ([src/arduino](https://github.com/giuliom95/arduino-maya/tree/master/src/arduino))

## How to use this
### What do you need 
* An Arduino board. _I've used an UNO v3. Other boards are ok. Just watch out for interrupt mappings_
* Three potentiometers. _I recommend sliders. But the choice is yours_
* Jumper wires
* pySerial ([https://github.com/pyserial/pyserial](https://github.com/pyserial/pyserial))
* Maya. _I've used the 2017 v3 Student Edition. Not too old versions are fine too_
### Quick Start
1. Follow this circuit diagram to make the connections:  
![Circuit diagram](https://cdn.rawgit.com/giuliom95/arduino-maya/master/docs/images/circuit.svg)
2. Flash the Arduino sketch `src/arduino/firmware.ino` to your board.
3. Put the `src/maya-plugin/arduinomaya.py` plugin into the Maya `plug-ins` folder.
4. Load the `arduinomaya.py` plugin within a Maya session.
5. Start the `src/driver/serial2maya.py` script.
5. Connect the three available channels using the GUI that can be brought up with the `arduinoGUI` command.
6. Enjoy.

## How does this works
Here an approximate system diagram:  
![System diagram](https://cdn.rawgit.com/giuliom95/arduino-maya/master/docs/images/system.svg)  
The data flow is pretty simple. The potentiometers generate analog signals. The Arduino board converts them with its ADC and sends them through serial connection to the computer where Maya is running. Here the signals are translated into Maya commands and are feeded to the Maya session through its `commandPort` socket.
Finally, Maya must understand them and modify the current scene.

To make this work, three software pieces are needed: the Arduino firmware, the "Serial to Maya" driver, and a Maya plugin. Here the details for each piece.

### 1: The firmware
The provided Arduino firmware reads the three analog signals that comes into `A0`,`A1`, and `A2` ports. Every ~30ms it puts the delta value for each port in to the Serial outgoing stream.
### 2: The "bridge" program
It is a Python script that uses the `pySerial` lib for Arduino to PC serial communication and the `socket` module to send messages to Maya. It runs an endless loop that launches the MEL command defined in the Maya plugin.
### 3: The Maya plugin
The plugin adds four commands. Usually the user should invoke only `arduinoGUI`.
* `arduinoGUI`: Brings up the GUI.
* `arduinoConnectAttribute <channel> <object> <attribute>`: This connects the `channel` to the `attribute` of the given `object`. The `attribute` must be a float attribute. **Example:** `arduinoConnectAttribute 0 pCube1 rotateX` this connects the first channel (or potentiometer if you are using the firmware provided here) to the attribute `rotateX` of the `pCube1` object.
* `arduinoConnectTime <channel>`: This connects `channel` to the time slider.
* `arduinoUpdateChannel <channel> <delta>`: Adds `delta` to the attribute connected to `channel`.
