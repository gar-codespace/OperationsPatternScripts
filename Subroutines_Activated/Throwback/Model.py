# coding=utf-8
# © 2023 Greg Ritacco

"""
Throwback
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.TB.Model')

SNAP_SHOT_INDEX = 0

def resetConfigFileItems():

    return

def initializeSubroutine():
    
    return

def resetSubroutine():

    return

def refreshSubroutine():

    return

def createFolder():
    """
    Creates a 'throwback' folder in operations.
    """

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

# Save the extended data as well
    fileName = ts + '.D.json.o2o'
    targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', fileName)
    PSE.genericWriteReport(targetFile, PSE.dumpJson(configFile['Main Script']['LD']))

# Save the commit name
    fileName = ts + '.' + note + '.txt.o2o'
    targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', fileName)
    PSE.genericWriteReport(targetFile, 'note')

    print('Commit made at: ' + ts)

    return

def throwbackCommit(displayWidgets):
    """
    Sets the cars and engines rosters to the chosen throwback restore point.
    PSE.<x>.writeOperationsFile() also does a backup.
    """

    PSE.closeWindowByLevel(1)

    configFile = PSE.readConfigFile()

    throwbackRestorePoint = configFile['Throwback']['SS'][SNAP_SHOT_INDEX]

    for widget in displayWidgets:
        if widget.getName() == 'lCheckBox' and widget.selected:
            PSE.LM.dispose()
            roster = throwbackRestorePoint[0] + '.L.xml.o2o'
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
            PSE.LMX.readFile(targetFile)
            PSE.LMX.writeOperationsFile()
            _psLog.info('Throwback: ' + widget.getText() + ' to ' + throwbackRestorePoint[1])

    # Restore the extended data as well
        fileName = throwbackRestorePoint[0] + '.D.json.o2o'
        targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', fileName)
        configFile['Main Script'].update({'LD':PSE.loadJson(PSE.genericReadReport(targetFile))})
        PSE.writeConfigFile(configFile)

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

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)

    component = PSE.getComponentByName(frame, 'tbText')
    component.setText('')

    component = PSE.getComponentByName(frame, 'timeStamp')
    component.setText('')

    component = PSE.getComponentByName(frame, 'commitName')
    component.setText('')

    configFile = PSE.readConfigFile()
    configFile['Throwback'].update({'SS':[['', '']]})
    PSE.writeConfigFile(configFile)

    filePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback')
    files = PSE.JAVA_IO.File(filePath).list()
    for file in files:
        filePath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', file)
        PSE.JAVA_IO.File(filePath).delete()

    return

def validateCommits():
    """
    Mini controller.
    """
    countCommits()
    if SNAP_SHOT_INDEX <= 0:
        commits = getCommits()
        updateThrowbackConfig(commits)
        countCommits()

    return

def countCommits():

    global SNAP_SHOT_INDEX
    SNAP_SHOT_INDEX = len(PSE.readConfigFile('Throwback')['SS']) - 1

    return

def getCommits():
    """
    Returns a list of lists: [name, timeStamp]
    """

    commits = [['','']]
    
    targetDirectory = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback')
    for file in PSE.JAVA_IO.File(targetDirectory).listFiles():
        splitName = file.getName().split('.')

        if splitName[7] == 'txt':
            name = splitName[6]
            timestamp = '.'.join(splitName[:6])
            commits.append([timestamp, name])

    return commits

def updateThrowbackConfig(commits):

    configFile = PSE.readConfigFile()
    configFile['Throwback'].update({'SS':commits})
    PSE.writeConfigFile(configFile)

    return
