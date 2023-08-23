# coding=utf-8
# © 2023 Greg Ritacco

"""
jPlus
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.JP.Model')

def resetConfigFileItems():

    configFile =  PSE.readConfigFile()
    configFile['Main Script']['LD']['BD'] = ''
    configFile['Main Script']['LD']['LO'] = ''
    configFile['Main Script']['LD']['OR'] = ''
    configFile['Main Script']['LD']['SC'] = ''
    configFile['Main Script']['LD']['TR'] = ''
    configFile['Main Script']['LD']['yearModeled'] = ''
    configFile['Main Script']['LD']['JN'] = ''

    PSE.writeConfigFile(configFile)

    return

def refreshSubroutine():
    """
    Pulls config file and ops pro settings data into the jPlus frame.
    """

    configFile = PSE.readConfigFile()

    frameName = PSE.getBundleItem('Pattern Scripts')
    frame = PSE.JMRI.util.JmriJFrame.getFrame(frameName)

    component = PSE.getComponentByName(frame, 'operatingRoad')
    value = configFile['Main Script']['LD']['OR']
    component.setText(value)

    component = PSE.getComponentByName(frame, 'territory')
    value = configFile['Main Script']['LD']['TR']
    component.setText(value)

    component = PSE.getComponentByName(frame, 'location')
    value = configFile['Main Script']['LD']['LO']
    component.setText(value)

    component = PSE.getComponentByName(frame, 'useExtended')
    flag = configFile['Main Script']['CP']['EH']
    component.setSelected(flag)

    opsProSettingsItems = PSE.getOpsProSettingsItems()
    component = PSE.getComponentByName(frame, 'yearModeled')
    component.setText(opsProSettingsItems['YR'])

    configFile['Main Script']['LD'].update({'YR':opsProSettingsItems['YR']})
    configFile['Main Script']['LD'].update({'LN':opsProSettingsItems['LN']})
    configFile['Main Script']['LD'].update({'SC':opsProSettingsItems['SC']})
    PSE.writeConfigFile(configFile)

    print(PSE.getOpsProSettingsItems())

    return

def updateRailroadDetails(widgets):
    """
    Pushes data in the jPlus frame into the config file.
    """

    configFile = PSE.readConfigFile()
    for id, widget in widgets.items():
        configFile['Main Script']['LD'].update({id:widget.getText()})

    configFile['Main Script']['CP'].update({'EH':True})

    PSE.writeConfigFile(configFile)

    return

def extendedRailroadDetails():
    """
    Creates the composite railroad name from jPlus fields. 
    The jPlus composite name ['JN'] is added to ['Main Script']['LD']
    Sets 'use extended header' to True.
    """

    _psLog.debug('extendedRailroadDetails')

    configFile = PSE.readConfigFile()

    layoutDetails = configFile['Main Script']['LD']
    compositeRailroadName = PSE.makeCompositRailroadName(layoutDetails)

    configFile['Main Script']['LD'].update({'JN':compositeRailroadName})
    configFile['Main Script']['CP'].update({'EH':True})

    PSE.writeConfigFile(configFile)

    return

def pushDetailsToJmri():
    """
    Pushes year modeled to JMRI settings.
    """

    _psLog.debug('pushDetailsToJmri')

    configFile = PSE.readConfigFile()

    OSU = PSE.JMRI.jmrit.operations.setup
    OSU.Setup.setYearModeled(configFile['Main Script']['LD']['YR'])

    PSE.JMRI.jmrit.operations.setup.OperationsSettingsPanel().savePreferences()

    return

def refreshOperationsSettingsFrame():
    """
    Kind of a BS way to do this but I can't find any listeners.
    """

    title = PSE.JMRI.jmrit.operations.setup.Bundle().handleGetMessage('TitleOperationsSetup')
    for frame in PSE.JMRI.util.JmriJFrame.getFrameList():
        if frame.getTitle() == title:
            frame.setVisible(False)
            frame.dispose()
            x = PSE.JMRI.jmrit.operations.setup.OperationsSettingsFrame()
            x.setVisible(True)

    return
