# coding=utf-8
# Extended ìÄÅÉî
# support methods for the view script
# No restrictions on use
# © 2021 Greg Ritacco

import jmri
import java.awt
import javax.swing

def makeSwingBox(xWidth, xHeight):
    ''' Makes a swing box to the desired size'''

    xName = javax.swing.Box(javax.swing.BoxLayout.X_AXIS)
    xName.setPreferredSize(java.awt.Dimension(width=xWidth, height=xHeight))
    return xName

def makeWindow():
    '''Makes a swing frame with the desired name'''

    pFrame = javax.swing.JFrame()
    pFrame.contentPane.setLayout(javax.swing.BoxLayout(pFrame.contentPane, javax.swing.BoxLayout.Y_AXIS))
    pFrame.contentPane.setAlignmentX(java.awt.Component.LEFT_ALIGNMENT)
    pFrame.contentPane.setAlignmentX(0.0)
    iconPath = jmri.util.FileUtil.getHomePath() + 'JMRI\\OperationsYardPattern\\decpro5.png'
    icon = java.awt.Toolkit.getDefaultToolkit().getImage(iconPath)
    pFrame.setIconImage(icon)
    return pFrame
