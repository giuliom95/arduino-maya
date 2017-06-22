import socket
import serial

MAYA_ADDR = ('127.0.0.1', 1923)
ARDUINO_PORT = '/dev/ttyACM0'

if __name__ == '__main__':
    print('Welcome to the arduino-maya serial driver.')
    print('Maya address: {0}:{1}'.format(*MAYA_ADDR))
    print('Arduino port: {0}'.format(ARDUINO_PORT))

    mayaconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mayaconn.connect(MAYA_ADDR)
    print('Maya connection established.')

    arduinoconn = serial.Serial(ARDUINO_PORT)
    print('Arduino connection established.')

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
    print('Arduino connection closed.')

    mayaconn.close()
    print('Maya connection closed.')
