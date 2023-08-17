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
    configFile['Main Script']['LD']['RN'] = ''

    PSE.writeConfigFile(configFile)

    return

def extendedRailroadDetails():
    """
    Two additional details:
    Railroad Name ['RN'] and jPlus Composite Name ['JN'] are added to ['Main Script']['LD']
    Called on jPlus refresh
    """

    _psLog.debug('extendedRailroadDetails')

    configFile = PSE.readConfigFile()
    layoutDetails = configFile['Main Script']['LD']
    OSU = PSE.JMRI.jmrit.operations.setup

    layoutDetails.update({'RN':OSU.Setup.getRailroadName()})

    layoutDetails.update({'JN':makeCompositRailroadName(layoutDetails)})

    PSE.writeConfigFile(configFile)

    return

def makeCompositRailroadName(layoutDetails):
    """
    Uses jPlus layout properties to make a composite name for other OPS subroutines.
    """

    _psLog.debug('makeCompositRailroadName')

    operatingRoad = layoutDetails['OR']
    territory = layoutDetails['TR']
    location = layoutDetails['LO']

    compositeName = operatingRoad + '\n' + territory + '\n' + location

    return compositeName

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
