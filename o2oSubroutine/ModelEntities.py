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

    reportName = PatternScriptEntities.BUNDLE['o2o Work Events']
    fileName = reportName + '.json'
    targetDir = PatternScriptEntities.PROFILE_PATH + '\\operations\\jsonManifests'
    targetPath = PatternScriptEntities.OS_Path.join(targetDir, fileName)

    workEventList = PatternScriptEntities.genericReadReport(targetPath)
    jsonFile = PatternScriptEntities.loadJson(workEventList)

    return jsonFile

def getTpExport(fileName):
    """Generic file getter, fileName includes .txt
        Used by:
        ModelImport.TrainPlayerImporter.getTpReportFiles
        """

    targetDir = PatternScriptEntities.JMRI.util.FileUtil.getHomePath() + '\\AppData\\Roaming\\TrainPlayer\\Reports'
    targetPath = PatternScriptEntities.OS_Path.join(targetDir, fileName)

    if PatternScriptEntities.JAVA_IO.File(targetPath).isFile():
        tpExport = PatternScriptEntities.genericReadReport(targetPath).split('\n')
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
