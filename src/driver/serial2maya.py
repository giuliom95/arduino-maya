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
        deltas = arduinoconn.readline().split()
        for i, d in enumerate(deltas):
            try:
                int(d)
            except:
                pass
            else:
                if d != '0':
                    cmd = 'arduinoUpdateChannel ' + str(i) + ' ' + d
                    mayaconn.send(cmd)

    arduinoconn.close()
    print('Arduino connection closed.')

    mayaconn.close()
    print('Maya connection closed.')
