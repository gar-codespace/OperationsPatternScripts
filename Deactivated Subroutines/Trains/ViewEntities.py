# coding=utf-8
# © 2023 Greg Ritacco

"""
Template subroutine.
Replace XX with a designator for this subroutines name.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230201

class templateSubroutinePanel:

    def __init__(self):
        """The *.setName value is the name of the action for the widget"""

        self.controlWidgets = []

        return

    def templatePanelMaker(self):
        """Build the GUI here."""

        tpPanel = PSE.JAVX_SWING.JPanel()
        tableModel = PSE.JMRI.jmrit.operations.trains.TrainsTableModel()
        print(tableModel.getColumnCount())
        newTable = PSE.JAVX_SWING.JTable(tableModel)

        column = newTable.getColumnModel().getColumn(0)
        column.setPreferredWidth(50)

        
        scrollPanel = PSE.JAVX_SWING.JScrollPane(newTable)
        newTable.setFillsViewportHeight(True)
        tpPanel.add(scrollPanel)





        # scrollPanel.border = PSE.JAVX_SWING.BorderFactory.createLineBorder(PSE.JAVA_AWT.Color.GRAY)
        # scrollPanel.setName('scrollPanel')




        # JScrollPane scrollPane = new JScrollPane(table);
        # tpPanel.add(table)

        nrButton = PSE.JAVX_SWING.JButton()
        nrButton.setText(PSE.BUNDLE['xyzzy'])
        nrButton.setName('button')
        self.controlWidgets.append(nrButton)

        # tpPanel.add(nrButton)
        # tpPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(20,0)))

        return tpPanel

    def templateWidgetGetter(self):
        """Returns all the widgets."""

        return self.controlWidgets
