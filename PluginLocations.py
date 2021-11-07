# coding=utf-8
# Extended ìÄÅÉî
# build the plugin into different locations
# No restrictions on use
# © 2021 Greg Ritacco

# Edit PatternConfig.json - PluginLocation
import jmri

def trainsTable():
    '''The plugin will be added to the bottom of the trains window'''
    
    return  jmri.jmrit.operations.trains.TrainsTableFrame()
