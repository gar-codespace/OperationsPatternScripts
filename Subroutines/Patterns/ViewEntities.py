# coding=utf-8
# © 2021, 2022 Greg Ritacco

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230101

class TrackPatternPanel:
    """Makes the pattern tracks subroutine panel
        Called by:
        View.ManageGui.makeSubroutinePanel"""

    def __init__(self):

        self.configFile = PSE.readConfigFile('Patterns')

        self.yardTracksOnly = PSE.JAVX_SWING.JCheckBox()
        self.yardTracksOnly.setText(PSE.BUNDLE['Yard tracks only'] + ' ')
        self.yardTracksOnly.setSelected(self.configFile['PA'])
        self.yardTracksOnly.setName('ytoCheckBox')

        self.ypButton = PSE.JAVX_SWING.JButton()
        self.ypButton.setText(PSE.BUNDLE['Pattern Report'])
        self.ypButton.setName('ypButton')

        self.scButton = PSE.JAVX_SWING.JButton()
        self.scButton.setText(PSE.BUNDLE['Set Rolling Stock to Track'])
        self.scButton.setName('scButton')

        self.trackCheckBoxes = []

        return

    def makeLocationRow(self):
        """Make widget row containing: 'Division:', combo box, 'Loaction:', combo box, 'Yard Tracks Only', 'Ignore Track Length'.
            PSE.LM.getComboBox() includes box.addItem(null); which is unwanted
            """

        patternComboBox = PSE.JAVX_SWING.JPanel()
        patternComboBox.setAlignmentX(PSE.JAVX_SWING.JPanel.CENTER_ALIGNMENT)

        divisionLabel = PSE.JAVX_SWING.JLabel(PSE.BUNDLE['Division:'])
        divisionList = self.configFile['AD']
        # divisionList.insert(0, '') # This is how JMRI does it.
        self.divisionComboBox = PSE.JAVX_SWING.JComboBox(divisionList)
        self.divisionComboBox.setName('jDivision')
        self.divisionComboBox.setSelectedItem(self.configFile['PD'])

        locationLabel = PSE.JAVX_SWING.JLabel(PSE.BUNDLE['Location:'])
        locationList = self.configFile['AL']
        self.locationComboBox = PSE.JAVX_SWING.JComboBox(locationList)
        self.locationComboBox.setName('jLocations')
        self.locationComboBox.setSelectedItem(self.configFile['PL'])

        patternComboBox.add(divisionLabel)
        patternComboBox.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        patternComboBox.add(self.divisionComboBox)
        patternComboBox.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        patternComboBox.add(locationLabel)
        patternComboBox.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        patternComboBox.add(self.locationComboBox)
        patternComboBox.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(8,0)))
        patternComboBox.add(self.yardTracksOnly)

        return patternComboBox

    def makeTracksRow(self):
        """Make the row of check boxes, one for each track"""

        tracksPanel = PSE.JAVX_SWING.JPanel()
        tracksPanel.setAlignmentX(PSE.JAVX_SWING.JPanel.CENTER_ALIGNMENT)

        rowLabel = PSE.JAVX_SWING.JLabel()
        tracksPanel.add(rowLabel)
        trackDict = self.configFile['PT'] # pattern tracks
        if trackDict:
            rowLabel.text = PSE.BUNDLE['Track List:'] + ' '
            for track, flag in sorted(trackDict.items()):
                trackCheckBox = tracksPanel.add(PSE.JAVX_SWING.JCheckBox(track, flag))
                self.trackCheckBoxes.append(trackCheckBox)
            self.ypButton.setEnabled(True)
            self.scButton.setEnabled(True)
        else:
            self.ypButton.setEnabled(False)
            self.scButton.setEnabled(False)
            rowLabel.text = PSE.BUNDLE['There are no tracks for this selection']

        return tracksPanel

    def makeButtonsRow(self):
        """Make the row of action buttons: 'Track Pattern', 'Set Rolling Stock.' """

        buttonPanel = PSE.JAVX_SWING.JPanel()
        buttonPanel.setAlignmentX(PSE.JAVX_SWING.JPanel.CENTER_ALIGNMENT)
        buttonPanel.add(self.ypButton)
        buttonPanel.add(PSE.JAVX_SWING.Box.createRigidArea(PSE.JAVA_AWT.Dimension(30,0)))
        buttonPanel.add(self.scButton)

        return buttonPanel

    def getPanelWidgets(self):
        """A list of the widgets created by this class"""

        panelWidgets = []
        panelWidgets.append(self.divisionComboBox)
        panelWidgets.append(self.locationComboBox)
        panelWidgets.append(self.yardTracksOnly)
        panelWidgets.append(self.trackCheckBoxes)
        panelWidgets.append(self.ypButton)
        panelWidgets.append(self.scButton)

        return panelWidgets

    def makeTrackPatternPanel(self):
        """Make the pattern tracks panel object"""

        tpPanel = PSE.JAVX_SWING.JPanel() # the pattern tracks panel
        tpPanel.setLayout(PSE.JAVX_SWING.BoxLayout(tpPanel, PSE.JAVX_SWING.BoxLayout.Y_AXIS))

        tpPanel.add(self.makeLocationRow())
        tpPanel.add(self.makeTracksRow())
        tpPanel.add(self.makeButtonsRow())

        return tpPanel


