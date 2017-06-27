import socket
import serial
import time

MAYA_ADDR = ('127.0.0.1', 1923)
ARDUINO_PORT = '/dev/ttyACM0'

if __name__ == '__main__':
    print('Welcome to the arduino-maya serial driver.')
    print('Press CTRL-C to exit.')
    print('')
    print('[INFO] Maya address: {0}:{1}'.format(*MAYA_ADDR))
    print('[INFO] Arduino port: {0}'.format(ARDUINO_PORT))

    mayaconn = None
    while mayaconn is None:
        try:
            mayaconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mayaconn.connect(MAYA_ADDR)
        except:
            mayaconn = None
            print('[ERROR] Maya connection refused.')
            print('[ERROR] (Maybe you didn\'t load the plugin in Maya?)')
            print('[INFO] Trying again in 5 seconds...')
            time.sleep(5)

    print('[INFO] Maya connection established.')

    arduinoconn = serial.Serial(ARDUINO_PORT)
    print('[INFO] Arduino connection established.')

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
    print('[INFO] Arduino connection closed.')

    mayaconn.close()
    print('[INFO] Maya connection closed.')
