# coding=utf-8
# Extended ìÄÅÉî
# build the plugin into different locations
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import java.awt
import javax.swing
from apps import Apps

def trainsTable():
    '''Add the plugin to the bottom of the trains window'''

    return  jmri.jmrit.operations.trains.TrainsTableFrame()

def homeScreen():
    '''Add the plugin to the Panel Pro home screen
NOTE: This location does not support DecoderPro'''

    return Apps.buttonSpace()

def uniqueWindow():
    '''Add the plugin to its own window'''

    piFrame = javax.swing.JFrame('Pattern Scripts')
    iconPath = jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsPatternScripts\\decpro5.png'
    icon = java.awt.Toolkit.getDefaultToolkit().getImage(iconPath)
    piFrame.setIconImage(icon)
    piFrame.setLocationRelativeTo(Apps.buttonSpace())
    piFrame.setSize(600,200)
    piFrame.setDefaultCloseOperation(javax.swing.JFrame.HIDE_ON_CLOSE)

    return piFrame
