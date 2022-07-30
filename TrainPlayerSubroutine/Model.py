# coding=utf-8
# © 2021, 2022 Greg Ritacco

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import ModelEntities

import xml.dom.minidom as MD
from os import linesep as osLinesep

SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.Model'
SCRIPT_REV = 20220101

######################################################################################################################
# Location reconciliation
######################################################################################################################

def updateRoadsAndTypes():
    """Mini Controller to update the OperationsCarRoster.xml
        roads and types elements
        """

    carHack = HackXml('OperationsCarRoster')
    carHack.getXmlTree()

    locoHack = HackXml('OperationsEngineRoster')
    locoHack.getXmlTree()

    updatedOperationsCarRoster = UpdateOperationsCarRoster()
    updatedOperationsCarRoster.checkList()

    allTpItems = updatedOperationsCarRoster.getAllTpRoads()
    carHack.updateXmlElement('roads', allTpItems)

    allTpItems = updatedOperationsCarRoster.getAllTpCarAar()
    carHack.updateXmlElement('types', allTpItems)

    allTpItems = updatedOperationsCarRoster.getAllTpLocoTypes()
    locoHack.updateXmlElement('types', allTpItems)

    allTpItems = updatedOperationsCarRoster.getAllTpLocoModels()
    locoHack.updateXmlElement('models', allTpItems)

    carHack.patchUpDom(u'<!DOCTYPE operations-config SYSTEM "/xml/DTD/operations-cars.dtd">')
    carHack.saveUpdatedXml()

    locoHack.patchUpDom(u'<!DOCTYPE operations-config SYSTEM "/xml/DTD/operations-engines.dtd">')
    locoHack.saveUpdatedXml()

    return


class HackXml:
    """Pretty much tuned specifically for roads and types"""

    def __init__(self, xmlFileName):

        self.filePath = PatternScriptEntities.PROFILE_PATH + '\\operations\\' + xmlFileName + '.xml'
        self.tree = MD.parseString("<junk/>")
        self.xmlComment = SCRIPT_NAME + ' - ' + PatternScriptEntities.timeStamp()
        # self.docAttr = u'<!DOCTYPE operations-config SYSTEM "/xml/DTD/operations-cars.dtd">'
        self.xmlString = ''

        return

    def getXmlTree(self):

        if not PatternScriptEntities.JAVA_IO.File(self.filePath).isFile():
            return False

        with PatternScriptEntities.codecsOpen(self.filePath, 'r', encoding=PatternScriptEntities.ENCODING) as textWorkFile:
            self.tree = MD.parse(textWorkFile)

        return

    def updateXmlElement(self, elementName, newList):
        """Replaces elementName nodes with new nodes from the supplied list
            Also adds a comment
            """

        root = self.tree.documentElement

        topElement = root.getElementsByTagName(elementName)[0]
        for item in topElement.childNodes:
            if item.nodeType == item.COMMENT_NODE:
                topElement.removeChild(item)
            if item.nodeType == item.ELEMENT_NODE:
                topElement.removeChild(item)
                eName = item.tagName

        xComment = self.tree.createComment(self.xmlComment)
        topElement.appendChild(xComment)

        for item in newList:
            newElement = self.tree.createElement(eName)
            newElement.setAttribute('name', item)
            topElement.appendChild(newElement)

        return

    def patchUpDom(self, xmlPatch):
        """Work around DOM's limitations"""

        self.xmlString = self.tree.toprettyxml(indent ="\t")
    # https://stackoverflow.com/questions/1140958/whats-a-quick-one-liner-to-remove-empty-lines-from-a-python-string
        self.xmlString = [s for s in self.xmlString.splitlines() if s.strip()]
    # Put the DOCTYPE back in
        self.xmlString.insert(2, xmlPatch)
        self.xmlString = osLinesep.join(self.xmlString)

        return

    def saveUpdatedXml(self):

        with PatternScriptEntities.codecsOpen(self.filePath, 'wb', encoding=PatternScriptEntities.ENCODING) as textWorkFile:
            textWorkFile.write(self.xmlString)

        return

def updateLocations():
    """Mini Controller that synchronizes the JMRI locations data to TrainPlayer's
        AO Locale data.
        """

    reconsiledLocations = ReconsileLocations()
    reconsiledLocations.checkList()
    reconsiledLocations.makeTpLocationList()
    reconsiledLocations.makeTpIndustryList()
    reconsiledLocations.dovetailTpLists()

    # Do more stuff here

    return

