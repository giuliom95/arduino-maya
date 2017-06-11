import sys
import maya.api.OpenMaya as OpenMaya
import pymel.core as pmc


def maya_useNewAPI():
    '''
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    '''
    pass


##########################################################
# Node Class definition
##########################################################
class NodeClass(OpenMaya.MPxNode):
    nodeName = 'arduinoNode'
    nodeClassify = 'utility/general'
    nodeId = OpenMaya.MTypeId(0x1923)

    aMultiplier = OpenMaya.MObject()
    aValue = OpenMaya.MObject()
    aOutput = OpenMaya.MObject()

    def __init__(self):
        OpenMaya.MPxNode.__init__(self)

    @staticmethod
    def nodeCreator():
        return NodeClass()

    @staticmethod
    def nodeInitializer():
        '''
        Three float numeric attributes are needed:
            * aMultiplier (input): 
                This input can be controlled by the user
                and determines the influence of every step 
                of the rotary encoder.
            * aValue (input):
                This stores the current value. It is hidden
                from the user.
            * aOutput (output):
                This is the plug to connect to the node
                to control.
        '''
        numericAttributeFn = OpenMaya.MFnNumericAttribute()

        NodeClass.aMultiplier = numericAttributeFn.create(
            'multiplier', 'mul',
            OpenMaya.MFnNumericData.kFloat, 1.0
        )
        numericAttributeFn.writable = True
        numericAttributeFn.storable = True

        NodeClass.aValue = numericAttributeFn.create(
            'value', 'val',
            OpenMaya.MFnNumericData.kFloat, 0
        )
        numericAttributeFn.writable = True
        numericAttributeFn.storable = True
        numericAttributeFn.hidden = True

        NodeClass.aOutput = numericAttributeFn.create(
            'output', 'o',
            OpenMaya.MFnNumericData.kFloat
        )
        numericAttributeFn.storable = False
        numericAttributeFn.writable = False
        numericAttributeFn.readable = True

        NodeClass.addAttribute(NodeClass.aMultiplier)
        NodeClass.addAttribute(NodeClass.aValue)
        NodeClass.addAttribute(NodeClass.aOutput)

        NodeClass.attributeAffects(
            NodeClass.aValue,
            NodeClass.aOutput
        )

    def compute(self, pPlug, pDataBlock):
        '''
        The node computation is easy. We broadcast directly
        the aValue attribute to the aOutput one.
        '''
        if pPlug == NodeClass.aOutput:
            aValHandle = pDataBlock.inputValue(NodeClass.aValue)
            aOutHandle = pDataBlock.outputValue(NodeClass.aOutput)

            aOutHandle.setFloat(aValHandle.asFloat())

            aOutHandle.setClean()
        else:
            return OpenMaya.kUnknownParameter


##########################################################
# Command Class definition
##########################################################
class CommandClass(OpenMaya.MPxCommand):
    commandName = 'arduinoUpdateChannel'

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @staticmethod
    def commandCreator():
        return CommandClass()

    def doIt(self, args):
        '''
        To control the attributes of the arduinoNode instance,
        we use PyMEL. It's for sure the slowest approach to
        compute, but it is also the faster to code.
        '''
        delta = args.asInt(0)
        node = pmc.ls(et=pmc.nt.ArduinoNode)[0]
        mul = node.getAttr('mul')
        node.setAttr('val', node.getAttr('val') + delta*mul)


##########################################################
# Plug-in initialization.
##########################################################
def initializePlugin(mobject):
    pmc.commandPort(n=':1923')

    mplugin = OpenMaya.MFnPlugin(mobject)

    try:
        mplugin.registerNode(
            NodeClass.nodeName,
            NodeClass.nodeId,
            NodeClass.nodeCreator,
            NodeClass.nodeInitializer,
            OpenMaya.MPxNode.kDependNode,
            NodeClass.nodeClassify
        )
    except:
        sys.stderr.write(
            'Failed to register node: ' + NodeClass.nodeName)
        raise

    try:
        mplugin.registerCommand(
            CommandClass.commandName,
            CommandClass.commandCreator
        )
    except:
        sys.stderr.write(
            'Failed to register command: ' + CommandClass.commandName)
        raise


def uninitializePlugin(mobject):
    pmc.commandPort(n=':1923', cl=True)

    mplugin = OpenMaya.MFnPlugin(mobject)

    try:
        mplugin.deregisterNode(NodeClass.nodeId)
    except:
        sys.stderr.write(
            'Failed to deregister node: ' + NodeClass.nodeName)
        raise

    try:
        mplugin.deregisterCommand(CommandClass.commandName)
    except:
        sys.stderr.write(
            'Failed to unregister command: ' + CommandClass.commandName)
        raise
