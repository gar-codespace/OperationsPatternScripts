# coding=utf-8
# © 2023 Greg Ritacco

"""
Throwback
"""

from opsEntities import PSE

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

_psLog = PSE.LOGGING.getLogger('OPS.TB.Model')

TC_INDEX = 1


""" Routines called by the plugin listeners """


def resetConfigFileItems():

    return

def initializeSubroutine():

    return

def resetSubroutine():

    return

def refreshSubroutine():

    return

def addSubroutineListeners():
    """
    Add any listeners specific to this subroutine.
    """

    return

def removeSubroutineListeners():
    """
    Removes any listeners specific to this subroutine.
    """

    return


""" Routines specific to this subroutine """


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
    """
    There is at least 1 throwback commit.
    """

    global TC_INDEX
    TC_INDEX -= 1
    TC_INDEX = max(0, TC_INDEX)

    return PSE.readConfigFile('Throwback')['TC'][TC_INDEX]

def nextCommit():

    tc = PSE.readConfigFile('Throwback')['TC']

    global TC_INDEX
    TC_INDEX += 1
    TC_INDEX = min(len(tc) - 1, TC_INDEX)

    return tc[TC_INDEX]

def stampTime():
    """
    Returns the time in format: YYYY.MO.DY.24.MN.SC
    """

    return PSE.TIME.strftime('%Y.%m.%d.%H.%M.%S', PSE._getTime())

def makeCommit(commitName):

    configFile = PSE.readConfigFile()
    ts = stampTime()
    configFile['Throwback']['TC'].append([ts, commitName])
    PSE.writeConfigFile(configFile)

    xmlList = ['CMX', 'EMX', 'LMX', 'RMX', 'TMX']
    for xml in xmlList:
        roster = getattr(PSE, xml)
        fileName = roster.getOperationsFileName()
        targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', fileName)
        if PSE.JAVA_IO.File(targetFile).isFile():
            roster.save()
            copyFrom = PSE.JAVA_IO.File(targetFile).toPath()

            fileName = '{}.{}.xml'.format(ts, xml[:1])
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', fileName)
            copyTo = PSE.JAVA_IO.File(targetFile).toPath()

            PSE.JAVA_NIO.Files.copy(copyFrom, copyTo, PSE.JAVA_NIO.StandardCopyOption.REPLACE_EXISTING)
            PSE.JAVA_IO.File(targetFile).setReadOnly()

# Save the commit name
    fileName = '{}.A.txt'.format(ts)
    targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', fileName)
    PSE.genericWriteReport(targetFile, commitName)

# Save the extended data as well
    fileName = '{}.D.json'.format(ts)
    targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', fileName)
    try:
        extendedData = PSE.dumpJson(configFile['jPlus']['LD'])
        PSE.genericWriteReport(targetFile, extendedData)
    except:
        pass

    print('Commit made at: ' + ts)

    return

def throwbackCommit(displayWidgets):
    """
    Sets the cars and engines rosters to the chosen throwback restore point.
    PSE.<x>.writeOperationsFile() also does a backup.
    """

    PSE.closeWindowByLevel(1)

    configFile = PSE.readConfigFile()

    throwbackRestorePoint = configFile['Throwback']['TC'][TC_INDEX]

    for widget in displayWidgets:
        if widget.getName() == 'lCheckBox' and widget.selected:
            PSE.LM.dispose()
            roster = '{}.L.xml'.format(throwbackRestorePoint[0])
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
            PSE.LMX.readFile(targetFile)
            PSE.LMX.writeOperationsFile()
            _psLog.info('Throwback: {} to commit: {}'.format(widget.getText(), throwbackRestorePoint[1]))

    for widget in displayWidgets:
        if widget.getName() == 'rCheckBox' and widget.selected:
            PSE.RM.dispose()
            roster = '{}.R.xml'.format(throwbackRestorePoint[0])
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
            PSE.RMX.readFile(targetFile)
            PSE.RMX.writeOperationsFile()
            _psLog.info('Throwback: {} to commit: {}'.format(widget.getText(), throwbackRestorePoint[1]))

    for widget in displayWidgets:
        if widget.getName() == 'tCheckBox' and widget.selected:
            PSE.TM.dispose()
            roster = '{}.T.xml'.format(throwbackRestorePoint[0])
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
            PSE.TMX.readFile(targetFile)
            PSE.TMX.writeOperationsFile()
            _psLog.info('Throwback: {} to commit: {}'.format(widget.getText(), throwbackRestorePoint[1]))

    for widget in displayWidgets:
        if widget.getName() == 'cCheckBox' and widget.selected:
            PSE.CM.dispose()
            roster = '{}.C.xml'.format(throwbackRestorePoint[0])
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
            PSE.CMX.readFile(targetFile)
            PSE.CMX.writeOperationsFile()
            _psLog.info('Throwback: {} to commit: {}'.format(widget.getText(), throwbackRestorePoint[1]))

    for widget in displayWidgets:
        if widget.getName() == 'eCheckBox' and widget.selected:
            PSE.EM.dispose()
            roster = '{}.E.xml'.format(throwbackRestorePoint[0])
            targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', roster)
            PSE.EMX.readFile(targetFile)
            PSE.EMX.writeOperationsFile()
            _psLog.info('Throwback: {} to commit: {}'.format(widget.getText(), throwbackRestorePoint[1]))

    # Restore the extended data as well
        fileName = '{}.D.json'.format(throwbackRestorePoint[0])
        targetFile = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback', fileName)
        try:
            configFile['jPlus'].update({'LD':PSE.loadJson(PSE.genericReadReport(targetFile))})
        except:
            pass

        PSE.writeConfigFile(configFile)

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
    configFile['Throwback'].update({'TC':[['', '']]})
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
    # countCommits()
    # if TC_INDEX <= 0:
    commits = getCommits()
    updateThrowbackConfig(commits)
    countCommits()

    return

def countCommits():

    global TC_INDEX
    TC_INDEX = len(PSE.readConfigFile('Throwback')['TC']) - 1

    return

def getCommits():
    """
    Returns a list of lists: [name, timeStamp]
    """

    commits = [['','']]
    
    targetDirectory = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'throwback')
    for file in PSE.JAVA_IO.File(targetDirectory).listFiles():
        splitName = file.getName().split('.')

        if splitName[-1] == 'txt':
            name = PSE.genericReadReport(file.toString())
            timestamp = '.'.join(splitName[:6])
            commits.append([timestamp, name])

    return commits

def updateThrowbackConfig(commits):
    

    configFile = PSE.readConfigFile()
    configFile['Throwback'].update({'TC':commits})
    PSE.writeConfigFile(configFile)

    return
