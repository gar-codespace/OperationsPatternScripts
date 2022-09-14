# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.ModelEntities'
SCRIPT_REV = 20220101

def getWorkEvents():
    """Gets the o2o work events file
        Used by:
        ModelWorkEvents.ConvertPtMergedForm.getWorkEvents
        ModelWorkEvents.o2oWorkEvents.getWorkEvents
        """

    workEventName = PatternScriptEntities.BUNDLE['o2o Work Events']
    jsonFileName = PatternScriptEntities.PROFILE_PATH + 'operations\\jsonManifests\\' + workEventName + '.json'
    workEventList = PatternScriptEntities.genericReadReport(jsonFileName)
    jsonFile = PatternScriptEntities.loadJson(workEventList)

    return jsonFile

def getTpExport(fileName):
    """Generic file getter
        Used by:
        ModelImport.TrainPlayerImporter.getTpReportFiles
        """

    fullPath = "AppData\\Roaming\\TrainPlayer\\Reports\\" + fileName
    tpExportPath = PatternScriptEntities.JMRI.util.FileUtil.getHomePath() + fullPath

    if PatternScriptEntities.JAVA_IO.File(tpExportPath).isFile():
        tpExport = PatternScriptEntities.genericReadReport(tpExportPath).split('\n')
        return tpExport
    else:
        return
    return

def parseCarId(carId):
    """Splits a TP car id into a JMRI road name and number
        Used by:
        ModelImport.TrainPlayerImporter.getAllTpRoads
        ModelNew.NewRollingStock.makeTpRollingStockData
        ModelNew.NewRollingStock.newCars
        ModelNew.NewRollingStock.newLocos
        """

    rsRoad = ''
    rsNumber = ''

    for character in carId:
        if character.isspace() or character == '-':
            continue
        if character.isdecimal():
            rsNumber += character
        else:
            rsRoad += character

    return rsRoad, rsNumber

def getSetToLocationAndTrack(locationName, trackName):
    """Used by:
        ModelNew.NewRollingStock.newCars
        ModelNew.NewRollingStock.newLocos
        """

    try:
        location = PatternScriptEntities.LM.getLocationByName(locationName)
        track = location.getTrackByName(trackName, None)
        return location, track
    except:
        print('Not found: ', locationName, trackName)
        return None, None




# def getLoadType(type, load):
#     """Used by:
#         ModelWorkEvents.ConvertPtMergedForm.parsePsWorkEventRs
#         ModelWorkEvents.ConvertJmriManifest.parseRS
#         """
#
#     tc = PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.CarLoads
#     TCM = PatternScriptEntities.JMRI.InstanceManager.getDefault(tc)
#
#     lt = 'O'
#     loadType = TCM.getLoadType(type, load)
#     if loadType == 'empty':
#         lt = 'E'
#     if loadType == 'load':
#         lt = 'L'
#
#     return lt
