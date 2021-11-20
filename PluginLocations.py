# coding=utf-8
# Extended ìÄÅÉî
# build the plugin into different locations
# No restrictions on use
# © 2021 Greg Ritacco 

# Edit PatternConfig.json - PluginLocation
import jmri
from apps import Apps

def trainsTable():
    '''The plugin will be added to the bottom of the trains window'''

    return  jmri.jmrit.operations.trains.TrainsTableFrame()

def homeScreen():
    '''Add the plugin to the Panel Pro home screen'''

# NOTE: This location does not support DecoderPro.
    return Apps.buttonSpace()
