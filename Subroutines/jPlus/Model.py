# coding=utf-8
# © 2023 Greg Ritacco

"""jPlus"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201


_psLog = PSE.LOGGING.getLogger('OPS.JP.Model')

def resetConfigFileItems():
    """Called from PSE.remoteCalls('resetCalls')"""

    # configFile = PSE.readConfigFile()
    # configFile['Main Script']['LD'].update({'BD':''})
    # configFile['Main Script']['LD'].update({'LN':''})
    # configFile['Main Script']['LD'].update({'LO':''})
    # configFile['Main Script']['LD'].update({'OR':''})
    # configFile['Main Script']['LD'].update({'SC':''})
    # configFile['Main Script']['LD'].update({'TR':''})
    # configFile['Main Script']['LD'].update({'YR':''})

    # PSE.writeConfigFile(configFile)

    return

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
    """
    Writes the JMRI year modeled from settings into the jPlus Year Modeled text box.
    Called by:
    """
    
    configFile = PSE.readConfigFile()
    try:
        configFile['Main Script']['CP']['Subroutines.jPlus']
    except:
        return

    OSU = PSE.JMRI.jmrit.operations.setup
    yr = OSU.Setup.getYearModeled()

    configFile['Main Script']['LD'].update({'YR':yr})
    PSE.writeConfigFile(configFile)

    try: # PS plugin started with jPlus hidden
        frameTitle = PSE.BUNDLE['Pattern Scripts']
        targetPanel = PSE.getComponentByName(frameTitle, 'yearModeled')
        targetPanel.setText(yr)
    except:
        pass

    return

def setExpandedHeader():
    """
    Makes an expanded header with escapes from the layout details ['LD'] fields.
    Called by:
    """

    OSU = PSE.JMRI.jmrit.operations.setup
    configFile = PSE.readConfigFile()

    webSafeHeader = configFile['Main Script']['LD']['LN']
    extendedHeader = configFile['Main Script']['LD']['OR']
    if not extendedHeader:
        extendedHeader = unicode(OSU.Setup.getRailroadName(), PSE.ENCODING)

    if configFile['Main Script']['LD']['TR']:
        extendedHeader += '\n' + configFile['Main Script']['LD']['TR']

    if configFile['Main Script']['LD']['LO']:
        extendedHeader += '\n' + configFile['Main Script']['LD']['LO']

    OSU.Setup.setRailroadName(webSafeHeader)
# Write the unescaped version to disk
    PSE.JMRI.jmrit.operations.setup.OperationsSettingsPanel().savePreferences()
# Put the escaped version back into ram
    OSU.Setup.setRailroadName(extendedHeader)

    return
