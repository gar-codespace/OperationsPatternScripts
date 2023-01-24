# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""

"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

class tbSubroutinePanel:

    def __init__(self):
        """The *.setName value is the name of the action for the widget"""

        self.controlWidgets = []
        self.displayWidgets = []
        self.configFile = PSE.readConfigFile()

        return

    def tbPanelMaker(self):

        snapShot = self.configFile['Throwback']['SS']

        lastSnapShot = snapShot[-1]

        tpPanel = PSE.JAVX_SWING.JPanel()

        selectionFrame = PSE.JAVX_SWING.JPanel() # the track pattern panel
        selectionFrame.setName('selectionFrame')
        selectionFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.BUNDLE[u'Total Commits'] + u' - ' + str(len(snapShot) - 1))

        actionFrame = PSE.JAVX_SWING.JPanel() # the track pattern panel
        actionFrame.setName('actionFrame')
        actionFrame.border = PSE.JAVX_SWING.BorderFactory.createTitledBorder(PSE.BUNDLE[u'Action'])

        ssButton = PSE.JAVX_SWING.JButton()
        ssButton.setText(PSE.BUNDLE[u'Commit'])
        ssButton.setName('commit')
        self.controlWidgets.append(ssButton)

        pvButton = PSE.JAVX_SWING.JButton()
        pvButton.setText(PSE.BUNDLE[u'Previous'])
        pvButton.setName('previous')
        self.controlWidgets.append(pvButton)

        timeStampLabel = PSE.JAVX_SWING.JLabel(lastSnapShot[0])
        timeStampLabel.setName('timeStamp')
        self.displayWidgets.append(timeStampLabel)

        tbText = PSE.JAVX_SWING.JTextField(20)
        tbText.setText(lastSnapShot[1])
        tbText.setName('tbText')
        self.displayWidgets.append(tbText)

        nxButton = PSE.JAVX_SWING.JButton()
        nxButton.setText(PSE.BUNDLE[u'Next'])
        nxButton.setName('next')
        self.controlWidgets.append(nxButton)

        tbButton = PSE.JAVX_SWING.JButton()
        tbButton.setText(PSE.BUNDLE[u'Throwback'])
        tbButton.setName('throwback')
        self.controlWidgets.append(tbButton)

        rsButton = PSE.JAVX_SWING.JButton()
        rsButton.setText(PSE.BUNDLE[u'Reset'])
        rsButton.setName('reset')
        self.controlWidgets.append(rsButton)

        selectionFrame.add(pvButton)
        selectionFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
        selectionFrame.add(timeStampLabel)
        selectionFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(10,0)))
        selectionFrame.add(tbText)
        selectionFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))
        selectionFrame.add(nxButton)

        actionFrame.add(ssButton)
        actionFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(10,0)))
        actionFrame.add(tbButton)
        actionFrame.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(10,0)))
        actionFrame.add(rsButton)

        tpPanel.add(selectionFrame)
        tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(40,0)))
        tpPanel.add(actionFrame)

        return tpPanel

    def tbWidgetGetter(self):

        return self.controlWidgets, self.displayWidgets

    # def getLastSnapShot(self):

    #     lastSnapShot = self.configFile['Throwback']['SS'][-1]
