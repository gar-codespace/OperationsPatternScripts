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

    configFile = PSE.readConfigFile()



    if not 'o2o' in PSE.getSubroutineDirs():
        return

    # if not configFile['CP']['o2oSubroutine']:
    #     return


    fileName = 'tpRailroadData.json'
    filePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)

    if PSE.JAVA_IO.File(filePath).isFile():
        sourceData = PSE.loadJson(PSE.genericReadReport(filePath))
    else:
        return

    configFile['jPlus'].update({'OR':sourceData['operatingRoad']})
    configFile['jPlus'].update({'TR':sourceData['territory']})
    configFile['jPlus'].update({'LO':sourceData['location']})
    configFile['jPlus'].update({'YR':sourceData['year']})

    OSU = PSE.JMRI.jmrit.operations.setup
    OSU.Setup.setYearModeled(configFile['jPlus']['YR'])

    PSE.writeConfigFile(configFile)

    return
