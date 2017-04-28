import socket
import serial

MAYA_ADDR = ('127.0.0.1', 1923)
ARDUINO_PORT = '/dev/ttyACM0'

if __name__ == '__main__':
    mayaconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mayaconn.connect(MAYA_ADDR)
    arduinoconn = serial.Serial(ARDUINO_PORT)

    while True:
        delta = arduinoconn.readline().rstrip()
        try:
            int(delta)
        except:
            pass
        else:
            if delta != '0':
                cmd = 'arduinoUpdateChannel ' + delta
                mayaconn.send(cmd)

    arduinoconn.close()
    mayaconn.close()
