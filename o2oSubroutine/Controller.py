# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""The o2o Subroutine."""

from opsEntities import PSE
from o2oSubroutine import Model
from o2oSubroutine import ModelImport
from o2oSubroutine import ModelWorkEvents
from o2oSubroutine import View
from PatternTracksSubroutine import Controller as PtController
from jPlusSubroutine import Controller as JpController

SCRIPT_NAME = 'OperationsPatternScripts.o2oSubroutine.Controller'
SCRIPT_REV = 20221010

_psLog = PSE.LOGGING.getLogger('OPS.o2o.Controller')


def o2oSwitchList(ptSetCarsForm):
    """Make the JMRI Report - o2o Work Events.csv file"""

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

def updateSubroutine(parent):
    """Allows other subroutines to update and restart the o2o Sub.
        Not implemented.
        """

    if not parent:
        return

    # Do stuff here.

    for component in parent.getComponents():
        if component.getName() == 'o2oSubroutine':
            restartSubroutine(component.getComponents()[0])

    return

def restartSubroutine(subroutineFrame):
    """Subroutine restarter.
        Used by:
        updateSubroutine
        """

    subroutinePanel = StartUp(subroutineFrame).makeSubroutinePanel()
    subroutineFrame.removeAll()
    subroutineFrame.add(subroutinePanel)
    subroutineFrame.revalidate()

    return

def setDropDownText():
    """itemMethod - Set the drop down text per the config file o2oSubroutine Include flag ['CP']['IO']"""

    patternConfig = PSE.readConfigFile('CP')
    if patternConfig['o2oSubroutine']:
        menuText = PSE.BUNDLE[u'Disable o2o subroutine']
    else:
        menuText = PSE.BUNDLE[u'Enable o2o subroutine']

    return menuText, 'ooItemSelected'

def actionListener(EVENT):
    """menu item-Tools/Enable o2o subroutine"""

    _psLog.debug(EVENT)
    patternConfig = PSE.readConfigFile()

    if patternConfig['CP']['o2oSubroutine']: # If enabled, turn it off
        patternConfig['CP']['o2oSubroutine'] = False
        EVENT.getSource().setText(PSE.BUNDLE[u'Enable o2o subroutine'])

        # self.removeTrainsTableListener()
        # self.removeBuiltTrainListener()

        _psLog.info('o2o subroutine deactivated')
        print('o2o subroutine deactivated')
    else:
        patternConfig['CP']['o2oSubroutine'] = True
        EVENT.getSource().setText(PSE.BUNDLE[u'Disable o2o subroutine'])

        # self.addTrainsTableListener()
        # self.addBuiltTrainListener()

        _psLog.info('o2o subroutine activated')
        print('o2o subroutine activated')

    PSE.writeConfigFile(patternConfig)
    # self.shutdownPlugin()
    # self.startupPlugin()

    return


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

        PSE.closeOutputPanel()

        if ModelImport.importTpRailroad():
            print('TrainPlayer railroad data imported OK')
            _psLog.info('TrainPlayer railroad data imported OK')
        else:
            print('TrainPlayer railroad not imported')
            _psLog.critical('TrainPlayer railroad not imported')
            return

        if Model.newJmriRailroad():
            parent = PSE.findPluginPanel(EVENT.getSource())
            PtController.updateSubroutine(parent)
            JpController.updateSubroutine(parent)

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

        PSE.closeOutputPanel()

        if ModelImport.importTpRailroad():
            print('TrainPlayer railroad data imported OK')
            _psLog.info('TrainPlayer railroad data imported OK')
        else:
            print('TrainPlayer railroad not imported')
            _psLog.critical('TrainPlayer railroad not imported')
            return

        if Model.updateJmriRailroad():
            # parent = EVENT.getSource().getParent().getParent().getParent().getParent()
            parent = PSE.findPluginPanel(EVENT.getSource())
            PtController.updateSubroutine(parent)
            JpController.updateSubroutine(parent)

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

        PSE.closeOutputPanel()

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