class ReconsileLocations:

    def __init__(self):

        self.tpLocationsFile = 'TrainPlayer Export - Locations.txt'
        self.tpIndustriesFile = 'TrainPlayer Export - Industries.txt'

        self.tpLocations = []
        self.tpLocationList = []

        self.tpIndustries = []
        self.tpIndustryList = []

        self.dovetailedTpList = []

        return

    def checkList(self):

        try:
            self.tpLocations = ModelEntities.getTpExport(self.tpLocationsFile)
            self.tpLocations.pop(0) # Remove the header
        except:
            print('Not found: ' + self.tpLocationsFile)
            pass

        try:
            self.tpIndustries = ModelEntities.getTpExport(self.tpIndustriesFile)
            self.tpIndustries.pop(0) # Remove the header
        except:
            print('Not found: ' + self.tpIndustriesFile)
            pass

        return

    def makeTpLocationList(self):
        """Using TP nomenclature-
            tpLocationList format: ID, JMRI Location Name, JMRI Track Name, Type, Spaces
            """

        for lineItem in self.tpLocations:
            self.tpLocationList.append(lineItem.split(';'))

        return

    def makeTpIndustryList(self):
        """Using TP nomenclature-
            tpIndustryList format: ID, JMRI Location Name, JMRI Track Name, Industry, AAR, S/R, Load, Staging, ViaIn
            """

        for lineItem in self.tpIndustries:
            self.tpIndustryList.append(lineItem.split(';'))

        return

    def dovetailTpLists(self):
        """Using TP nomenclature-
            dovetailedTpList format: ID, JMRI Location Name, JMRI Track Name, Type, Spaces, AAR, S/R, Load, Staging, ViaIn
            """

        for lineItem in self.tpLocationList:
            loc = lineItem[1]
            trk = lineItem[2]
            industryItems = self.getIndustryItems(loc, trk)
            if len(industryItems) == 0:
                industryItems = [[u'', u'', u'', u'']]
            for item in industryItems:
                self.dovetailedTpList.append(lineItem + item)

        return

    def getIndustryItems(self, location, track):
        """Using TP nomenclature-
            Returns: AAR, S/R, Load, Staging, ViaIn
            If TP industries are not being used, tpIndustryList is empty
            industryItems is a list of lists
            """

        industryItems = []
        for lineItem in self.tpIndustryList:
            if lineItem[1] == location and lineItem[2] == track:
                lineItem.pop(0) # Remove ID
                lineItem.pop(0) # Remove Locale
                lineItem.pop(0) # Remove Track
                lineItem.pop(0) # Remove Industry
                industryItems.append(lineItem)

        return industryItems


######################################################################################################################
# Reconsile rolling stock inventory
######################################################################################################################


def updateInventory():
    """Mini Controller that synchronizes the JMRI car data to TrainPlayer's
        AO Car data.
        """
    xmlHack = HackXml('OperationsCarRoster')
    tree = xmlHack.getXmlTree()

    reconsiledInventory = ReconsileInventory()
    reconsiledInventory.checkList()
    reconsiledInventory.splitTpList()



    # reconsiledInventory.getJmriOrphans()


    return

