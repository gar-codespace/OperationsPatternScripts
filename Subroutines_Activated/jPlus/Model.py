# coding=utf-8
# © 2023 Greg Ritacco

"""
jPlus
"""

from opsEntities import PSE
from opsEntities import TextReports

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.JP.Model')

""" Actions called by the plugin listeners """

def resetConfigFileItems():
    
    return

def initializeSubroutine():

    configFile = PSE.readConfigFile()

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)

    component = PSE.getComponentByName(frame, 'operatingRoad')
    value = configFile['Main Script']['LD']['OR']
    component.setText(value)

    component = PSE.getComponentByName(frame, 'territory')
    value = configFile['Main Script']['LD']['TR']
    component.setText(value)

    component = PSE.getComponentByName(frame, 'location')
    value = configFile['Main Script']['LD']['LO']
    component.setText(value)

    component = PSE.getComponentByName(frame, 'useExtended')
    flag = configFile['Main Script']['CP']['EH']
    component.setSelected(flag)

    return

def resetSubroutine():

    return

def refreshSubroutine():

    configFile = PSE.readConfigFile()

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)

    component = PSE.getComponentByName(frame, 'operatingRoad')
    value = configFile['Main Script']['LD']['OR']
    component.setText(value)

    component = PSE.getComponentByName(frame, 'territory')
    value = configFile['Main Script']['LD']['TR']
    component.setText(value)

    component = PSE.getComponentByName(frame, 'location')
    value = configFile['Main Script']['LD']['LO']
    component.setText(value)

    component = PSE.getComponentByName(frame, 'useExtended')
    flag = configFile['Main Script']['CP']['EH']
    component.setSelected(flag)

    component = PSE.getComponentByName(frame, 'yearModeled')
    OSU = PSE.JMRI.jmrit.operations.setup
    yearModeled = OSU.Setup.getYearModeled()
    component.setText(yearModeled)

    return

def opsAction1(message=None):
    """
    Modifies the trains json manifest with the extended railroad detail.
    """

    if message == 'TrainBuilt':
        train = PSE.getNewestTrain()

        manifest = PSE.getTrainManifest(train)
        manifest.update({'railroad':PSE.getExtendedRailroadName()})
        PSE.saveManifest(manifest, train)

    return

def opsAction2(message=None):
    """
    Writes a new text manifest from the extended manifest.
    """

    if message == 'TrainBuilt':
        train = PSE.getNewestTrain()
        manifest = PSE.getTrainManifest(train)

        textManifest = TextReports.opsTextManifest(manifest)
        manifestName = 'train ({}).txt'.format(train.toString())
        manifestPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'manifests', manifestName)
        PSE.genericWriteReport(manifestPath, textManifest)

    return

def opsAction3(message=None):
    
    tpDirectory = PSE.OS_PATH.join(PSE.JMRI.util.FileUtil.getHomePath(), 'AppData', 'Roaming', 'TrainPlayer', 'Reports')
# Make a work event list from a JMRI manifest
    if PSE.JAVA_IO.File(tpDirectory).isDirectory() and message == 'TrainBuilt':   
        train = PSE.getNewestTrain()
        manifest = PSE.getTrainManifest(train)
        o2oWorkEvents = ModelWorkEvents.o2oWorkEvents(manifest)

        outPutName = 'JMRI Report - o2o Workevents.csv'
        o2oWorkEventPath = PSE.OS_PATH.join(tpDirectory, outPutName)
        PSE.genericWriteReport(o2oWorkEventPath, o2oWorkEvents)
# Make a work event list from an OPS switch list
    elif PSE.JAVA_IO.File(tpDirectory).isDirectory() and message == 'opsSwitchList':   
        manifest = PSE.getOpsSwitchList()
        o2oWorkEvents = ModelWorkEvents.o2oWorkEvents(manifest)

        outPutName = 'JMRI Report - o2o Workevents.csv'
        o2oWorkEventPath = PSE.OS_PATH.join(tpDirectory, outPutName)
        PSE.genericWriteReport(o2oWorkEventPath, o2oWorkEvents)

    else:
        _psLog.warning('TrainPlayer Reports destination directory not found')
        print('TrainPlayer Reports destination directory not found')

    return

""" Routines specific to this subroutine """

def updateRailroadDetails(widgets):
    """
    Pushes data from the jPlus frame into the config file.
    """

    configFile = PSE.readConfigFile()
    for id, widget in widgets.items():
        configFile['Main Script']['LD'].update({id:widget.getText()})

    configFile['Main Script']['CP'].update({'EH':True})

    PSE.writeConfigFile(configFile)

    return

def extendedRailroadDetails():
    """
    Creates the composite railroad name from jPlus fields. 
    The jPlus composite name ['JN'] is added to ['Main Script']['LD']
    Sets 'use extended header' to True.
    """

    _psLog.debug('extendedRailroadDetails')

    configFile = PSE.readConfigFile()

    layoutDetails = configFile['Main Script']['LD']
    compositeRailroadName = PSE.makeCompositRailroadName(layoutDetails)

    configFile['Main Script']['LD'].update({'JN':compositeRailroadName})
    configFile['Main Script']['CP'].update({'EH':True})

    PSE.writeConfigFile(configFile)

    return

def pushDetailsToJmri():
    """
    Pushes year modeled to JMRI settings.
    """

    _psLog.debug('pushDetailsToJmri')

    configFile = PSE.readConfigFile()

    OSU = PSE.JMRI.jmrit.operations.setup
    OSU.Setup.setYearModeled(configFile['Main Script']['LD']['YR'])

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
