import sys
import maya.api.OpenMaya as OpenMaya
import pymel.core as pmc


class Channel():
    channel = ('', '')


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
        if len(args) != 2:
            raise AttributeError('Syntax: object name, object attribute')

        obj_name = args.asString(0)
        obj_attr = args.asString(1)

        try:
            obj = pmc.ls(obj_name)[0]
        except:
            raise AttributeError('No object called ' + obj_name)

        if not obj.hasAttr(obj_attr):
            raise AttributeError('No attribute of ' + obj_name + ' called ' + obj_attr)

        if type(obj.getAttr(obj_attr)) != float:
            raise AttributeError('Attribute ' + obj_attr + ' of ' + obj_name + ' is not a float.' )

        Channel.channel = (obj_name, obj_attr)


class UpdateChannelCommand(OpenMaya.MPxCommand):
    commandName = 'arduinoUpdateChannel'

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @staticmethod
    def commandCreator():
        return UpdateChannelCommand()

    def doIt(self, args):
        delta = args.asInt(0)
        obj_name, obj_attr = Channel.channel
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
        mplugin.deregisterCommand(UpdateChannelCommand.commandName)
    except:
        sys.stderr.write(
            'Failed to unregister command: ' + UpdateChannelCommand.commandName)
        raise
