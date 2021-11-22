# coding=utf-8
# Extended ìÄÅÉî
# build the plugin into different locations
# No restrictions on use
# © 2021 Greg Ritacco

# Edit PatternConfig.json - PluginLocation
import jmri
import java.awt
import javax.swing
from apps import Apps

def trainsTable():
    '''The plugin will be added to the bottom of the trains window'''

    return  jmri.jmrit.operations.trains.TrainsTableFrame()

def homeScreen():
    '''Add the plugin to the Panel Pro home screen'''
# NOTE: This location does not support DecoderPro.
    return Apps.buttonSpace()

def uniqueWindow():
    '''Add the plugin to its own window'''

    piButton = javax.swing.JButton()
    piButton.text = u'PatternScripts'
    Apps.buttonSpace().add(piButton)
    Apps.buttonSpace().revalidate()
    piFrame = javax.swing.JFrame()
    iconPath = jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts\\decpro5.png'
    icon = java.awt.Toolkit.getDefaultToolkit().getImage(iconPath)
    piFrame.setIconImage(icon)
    return
