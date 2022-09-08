# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Process methods for the Set Cars Form for Track X form"""

from psEntities import PatternScriptEntities
from PatternTracksSubroutine import ModelEntities
from o2oSubroutine import ModelWorkEvents

SCRIPT_NAME = 'OperationsPatternScripts.PatternTracksSubroutine.ModelSetCarsForm'
SCRIPT_REV = 20220101

_psLog = PatternScriptEntities.LOGGING.getLogger('PS.PT.ModelSetCarsForm')

def switchListButton(setCarsForm, textBoxEntry):
    """Mini controller when the Track Pattern Report button is pressed
        Formats and displays the Switch List for Track report
        Used by:
        ControllerSetCarsForm.CreateSetCarsFormGui.switchListButton
        """

    userInputList = makeUserInputList(textBoxEntry)
    mergedForm = mergeForms(setCarsForm, userInputList)
    workEventName = ModelEntities.writeWorkEventListAsJson(mergedForm)

    return

def makeUserInputList(textBoxEntry):
    """Used by:
        switchListButton
        """

    userInputList = []
    for userInput in textBoxEntry:
        userInputList.append(unicode(userInput.getText(), PatternScriptEntities.ENCODING))

    return userInputList

def mergeForms(setCarsForm, userInputList):
    """Merge the values in textBoxEntry into the ['Set to'] field of setCarsForm.
        This preps the setCarsForm for the o2o sub.
        Used by:
        switchListButton
        """

    _psLog.debug('ModelSetCarsForm.mergeForms')

    longestTrackString = findLongestTrackString()
    allTracksAtLoc = ModelEntities.getTracksByLocation(None)

    i = 0
    locos = setCarsForm['locations'][0]['tracks'][0]['locos']
    for loco in locos:
        setTrack = PatternScriptEntities.BUNDLE['Hold']
        setTrack = PatternScriptEntities.formatText('[' + setTrack + ']', longestTrackString + 1)
        loco.update({'Set_To': setTrack})

        userInput = unicode(userInputList[i], PatternScriptEntities.ENCODING)
        if userInput in allTracksAtLoc:
            setTrack = PatternScriptEntities.formatText('[' + userInput + ']', longestTrackString + 1)
            loco.update({'Set_To': setTrack})
        i += 1

    cars = setCarsForm['locations'][0]['tracks'][0]['cars']
    for car in cars:
        setTrack = PatternScriptEntities.BUNDLE['Hold']
        setTrack = PatternScriptEntities.formatText('[' + setTrack + ']', longestTrackString + 1)
        car.update({'Set_To': setTrack})

        userInput = unicode(userInputList[i], PatternScriptEntities.ENCODING)
        if userInput in allTracksAtLoc:
            setTrack = PatternScriptEntities.formatText('[' + userInput + ']', longestTrackString + 1)
            car.update({'Set_To': setTrack})
        i += 1

    return setCarsForm

def findLongestTrackString():
    """Used by:
        mergeForms
        """

    longestTrackString = 6 # 6 is the length of [Hold]
    for track in PatternScriptEntities.readConfigFile('PT')['PT']: # Pattern Tracks
        if len(track) > longestTrackString:
            longestTrackString = len(track)

    return longestTrackString

def testValidityOfForm(setCarsForm, textBoxEntry):
    """Checks that both submitted forms are the same length
        Used by:
        ControllerSetCarsForm.CreateSetCarsFormGui.quickCheck
        """

    _psLog.debug('ModelSetCarsForm.testValidityOfForm')

    locoCount = len(setCarsForm['locations'][0]['tracks'][0]['locos'])
    carCount = len(setCarsForm['locations'][0]['tracks'][0]['cars'])

    if len(textBoxEntry) == locoCount + carCount:
        return True
    else:
        _psLog.critical('mismatched input list and car roster lengths')
        return False

def setRsToTrack(mergedForm):
    """When the set cars to track button of any set cars form is pressed"""

    _psLog.debug('ModelSetCarsForm.setRsToTrack')

    setCount = 0

    for loco in mergedForm['locations']['locos']:
        locoObject =  PatternScriptEntities.EM.getByRoadAndNumber(loco['Road'], loco['Number'])
        updatedRs = UpdateRollingStock(locoObject, loco['Set to'])
        setResult = updatedRs.setRollingStock()
        if setResult == 'okay':
            setCount += 1
    # PatternScriptEntities.EMX.save()

    for car in mergedForm['locations']['cars']:
        carObject =  PatternScriptEntities.CM.getByRoadAndNumber(car['Road'], car['Number'])
        updatedRs = UpdateRollingStock(carObject, car['Set to'])
        setResult = updatedRs.setRollingStock()
        if setResult == 'okay':
            updatedRs.rsUpdate()
            updatedRs.scheduleUpdate()
            setCount += 1
    # PatternScriptEntities.CMX.save()

    _psLog.info('Rolling stock count: ' + str(setCount) + ', processed.')

    return

