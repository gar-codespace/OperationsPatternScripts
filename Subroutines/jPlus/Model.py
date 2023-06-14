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

    PSE.writeConfigFile(configFile)

    return

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