class ReconsileInventory:

    def __init__(self):

        # self.errorReport = PatternScriptEntities.BUNDLE['Update Inventory Error Report']
        # self.setCarsError = ''
        # self.carsNotFound = [] # A list so it can be sorted
        # self.locationNotFound = ''

        self.tpInventoryFile = 'TrainPlayer Export - Inventory.txt'
        # self.jmriInventory  = []
        self.tpInventory = []
        self.tpCars = []
        self.tpLocos = []

        self.jmriCars = PatternScriptEntities.CM.getByLocationList()
        self.jmriLocos = PatternScriptEntities.EM.getByLocationList()

        self.jmriOrphans = []
        self.tpOrphans = []





        self.jmriInventoryId = []
        self.tpInventoryId = []


        return

    def checkList(self):

        try:
            self.tpInventory = ModelEntities.getTpExport(self.tpInventoryFile)
            self.tpInventory.pop(0) # Remove the header
        except:
            print('Not found: ' + self.tpInventoryFile)
            pass

        return

    def splitTpList(self):
        """Using TP nomenclature-
            tpLocationList format: Car, Type, AAR, JMRI Location, JMRI Track, Load, Kernel
            """

        for item in self.tpInventory:
            if item[0].startswith('E'):
                self.tpLocos.append(item)
            else:
                self.tpCars.append(item)

        return

    def getJmriOrphans(self):

        for item in self.jmriCars:
            if not item.getId() in self.tpCars:
                self.jmriOrphans.append(item.getId())
                print(item.getId())

        for item in self.jmriLocos:
            if not item.getId() in self.tpCars:
                self.jmriOrphans.append(item.getId())
                print(item.getId())

        return








    def makeIdLists(self):

        for item in self.jmriInventory:
            self.jmriInventoryId.append(item.getId())

        # for item in self.tpInventory:
        #     self.tpInventoryId.append(item.split(';')[0])

        return

    def getTpOrphans(self):

        for id in self.tpInventoryId:
            if id not in self.jmriInventoryId:
                self.tpOrphans.append(id)

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


class UpdateOperationsCarRoster:

    def __init__(self):

        self.tpInventoryFile = 'TrainPlayer Export - Inventory.txt'
        self.tpInventory = []
        self.tpLocations = []
        self.allTpAar = []
        self.allTpCarAar = []
        self.allTpLocoAar = []
        self.allTpRoads = []
        self.allJmriRoads = []

        return

    def checkList(self):

        try:
            # self.tpInventory = ModelEntities.getTpInventory()
            self.tpInventory = ModelEntities.getTpExport(self.tpInventoryFile)
            self.tpInventory.pop(0) # Remove the header
        except:
            pass

        try:
            self.tpLocations = ModelEntities.getTpLocations()
            self.tpLocations.pop(0) # Remove the header
        except:
            pass

    def getAllTpRoads(self):

        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            road, number = ModelEntities.parseCarId(splitItem[0])
            self.allTpRoads.append(road)

        self.allTpRoads = list(set(self.allTpRoads))

        return self.allTpRoads

    def getAllTpCarAar(self):

        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('E'):
                continue
            else:
                self.allTpCarAar.append(splitItem[2])

        return list(set(self.allTpCarAar))

    def getAllTpLocoTypes(self):

        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('E'):
                self.allTpLocoAar.append(splitItem[2])

        return list(set(self.allTpLocoAar))

    def getAllTpLocoModels(self):

        for lineItem in self.tpInventory:
            splitItem = lineItem.split(';')
            if splitItem[2].startswith('E'):
                self.allTpLocoAar.append(splitItem[1])

        return list(set(self.allTpLocoAar))


######################################################################################################################
# o2o work event list classes
######################################################################################################################


class TrackPatternTranslationToTp:
    """TrainPlayer Manifest-
        Translate Track Patterns from OperationsPatternScripts for TrainPlayer O2O script compatability
        """

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
    """TrainPlayer Manifest-
        Translate manifests from JMRI for TrainPlayer o2o script compatability
        """

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
    """TrainPlayer Manifest-
        Process the translated work event lists to a CSV list formatted for the
        TrainPlayer o2o scripts
        """

    def __init__(self):

        self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.ProcessWorkEventList')
        # self.locationHash = ExportJmriLocations().makeLocationHash()

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


class WriteWorkEventListToTp:
    """TrainPlayer Manifest-
        Writes the o2o work events list
        """

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


# class ExportJmriLocations:
#     """TrainPlayer Manifest-Support class
#         Returns a list of location names and comments for the whole profile
#         """
#
#     def __init__(self):
#
#         self.psLog = PatternScriptEntities.LOGGING.getLogger('PS.TP.ExportJmriLocations')
#
#         return
#
#     def makeLocationHash(self):
#
#         locationHash = {}
#
#         for location in PatternScriptEntities.LM.getLocationsByIdList():
#             locationName = unicode(location.getName(), PatternScriptEntities.ENCODING)
#             tracks = location.getTracksList()
#             for track in tracks:
#                 trackName = unicode(track.getName(), PatternScriptEntities.ENCODING)
#                 trackComment = unicode(track.getComment(), PatternScriptEntities.ENCODING)
#                 locationHash[locationName + u';' + trackName] = trackComment
#
#         return locationHash
