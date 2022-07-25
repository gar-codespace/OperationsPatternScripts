# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import ModelEntities

from codecs import open as codecsOpen
import xml.dom.minidom as MD
from os import linesep as osLinesep
from xml.dom.minidom import parseString
from xml.dom.minidom import DOMImplementation

SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.Model'
SCRIPT_REV = 20220101

class ExportJmriLocations:
    """Writes a list of location names and comments for the whole profile"""

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.ExportJmriLocations')

        return

    def makeLocationHash(self):

        locationHash = {}

        for location in PatternScriptEntities.LM.getLocationsByIdList():
            locationName = unicode(location.getName(), PatternScriptEntities.ENCODING)
            tracks = location.getTracksList()
            for track in tracks:
                trackName = unicode(track.getName(), PatternScriptEntities.ENCODING)
                trackComment = unicode(track.getComment(), PatternScriptEntities.ENCODING)
                locationHash[locationName + u';' + trackName] = trackComment

        return locationHash

class TrackPatternTranslationToTp:
    """Translate Track Patterns from OperationsPatternScripts for TrainPlayer O2O script compatability"""

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.TrainPlayerTranslationToTp')

        return

    def modifySwitchList(self, setCarsForm, textBoxEntry):
        """Replaces car['Set to'] = [ ] with the track comment"""

        self.psLog.debug('PatternTracksExport.modifySwitchList')

        location = setCarsForm['locations'][0]['locationName']
        trackName = setCarsForm['locations'][0]['tracks'][0]['trackName']
        locationTracks = PatternScriptEntities.LM.getLocationByName(location).getTracksList()
        trackList = []
        for track in locationTracks:
            trackList.append(track.getName())

        userInputList = []
        for userInput in textBoxEntry:
            inputText = unicode(userInput.getText(), PatternScriptEntities.ENCODING)
            if inputText in trackList:
                userInputList.append(inputText)
            else:
                userInputList.append(trackName)

        i = 0
        locoList = []
        for loco in setCarsForm['locations'][0]['tracks'][0]['locos']:
            loco['Set to'] = location + ';' + userInputList[i]
            locoList.append(loco)
            i += 1
        setCarsForm['locations'][0]['tracks'][0]['locos'] = locoList

        carList = []
        for car in setCarsForm['locations'][0]['tracks'][0]['cars']:
            car['Set to'] = location + ';' +  userInputList[i]
            carList.append(car)
            i += 1
        setCarsForm['locations'][0]['tracks'][0]['cars'] = carList

        return setCarsForm

    def appendSwitchList(self, modifiedForm):

        self.psLog.debug('PatternTracksExport.appendSwitchList')

        headerNames = PatternScriptEntities.readConfigFile('PT')
        reportTitle = PatternScriptEntities.BUNDLE[u'Work Event List for TrainPlayer©']
        jsonFile = PatternScriptEntities.PROFILE_PATH + 'operations\\jsonManifests\\' + reportTitle + '.json'
        jsonSwitchList = PatternScriptEntities.genericReadReport(jsonFile)
        tpSwitchList =  PatternScriptEntities.loadJson(jsonSwitchList)

        for loco in modifiedForm['locations'][0]['tracks'][0]['locos']:
            tpSwitchList['locations'][0]['tracks'][0]['locos'].append(loco)

        for car in modifiedForm['locations'][0]['tracks'][0]['cars']:
            tpSwitchList['locations'][0]['tracks'][0]['cars'].append(car)

        return tpSwitchList

class JmriTranslationToTp:
    """Translate manifests from JMRI for TrainPlayer o2o script compatability"""

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.JmriTranslationToTp')

        print(SCRIPT_NAME + '.JmriTranslationToTp ' + str(SCRIPT_REV))

        return

    def getTrainAsDict(self, train):

        manifest = PatternScriptEntities.JMRI.util.FileUtil.readFile( \
                PatternScriptEntities.JMRI.jmrit.operations.trains.JsonManifest(train).getFile() \
                )

        trainAsDict = PatternScriptEntities.loadJson(manifest)
        trainAsDict['comment'] = train.getComment()

        return trainAsDict

    def translateManifestHeader(self, completeJmriManifest):

        self.psLog.debug('Model.translateManifestHeader')

        jmriDateAsEpoch = PatternScriptEntities.convertJmriDateToEpoch(completeJmriManifest[u'date'])
        completeJmriManifest['date'] = PatternScriptEntities.timeStamp(jmriDateAsEpoch)
        completeJmriManifest['trainDescription'] = completeJmriManifest['description']
        completeJmriManifest['trainName'] = completeJmriManifest['userName']
        completeJmriManifest['trainComment'] = completeJmriManifest['comment']
        completeJmriManifest.pop('description', 'Description')
        completeJmriManifest.pop('userName', 'Name')
        completeJmriManifest.pop('comment', 'Comment')

        return completeJmriManifest

    def translateManifestBody(self, completeJmriManifest):

        self.psLog.debug('Model.translateManifestBody')

        locationList = []
        loadTypeRubric = ModelEntities.getLoadTypeRubric('OperationsCarRoster', './loads/load')

        for location in completeJmriManifest[u'locations']:
            tpLocation = ModelEntities.parseJmriLocations(location, loadTypeRubric)
            locationList.append(tpLocation)

        return locationList

