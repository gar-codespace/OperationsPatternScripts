"""Keep all the listeners in one place."""

from opsEntities import PSE

SCRIPT_NAME = 'OperationsPatternScripts.opsEntities.Listeners'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('OPS.OE.Listeners')


class LocationComboBox(PSE.JAVA_AWT.event.ActionListener):
    """Event triggered from location combobox use."""

    def __init__(self, subroutineFrame):

        self.subroutineFrame = subroutineFrame

        return

    def actionPerformed(self, EVENT):

        xModule = __import__('PatternTracksSubroutine', globals(), locals(), ['Controller', 'Model'], 0)

        xModule.Model.updatePatternLocation(EVENT.getSource().getSelectedItem())
        xModule.Controller.restartSubroutine(self.subroutineFrame)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return


class TextBoxEntry(PSE.JAVA_AWT.event.MouseAdapter):
    """When any of the 'Set Cars Form for Track X' text input boxes is clicked on."""

    def __init__(self):

        return

    def mouseClicked(self, MOUSE_CLICKED):

        if PSE.TRACK_NAME_CLICKED_ON:
            MOUSE_CLICKED.getSource().setText(PSE.TRACK_NAME_CLICKED_ON)
        else:
            _psLog.warning('No track was selected')

        return


class TrainsTable(PSE.JAVX_SWING.event.TableModelListener):
    """Catches user add or remove train while o2oSubroutine is enabled."""

    def __init__(self, builtTrainListener):

        self.builtTrainListener = builtTrainListener

        return

    def tableChanged(self, TABLE_CHANGE):

        trainList = PSE.TM.getTrainsByIdList()
        for train in trainList:
        # Does not throw error if there is no listener to remove :)
            train.removePropertyChangeListener(self.builtTrainListener)
            train.addPropertyChangeListener(self.builtTrainListener)

        return


class BuiltTrain(PSE.JAVA_BEANS.PropertyChangeListener):
    """Starts o2oWorkEventsBuilder on trainBuilt."""

    def propertyChange(self, TRAIN_BUILT):

        if TRAIN_BUILT.propertyName == 'TrainBuilt' and TRAIN_BUILT.newValue:
            xModule = __import__('o2oSubroutine', globals(), locals(), ['BuiltTrainExport'], 0)

            o2oWorkEvents = xModule.BuiltTrainExport.o2oWorkEventsBuilder()
            o2oWorkEvents.passInTrain(TRAIN_BUILT.getSource())
            o2oWorkEvents.start()

        return


class PatternScriptsWindow(PSE.JAVA_AWT.event.WindowListener):
    """Listener to respond to the plugin window operations.
        May be expanded in v3.
        """

    def __init__(self):

        return

    def windowClosed(self, WINDOW_CLOSED):

        button = PSE.getPsButton()
        button.setEnabled(True)

        return

    def windowClosing(self, WINDOW_CLOSING):

        PSE.updateWindowParams(WINDOW_CLOSING.getSource())
        PSE.closeSetCarsWindows()
        WINDOW_CLOSING.getSource().dispose()

        return

    def windowOpened(self, WINDOW_OPENED):

        button = PSE.getPsButton()
        button.setEnabled(False)

        return

    def windowIconified(self, WINDOW_ICONIFIED):
        return
    def windowDeiconified(self, WINDOW_DEICONIFIED):
        return
    def windowActivated(self, WINDOW_ACTIVATED):
        return
    def windowDeactivated(self, WINDOW_DEACTIVATED):
        return
