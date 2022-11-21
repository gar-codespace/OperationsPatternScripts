# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Template."""

from opsEntities import PSE

SCRIPT_NAME = 'OperationsPatternScripts.jPlusSubroutine.Model'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.JP.Model')

def jPanelSetup():
    """Copy the jPanel data from tpRailroadData.json into the JP fields of the config file."""

    configFile = PSE.readConfigFile()

    if not configFile['CP']['o2oSubroutine']:
        return

    try:
        fileName = 'tpRailroadData.json'
        filePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)
        sourceData = PSE.loadJson(PSE.genericReadReport(filePath))
    except:
        pass

    try:
        configFile['JP'].update({'OR':sourceData['operatingRoad']})
        configFile['JP'].update({'TR':sourceData['territory']})
        configFile['JP'].update({'LO':sourceData['location']})
        configFile['JP'].update({'YR':sourceData['year']})
    except:
        pass

    OSU = PSE.JMRI.jmrit.operations.setup
    OSU.Setup.setYearModeled(configFile['JP']['YR'])

    PSE.writeConfigFile(configFile)

    return
