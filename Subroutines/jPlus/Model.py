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
    configFile['Main Script']['LD']['YR'] = ''
    configFile['Main Script']['LD']['JN'] = ''

    PSE.writeConfigFile(configFile)

    return

def refreshSubroutine():

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

    component = PSE.getComponentByName(frame, 'yearModeled')
    value = configFile['Main Script']['LD']['YR']
    component.setText(value)

    component = PSE.getComponentByName(frame, 'useExtended')
    flag = configFile['Main Script']['CP']['EH']
    component.setSelected(flag)

    return

def updateRailroadDetails(widgets):

    configFile = PSE.readConfigFile()
    for id, widget in widgets.items():
        configFile['Main Script']['LD'].update({id:widget.getText()})

    configFile['Main Script']['LD'].update({'LN':PSE.getJmriRailroadName()})

    configFile['Main Script']['CP'].update({'EH':True})

    PSE.writeConfigFile(configFile)

    return

def extendedRailroadDetails():
    """
    Two additional details:
    The jPlus Composite Name ['JN'] is added to ['Main Script']['LD']
    Called on jPlus refresh
    """

    _psLog.debug('extendedRailroadDetails')

    configFile = PSE.readConfigFile()
    layoutDetails = configFile['Main Script']['LD']
    OSU = PSE.JMRI.jmrit.operations.setup
    OSU.Setup.setYearModeled(configFile['Main Script']['LD']['YR'])

    layoutDetails.update({'JN':PSE.makeCompositRailroadName(layoutDetails)})

    configFile['Main Script']['CP'].update({'EH':True})

    PSE.writeConfigFile(configFile)

    return

def updateYearModeled():
    """
    Writes the JMRI year modeled from settings into the jPlus Year Modeled text box.
    Called by:
    """

    _psLog.debug('updateYearModeled')

    OSU = PSE.JMRI.jmrit.operations.setup
    jmriYear = OSU.Setup.getYearModeled()

    configFile = PSE.readConfigFile()
    configFile['Main Script']['LD'].update({'YR':jmriYear})
    PSE.writeConfigFile(configFile)

    frameTitle = PSE.getBundleItem('Pattern Scripts')        
    targetPanel = PSE.getComponentByName(frameTitle, 'yearModeled')
    targetPanel.setText(jmriYear)

    return

def extendedHeaderActivator(state):
    """
    Sets configFile['Main Script]['CP']['EH"] to true or false.
    """

    configFile = PSE.readConfigFile()
    configFile['Main Script']['CP'].update({'EH':state})
    PSE.writeConfigFile(configFile)

    return
