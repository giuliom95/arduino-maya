import sys
import maya.api.OpenMaya as OpenMaya
import pymel.core as pmc

# GUI imports
from maya import OpenMayaUI as omui
from PySide2 import QtCore, QtGui, QtWidgets
from shiboken2 import wrapInstance

CHANNELS_NUM = 3
CHANNEL_MAX = 1023.

class Channel():
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
        syntax = 'Syntax: <channel>, <object name>, <object attribute>, <min value>, <max value>'
        if len(args) != 5:
            raise ValueError('Wrong arguments number. ' + syntax)

        try:
            channel = args.asInt(0)
            objName = args.asString(1)
            objAttr = args.asString(2)
            minVal = args.asFloat(3)
            maxVal = args.asInt(4)
        except:
            raise ValueError('Invalid arguments. ' + syntax)

        if channel > CHANNELS_NUM or channel < 0:
            raise ValueError('Invalid channel number. ' + syntax)

        try:
            obj = pmc.ls(objName)[0]
        except:
            raise ValueError('No object called ' + objName)

        if not obj.hasAttr(objAttr):
            raise ValueError('No attribute of ' + objName + ' called ' + objAttr)

        if type(obj.getAttr(objAttr)) != float:
            raise ValueError('Attribute ' + objAttr + ' of ' + objName + ' is not a float.')

        Channel.channels[channel] = {'obj': objName, 'attr': objAttr, 'min': minVal, 'max': maxVal}

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
            raise ValueError('Wrong arguments number. ' + syntax)

        try:
            channel = args.asInt(0)
        except:
            raise ValueError('Invalid channel. ' + syntax)

        if channel > CHANNELS_NUM or channel < 0:
            raise ValueError('Invalid channel number. ' + syntax)

        Channel.channels[channel] = 'time'


class UpdateChannelCommand(OpenMaya.MPxCommand):
    commandName = 'arduinoUpdateChannel'

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @staticmethod
    def commandCreator():
        return UpdateChannelCommand()

    def doIt(self, args):
        channel = args.asInt(0)
        value = args.asInt(1)

        if Channel.channels[channel] == 'time':
            newT = pmc.currentTime() + value
            pmc.currentTime(newT)
        else:
            ch = Channel.channels[channel]
            objName = ch['obj']
            objAttr = ch['attr']
            if objName == '':
                return
            obj = pmc.ls(objName)[0]
            newValue = (ch['max']-ch['min'])*(value / CHANNEL_MAX) + ch['min']
            obj.setAttr(objAttr, newValue)


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
            raise ValueError('Wrong arguments number. ' + syntax)

        cmd = args.asString(0)
        if cmd == 'show':
            self.window.show()
        else:
            raise ValueError('Command not recognized.')


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


class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=getMayaWindow()):
        super(Window, self).__init__(parent)
