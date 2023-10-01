# coding=utf-8
# © 2023 Greg Ritacco

"""
Routines to create various manifests and switch lists.
"""

from opsEntities import PSE

SCRIPT_NAME = PSE.SCRIPT_DIR + '.' + __name__
SCRIPT_REV = 20230901

TMT = PSE.JMRI.jmrit.operations.trains.TrainManifestText()
_psLog = PSE.LOGGING.getLogger('OPS.OE.Manifest')

def jsonManifest(train):
    """
    Mini controller
    Modifies the json manifest and sorts it in sequence order.
    """
    
    addSequenceToManifest(train)
    resequenceManifest(train)

    return

def addSequenceToManifest(train):
    """
    Adds an attribute called 'sequence' and it's value to an existing json manifest.
    """

    _psLog.debug('Manifest.addSequenceToManifest')

    isSequenceHash, sequenceHash = PSE.getSequenceHash()

    trainName = 'train-' + train.toString() + '.json'
    manifestPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', trainName)
    manifest = PSE.loadJson(PSE.genericReadReport(manifestPath))

    for location in manifest['locations']:
        for car in location['cars']['add']:
            carID = car['road'] + ' ' + car['number']
            sequence = sequenceHash['cars'][carID]
            car['sequence'] = sequence
        for car in location['cars']['remove']:
            carID = car['road'] + ' ' + car['number']
            sequence = sequenceHash['cars'][carID]
            car['sequence'] = sequence

    PSE.genericWriteReport(manifestPath, PSE.dumpJson(manifest))

    return

def resequenceManifest(train):
    """
    Resequences an existing json manifest by its sequence value.
    """

    _psLog.debug('Manifest.resequenceManifest')

    trainName = 'train-' + train.toString() + '.json'
    manifestPath = PSE.OS_PATH.join(PSE.PROFILE_PATH, 'operations', 'jsonManifests', trainName)
    manifest = PSE.loadJson(PSE.genericReadReport(manifestPath))

    for location in manifest['locations']:
        cars = location['cars']['add']
        cars.sort(key=lambda row: row['sequence'])

        cars = location['cars']['remove']
        cars.sort(key=lambda row: row['sequence'])

    PSE.genericWriteReport(manifestPath, PSE.dumpJson(manifest))

    return

def textManifest(train):
    """
    Creates a text manifest for the built train.
    """

    _psLog.debug('Manifest.textManifest')

    textManifest = ''
    
    isSequenceHash, sequenceHash = PSE.getSequenceHash()
    carSeq = []
    locoSeq = []

    for loco in PSE.EM.getByTrainBlockingList(train):
        locoSeq.append((loco, sequenceHash['locos'][loco.toString()]))

    for car in PSE.CM.getByTrainDestinationList(train):
        carSeq.append((car, sequenceHash['cars'][car.toString()]))

    locoSeq.sort(key=lambda row: row[1])
    carSeq.sort(key=lambda row: row[1])

# Header
    textManifest += PSE.getExtendedRailroadName() + '\n'
    textManifest += '\n'

    textManifest += TMT.getStringManifestForTrain().format(train.getName(), train.getDescription()) + '\n'
    textManifest += PSE.validTime() + '\n'
    textManifest += '\n'

# Body
    routeList = train.getRoute().getLocationsBySequenceList()
    for rl in routeList:
        textManifest += TMT.getStringScheduledWork().format(rl.toString()) + '\n'
        for loco in locoSeq:
            # Pick up
            if loco[0].getLocation().toString() == rl.toString():
                prefix = PSE.JMRI.jmrit.operations.setup.Setup.getPickupEnginePrefix()       
                line = PSE.JMRI.jmrit.operations.trains.TrainCommon().pickupEngine(loco[0])
                textManifest += prefix + line + '\n'
            # Set out
            if loco[0].getRouteDestination().toString() == rl.toString():
                prefix = PSE.JMRI.jmrit.operations.setup.Setup.getDropEnginePrefix()
                line = PSE.JMRI.jmrit.operations.trains.TrainCommon().dropEngine(loco[0])
                textManifest += prefix + line + '\n'

        for car in carSeq:
            # Pick up
            if car[0].getLocation().toString() == rl.toString():
                prefix = PSE.JMRI.jmrit.operations.setup.Setup.getPickupCarPrefix()       
                line = PSE.JMRI.jmrit.operations.trains.TrainCommon().pickupCar(car[0], True, False)
                textManifest += prefix + line + '\n'
            # Set out
            if car[0].getRouteDestination().toString() == rl.toString():
                prefix = PSE.JMRI.jmrit.operations.setup.Setup.getDropCarPrefix()
                line = PSE.JMRI.jmrit.operations.trains.TrainCommon().dropCar(car[0], True, False)
                textManifest += prefix + line + '\n'
            # Move
            # if car[0].getRouteDestination().toString() == car[0].getLocation().toString() and car[0].getLocation().toString() == rl.toString():
            if car[0].getRouteDestination().toString() == car[0].getLocation().toString() == rl.toString():
                prefix = PSE.JMRI.jmrit.operations.setup.Setup.getLocalPrefix()       
                line = PSE.JMRI.jmrit.operations.trains.TrainCommon().localMoveCar(car[0], True)
                textManifest += prefix + line + '\n'

        textManifest += TMT.getStringTrainDepartsCars().format(rl.toString(), rl.getTrainDirectionString(), train.getNumberCarsInTrain(rl), train.getTrainLength(rl), PSE.JMRI.jmrit.operations.setup.Setup.getLengthUnit(), train.getTrainWeight(rl)) + '\n'
        textManifest += '\n'

# Footer
    textManifest += TMT.getStringTrainTerminates().format(routeList[-1].toString()) + '\n'
        
    return textManifest