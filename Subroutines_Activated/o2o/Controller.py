# coding=utf-8
# © 2023 Greg Ritacco

"""
The o2o Subroutine creates a JMRI railroad from TrainPlayer data.
It also exports a JMRI manifest and Patterns switch list into a Quick Keys work events list.
On the TrainPlayer side, the Quick Keys suite of scripts is used to import from and export to the JMRI railroad.
"""

from opsEntities import PSE
from Subroutines_Activated.o2o import Listeners
from Subroutines_Activated.o2o import Model
from Subroutines_Activated.o2o import ModelImport
from Subroutines_Activated.o2o import View

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

_psLog = PSE.LOGGING.getLogger('OPS.o2o.Controller')

def getSubroutineDropDownItem():
    """Pattern Scripts/Tools/'Show or disable' Subroutines.<subroutine>"""

    subroutineName = __package__.split('.')[1]

    menuItem = PSE.JAVX_SWING.JMenuItem()

    configFile = PSE.readConfigFile()
    if configFile[subroutineName]['SV']:
        menuText = PSE.getBundleItem('Hide') + ' ' + __package__
    else:
        menuText = PSE.getBundleItem('Show') + ' ' + __package__

    menuItem.setName(__package__)
    menuItem.setText(menuText)

    return menuItem


class StartUp:
    """Start the o2o subroutine"""

    def __init__(self):

        self.configFile = PSE.readConfigFile()

        return

    def getSubroutine(self):
        """
        Returns the subroutine and activates the widgets.
        """

        subroutine, self.widgets = View.ManageGui().makeSubroutine()
        subroutineName = __package__.split('.')[1]
        subroutine.setVisible(self.configFile[subroutineName]['SV'])
        self.activateWidgets()

        _psLog.info(__package__ + ' makeFrame completed')

        return subroutine

    def startUpTasks(self):

        PSE.LM.addPropertyChangeListener(Listeners.ListenToThePSWindow())
        
        return

    def activateWidgets(self):
        """
        The *.getName value is the name of the action for the widget.
        IE: initializeJmriRailroad, updateJmriLocations
        """

        for widget in self.widgets:
            widget.actionPerformed = getattr(self, widget.getName())

        return

    def getWidget(self, name):

        for widget in self.widgets:
            if widget.getName() == name:
                return widget
            
    def initializeJmriRailroad(self, EVENT):
        """
        Initializes JMRI Cars, Engines, and Locations.
        Backs up Trains and Routes.
        """

        _psLog.debug(EVENT)

        if not ModelImport.importTpRailroad():
            return
        
        PSE.closeWindowByLevel(level=1)

        firstPress = PSE.getBundleItem('Initialize Railroad')
        secondPress = PSE.getBundleItem('Confirm')

        if EVENT.getSource().text == firstPress:
            EVENT.getSource().setText(secondPress)
            self.getWidget('cancel').setVisible(True)
        else:
            Model.resetBuiltTrains()
            Model.initializeJmriRailroad()
            EVENT.getSource().setText(firstPress)
            self.getWidget('cancel').setVisible(False)

            PSE.LM.firePropertyChange('jmriDataSets', False, True)
            PSE.LM.firePropertyChange('extendedDetails', False, True)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))
        return

    def updateJmriLocations(self, EVENT):
        """
        Applies changes made to the TrainPlayer/OC/Locations tab.
        """

        _psLog.debug(EVENT)

        if not ModelImport.importTpRailroad():
            return

        PSE.closeWindowByLevel(level=2)

        Model.resetBuiltTrains()
        Model.updateJmriLocations()

        PSE.LM.firePropertyChange('jmriDataSets', False, True)
        PSE.LM.firePropertyChange('extendedDetails', False, True)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def updateJmriTracks(self, EVENT):
        """
        Applies changes made to the TrainPlayer/OC/Industries tab.
        """

        _psLog.debug(EVENT)

        if not ModelImport.importTpRailroad():
            return

        PSE.closeWindowByLevel(level=2)

        Model.resetBuiltTrains()
        Model.updateJmriTracks()

        PSE.LM.firePropertyChange('jmriDataSets', False, True)
        PSE.LM.firePropertyChange('extendedDetails', False, True)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return
    
    def updateJmriRollingingStock(self, EVENT):
        """
        Writes new or updated car and engine data.
        """

        _psLog.debug(EVENT)

        if not ModelImport.importTpRailroad():
            return

        PSE.closeWindowByLevel(level=2)

        Model.resetBuiltTrains()
        Model.updateJmriRollingingStock()

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def updateJmriProperties(self, EVENT):
        """
        Writes the extended railroad details.
        """

        _psLog.debug(EVENT)

        if not ModelImport.importTpRailroad():
            return
        
        Model.updateJmriProperties()

        PSE.LM.firePropertyChange('extendedDetails', False, True)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def cancel(self, EVENT):
        """
        Cancel the initialization.
        """

        EVENT.getSource().setVisible(False)
        self.getWidget('initializeJmriRailroad').setText(PSE.getBundleItem('Initialize Railroad'))

        return