class ProcessWorkEventList:
    """Process the translated work event lists to a CSV list formatted for the TrainPlayer o2o scripts"""

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.ProcessWorkEventList')
        self.locationHash = ExportJmriLocations().makeLocationHash()

        return

    def makeTpHeader(self, appendedTpSwitchList):
        """The jason manifest is encoded in HTML Entity,
        csv writer does not encode utf-8,
        stolen from: https://stackoverflow.com/questions/2087370/decode-html-entities-in-python-string
        """

        self.psLog.debug('Model.makeTpHeader')
        header = 'HN,' + PatternScriptEntities.HTML_PARSER().unescape(appendedTpSwitchList['railroad']) + '\n'
        header += 'HT,' + PatternScriptEntities.HTML_PARSER().unescape(appendedTpSwitchList['trainName']) + '\n'
        header += 'HD,' + PatternScriptEntities.HTML_PARSER().unescape(appendedTpSwitchList['trainDescription']) + '\n'
        header += 'HC,' + PatternScriptEntities.HTML_PARSER().unescape(appendedTpSwitchList['trainComment']) + '\n'
        header += 'HV,' + PatternScriptEntities.HTML_PARSER().unescape(appendedTpSwitchList['date']) + '\n'
        header += u'WT,' + str(len(appendedTpSwitchList['locations'])) + '\n'

        return header

    def makeTpLocations(self, appendedTpSwitchList):
        """The jason manifest is encoded in HTML Entity,
        csv writer does not encode utf-8
        """

        self.psLog.debug('Model.makeTpLocations')

        tpLocations = ''

        i = 1
        for location in appendedTpSwitchList['locations']:
            tpLocations += u'WE,' + str(i) + ',' + location['locationName'] + '\n'
            for track in location['tracks']:
                for loco in track['locos']:
                    tpLocations += ",".join(self.makeLine(loco)) + '\n'
                for car in track['cars']:
                    tpLocations += ",".join(self.makeLine(car)) + '\n'
            i += 1

        return tpLocations + '\n'

    def makeLine(self, rS):

        # trackComment = self.locationHash[rS[u'Set to']]

        ID = rS[PatternScriptEntities.SB.handleGetMessage('Road')] + rS[PatternScriptEntities.SB.handleGetMessage('Number')]
    # Process FD&T
        FDandT = rS[PatternScriptEntities.SB.handleGetMessage('FD&Track')]
        FDandT = FDandT.replace(', ', ';')
    # Pickup Cars are tagged with their final destination, all others tagged with destination
        if rS[u'PUSO'] == 'PC':
            rsSetTo = FDandT
        else:
            rsSetTo = rS[u'Set to']
    # Process load Type into a single character string
        loadType = rS[PatternScriptEntities.SB.handleGetMessage('Load_Type')]
        if rS[PatternScriptEntities.SB.handleGetMessage('Load_Type')] == 'Empty':
            loadType = 'E'
        if rS[PatternScriptEntities.SB.handleGetMessage('Load_Type')] == 'Load':
            loadType = 'L'

        rsLine  = [
                  rS[u'PUSO'] + ','
                + ID + ','
                + rS[PatternScriptEntities.SB.handleGetMessage('Road')] + ','
                + rS[PatternScriptEntities.SB.handleGetMessage('Number')] + ','
                + rS[PatternScriptEntities.SB.handleGetMessage('Type')] + ','
                + loadType + ','
                + rS[PatternScriptEntities.SB.handleGetMessage('Load')] + ','
                + rS[PatternScriptEntities.SB.handleGetMessage('Track')] + ','
                + rsSetTo
                ]

        return rsLine

    def writeTpWorkEventListAsJson(self, appendedTpSwitchList):

        self.psLog.debug('Model.writeTpWorkEventListAsJson')

        reportTitle = appendedTpSwitchList['trainDescription']
        jsonReoprtPath = PatternScriptEntities.PROFILE_PATH + 'operations\\jsonManifests\\' + reportTitle + '.json'
        jsonReport = PatternScriptEntities.dumpJson(appendedTpSwitchList)
        PatternScriptEntities.genericWriteReport(jsonReoprtPath, jsonReport)

        print(SCRIPT_NAME + '.ProcessWorkEventList ' + str(SCRIPT_REV))

        return


