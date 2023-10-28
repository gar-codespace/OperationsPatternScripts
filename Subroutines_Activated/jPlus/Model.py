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

    targetPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'tpRailroadData.json')

    if not PSE.JAVA_IO.File(targetPath).isFile():
        _psLog.info('tpRailroadData.json not found')
        return

    configFile = PSE.readConfigFile()
    
    PSE.JAVA_IO.File(targetPath).isFile()
    tpReport = PSE.loadJson(PSE.genericReadReport(targetPath))

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)

    value = tpReport['Extended_operatingRoad']
    component = PSE.getComponentByName(frame, 'operatingRoad')
    component.setText(value)
    configFile['jPlus']['LD'].update({'OR':value})

    value = tpReport['Extended_territory']
    component = PSE.getComponentByName(frame, 'territory')
    component.setText(value)
    configFile['jPlus']['LD'].update({'TR':value})

    value = tpReport['Extended_location']
    component = PSE.getComponentByName(frame, 'location')
    component.setText(value)
    configFile['jPlus']['LD'].update({'LO':value})

    PSE.writeConfigFile(configFile)

    return


""" Routines specific to this subroutine """


def modifyPatternReport():

    reportName = PSE.getBundleItem('ops-Pattern Report') + '.json'
    _modifyAction(reportName)

    return

def modifySwitchList():

    reportName = PSE.getBundleItem('ops-Switch List') + '.json'
    _modifyAction(reportName)
    
    return

def modifyManifest():

    reportName = 'train-{}.json'.format(PSE.getNewestTrain().toString())
    _extendManifest(reportName)
    _modifyAction(reportName)

    return

def _modifyAction(reportName):

    reportPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', reportName)
    report = PSE.loadJson(PSE.genericReadReport(reportPath))
    report.update({'railroad':_getExtendedRailroadName()})

    PSE.genericWriteReport(reportPath, PSE.dumpJson(report))

    return

def _extendManifest(reportName):
    """
    Adds additional attributes found in the print options dialog.
    """

    reportPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', reportName)
    report = PSE.loadJson(PSE.genericReadReport(reportPath))
    for location in report['locations']:
        for car in location['cars']['add']:
            carObject = PSE.CM.getByRoadAndNumber(car['road'], car['number'])
            kSize = 0
            kernelName = carObject.getKernelName()
            if kernelName:
                kSize = PSE.KM.getKernelByName(kernelName).getSize()
            car['kernelSize'] = kSize
            car['finalDestination']={'userName':carObject.getFinalDestinationName(), 'track':{'userName':carObject.getFinalDestinationTrackName()}}
            car['loadType'] = carObject.getLoadType()
            car['division'] = PSE.LM.getLocationByName(car['location']['userName']).getDivisionName()

        for car in location['cars']['remove']:
            carObject = PSE.CM.getByRoadAndNumber(car['road'], car['number'])
            kSize = 0
            kernelName = carObject.getKernelName()
            if kernelName:
                kSize = PSE.KM.getKernelByName(kernelName).getSize()
            car['kernelSize'] = kSize
            car['finalDestination']={'userName':carObject.getFinalDestinationName(), 'track':{'userName':carObject.getFinalDestinationTrackName()}}
            car['loadType'] = carObject.getLoadType()
            car['division'] = PSE.LM.getLocationByName(car['location']['userName']).getDivisionName()

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
    compositeRailroadName = PSE.makeCompositRailroadName(layoutDetails)

    configFile['jPlus']['LD'].update({'JN':compositeRailroadName})
    configFile['jPlus']['LD'].update({'EH':True})

    PSE.writeConfigFile(configFile)

    return

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