def makeReportItemWidthMatrix():
    """The attribute widths (AW) for each of the rolling stock attributes is defined in the report matrix (RM) of the config file.
        Called by:
        """

    reportMatrix = {}
    attributeWidths = PSE.readConfigFile('Patterns')['RM']['AW']

    for aKey, aValue in attributeWidths.items():
        reportMatrix[aKey] = aValue

    return reportMatrix

def modifyTrackPatternReport(trackPattern):
    """Make adjustments to the way the reports display here.
        The undeflying json is not changed.
        Replaces blank Dest and FD with standins.
        Replaces load type with short load type.
        Called by:
        View.trackPatternButton
        View.setRsButton
        ModelSetCarsForm.makeMergedForm
        """

    standins = PSE.readConfigFile('Patterns')['RM']

    tracks = trackPattern['locations'][0]['tracks']
    for track in tracks:
        for loco in track['locos']:
            destStandin, fdStandin = getStandins(loco, standins)
            loco.update({'Destination': destStandin})

        for car in track['cars']:
            destStandin, fdStandin = getStandins(car, standins)
            car.update({'Destination': destStandin})
            car.update({'Final Dest': fdStandin})
            shortLoadType = PSE.getShortLoadType(car)
            car.update({'Load Type': shortLoadType})

    return trackPattern

def getStandins(car, standins):
    """Replaces null destination and fd with the standin from the config file
        Called by:
        modifyTrackPatternReport
        """

    destStandin = car['Destination']
    if not car['Destination']:
        destStandin = standins['DS']

    try: # No FD for locos
        fdStandin = car['Final Dest']
        if not car['Final Dest']:
            fdStandin = standins['FD']
    except:
        fdStandin = ''

    return destStandin, fdStandin
    
def makeTextReportHeader(textWorkEventList):
    """Makes the header for generic text reports
        Called by:
        View.ManageGui.trackPatternButton'
        ViewSetCarsForm.switchListButton
        """

    patternLocation = PSE.readConfigFile('Patterns')['PL']
    divisionName = textWorkEventList['division']
    workLocation = ''
    if divisionName:
        workLocation = divisionName + ' - ' + patternLocation
    else:
        workLocation = patternLocation

    textReportHeader    = textWorkEventList['railroadName'] + '\n\n' \
                        + PSE.BUNDLE['Work Location:'] + ' ' + workLocation + '\n' \
                        + textWorkEventList['date'] + '\n\n'

    return textReportHeader

def makeTextReportLocations(textWorkEventList, trackTotals):
    """Makes the body for generic text reports
        Called by:
        View.ManageGui.trackPatternButton'
        ViewSetCarsForm.switchListButton
        """

    locoItems = PSE.JMRI.jmrit.operations.setup.Setup.getDropEngineMessageFormat()
    carItems = PSE.JMRI.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()

    reportSwitchList = ''
    reportTally = [] # running total for all tracks
    for track in textWorkEventList['locations'][0]['tracks']:
        lengthOfLocos = 0
        lengthOfCars = 0
        trackTally = []
        trackName = track['trackName']
        trackLength = track['length']
        reportSwitchList += PSE.BUNDLE['Track:'] + ' ' + trackName + '\n'
        switchListRow = ''

        for loco in track['locos']:
            lengthOfLocos += int(loco['Length']) + 4
            reportSwitchList += loco['Set_To'] + loopThroughRs('loco', loco) + '\n'

        for car in track['cars']:
            lengthOfCars += int(car['Length']) + 4
            reportSwitchList += car['Set_To'] + loopThroughRs('car', car) + '\n'
            trackTally.append(car['Final Dest'])
            reportTally.append(car['Final Dest'])

        if trackTotals:
            totalLength = lengthOfLocos + lengthOfCars
            reportSwitchList += PSE.BUNDLE['Total Cars:'] + ' ' \
                + str(len(track['cars'])) + ' ' + PSE.BUNDLE['Track Length:']  + ' ' \
                + str(trackLength) +  ' ' + PSE.BUNDLE['Eqpt. Length:']  + ' ' \
                + str(totalLength) + ' ' +  PSE.BUNDLE['Available:']  + ' '  \
                + str(trackLength - totalLength) \
                + '\n\n'
            reportSwitchList += PSE.BUNDLE['Track Totals for Cars:'] + '\n'
            for track, count in sorted(PSE.occuranceTally(trackTally).items()):
                reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'
        reportSwitchList += '\n'

    if trackTotals:
        reportSwitchList += '\n' + PSE.BUNDLE['Report Totals for Cars:'] + '\n'
        for track, count in sorted(PSE.occuranceTally(reportTally).items()):
            reportSwitchList += ' ' + track + ' - ' + str(count) + '\n'

    return reportSwitchList