class UpdateOperationsConfig:

    def __init__(self):

        self.tpInventory = []
        self.tpLocations = []
        self.allTpAar = []
        self.allTpRoads = []
        self.allJmriRoads = []

        self.xmlComment = SCRIPT_NAME + ' - ' + PatternScriptEntities.timeStamp()
        self.docAttr = u'<!DOCTYPE operations-config SYSTEM "/xml/DTD/operations-cars.dtd">'

        return

    def checkList(self):

        try:
            self.tpInventory = ModelEntities.getTpInventory()
            self.tpInventory.pop(0) # Remove the header
        except:
            pass

        try:
            self.tpLocations = ModelEntities.getTpLocations()
            self.tpLocations.pop(0) # Remove the header
        except:
            pass

    def getAllTpAar(self):

        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            self.allTpAar.append(splitItem[1])

        self.allTpAar = list(set(self.allTpAar))

        return

    def getAllTpRoads(self):

        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            road, number = ModelEntities.parseCarId(splitItem[0])
            self.allTpRoads.append(road)

        self.allTpRoads = list(set(self.allTpRoads))

        return

    def getRoadsFromXml(self):

        roadsElement = PatternScriptEntities.xmlWrangler('OperationsCarRoster')
        roads = roadsElement.getXml('./roads/road')
        print(len(roads))
        for item in roads:
            self.allJmriRoads.append(item.attrib)

        print(self.allJmriRoads)

        return

    def test(self):

        filePath = PatternScriptEntities.PROFILE_PATH + '\\operations\\OperationsCarRoster.xml'
        if not PatternScriptEntities.JAVA_IO.File(filePath).isFile():
            return False

        with codecsOpen(filePath, 'r', encoding=PatternScriptEntities.ENCODING) as textWorkFile:
            tree = MD.parse(textWorkFile)

        root = tree.documentElement

        nRoads = root.getElementsByTagName('roads')[0]

        for item in nRoads.childNodes:
            if item.nodeType == item.COMMENT_NODE:
                nRoads.removeChild(item)
            if item.nodeType == item.ELEMENT_NODE:
                nRoads.removeChild(item)

        xComment = tree.createComment(self.xmlComment)
        nRoads.appendChild(xComment)

        for road in self.allTpRoads:
            newRoad = tree.createElement('road')
            newRoad.setAttribute('name', road)
            nRoads.appendChild(newRoad)

        xmlString = tree.toprettyxml(indent ="\t")
        # https://stackoverflow.com/questions/1140958/whats-a-quick-one-liner-to-remove-empty-lines-from-a-python-string
        xmlString = [s for s in xmlString.splitlines() if s.strip()]
        # Put the DOCTYPE back in
        xmlString.insert(2, self.docAttr)
        xmlString = osLinesep.join(xmlString)

        # xmlString = osLinesep.join([s for s in xmlString.splitlines() if s.strip()])

        with codecsOpen(filePath, 'wb', encoding=PatternScriptEntities.ENCODING) as textWorkFile:
            textWorkFile.write(xmlString)

        PatternScriptEntities.JMRI.jmrit.operations.rollingstock.cars.CarManagerXml.save()
        
        return


class WriteWorkEventListToTp:

    def __init__(self, workEventList):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.WriteWorkEventListToTp')

        self.jmriManifestPath = PatternScriptEntities.JMRI.util.FileUtil.getHomePath() \
                + "AppData\Roaming\TrainPlayer\Reports\JMRI Export - Work Events.csv"
        self.workEventList = workEventList

        return

    def asCsv(self):

        self.psLog.debug('Model.WriteWorkEventListToTp.asCsv')

        if PatternScriptEntities.CheckTpDestination().directoryExists():
            PatternScriptEntities.genericWriteReport(self.jmriManifestPath, self.workEventList)

        print(SCRIPT_NAME + '.WriteWorkEventListToTp ' + str(SCRIPT_REV))

        return

