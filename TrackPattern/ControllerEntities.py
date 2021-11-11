# coding=utf-8
# Extended ìÄÅÉî
# Controller script for the track pattern subroutine
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import logging
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts')
import MainScriptEntities
import TrackPattern.View
import TrackPattern.Model
import TrackPattern.ViewSetCarsForm

def buttonBoilerplate(controls):
    '''Updates the config file when a button is pressed'''

    focusOn = MainScriptEntities.readConfigFile('TP')
    focusOn.update({"PL": controls[0].text})
    focusOn.update({"PA": controls[1].selected})
    focusOn.update({"PI": controls[2].selected})
    focusOn.update({"PT": TrackPattern.Model.getAllTracks(controls[3])})
    newConfigFile = MainScriptEntities.readConfigFile('all')
    newConfigFile.update({"TP": focusOn})
    MainScriptEntities.updateConfigFile(newConfigFile)

    return