def loopThroughRs(type, rsAttribs):
    """Creates a line containing the attrs in get * MessageFormat
        Called by:
        makeTextReportLocations
        """

    reportWidth = PSE.REPORT_ITEM_WIDTH_MATRIX
    switchListRow = ''
    rosetta = PSE.translateMessageFormat()

    if type == 'loco':
        messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getDropEngineMessageFormat()
    if type == 'car':
        messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()

    for lookup in messageFormat:
        item = rosetta[lookup]

        if 'Tab' in item:
            continue

        itemWidth = reportWidth[item]
        switchListRow += PSE.formatText(rsAttribs[item], itemWidth)

    return switchListRow

def makeTrackPatternCsv(trackPattern):
    """Notice that I added a double quote for the railroadName entry.
        The csv import keeps the j Pluse extended data in thr csv RN field.
        CSV writer does not support utf-8
        Called by:
        Model.writeTrackPatternCsv
        """

    trackPatternCsv = u'Operator,Description,Parameters\n' \
                    u'RT,Report Type,' + trackPattern['trainDescription'] + '\n' \
                    u'RN,Railroad Name,"' + trackPattern['railroadName'] + '"\n' \
                    u'LN,Location Name,' + trackPattern['locations'][0]['locationName'] + '\n' \
                    u'PRNTR,Printer Name,\n' \
                    u'YPC,Yard Pattern Comment,' + trackPattern['trainComment'] + '\n' \
                    u'VT,Valid,' + trackPattern['date'] + '\n'
    for track in trackPattern['locations'][0]['tracks']: # There is only one location
        trackPatternCsv += u'TN,Track name,' + unicode(track['trackName'], PSE.ENCODING) + '\n'
        trackPatternCsv += u'Set_To,Road,Number,Type,Model,Length,Weight,Consist,Owner,Track,Location,Destination,Comment\n'
        for loco in track['locos']:
            trackPatternCsv +=  loco['Set_To'] + ',' \
                            + loco['Road'] + ',' \
                            + loco['Number'] + ',' \
                            + loco['Type'] + ',' \
                            + loco['Model'] + ',' \
                            + loco['Length'] + ',' \
                            + loco['Weight'] + ',' \
                            + loco['Consist'] + ',' \
                            + loco['Owner'] + ',' \
                            + loco['Track'] + ',' \
                            + loco['Location'] + ',' \
                            + loco['Destination'] + ',' \
                            + loco['Comment'] + ',' \
                            + '\n'
        trackPatternCsv += u'Set_To,Road,Number,Type,Length,Weight,Load,Load_Type,Hazardous,Color,Kernel,Kernel_Size,Owner,Track,Location,Destination,Dest&Track,Final_Dest,FD&Track,Comment,Drop_Comment,Pickup_Comment,RWE\n'
        for car in track['cars']:
            trackPatternCsv +=  car['Set_To'] + ',' \
                            + car['Road'] + ',' \
                            + car['Number'] + ',' \
                            + car['Type'] + ',' \
                            + car['Length'] + ',' \
                            + car['Weight'] + ',' \
                            + car['Load'] + ',' \
                            + car['Load Type'] + ',' \
                            + str(car['Hazardous']) + ',' \
                            + car['Color'] + ',' \
                            + car['Kernel'] + ',' \
                            + car['Kernel Size'] + ',' \
                            + car['Owner'] + ',' \
                            + car['Track'] + ',' \
                            + car['Location'] + ',' \
                            + car['Destination'] + ',' \
                            + car['Dest&Track'] + ',' \
                            + car['Final Dest'] + ',' \
                            + car['FD&Track'] + ',' \
                            + car['Comment'] + ',' \
                            + car['SetOut Msg'] + ',' \
                            + car['PickUp Msg'] + ',' \
                            + car['RWE'] \
                            + '\n'

    return trackPatternCsv
