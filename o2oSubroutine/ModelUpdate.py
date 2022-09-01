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
        Nothing fancy, the old car and engine listts are written over"""

    ModelNew.closeAllEditWindows()
# Process the TP data
    newInventory = ModelNew.NewRollingStock()
    newInventory.getTpInventory()
    newInventory.splitTpList()
    newInventory.makeTpRollingStockData()
# Remove the cars and engines from memory
    PatternScriptEntities.CM.dispose()
    PatternScriptEntities.EM.dispose()
# Create new car and engine lists in memory
    newInventory.newCars()
    newInventory.newLocos()
# Write the new lists to the xml files, not changing the rest of the xml
    PatternScriptEntities.CMX.save()
    PatternScriptEntities.EMX.save()

    return