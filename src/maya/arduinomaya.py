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
    channels = [None]*CHANNELS_NUM


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
            return

        ch = Channels.channels[channel]

        if ch == 'time':
            newT = pmc.currentTime() + value
            pmc.currentTime(newT)
        elif ch is not None:
            ch = Channels.channels[channel]
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
        self.updateValues()

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
        reloadBtn.clicked.connect(self.updateValues)
        upperLayout.addWidget(reloadBtn)

        vLayout.addLayout(upperLayout)

        self.attrList = QtWidgets.QListWidget()
        vLayout.addWidget(self.attrList)

        self.chLabels = [None]*CHANNELS_NUM
        self.minLine = [None]*CHANNELS_NUM
        self.maxLine = [None]*CHANNELS_NUM
        for c in range(CHANNELS_NUM):
            # This will display 'ERROR' only if Window.updateValues() fails
            self.chLabels[c] = QtWidgets.QLabel('ERROR')
            self.chLabels[c].setContentsMargins(11, 0, 11, 0)

            self.minLine[c] = QtWidgets.QLineEdit()
            self.minLine[c].setValidator(QtGui.QDoubleValidator())
            self.minLine[c].setPlaceholderText('Min')
            self.minLine[c].setFixedWidth(50)

            self.maxLine[c] = QtWidgets.QLineEdit()
            self.maxLine[c].setValidator(QtGui.QDoubleValidator())
            self.maxLine[c].setPlaceholderText('Max')
            self.maxLine[c].setFixedWidth(50)

            connectBtn = QtWidgets.QPushButton('Connect channel #{0}'.format(c))
            connectBtn.clicked.connect(self.channelBtnClicked(c))
            connectBtn.setFixedWidth(120)

            row = QtWidgets.QHBoxLayout(self)
            row.addWidget(self.chLabels[c])
            row.addWidget(self.minLine[c])
            row.addWidget(self.maxLine[c])
            row.addWidget(connectBtn)
            vLayout.addLayout(row)

        self.setLayout(vLayout)

    def getAttrList(self):
        attr_names = []
        selection = pmc.ls(sl=True)
        if len(selection) > 0:
            obj = selection[0]
            self.objLabel.setText(str(obj))
            attrs = obj.listAttr(c=True, s=True, se=True, v=True, r=True, w=True, u=True, k=True)
            attr_names = [a.attrName(longName=True) for a in attrs]
            attr_names.sort()
        return attr_names

    def channelBtnClicked(self, channel):
        def cbc():
            minVal = float(self.minLine[channel].text())
            maxVal = float(self.maxLine[channel].text())
            attr = self.attrList.selectedItems()[0].text()
            obj = self.objLabel.text()
            pmc.arduinoConnectAttribute(channel, obj, attr, minVal, maxVal)
            self.updateValues()

        return cbc

    def updateValues(self):
        self.attrList.clear()
        self.objLabel.setText('Nothing selected')
        self.attrList.addItems(self.getAttrList())

        for c in range(CHANNELS_NUM):
            minVal = maxVal = ''
            assignedVal = 'Not assigned'

            ch = Channels.channels[c]
            if ch is not None:
                minVal = str(ch['min'])
                maxVal = str(ch['max'])
                assignedVal = ch['obj'] + '.' + ch['attr']

            self.chLabels[c].setText(assignedVal)
            self.minLine[c].setText(minVal)
            self.maxLine[c].setText(maxVal)
