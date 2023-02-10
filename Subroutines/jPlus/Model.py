# coding=utf-8
# © 2021, 2022 Greg Ritacco

""" """

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.JP.Model')

def jPanelSetup():
    """Copy the jPanel data from tpRailroadData.json into the JP fields of the config file."""

    _psLog.debug('jPanelSetup')

    fileName = 'tpRailroadData.json'
    filePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)

    if PSE.JAVA_IO.File(filePath).isFile():
        sourceData = PSE.loadJson(PSE.genericReadReport(filePath))
    else:
        return

    configFile = PSE.readConfigFile()
    configFile['Main Script']['LD'].update({'OR':sourceData['operatingRoad']})
    configFile['Main Script']['LD'].update({'TR':sourceData['territory']})
    configFile['Main Script']['LD'].update({'LO':sourceData['location']})
    configFile['Main Script']['LD'].update({'YR':sourceData['year']})
    PSE.writeConfigFile(configFile)

    return

def updateYearModeled():
    """Writes the JMRI year modeled from settings into the jPlus Year Modeled text box.
        Called by:
        """
    
    configFile = PSE.readConfigFile()
    if not configFile['Main Script']['CP']['Subroutines.jPlus']:
        return

    OSU = PSE.JMRI.jmrit.operations.setup
    yr = OSU.Setup.getYearModeled()

    configFile['Main Script']['LD'].update({'YR':yr})
    PSE.writeConfigFile(configFile)

    frameTitle = PSE.BUNDLE['Pattern Scripts']
    targetPanel = PSE.getComponentByName(frameTitle, 'yearModeled')
    targetPanel.setText(yr)

    return

def setExpandedHeader():
    """Makes an expanded header with escapes from the layout details ['LD'] fields.
        Called by:
        """

    configFile = PSE.readConfigFile()
    operatingRoad = configFile['Main Script']['LD']['OR']
    if not operatingRoad:
        OSU = PSE.JMRI.jmrit.operations.setup
        operatingRoad = unicode(OSU.Setup.getRailroadName(), PSE.ENCODING)

    header = operatingRoad
    if configFile['Main Script']['LD']['TR']:
        header += '\n' + configFile['Main Script']['LD']['TR']

    if configFile['Main Script']['LD']['LO']:
        header += '\n' + configFile['Main Script']['LD']['LO']

    OSU = PSE.JMRI.jmrit.operations.setup
    OSU.Setup.setRailroadName(header)
# Write the unescaped version to disk
    PSE.JMRI.jmrit.operations.setup.OperationsSettingsPanel().savePreferences()
# Put the escaped version back into ram
    OSU.Setup.setRailroadName(header)

    return
