"""Keep all the listeners in one place, plus a couple of utility methods."""

from opsEntities import PSE
from PatternTracksSubroutine import Controller
from PatternTracksSubroutine import Model
from o2oSubroutine import BuiltTrainExport

SCRIPT_NAME = 'OperationsPatternScripts.opsEntities.Listeners'
SCRIPT_REV = 20220101

_psLog = PSE.LOGGING.getLogger('OPS.OE.Listeners')


class LocationComboBox(PSE.JAVA_AWT.event.ActionListener):
    """Event triggered from location combobox use."""

    def __init__(self, subroutineFrame):

        self.subroutineFrame = subroutineFrame

        return

    def actionPerformed(self, EVENT):

        print('name:', self.subroutineFrame.getName())

        Model.updatePatternLocation(EVENT.getSource().getSelectedItem())
        Controller.restartSubroutine(self.subroutineFrame)

        print(SCRIPT_NAME + ' ' + str(SCRIPT_REV))

        return


class SetCarsTable(PSE.JAVA_BEANS.PropertyChangeListener):
    """ """

    def propertyChange(self, PS_WINDOW_CLOSING):

        print(PS_WINDOW_CLOSING.propertyName)

        if PS_WINDOW_CLOSING.propertyName == 'psWindowClosing' and PS_WINDOW_CLOSING.newValue:
            print('Yipee')

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
            train.removePropertyChangeListener(self.builtTrainListener)
    # Does not throw error if there is no listener to remove :)
            train.addPropertyChangeListener(self.builtTrainListener)

        return


class BuiltTrain(PSE.JAVA_BEANS.PropertyChangeListener):
    """Starts o2oWorkEventsBuilder on trainBuilt."""

    def propertyChange(self, TRAIN_BUILT):

        if TRAIN_BUILT.propertyName == 'TrainBuilt' and TRAIN_BUILT.newValue:

            o2oWorkEvents = BuiltTrainExport.o2oWorkEventsBuilder()
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
        WINDOW_CLOSED.getSource().dispose()

        return

    def windowClosing(self, WINDOW_CLOSING):

        PSE.closeSetCarsWindows()
        PSE.updateWindowParams(WINDOW_CLOSING.getSource())

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
