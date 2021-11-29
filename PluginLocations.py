# coding=utf-8
# Extended ìÄÅÉî
# build the plugin into different locations
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import jmri.util
import java.awt
import javax.swing
from apps import Apps
from sys import path
path.append(jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts')
import MainScriptEntities

scriptRev = 'OperationsPatternScripts.PluginLocations v20211125'

def trainsTable():
    '''Add the plugin to the bottom of the trains window'''

    print(scriptRev)

    return  jmri.jmrit.operations.trains.TrainsTableFrame()

def homeScreen():
    '''Add the plugin to the Panel Pro home screen
NOTE: This location does not support DecoderPro'''

    print(scriptRev)

    return Apps.buttonSpace()

def uniqueWindow():
    '''Add the plugin to its own window'''

    print(scriptRev)

    return jmri.util.JmriJFrame(u'Pattern Scripts')
