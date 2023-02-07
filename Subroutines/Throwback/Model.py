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
    """Make this into a loop"""

    configFile = PSE.readConfigFile()
    ts = PSE.timeStamp()

    for widget in displayWidgets:
        if widget.getClass() == PSE.JAVX_SWING.JTextField:
            note = widget.getText()

    configFile['Throwback']['SS'].append([ts, note])
    PSE.writeConfigFile(configFile)
    
# Cars
    roster = PSE.CMX.getOperationsFileName()
    targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', roster)
    if PSE.JAVA_IO.File(targetFile).isFile():
        PSE.CMX.save()
        copyFrom = PSE.JAVA_IO.File(targetFile).toPath()

        roster = ts + '.C.xml.bak'
        targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
        copyTo = PSE.JAVA_IO.File(targetFile).toPath()

        PSE.JAVA_NIO.Files.copy(copyFrom, copyTo, PSE.JAVA_NIO.StandardCopyOption.REPLACE_EXISTING)
        PSE.JAVA_IO.File(targetFile).setReadOnly()
# Engines
    roster = PSE.EMX.getOperationsFileName()
    targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', roster)
    if PSE.JAVA_IO.File(targetFile).isFile():
        PSE.EMX.save()
        copyFrom = PSE.JAVA_IO.File(targetFile).toPath()

        roster = ts + '.E.xml.bak'
        targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
        copyTo = PSE.JAVA_IO.File(targetFile).toPath()

        PSE.JAVA_NIO.Files.copy(copyFrom, copyTo, PSE.JAVA_NIO.StandardCopyOption.REPLACE_EXISTING)
        PSE.JAVA_IO.File(targetFile).setReadOnly()
# Locations
    roster = PSE.LMX.getOperationsFileName()
    targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', roster)
    if PSE.JAVA_IO.File(targetFile).isFile():
        PSE.LMX.save()
        copyFrom = PSE.JAVA_IO.File(targetFile).toPath()

        roster = ts + '.L.xml.bak'
        targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
        copyTo = PSE.JAVA_IO.File(targetFile).toPath()

        PSE.JAVA_NIO.Files.copy(copyFrom, copyTo, PSE.JAVA_NIO.StandardCopyOption.REPLACE_EXISTING)
        PSE.JAVA_IO.File(targetFile).setReadOnly()
# Routes
    roster = PSE.RMX.getOperationsFileName()
    targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', roster)
    if PSE.JAVA_IO.File(targetFile).isFile():
        PSE.RMX.save()
        copyFrom = PSE.JAVA_IO.File(targetFile).toPath()

        roster = ts + '.R.xml.bak'
        targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
        copyTo = PSE.JAVA_IO.File(targetFile).toPath()

        PSE.JAVA_NIO.Files.copy(copyFrom, copyTo, PSE.JAVA_NIO.StandardCopyOption.REPLACE_EXISTING)
        PSE.JAVA_IO.File(targetFile).setReadOnly()
# Trains
    roster = PSE.TMX.getOperationsFileName()
    targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', roster)
    if PSE.JAVA_IO.File(targetFile).isFile():
        PSE.TMX.save()
        copyFrom = PSE.JAVA_IO.File(targetFile).toPath()

        roster = ts + '.T.xml.bak'
        targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
        copyTo = PSE.JAVA_IO.File(targetFile).toPath()

        PSE.JAVA_NIO.Files.copy(copyFrom, copyTo, PSE.JAVA_NIO.StandardCopyOption.REPLACE_EXISTING)
        PSE.JAVA_IO.File(targetFile).setReadOnly()

    return

def throwbackSnapShot(displayWidgets):
    """Sets the cars and engines rosters to the chosen throwback restore point."""

    PSE.closeTopLevelWindows()
    throwbackRestorePoint = PSE.readConfigFile('Throwback')['SS'][SNAP_SHOT_INDEX]

    for widget in displayWidgets:
        if widget.getName() == 'cCheckBox' and widget.selected:
            # PSE.CM.dispose()
            roster = throwbackRestorePoint[0] + '.C.xml.bak'
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
            PSE.CMX.readFile(targetFile)
            PSE.CMX.writeOperationsFile() # Also does a backup

        if widget.getName() == 'eCheckBox' and widget.selected:
            # PSE.EM.dispose()
            roster = throwbackRestorePoint[0] + '.E.xml.bak'
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
            PSE.EMX.readFile(targetFile)
            PSE.EMX.writeOperationsFile()

        if widget.getName() == 'lCheckBox' and widget.selected:
            # PSE.LM.dispose()
            roster = throwbackRestorePoint[0] + '.L.xml.bak'
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
            PSE.LMX.readFile(targetFile)
            PSE.LMX.writeOperationsFile()

        if widget.getName() == 'rCheckBox' and widget.selected:
            # PSE.RM.dispose()
            roster = throwbackRestorePoint[0] + '.R.xml.bak'
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
            PSE.RMX.readFile(targetFile)
            PSE.RMX.writeOperationsFile()

        if widget.getName() == 'tCheckBox' and widget.selected:
            # PSE.TM.dispose()
            roster = throwbackRestorePoint[0] + '.T.xml.bak'
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
            PSE.TMX.readFile(targetFile)
            PSE.TMX.writeOperationsFile()
    
    # The order matters
    PSE.TMX.initialize()
    PSE.RMX.initialize()
    PSE.LMX.initialize()
    PSE.EMX.initialize()
    PSE.CMX.initialize()
    
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