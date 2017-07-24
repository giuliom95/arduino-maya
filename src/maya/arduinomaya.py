import sys
import maya.api.OpenMaya as OpenMaya
import pymel.core as pmc

# GUI imports
from maya import OpenMayaUI as omui
from PySide2 import QtCore, QtGui, QtWidgets
from shiboken2 import wrapInstance
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

CHANNELS_NUM = 3
CHANNEL_MAX = 1023.


class Channels():
    channels = [{}]*CHANNELS_NUM


def maya_useNewAPI():
    '''
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    '''
    pass


##########################################################
# Commands Classes definitions
##########################################################

class ConnectAttributeCommand(OpenMaya.MPxCommand):
    commandName = 'arduinoConnectAttribute'

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @staticmethod
    def commandCreator():
        return ConnectAttributeCommand()

    def doIt(self, args):
        syntax = 'Syntax: <channel> <object name> <object attribute> <min value> <max value>'
        if len(args) != 5:
            raise RuntimeError('Wrong arguments number. ' + syntax)

        try:
            channel = args.asInt(0)
            objName = args.asString(1)
            objAttr = args.asString(2)
            minVal = args.asFloat(3)
            maxVal = args.asInt(4)
        except:
            raise RuntimeError('Invalid arguments. ' + syntax)

        if channel > CHANNELS_NUM or channel < 0:
            raise RuntimeError('Invalid channel number. ' + syntax)

        try:
            obj = pmc.ls(objName)[0]
        except:
            raise RuntimeError('No object called ' + objName)

        if not obj.hasAttr(objAttr):
            raise RuntimeError('No attribute of ' + objName + ' called ' + objAttr)

        if type(obj.getAttr(objAttr)) != float:
            raise RuntimeError('Attribute ' + objAttr + ' of ' + objName + ' is not a float.')

        Channels.channels[channel] = {'obj': objName, 'attr': objAttr, 'min': minVal, 'max': maxVal}


class ConnectTimeCommand(OpenMaya.MPxCommand):
    commandName = 'arduinoConnectTime'

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @staticmethod
    def commandCreator():
        return ConnectTimeCommand()

    def doIt(self, args):
        syntax = 'Syntax: channel.'
        if len(args) != 1:
            raise RuntimeError('Wrong arguments number. ' + syntax)

        try:
            channel = args.asInt(0)
        except:
            raise RuntimeError('Invalid channel. ' + syntax)

        if channel > CHANNELS_NUM or channel < 0:
            raise RuntimeError('Invalid channel number. ' + syntax)

        Channels.channels[channel] = 'time'


class UpdateChannelCommand(OpenMaya.MPxCommand):
    commandName = 'arduinoUpdateChannel'

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @staticmethod
    def commandCreator():
        return UpdateChannelCommand()

    def doIt(self, args):
        channel = args.asInt(0)

        try:
            value = args.asInt(1)
        except TypeError:
            # We ignore broken data incoming from the driver
            pass

        if Channels.channels[channel] == 'time':
            newT = pmc.currentTime() + value
            pmc.currentTime(newT)
        else:
            try:
                ch = Channels.channels[channel]
                objName = ch['obj']
                objAttr = ch['attr']
                if objName == '':
                    return
                obj = pmc.ls(objName)[0]
                newValue = (ch['max']-ch['min'])*(value / CHANNEL_MAX) + ch['min']
                obj.setAttr(objAttr, newValue)
            except KeyError:
                # This should happen only if channel has not been set up
                pass


class GUIControlsCommand(OpenMaya.MPxCommand):
    commandName = 'arduinoGUI'
    syntax = 'Syntax: ' + commandName + ' <command>'

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)
        self.window = Window()

    @staticmethod
    def commandCreator():
        return GUIControlsCommand()

    def doIt(self, args):
        syntax = GUIControlsCommand.syntax
        if len(args) != 1:
            raise RuntimeError('Wrong arguments number. ' + syntax)

        cmd = args.asString(0)
        if cmd == 'show':
            self.window.show()
        else:
            raise RuntimeError('Command not recognized.')


