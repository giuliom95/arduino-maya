import sys
import maya.api.OpenMaya as OpenMaya
import pymel.core as pmc

CHANNELS_NUM = 2


class Channel():
    channels = [('', '')]*CHANNELS_NUM


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
        syntax = 'Syntax: channel, object name, object attribute'
        if len(args) != 3:
            raise ValueError('Wrong arguments number. ' + syntax)

        try:
            channel = args.asInt(0)
            obj_name = args.asString(1)
            obj_attr = args.asString(2)
        except:
            raise ValueError('Invalid arguments. ' + syntax)

        if channel > CHANNELS_NUM or channel < 0:
            raise ValueError('Invalid channel number. ' + syntax)

        try:
            obj = pmc.ls(obj_name)[0]
        except:
            raise ValueError('No object called ' + obj_name)

        if not obj.hasAttr(obj_attr):
            raise ValueError('No attribute of ' + obj_name + ' called ' + obj_attr)

        if type(obj.getAttr(obj_attr)) != float:
            raise ValueError('Attribute ' + obj_attr + ' of ' + obj_name + ' is not a float.' )

        Channel.channels[channel] = (obj_name, obj_attr)


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
        delta = args.asInt(1)
        if Channel.channels[channel] == 'time':
            new_t = pmc.currentTime() + delta
            pmc.currentTime(new_t)
        else:
            obj_name, obj_attr = Channel.channels[channel]
            if obj_name == '':
                return
            obj = pmc.ls(obj_name)[0]
            value = obj.getAttr(obj_attr)
            value += delta
            obj.setAttr(obj_attr, value)


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