class ReconsileLocations:

    def __init__(self):

        self.tpInventory = []
        self.tpLocations = []
        self.mergedTpLocations = []

        return

    def checkList(self):

        try:
            self.tpInventory = ModelEntities.getTpInventory()
            self.tpInventory.pop(0) # Remove the header
        except:
            pass

        try:
            self.tpLocations = ModelEntities.getTpLocations()
            self.tpLocations.pop(0) # Remove the header
        except:
            pass

    def mergeTpLists(self):
        """mergedTpLocations format: ID, Locale, Track, Type, Spaces, AAR """

        for lineItem in self.tpLocations:
            splitLine = lineItem.split(';')
            aarList = self.getAar(splitLine[1], splitLine[2])
            for aar in aarList:
                newLine = [splitLine[0], splitLine[1], splitLine[2], splitLine[3], splitLine[4], aar]
                self.mergedTpLocations.append(newLine)

        return

    def updateLocationAndTrack(self):
        """Implement later:
            use index for renaming location and track
            update track type
            update track length
            """

        for lineItem in self.mergedTpLocations:

            try:
                # location, track = ModelEntities.getSetToLocationAndTrack(lineItem[1], lineItem[2])
                location = PatternScriptEntities.LM.getLocationByName(lineItem[1])
                location.addTypeName(lineItem[5])
                location.store()
                # track.addTypeName(lineItem[5])
                # print(location.getName(), track.getName(), lineItem[5])
                # Update track length
                # Update track type
            except:
                # Add new location and/or track
                print('Not found: ', lineItem[1], lineItem[2])

        return

    def getAar(self, location, track):
        """get a de-duplicated list of aar for each location;track"""

        aarList = []
        for lineItem in self.tpInventory:
            splitLine = lineItem.split(';')
            if location == splitLine[2] and track == splitLine[3]:
                aarList.append(splitLine[1])

        return list(set(aarList))

class ReconsileInventory:

    def __init__(self):

        self.errorReport = PatternScriptEntities.BUNDLE['Update Inventory Error Report']
        self.setCarsError = ''
        self.carsNotFound = [] # A list so it can be sorted
        self.locationNotFound = ''

        self.jmriInventory  = []
        self.tpInventory = []

        self.jmriInventoryId = []
        self.tpInventoryId = []

        self.jmriOrphans = []
        self.tpOrphans = []


        return

    def checkList(self):

        self.tpInventory = ModelEntities.getTpInventory()
        if self.tpInventory:
            self.tpInventory.pop(0) # Remove the header
            return True
        else:
            return False

    def getJmriRs(self):

        cars = PatternScriptEntities.CM.getByLocationList()
        locos = PatternScriptEntities.EM.getByLocationList()
        self.jmriInventory = cars + locos

        return

    def makeIdLists(self):

        for item in self.jmriInventory:
            self.jmriInventoryId.append(item.getId())

        for item in self.tpInventory:
            self.tpInventoryId.append(item.split(';')[0])

        return

    def getTpOrphans(self):

        for id in self.tpInventoryId:
            if id not in self.jmriInventoryId:
                self.tpOrphans.append(id)

        return

    def getJmriOrphans(self):

        for id in self.jmriInventoryId:
            if id not in self.tpInventoryId:
                self.jmriOrphans.append(id)

        return

    def deleteJmriOrphans(self):

        for rs in self.jmriOrphans:
            try:
                loco = PatternScriptEntities.EM.getById(rs)
                PatternScriptEntities.EM.deregister(loco)
            except:
                pass

        for rs in self.jmriOrphans:
            try:
                car = PatternScriptEntities.CM.getById(rs)
                PatternScriptEntities.CM.deregister(car)
            except:
                pass

        return

    def addTpOrphans(self):

        for orphan in self.tpOrphans:
            rsLine = self.findRsAttibs(orphan)
            rsAttribs = rsLine.split(';')
            ModelEntities.addNewRs(rsAttribs)

        return

    def findRsAttibs(self, orphan):

        for item in self.tpInventory:
            if orphan in item:
                return item

        return

    def updateLocations(self):
        """lineItem format: RoadNumber, AAR, Location, Track, Loaded, Kernel, Type"""

        for lineItem in self.tpInventory:

            parsedLine = lineItem.split(';')

            if lineItem[2].startswith('E'):
                rs = PatternScriptEntities.EM.getById(parsedLine[0])
            else:
                rs = PatternScriptEntities.CM.getById(parsedLine[0])

            location, track = ModelEntities.getSetToLocationAndTrack(parsedLine[2], parsedLine[3])

            try:
                rs.setLocation(location, track)
                # print('Rolling Stock ', car.getRoadName(), ' set to: ' , location, track)
            except:
                print('Not found ', location.getName(), track.getName())

        return

    def getErrorReport(self):

        self.errorReport += '\n\n' + PatternScriptEntities.BUNDLE['List of rolling stock not updated:']
        self.errorReport += '\n' + self.setCarsError

        self.errorReport += '\n\n' + PatternScriptEntities.BUNDLE['List of tracks not found:']
        self.errorReport += '\n' + self.locationNotFound

        self.errorReport += '\n\n' + PatternScriptEntities.BUNDLE[u'TrainPlayer© cars not found in JMRI roster:']
        self.errorReport += '\n' + '\n'.join(sorted(self.carsNotFound[1:-1])) # [0] is the header

        return self.errorReport
