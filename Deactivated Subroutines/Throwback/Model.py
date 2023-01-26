# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""

"""

from opsEntities import PSE

SNAP_SHOT_INDEX = 0

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.TB.Model')

def createFolder():
    """Creates a 'throwback' folder in operations."""

    targetDirectory = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback')

    if not PSE.JAVA_IO.File(targetDirectory).isDirectory():
        PSE.JAVA_IO.File(targetDirectory).mkdirs()

        _psLog.info('Directory created: ' + targetDirectory)

    return

def previousSnapShot():

    configFile = PSE.readConfigFile('Throwback')['SS']

    global SNAP_SHOT_INDEX
    SNAP_SHOT_INDEX -= 1

    if SNAP_SHOT_INDEX == 0:
        SNAP_SHOT_INDEX = 1

    return configFile[SNAP_SHOT_INDEX]

def nextSnapShot():

    configFile = PSE.readConfigFile('Throwback')['SS']

    global SNAP_SHOT_INDEX
    SNAP_SHOT_INDEX += 1
    if SNAP_SHOT_INDEX >= len(configFile):
        SNAP_SHOT_INDEX = len(configFile) - 1

    return configFile[SNAP_SHOT_INDEX]

def takeSnapShot(displayWidgets):

    configFile = PSE.readConfigFile()
    ts = PSE.timeStamp()

    for widget in displayWidgets:
        if widget.getClass() == PSE.JAVX_SWING.JTextField:
            note = widget.getText()

    configFile['Throwback']['SS'].append([ts, note])
    PSE.writeConfigFile(configFile)

    PSE.CMX.save()
    PSE.EMX.save()

    roster = PSE.CMX.getOperationsFileName()
    targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', roster)
    copyFrom = PSE.JAVA_IO.File(targetFile).toPath()

    roster = ts + '.C.xml.bak'
    targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
    copyTo = PSE.JAVA_IO.File(targetFile).toPath()

    PSE.JAVA_NIO.Files.copy(copyFrom, copyTo, PSE.JAVA_NIO.StandardCopyOption.REPLACE_EXISTING)
    PSE.JAVA_IO.File(targetFile).setReadOnly()

    roster = PSE.EMX.getOperationsFileName()
    targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', roster)
    copyFrom = PSE.JAVA_IO.File(targetFile).toPath()

    roster = ts + '.E.xml.bak'
    targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
    copyTo = PSE.JAVA_IO.File(targetFile).toPath()

    PSE.JAVA_NIO.Files.copy(copyFrom, copyTo, PSE.JAVA_NIO.StandardCopyOption.REPLACE_EXISTING)
    PSE.JAVA_IO.File(targetFile).setReadOnly()

    return

def throwbackSnapShot():
    """Sets the cars and engines rosters to the chosen throwback restore point."""

    PSE.closeTroublesomeWindows()
    PSE.CM.dispose()
    PSE.EM.dispose()

    throwbackRestorePoint = PSE.readConfigFile('Throwback')['SS'][SNAP_SHOT_INDEX]

    roster = throwbackRestorePoint[0] + '.C.xml.bak'
    targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
    PSE.CMX.readFile(targetFile)
    PSE.CMX.writeOperationsFile() # Also does a backup

    roster = throwbackRestorePoint[0] + '.E.xml.bak'
    targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
    PSE.EMX.readFile(targetFile)
    PSE.EMX.writeOperationsFile()
    
    return

def resetThrowBack():

    configFile = PSE.readConfigFile()
    configFile['Throwback'].update({'SS':[['', '']]})
    PSE.writeConfigFile(configFile)

    filePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback')
    files = PSE.JAVA_IO.File(filePath).list()
    for file in files:
        filePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', file)
        PSE.JAVA_IO.File(filePath).delete()

    return

def countSnapShots():

    global SNAP_SHOT_INDEX
    SNAP_SHOT_INDEX = len(PSE.readConfigFile('Throwback')['SS']) - 1

    return