##########################################################
# Plug-in initialization.
##########################################################
def initializePlugin(mobject):
    pmc.commandPort(n=':1923')

    mplugin = OpenMaya.MFnPlugin(mobject)

    try:
        mplugin.registerCommand(
            ConnectAttributeCommand.commandName,
            ConnectAttributeCommand.commandCreator
        )
    except:
        sys.stderr.write(
            'Failed to register command: ' + ConnectAttributeCommand.commandName)
        raise

    try:
        mplugin.registerCommand(
            ConnectTimeCommand.commandName,
            ConnectTimeCommand.commandCreator
        )
    except:
        sys.stderr.write(
            'Failed to register command: ' + ConnectTimeCommand.commandName)
        raise

    try:
        mplugin.registerCommand(
            UpdateChannelCommand.commandName,
            UpdateChannelCommand.commandCreator
        )
    except:
        sys.stderr.write(
            'Failed to register command: ' + UpdateChannelCommand.commandName)
        raise

    try:
        mplugin.registerCommand(
            GUIControlsCommand.commandName,
            GUIControlsCommand.commandCreator
        )
    except:
        sys.stderr.write(
            'Failed to register command: ' + GUIControlsCommand.commandName)
        raise


def uninitializePlugin(mobject):
    pmc.commandPort(n=':1923', cl=True)

    mplugin = OpenMaya.MFnPlugin(mobject)

    try:
        mplugin.deregisterCommand(ConnectAttributeCommand.commandName)
    except:
        sys.stderr.write(
            'Failed to unregister command: ' + ConnectAttributeCommand.commandName)
        raise

    try:
        mplugin.deregisterCommand(ConnectTimeCommand.commandName)
    except:
        sys.stderr.write(
            'Failed to unregister command: ' + ConnectTimeCommand.commandName)
        raise

    try:
        mplugin.deregisterCommand(UpdateChannelCommand.commandName)
    except:
        sys.stderr.write(
            'Failed to unregister command: ' + UpdateChannelCommand.commandName)
        raise

    try:
        mplugin.deregisterCommand(GUIControlsCommand.commandName)
    except:
        sys.stderr.write(
            'Failed to unregister command: ' + GUIControlsCommand.commandName)
        raise


##########################################################
# GUI
##########################################################

def getMayaWindow():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtWidgets.QWidget)


class Window(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        self.setParent(getMayaWindow())
        self.setWindowFlags(QtCore.Qt.Window)

        self.setObjectName('arduinoMaya_GUI') 
        self.setWindowTitle('Arduino Maya')

        self.initUI()

    def initUI(self):
        vLayout = QtWidgets.QVBoxLayout(self)
        vLayout.setSpacing(0)
        vLayout.setContentsMargins(0, 0, 0, 0)

        upperLayout = QtWidgets.QHBoxLayout(self)
        upperLayout.setSpacing(0)

        self.objLabel = QtWidgets.QLabel('Nothing selected')
        self.objLabel.setIndent(11)
        upperLayout.addWidget(self.objLabel)

        reloadBtn = QtWidgets.QPushButton('Reload')
        reloadBtn.clicked.connect(self.reloadClicked)
        upperLayout.addWidget(reloadBtn)

        vLayout.addLayout(upperLayout)

        self.attrList = QtWidgets.QListWidget()
        vLayout.addWidget(self.attrList)

        self.chLabels = [None]*CHANNELS_NUM
        self.minLine = [None]*CHANNELS_NUM
        self.maxLine = [None]*CHANNELS_NUM
        for i in range(CHANNELS_NUM):
            self.chLabels[i] = QtWidgets.QLabel('Channel #{0}'.format(i+1))
            self.chLabels[i].setContentsMargins(11, 0, 11, 0)

            self.minLine[i] = QtWidgets.QLineEdit()
            self.minLine[i].setPlaceholderText('Min')
            self.minLine[i].setFixedWidth(50)

            self.maxLine[i] = QtWidgets.QLineEdit()
            self.maxLine[i].setPlaceholderText('Max')
            self.maxLine[i].setFixedWidth(50)

            connectBtn = QtWidgets.QPushButton('Connect')
            connectBtn.setFixedWidth(70)

            row = QtWidgets.QHBoxLayout(self)
            row.addWidget(self.chLabels[i])
            row.addWidget(self.minLine[i])
            row.addWidget(self.maxLine[i])
            row.addWidget(connectBtn)
            vLayout.addLayout(row)

        self.setLayout(vLayout)
