# coding=utf-8
# © 2023 Greg Ritacco

"""
Display methods for the Set Cars Form for Track X form
"""

from opsEntities import PSE
from Subroutines.Patterns import GUI

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

_psLog = PSE.LOGGING.getLogger('OPS.PT.ViewSetCarsForm')

class ManageSetCarsGui:

    def __init__(self, setCarsForm):

        self.setCarsForm = setCarsForm
        self.setCarsData = None
        self.allSetCarsWidgets = None

        return

    def makeSetCarsFrame(self):

        self.setCarsData, self.allSetCarsWidgets = GUI.makeSetCarsForTrackForm(self.setCarsForm)

        return

    def getSetCarsForTrackWindow(self):

        setCarsWindow = GUI.setCarsForTrackWindow(self.setCarsData)

        return setCarsWindow

    def getButtonDict(self):

        return self.allSetCarsWidgets

class ManagePopUp:

    def __init__(self):

        self.popupWidgets = None

        return

    def getPopupFrame(self):

        popupFrame, self.popupWidgets = GUI.setCarsPopup()

        return popupFrame

    def getPopupWidgets(self):

        return self.popupWidgets
   