# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PSE
from o2oSubroutine import ModelNew

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.ModelUpdate'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('PS.TP.ModelUpdate')

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
    PSE.CM.dispose()
    PSE.EM.dispose()
# Create new car and engine lists in memory
    newInventory.newCars()
    newInventory.newLocos()
# Write the new lists to the xml files, not changing the rest of the xml
    PSE.CMX.save()
    PSE.EMX.save()

    return
