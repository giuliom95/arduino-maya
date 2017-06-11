# Arduino-Maya communication suite
Software to make an Arduino board and a Maya session communicate.  
This can be particularly useful to create custom input devices.  
It is programmed in Python and Arduino language. It uses pySerial ([https://github.com/pyserial/pyserial](https://github.com/pyserial/pyserial)).

## Directory structure
This repository contains:
* A Maya Python API/PyMEL plugin
    ([src/maya-plugin](https://github.com/giuliom95/arduino-maya/tree/master/src/maya-plugin))
* A Python script to read the serial stream incoming from Arduino and feed it to Maya via socket connection
    ([src/driver](https://github.com/giuliom95/arduino-maya/tree/master/src/driver))
* An Arduino test sketch
    ([src/arduino](https://github.com/giuliom95/arduino-maya/tree/master/src/arduino))

## How to use this
### What do you need
* An Arduino board. _I've used an UNO v3. Other boards are ok. Just watch out for interrupt mappings_
* A three pin rotary encoder
* Jumper wires
* pySerial ([https://github.com/pyserial/pyserial](https://github.com/pyserial/pyserial))
* Maya. _I've used the 2017 v3 Student Edition. Other versions are fine_
### Quick Start
1. Connect the rotary encoder to the Arduino. Arduino UNO v3 pin mapping:  

| Rotary encoder pin | Arduino pin |
| ---                | ---         |
| `A`                | `D2`        |
| `B`                | `D8`        |
| `REF`              | `GND`       |
2. Flash the Arduino sketch to your board
3. Put the `src/maya-plugin/arduinomaya.py` plugin into the Maya `plug-ins` folder
4. Load the `arduinomaya.py` plugin within a Maya session
5. Create an `arduinoNode` and connect its `Output` attribute wherever you want.
6. Run the `src/driver/serial2maya.py` Python script
7. Enjoy

## How does this works
We got three entities: the Arduino board, the OS and the Maya session. We need to make them exchange messages:  
![System diagram](https://raw.githubusercontent.com/giuliom95/arduino-maya/master/docs/images/system_diagram.png)  
The Arduino board can communicate with the computer through a serial data stream via the USB cable and the OS can send commands to a Maya session through the `commandPort` socket built-in in Maya. So we need three software pieces: (1) the firmware on the Arduino board, (2) a "driver" that reads and feeds the serial stream to the `commandPort` socket and (3) a Maya plugin to provide an interface for external communication and to make the data available to its internal data structures.
### 1: The firmware
The Arduino firmware provided reads the pulses of a rotary encoder and outputs periodically the number of ticks that the encoder has done in that period. It uses the interrupts mapping of the Arduino UNO board.
### 2: The "bridge" program
It is a Python script that uses the `pySerial` lib for Arduino to PC serial communication and the `socket` module to send messages to Maya. It runs an endless loop that launches the MEL command defined in the Maya plugin passing as arguments the data coming through the serial port.
### 3: The Maya plugin
It adds to Maya a new DG node and a new MEL command.  
The DG node called `arduinoNode` has two visible float attributes: `Output` and `Multiplier`. The `Output` attribute must be connected to the node to control via Arduino (typically a transform or a rig component) while `Multiplier` manages the sensibility of the controls.  
The MEL command called `arduinoUpdateChannel` takes an integer as argument and modifies the `Output` attribute of the `arduinoNode` by adding to it the argument multiplied by the current value of the `Multiplier` attribute.

## To do
* Multiple channels support
* Make the `Value` attribute of `arduinoNode` set itself to the value of the plug which `Output` has been connected