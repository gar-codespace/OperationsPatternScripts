# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PSE

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.ModelEntities'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('PS.TP.ModelNew')

def getWorkEvents():
    """Gets the o2o work events file
        Used by:
        ModelWorkEvents.ConvertPtMergedForm.getWorkEvents
        ModelWorkEvents.o2oWorkEvents.getWorkEvents
        """

    reportName = PSE.BUNDLE['o2o Work Events']
    fileName = reportName + '.json'
    targetDir = PSE.PROFILE_PATH + '\\operations\\jsonManifests'
    targetPath = PSE.OS_Path.join(targetDir, fileName)

    workEventList = PSE.genericReadReport(targetPath)
    jsonFile = PSE.loadJson(workEventList)

    return jsonFile

def getTpExport(fileName):
    """Generic file getter, fileName includes .txt
        Used by:
        ModelImport.TrainPlayerImporter.getTpReportFiles
        """

    targetDir = PSE.JMRI.util.FileUtil.getHomePath() + '\\AppData\\Roaming\\TrainPlayer\\Reports'
    targetPath = PSE.OS_Path.join(targetDir, fileName)

    if PSE.JAVA_IO.File(targetPath).isFile():
        tpExport = PSE.genericReadReport(targetPath).split('\n')
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
        location = PSE.LM.getLocationByName(locationName)
        track = location.getTrackByName(trackName, None)
        return location, track
    except:
        print('Not found: ', locationName, trackName)
        return None, None

def closeAllEditWindows():
    """Close all the 'Edit' windows when the New button is pressed
        Lazy work around, figure this our for real later
        """

    for frameName in PSE.JMRI.util.JmriJFrame.getFrameList():
        frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)
        if frame.getTitle().startswith('Edit'):
            frame.setVisible(False)
            frame.dispose()

    return

def getTpRailroadData():
    """Add error handling"""

    tpRailroad = []

    reportName = 'tpRailroadData'
    fileName = reportName + '.json'
    targetDir = PSE.PROFILE_PATH + '\\operations'
    targetPath = PSE.OS_Path.join(targetDir, fileName)

    try:
        PSE.JAVA_IO.File(targetPath).isFile()
        _psLog.info('tpRailroadData.json OK')
    except:
        _psLog.warning('tpRailroadData.json not found')
        return

    report = PSE.genericReadReport(targetPath)
    tpRailroad = PSE.loadJson(report)

    return tpRailroad