class UpdateRollingStock:
    """Used by:
        setRsToTrack
        """

    def __init__(self, rollingStock, track):

        self.rollingStock = rollingStock

        location = PatternScriptEntities.readConfigFile('PT')['PL']
        self.toLocation = PatternScriptEntities.LM.getLocationByName(unicode(location, PatternScriptEntities.ENCODING))
        self.toTrack = self.toLocation.getTrackByName(unicode(track, PatternScriptEntities.ENCODING), None)

        return

    def setRollingStock(self):
        """Sets rolling stock to the chosen track.
            Subject to track type and load. Track length may be overidden.
            """
        ignoreTrackLength = PatternScriptEntities.readConfigFile('PT')['PI']
        if ignoreTrackLength:
            setResult = self.rollingStock.setLocation(self.toLocation, self.toTrack, True)
        else:
            setResult = self.rollingStock.setLocation(self.toLocation, self.toTrack)

        return setResult

    def rsUpdate(self):

        if self.toTrack.getTrackType() == 'Spur':
            self.rollingStock.setMoves(self.rollingStock.getMoves() + 1)

        self.rollingStock.setFinalDestinationTrack(None)
        self.rollingStock.setFinalDestination(None)

        return

    def scheduleUpdate(self):
        """If the to-track is a spur, try to set the load/empty requirement for the track
            Honors apply schedule flag. Toggles default L/E for spurs.
            """

        schedule = PatternScriptEntities.SM.getScheduleByName(self.toTrack.getScheduleName())
        if schedule and PatternScriptEntities.readConfigFile('PT')['AS']:
            carType = self.rollingStock.getTypeName()
            self.rollingStock.setLoadName(schedule.getItemByType(carType).getShipLoadName())
            self.rollingStock.setDestination(schedule.getItemByType(carType).getDestination(), schedule.getItemByType(carType).getDestinationTrack(), True) # force set dest
            schedule.getItemByType(carType).setHits(schedule.getItemByType(carType).getHits() + 1)
        else:
            if self.toTrack.getTrackType() == 'Spur':
                self.rollingStock.updateLoad() # Toggles default load

        return







# def makeLocationDict(setCarsForm, textBoxEntry):
#     """Replaces car['Set to'] = [ ] with either [Hold] or ['some other valid track']"""
#
#     _psLog.debug('ModelSetCarsForm.makeLocationDict')
#
#     trackName = setCarsForm['locations'][0]['tracks'][0]['trackName']
#     location = setCarsForm['locations'][0]['locationName']
#     allTracksAtLoc = ModelEntities.getTracksByLocation(None)
#
#     userInputList = []
#     for userInput in textBoxEntry:
#         userInputList.append(unicode(userInput.getText(), PatternScriptEntities.ENCODING))
#
#     longestTrackString = 6 # 6 is the length of [Hold]
#     for track in PatternScriptEntities.readConfigFile('PT')['PT']: # Pattern Tracks
#         if len(track) > longestTrackString:
#             longestTrackString = len(track)
#
#     i = 0
#     locoList = []
#     for loco in setCarsForm['locations'][0]['tracks'][0]['locos']:
#         setTrack = PatternScriptEntities.BUNDLE['Hold']
#         userInput = unicode(userInputList[i], PatternScriptEntities.ENCODING)
#         if userInput in allTracksAtLoc and userInput != trackName:
#             setTrack = userInput
#         loco[PatternScriptEntities.BUNDLE['Set to']] = PatternScriptEntities.formatText('[' + setTrack + ']', longestTrackString + 2)
#         locoList.append(loco)
#         i += 1
#
#     carList = []
    # for car in setCarsForm['locations'][0]['tracks'][0]['cars']:
    #     setTrack = PatternScriptEntities.BUNDLE['Hold']
    #     userInput = unicode(userInputList[i], PatternScriptEntities.ENCODING)
    #     if userInput in allTracksAtLoc and userInput != trackName:
    #         setTrack = userInput
    #     car[PatternScriptEntities.BUNDLE['Set to']] = PatternScriptEntities.formatText('[' + setTrack + ']', longestTrackString + 2)
    #     carList.append(car)
    #     i += 1
#
#     trackDetails = {}
#     trackDetails['trackName'] = trackName
#     trackDetails['length'] = 1
#     trackDetails['locos'] = locoList
#     trackDetails['cars'] = carList
#
#     setCarsForm['locations'] = {'locationName': location, 'cars': carList, 'locos': locoList, 'length': 1}
#
#     # locationDict = {}
#     # locationDict['locationName'] = location
#     # locationDict['tracks'] = [trackDetails]
#
#     return setCarsForm



# def exportSetCarsFormToTp(setCarsForm, textBoxEntry):
#
#     _psLog.debug('ModelSetCarsForm.exportSetCarsFormToTp')
#
#     if PatternScriptEntities.CheckTpDestination().directoryExists():
#
#         tpSwitchList = ModelWorkEvents.TrackPatternTranslationToTp()
#         modifiedSwitchList = tpSwitchList.modifySwitchList(setCarsForm, textBoxEntry)
#         appendedTpSwitchList = tpSwitchList.appendSwitchList(modifiedSwitchList)
#
#         tpWorkEventProcessor = ModelWorkEvents.ProcessWorkEventList()
#         tpWorkEventProcessor.writeTpWorkEventListAsJson(appendedTpSwitchList)
#         tpSwitchListHeader = tpWorkEventProcessor.makeTpHeader(appendedTpSwitchList)
#         tpSwitchListLocations = tpWorkEventProcessor.makeTpLocations(appendedTpSwitchList)
#
#         ModelWorkEvents.WriteWorkEventListToTp(tpSwitchListHeader + tpSwitchListLocations).asCsv()
#
#     return
