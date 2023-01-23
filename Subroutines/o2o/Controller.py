# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""The o2o Subroutine."""

from opsEntities import PSE
from o2oSubroutine import Listeners
from o2oSubroutine import Model
from o2oSubroutine import ModelImport
from o2oSubroutine import ModelWorkEvents
from o2oSubroutine import View
from PatternTracksSubroutine import Controller as PtController
from jPlusSubroutine import Controller as JpController

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

_psLog = PSE.LOGGING.getLogger('OPS.o2o.Controller')


def o2oSwitchList(ptSetCarsForm):
    """Make the JMRI Report - o2o Work Events.csv file.
        There is dependency with PatternTracksSubroutine.
        """

    ModelWorkEvents.appendSetCarsForm(ptSetCarsForm)
# Convert the o2o Work Events file to the format used by TrainPlayer
    o2o = ModelWorkEvents.o2oSwitchListConversion()
    o2o.o2oSwitchListGetter()
    o2o.thinTheHerd()
    o2o.o2oSwitchListUpdater()
    o2oSwitchList = o2o.getO2oSwitchList()
# Common post processor for o2oButton and BuiltTrainExport.o2oWorkEventsBuilder.handle
    o2o = ModelWorkEvents.o2oWorkEvents(o2oSwitchList)
    o2o.o2oHeader()
    o2o.o2oLocations()
    o2o.saveList()

    return

def startDaemons():
    """Methods called when this subroutine is initialized by the Main Script.
        These calls are not turned off.
        """

    Listeners.addTrainsTableListener()

    return

def activatedCalls():
    """Methods called when this subroutine is activated."""

    Listeners.addBuiltTrainListener()

    return

def deActivatedCalls():
    """Methods called when this subroutine is deactivated."""

    Listeners.removeBuiltTrainListener()

    return

def refreshCalls():
    """Methods called when the subroutine needs to be refreshed."""

    return
    
def setDropDownText():
    """Pattern Scripts/Tools/itemMethod - Set the drop down text per the config file o2oSubroutine Include flag ['CP'][<subroutine name>]"""

    patternConfig = PSE.readConfigFile('CP')
    if patternConfig['o2oSubroutine']:
        menuText = PSE.BUNDLE[u'Disable'] + ' ' + __package__
    else:
        menuText = PSE.BUNDLE[u'Enable'] + ' ' + __package__

    return menuText, 'ooItemSelected'


class StartUp:
    """Start the o2o subroutine"""

    def __init__(self, subroutineFrame=None):

        self.subroutineFrame = subroutineFrame

        return

    def makeSubroutineFrame(self):
        """Makes the title border frame"""

        self.subroutineFrame = View.ManageGui().makeSubroutineFrame()
        subroutinePanel = self.makeSubroutinePanel()
        self.subroutineFrame.add(subroutinePanel)

        _psLog.info('o2o makeFrame completed')

        return self.subroutineFrame

    def makeSubroutinePanel(self):
        """Makes the control panel that sits inside the frame"""

        self.subroutinePanel, self.widgets = View.ManageGui().makeSubroutinePanel()
        self.activateWidgets()

        return self.subroutinePanel

    def startUpTasks(self):
        """Run these tasks when this subroutine is started."""

        return

    def activateWidgets(self):
        """The *.getName value is the name of the action for the widget.
            IE: newJmriRailroad, updateJmriRailroad
            """

        for widget in self.widgets:
            widget.actionPerformed = getattr(self, widget.getName())

        return

    def newJmriRailroad(self, EVENT):
        """Creates a new JMRI railroad from the tpRailroadData.json file"""

        _psLog.debug(EVENT)

        PSE.closeOutputFrame()

        if ModelImport.importTpRailroad():
            print('TrainPlayer railroad data imported OK')
            _psLog.info('TrainPlayer railroad data imported OK')
        else:
            print('TrainPlayer railroad not imported')
            _psLog.critical('TrainPlayer railroad not imported')
            return

        if Model.newJmriRailroad():

            configfile = PSE.readConfigFile()
            configfile['PT'].update({'PD': ''})
            configfile['PT'].update({'PL': ''})
            PSE.writeConfigFile(configfile)

            PSE.restartAllSubroutines()

            print('New JMRI railroad built from TrainPlayer data')
            _psLog.info('New JMRI railroad built from TrainPlayer data')
        else:
            print('New JMRI railroad not built')
            _psLog.critical('New JMRI railroad not built')

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def updateJmriRailroad(self, EVENT):
        """Updates the locations data and writes new car and engine data."""

        _psLog.debug(EVENT)

        PSE.closeOutputFrame()

        if ModelImport.importTpRailroad():
            print('TrainPlayer railroad data imported OK')
            _psLog.info('TrainPlayer railroad data imported OK')
        else:
            print('TrainPlayer railroad not imported')
            _psLog.critical('TrainPlayer railroad not imported')
            return

        if Model.updateJmriRailroad():

            configfile = PSE.readConfigFile()
            configfile['PT'].update({'PD': ''})
            configfile['PT'].update({'PL': ''})
            PSE.writeConfigFile(configfile)

            PSE.restartAllSubroutines()

            print('JMRI railroad updated from TrainPlayer data')
            _psLog.info('JMRI railroad updated from TrainPlayer data')
        else:
            print('JMRI railroad not updated')
            _psLog.critical('JMRI railroad not updated')

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return

    def updateJmriRollingingStock(self, EVENT):
        """Writes new car and engine data."""

        _psLog.debug(EVENT)

        PSE.closeOutputFrame()

        if ModelImport.importTpRailroad():
            print('TrainPlayer railroad data imported OK')
            _psLog.info('TrainPlayer railroad data imported OK')
        else:
            print('TrainPlayer railroad not imported')
            _psLog.critical('TrainPlayer railroad not imported')
            return

        if Model.updateJmriRollingingStock():
            print('JMRI rolling stock updated')
            _psLog.info('JMRI rolling stock updated')
        else:
            print('JMRI rolling stock not updated')
            _psLog.critical('JMRI rolling stock not updated')

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return
