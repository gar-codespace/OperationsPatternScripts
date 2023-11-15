# coding=utf-8
# © 2023 Greg Ritacco

"""
jPlus
"""

from opsEntities import PSE
from Subroutines_Activated.jPlus import SubroutineListeners

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.JP.Model')


""" Routines called by the plugin listeners """


def resetConfigFileItems():
    
    return

def initializeSubroutine():
    """
    Set values from the config file.
    """

    configFile = PSE.readConfigFile()

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)

    component = PSE.getComponentByName(frame, 'operatingRoad')
    value = configFile['jPlus']['LD']['OR']
    component.setText(value)

    component = PSE.getComponentByName(frame, 'territory')
    value = configFile['jPlus']['LD']['TR']
    component.setText(value)

    component = PSE.getComponentByName(frame, 'location')
    value = configFile['jPlus']['LD']['LO']
    component.setText(value)

    component = PSE.getComponentByName(frame, 'useExtended')
    flag = configFile['jPlus']['LD']['EH']
    component.setSelected(flag)

    return

def resetSubroutine():

    _psLog.debug('resetConfigFile')

    configFile = PSE.readConfigFile()

    configFile['jPlus']['LD'].update({"BD":""})
    configFile['jPlus']['LD'].update({"JN":""})
    configFile['jPlus']['LD'].update({"LN":""})
    configFile['jPlus']['LD'].update({"LO":""})
    configFile['jPlus']['LD'].update({"OR":""})
    configFile['jPlus']['LD'].update({"SC":""})
    configFile['jPlus']['LD'].update({"TR":""})
    configFile['jPlus']['LD'].update({"YR":""})

    PSE.writeConfigFile(configFile)

    return

def refreshSubroutine():

    configFile = PSE.readConfigFile()
    
    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)

    component = PSE.getComponentByName(frame, 'operatingRoad')
    component.setText(configFile['jPlus']['LD']['OR'])

    component = PSE.getComponentByName(frame, 'territory')
    component.setText(configFile['jPlus']['LD']['TR'])

    component = PSE.getComponentByName(frame, 'location')
    component.setText(configFile['jPlus']['LD']['LO'])

    component = PSE.getComponentByName(frame, 'yearModeled')
    component.setText(configFile['jPlus']['LD']['YR'])

    component = PSE.getComponentByName(frame, 'useExtended')
    component.setSelected(configFile['jPlus']['LD']['EH'])

    updateYearModeled()

    return

def addSubroutineListeners():
    """
    Add any listeners specific to this subroutine.
    """

    PSE.LM.addPropertyChangeListener(SubroutineListeners.ExtendedAttributesListener())

    return

def removeSubroutineListeners():
    """
    Removes any listeners specific to this subroutine.
    """

    for listener in PSE.LM.getPropertyChangeListeners():
        if isinstance(listener, PSE.JAVA_BEANS.PropertyChangeListener) and 'ExtendedAttributesListener' in listener.toString():
            PSE.LM.removePropertyChangeListener(listener)

    return


""" Routines specific to this subroutine """


def putExtendedProperties(propertyOldValue):
    """
    Another subroutine can send extended details to jPlus.
    The details are written to the config file and jPlus is updated.
    """

    configFile = PSE.readConfigFile()

    configFile['jPlus']['LD']['OR'] = propertyOldValue[0]
    configFile['jPlus']['LD']['TR'] = propertyOldValue[1]
    configFile['jPlus']['LD']['LO'] = propertyOldValue[2]
    configFile['jPlus']['LD']['YR'] = propertyOldValue[3]
    configFile['jPlus']['LD']['EH'] = True

    layoutDetails = {}
    layoutDetails['OR'] = propertyOldValue[0]
    layoutDetails['TR'] = propertyOldValue[1]
    layoutDetails['LO'] = propertyOldValue[2]

    configFile['jPlus']['LD']['JN'] = makeCompositRailroadName(layoutDetails)

    PSE.writeConfigFile(configFile)

    return

def modifyPatternReport():

    reportName = PSE.getBundleItem('ops-Pattern Report') + '.json'
    _modifyAction(reportName)

    return

def modifySwitchList():

    reportName = PSE.getBundleItem('ops-Switch List') + '.json'
    _modifyAction(reportName)
    
    return

def modifyManifest(manifestName):

    PSE.extendManifest(manifestName)
    _modifyAction(manifestName)

    return

def _modifyAction(reportName):

    reportPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', reportName)
    report = PSE.loadJson(PSE.genericReadReport(reportPath))
    report.update({'railroad':_getExtendedRailroadName()})

    PSE.genericWriteReport(reportPath, PSE.dumpJson(report))

    return

def _getExtendedRailroadName():
    """
    Returns either the extended railroad name or the JMRI railroad name.
    """

    configFile = PSE.readConfigFile()
    OSU = PSE.JMRI.jmrit.operations.setup
    
    railroadName = OSU.Setup.getRailroadName()
    if configFile['jPlus']['LD']['EH']:
        railroadName = configFile['jPlus']['LD']['JN']

    return railroadName

def updateRailroadDetails(widgets):
    """
    Pushes data from the jPlus frame into the config file.
    """

    configFile = PSE.readConfigFile()
    for id, widget in widgets.items():
        configFile['jPlus']['LD'].update({id:widget.getText()})

    configFile['jPlus']['LD'].update({'EH':True})

    PSE.writeConfigFile(configFile)

    return

def compositeRailroadName():
    """
    Creates the composite railroad name from jPlus fields. 
    The jPlus composite name ['JN'] is added to ['jPlus']['LD']
    Sets 'use extended header' to True.
    """

    _psLog.debug('compositeRailroadName')

    configFile = PSE.readConfigFile()

    layoutDetails = configFile['jPlus']['LD']
    compositeRailroadName = makeCompositRailroadName(layoutDetails)

    configFile['jPlus']['LD'].update({'JN':compositeRailroadName})
    configFile['jPlus']['LD'].update({'EH':True})

    PSE.writeConfigFile(configFile)

    return

def makeCompositRailroadName(layoutDetails):
    """
    Uses configFile['Main Script']['LD'] data to make a composite name for use by OPS subroutines.
    """

    _psLog.debug('makeCompositRailroadName')

    a = ''
    if layoutDetails['OR']:
        a = '{}\n'.format(layoutDetails['OR'])

    b = ''
    if layoutDetails['TR']:
        b = '{}\n'.format(layoutDetails['TR'])

    c = ''
    if layoutDetails['LO']:
        c = layoutDetails['LO']

    return a + b + c

def updateYearModeled():
    """
    Pushes year modeled to JMRI settings.
    """

    _psLog.debug('updateYearModeled')

    configFile = PSE.readConfigFile()

    OSU = PSE.JMRI.jmrit.operations.setup
    OSU.Setup.setYearModeled(configFile['jPlus']['LD']['YR'])

    PSE.JMRI.jmrit.operations.setup.OperationsSettingsPanel().savePreferences()

    return

def refreshOperationsSettingsFrame():
    """
    Kind of a BS way to do this but I can't find any listeners.
    """

    title = PSE.SB.handleGetMessage('TitleOperationsSetup')
    for frame in PSE.JMRI.util.JmriJFrame.getFrameList():
        if frame.getTitle() == title:
            frame.setVisible(False)
            frame.dispose()
            x = PSE.JMRI.jmrit.operations.setup.OperationsSettingsFrame()
            x.setVisible(True)

    return
