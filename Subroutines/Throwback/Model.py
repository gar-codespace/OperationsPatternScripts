# coding=utf-8
# © 2023 Greg Ritacco

"""
Throwback
"""

from opsEntities import PSE

SNAP_SHOT_INDEX = 0

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201


_psLog = PSE.LOGGING.getLogger('OPS.TB.Model')


def createFolder():
    """Creates a 'throwback' folder in operations."""

    targetDirectory = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback')

    if not PSE.JAVA_IO.File(targetDirectory).isDirectory():
        PSE.JAVA_IO.File(targetDirectory).mkdirs()

        _psLog.info('Directory created: ' + targetDirectory)

    return

def previousCommit():

    snapShots = PSE.readConfigFile('Throwback')['SS']
    numberOfEntries = len(snapShots)
    if numberOfEntries == 1:
        minimum = 0
    else:
        minimum = 1

    global SNAP_SHOT_INDEX
    SNAP_SHOT_INDEX -= 1

    if SNAP_SHOT_INDEX < 1:
        SNAP_SHOT_INDEX = minimum

    return snapShots[SNAP_SHOT_INDEX]

def nextCommit():

    snapShots = PSE.readConfigFile('Throwback')['SS']
    numberOfEntries = len(snapShots)

    global SNAP_SHOT_INDEX
    SNAP_SHOT_INDEX += 1
    if SNAP_SHOT_INDEX >= numberOfEntries:
        SNAP_SHOT_INDEX = numberOfEntries - 1

    return snapShots[SNAP_SHOT_INDEX]

def makeCommit(displayWidgets):

    configFile = PSE.readConfigFile()
    ts = PSE.timeStamp()

    for widget in displayWidgets:
        if widget.getClass() == PSE.JAVX_SWING.JTextField:
            note = widget.getText()

    configFile['Throwback']['SS'].append([ts, note])
    PSE.writeConfigFile(configFile)

    xmlList = ['CMX', 'EMX', 'LMX', 'RMX', 'TMX']

    for xml in xmlList:
        roster = getattr(PSE, xml)
        fileName = roster.getOperationsFileName()
        targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)
        if PSE.JAVA_IO.File(targetFile).isFile():
            roster.save()
            copyFrom = PSE.JAVA_IO.File(targetFile).toPath()

            fileName = ts + '.' + xml[:1] + '.xml.o2o'
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', fileName)
            copyTo = PSE.JAVA_IO.File(targetFile).toPath()

            PSE.JAVA_NIO.Files.copy(copyFrom, copyTo, PSE.JAVA_NIO.StandardCopyOption.REPLACE_EXISTING)
            PSE.JAVA_IO.File(targetFile).setReadOnly()

    return

def throwbackCommit(displayWidgets):
    """
    Sets the cars and engines rosters to the chosen throwback restore point.
    PSE.<x>.writeOperationsFile() also does a backup.
    """

    PSE.closeTopLevelWindows()

    throwbackRestorePoint = PSE.readConfigFile('Throwback')['SS'][SNAP_SHOT_INDEX]

    for widget in displayWidgets:
        if widget.getName() == 'lCheckBox' and widget.selected:
            PSE.LM.dispose()
            roster = throwbackRestorePoint[0] + '.L.xml.o2o'
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
            PSE.LMX.readFile(targetFile)
            PSE.LMX.writeOperationsFile()
            _psLog.info('Throwback: ' + widget.getText() + ' to ' + throwbackRestorePoint[1])

    for widget in displayWidgets:
        if widget.getName() == 'rCheckBox' and widget.selected:
            PSE.RM.dispose()
            roster = throwbackRestorePoint[0] + '.R.xml.o2o'
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
            PSE.RMX.readFile(targetFile)
            PSE.RMX.writeOperationsFile()
            _psLog.info('Throwback: ' + widget.getText() + ' to ' + throwbackRestorePoint[1])

    for widget in displayWidgets:
        if widget.getName() == 'tCheckBox' and widget.selected:
            PSE.TM.dispose()
            roster = throwbackRestorePoint[0] + '.T.xml.o2o'
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
            PSE.TMX.readFile(targetFile)
            PSE.TMX.writeOperationsFile()
            _psLog.info('Throwback: ' + widget.getText() + ' to ' + throwbackRestorePoint[1])

    for widget in displayWidgets:
        if widget.getName() == 'cCheckBox' and widget.selected:
            PSE.CM.dispose()
            roster = throwbackRestorePoint[0] + '.C.xml.o2o'
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
            PSE.CMX.readFile(targetFile)
            PSE.CMX.writeOperationsFile()
            _psLog.info('Throwback: ' + widget.getText() + ' to ' + throwbackRestorePoint[1])

    for widget in displayWidgets:
        if widget.getName() == 'eCheckBox' and widget.selected:
            PSE.EM.dispose()
            roster = throwbackRestorePoint[0] + '.E.xml.o2o'
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
            PSE.EMX.readFile(targetFile)
            PSE.EMX.writeOperationsFile()
            _psLog.info('Throwback: ' + widget.getText() + ' to ' + throwbackRestorePoint[1])

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

def countCommits():

    global SNAP_SHOT_INDEX
    SNAP_SHOT_INDEX = len(PSE.readConfigFile('Throwback')['SS']) - 1

    return