# coding=utf-8
# © 2023 Greg Ritacco

"""jPlus"""

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
    
    configFile = PSE.readConfigFile()
    try:
        configFile['Main Script']['CP']['Subroutines.jPlus']
    except:
        return

    OSU = PSE.JMRI.jmrit.operations.setup
    yr = OSU.Setup.getYearModeled()

    configFile['Main Script']['LD'].update({'YR':yr})
    PSE.writeConfigFile(configFile)

    try: # PS plugin started with jPlus hidden
        frameTitle = PSE.BUNDLE['Pattern Scripts']
        targetPanel = PSE.getComponentByName(frameTitle, 'yearModeled')
        targetPanel.setText(yr)
    except:
        pass

    return

def activateExtendedHeader():
    """
    Sets configFile['Main Script]['CP']['EH"] to true.
    """

    configFile = PSE.readConfigFile()
    configFile['Main Script']['CP'].update({'EH':True})
    PSE.writeConfigFile(configFile)

    return

def deactivateExtendedHeader():
    """
    Sets configFile['Main Script]['CP']['EH"] to false.
    """

    configFile = PSE.readConfigFile()
    configFile['Main Script']['CP'].update({'EH':False})
    PSE.writeConfigFile(configFile)

    return
