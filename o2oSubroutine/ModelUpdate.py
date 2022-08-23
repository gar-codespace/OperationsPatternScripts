# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities
from o2oSubroutine import ModelNew
from o2oSubroutine import ModelEntities

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.ModelUpdate'
SCRIPT_REV = 20220101

_psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.ModelUpdate')

def updateRollingStock():
    """Mini controller to update the rolling stock inventory.
        Nothing fancy, the old ones are written over"""

    updateXML = UpdateXML()
    updateXML.deleteRsXml()

    newInventory = ModelNew.NewRollingStock()
    newInventory.getTpInventory()
    newInventory.splitTpList()
    newInventory.newCars()
    newInventory.newLocos()
    PatternScriptEntities.CMX.save()
    PatternScriptEntities.EMX.save()
    
    return


class UpdateXML:

    def __init__(self):

        self.o2oConfig =  PatternScriptEntities.readConfigFile('o2o')

        self.TpRailroad = ModelNew.getTpRailroadData()

        self.OperationsCarRoster = PatternScriptEntities.CMX
        self.OperationsEngineRoster = PatternScriptEntities.EMX
        self.OperationsLocationRoster = PatternScriptEntities.LMX

        return

    def deleteRsXml(self):

        reportPath = PatternScriptEntities.PROFILE_PATH + 'operations\\'
        opsFileList = PatternScriptEntities.JAVA_IO.File(reportPath).listFiles()
        for file in opsFileList:
            if file.toString().startswith('OperationsCarRoster') or file.toString().startswith('OperationsEngineRoster'):
                file.delete()

        PatternScriptEntities.CM.dispose()
        PatternScriptEntities.EM.dispose()

        return
