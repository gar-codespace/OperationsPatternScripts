# coding=utf-8
# © 2023 Greg Ritacco

"""
TRE is an abbreviation for Text Report Entities.
Helper methods for TextReports.py are here
"""

from opsEntities import PSE

SCRIPT_NAME = '{}.{}'.format(PSE.SCRIPT_DIR, __name__)
SCRIPT_REV = 20231001

def makeReportItemWidthMatrix():
    """
    The attribute widths (AW) for each of the rolling stock attributes is defined in the report matrix (RM) of the config file.
    """

    reportMatrix = {}
    attributeWidths = PSE.readConfigFile('Main Script')['US']['AW']

    for aKey, aValue in attributeWidths.items():
        try: # Include translated JMRI fields
            reportMatrix[PSE.SB.handleGetMessage(aKey)] = aValue
        except: # Include custom OPS fields
            reportMatrix[aKey] = aValue

    PSE.REPORT_ITEM_WIDTH_MATRIX = reportMatrix

    return

def translateMessageFormat():
    """
    The messageFormat is in the locale's language, it has to be hashed to the plugin fields.
    These are the pulldown items in Tools/Print Options/<> Message Format
    """

    rosetta = {}
#Common
    rosetta[PSE.SB.handleGetMessage('Road')] = 'Road'
    rosetta[PSE.SB.handleGetMessage('Number')] = 'Number'
    rosetta[PSE.SB.handleGetMessage('Type')] = 'Type'   
    rosetta[PSE.SB.handleGetMessage('Length')] = 'Length'
    rosetta[PSE.SB.handleGetMessage('Color')] = 'Color'
    rosetta[PSE.SB.handleGetMessage('Weight')] = 'Weight'
    rosetta[PSE.SB.handleGetMessage('Comment')] = 'Comment'
    rosetta[PSE.SB.handleGetMessage('Division')] = 'Division'
    rosetta[PSE.SB.handleGetMessage('Location')] = 'Location'
    rosetta[PSE.SB.handleGetMessage('Track')] = 'Track'
    rosetta[PSE.SB.handleGetMessage('Destination')] = 'Destination'
    rosetta[PSE.SB.handleGetMessage('Owner')] = 'Owner'
    rosetta[PSE.SB.handleGetMessage('Tab')] = 'Tab'
    rosetta[PSE.SB.handleGetMessage('Tab2')] = 'Tab2'
    rosetta[PSE.SB.handleGetMessage('Tab3')] = 'Tab3'
# Locos
    rosetta[PSE.SB.handleGetMessage('Model')] = 'Model'
    rosetta[PSE.SB.handleGetMessage('DCC_Address')] = 'DCC_Address'
    rosetta[PSE.SB.handleGetMessage('Consist')] = 'Consist'
# Cars
    rosetta[PSE.SB.handleGetMessage('Load_Type')] = 'Load_Type'
    rosetta[PSE.SB.handleGetMessage('Load')] = 'Load'
    rosetta[PSE.SB.handleGetMessage('Hazardous')] = 'Hazardous'
    rosetta[PSE.SB.handleGetMessage('Kernel')] = 'Kernel'
    rosetta[PSE.SB.handleGetMessage('Kernel_Size')] = 'Kernel_Size'
    rosetta[PSE.SB.handleGetMessage('Dest&Track')] = 'Dest&Track'
    rosetta[PSE.SB.handleGetMessage('Final_Dest')] = 'Final_Dest'
    rosetta[PSE.SB.handleGetMessage('FD&Track')] = 'FD&Track'
    rosetta[PSE.SB.handleGetMessage('SetOut_Msg')] = 'SetOut_Msg'
    rosetta[PSE.SB.handleGetMessage('PickUp_Msg')] = 'PickUp_Msg'
    rosetta[PSE.SB.handleGetMessage('RWE')] = 'RWE'

    PSE.ROSETTA = rosetta

    return

def translateLocoFormat(loco):
    """
    For items found in the Setup.get<loco>ManifestMessageFormat()
    """
                
    newCarFormat = {}

    newCarFormat['Road'] = loco['road']
    newCarFormat['Number'] = loco['number']
    newCarFormat['Type'] = loco['carType']
    newCarFormat['Model'] = loco['model']
    newCarFormat['Length'] = loco['length']
    newCarFormat['Weight'] = loco['weightTons']
    newCarFormat['Consist'] = loco['consist']
    newCarFormat['Owner'] = loco['owner']
    newCarFormat['Track'] = loco['location']['track']['userName']
    newCarFormat['Destination'] = loco['destination']['userName']
    newCarFormat['Location'] = loco['location']['userName']
    newCarFormat['Comment'] = loco['comment']
    newCarFormat['DCC_Address'] = loco['dccAddress']

    return newCarFormat

def translateCarFormat(car):
    """
    For items found in the Setup.get<car>ManifestMessageFormat()
    """
                
    newCarFormat = {}

    newCarFormat['Road'] = car[u'road']
    newCarFormat['Number'] = car[u'number']
    newCarFormat['Type'] = car[u'carType']
    newCarFormat['Length'] = car[u'length']
    newCarFormat['Weight'] = car[u'weightTons']
    newCarFormat['Load'] = car[u'load']
    newCarFormat['Load_Type'] = car[u'loadType']
    newCarFormat['Hazardous'] = car[u'hazardous']
    newCarFormat['Color'] = car[u'color']
    newCarFormat['Kernel'] = car[u'kernel']
    newCarFormat['Kernel_Size'] = car[u'kernelSize']
    newCarFormat['Owner'] = car[u'owner']
    newCarFormat['Division'] = car[u'division']
    newCarFormat['Location'] = car['location'][u'userName']
    newCarFormat['Track'] = car['location']['track'][u'userName']
    newCarFormat['Destination'] = car['destination'][u'userName']
    newCarFormat['Dest&Track'] = u'{}-{}'.format(car['destination'][u'userName'], car['destination']['track'][u'userName'])
    newCarFormat['Final_Dest'] = car['finalDestination'][u'userName']
    newCarFormat['FD&Track'] = u'{}-{}'.format(car['finalDestination'][u'userName'], car['finalDestination']['track'][u'userName'])
    newCarFormat['Comment'] = car[u'comment']
    newCarFormat['SetOut_Msg'] = car[u'removeComment']
    newCarFormat['PickUp_Msg'] = car[u'addComment']
    newCarFormat['RWE'] = car[u'returnWhenEmpty']

    return newCarFormat

def getShortLoadType(car):
    """
    Replaces empty and load with E, L, or O for occupied.
    JMRI defines custom load type as empty but default load type as E, hence the 'or' statement.
    Load, Empty, Occupied and Unknown are translated by the bundle.
    """

    carObject = PSE.CM.getByRoadAndNumber(car['road'], car['number'])

    lt =  PSE.getBundleItem(u'Unknown').upper()[0]
    if carObject.getLoadName() == 'E':
        lt = PSE.getBundleItem(u'Empty').upper()[0]
    if carObject.getLoadName() == 'L':
        lt = PSE.getBundleItem(u'Load').upper()[0]
    if carObject.getLoadType() == 'empty' or carObject.getLoadType() == 'E':
        lt = PSE.getBundleItem(u'Empty').upper()[0]

    if carObject.getLoadType() == 'load' or carObject.getLoadType() == 'L':
        lt = PSE.getBundleItem(u'Load').upper()[0]

    if carObject.isCaboose() or carObject.isPassenger():
        lt = PSE.getBundleItem(u'Occupied').upper()[0]

    return lt

def pickupLoco(loco, manifest, twoCol):
    """
    Based on the JMRI version.
    """

    carItems = translateLocoFormat(loco)

    line = ''

    messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getPickupEngineMessageFormat()

    for messageItem in messageFormat:
        if 'Tab' in messageItem or messageItem == ' ':
            continue

        lineItem = carItems[PSE.ROSETTA[messageItem]]
        lineWidth = PSE.REPORT_ITEM_WIDTH_MATRIX[messageItem]

    # Special case handling for loco number
        if PSE.ROSETTA[messageItem] == 'Number':
            lineItem = lineItem.rjust(lineWidth)

        line += '{} '.format(lineItem.ljust(lineWidth)[:lineWidth])

    return line

def setoutLoco(loco, manifest, twoCol):
    """
    Based on the JMRI version.
    """

    carItems = translateLocoFormat(loco)

    line = ''

    messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getDropEngineMessageFormat()

    for messageItem in messageFormat:
        if 'Tab' in messageItem or messageItem == ' ':
            continue

        lineItem = carItems[PSE.ROSETTA[messageItem]]
        lineWidth = PSE.REPORT_ITEM_WIDTH_MATRIX[messageItem]

    # Special case handling for loco number
        if PSE.ROSETTA[messageItem] == 'Number':
            lineItem = lineItem.rjust(lineWidth)

        line += '{} '.format(lineItem.ljust(lineWidth)[:lineWidth])

    return line

def pickupCar(car, manifest, twoCol):
    """
    Based on the JMRI version.
    """

    carItems = translateCarFormat(car)

    line = ''

    if manifest:
        messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getPickupManifestMessageFormat()
    else:
        messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getPickupSwitchListMessageFormat()

    for messageItem in messageFormat:

        if 'Tab' in messageItem or messageItem == ' ':
            continue

        lineItem = carItems[PSE.ROSETTA[messageItem]]
        lineWidth = PSE.REPORT_ITEM_WIDTH_MATRIX[messageItem]

    # Special case handling for car load type
        if PSE.ROSETTA[messageItem] == 'Load_Type':
            lineItem = getShortLoadType(car).ljust(1)
            lineWidth = 1
    # Special case handling for car number
        if PSE.ROSETTA[messageItem] == 'Number':
            lineItem = lineItem.rjust(lineWidth)
    # Special case handling for the hazardous flag
        if PSE.ROSETTA[messageItem] == 'Hazardous' and car['hazardous']:
            lineItem = messageItem[0].upper()
            lineWidth = 1
        elif PSE.ROSETTA[messageItem] == 'Hazardous' and not car['hazardous']:
            lineItem = ' '
            lineWidth = 1

        line += '{} '.format(lineItem.ljust(lineWidth)[:lineWidth])

    return line

def dropCar(car, manifest, twoCol):
    """
    Based on the JMRI version.
    """

    carItems = translateCarFormat(car)

    line = ''

    if manifest:
        messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getDropManifestMessageFormat()
    else:
        messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getDropSwitchListMessageFormat()

    for messageItem in messageFormat:

        if 'Tab' in messageItem or messageItem == ' ':
            continue

        lineItem = carItems[PSE.ROSETTA[messageItem]]
        lineWidth = PSE.REPORT_ITEM_WIDTH_MATRIX[messageItem]

    # Special case handling for car load type
        if PSE.ROSETTA[messageItem] == 'Load_Type':
            lineItem = getShortLoadType(car).ljust(1)
            lineWidth = 1
    # Special case handling for car number
        if PSE.ROSETTA[messageItem] == 'Number':
            lineItem = lineItem.rjust(lineWidth)
    # Special case handling for the hazardous flag
        if PSE.ROSETTA[messageItem] == 'Hazardous' and car['hazardous']:
            lineItem = messageItem[0].upper()
            lineWidth = 1
        elif PSE.ROSETTA[messageItem] == 'Hazardous' and not car['hazardous']:
            lineItem = ' '
            lineWidth = 1

        line += '{} '.format(lineItem.ljust(lineWidth)[:lineWidth])

    return line

def localMoveCar(car, manifest, twoCol):
    """
    Based on the JMRI version.
    """

    carItems = translateCarFormat(car)

    line = ''

    if manifest:
        messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getLocalManifestMessageFormat()
    else:
        messageFormat = PSE.JMRI.jmrit.operations.setup.Setup.getLocalSwitchListMessageFormat()

    for messageItem in messageFormat:

        if 'Tab' in messageItem or messageItem == ' ':
            continue

        lineItem = carItems[PSE.ROSETTA[messageItem]]
        lineWidth = PSE.REPORT_ITEM_WIDTH_MATRIX[messageItem]

    # Special case handling for car load type
        if PSE.ROSETTA[messageItem] == 'Load_Type':
            lineItem = getShortLoadType(car).ljust(1)
            lineWidth = 1
    # Special case handling for car number
        if PSE.ROSETTA[messageItem] == 'Number':
            lineItem = lineItem.rjust(lineWidth)
    # Special case handling for the hazardous flag
        if PSE.ROSETTA[messageItem] == 'Hazardous' and car['hazardous']:
            lineItem = messageItem[0].upper()
            lineWidth = 1
        elif PSE.ROSETTA[messageItem] == 'Hazardous' and not car['hazardous']:
            lineItem = ' '
            lineWidth = 1

        line += '{} '.format(lineItem.ljust(lineWidth)[:lineWidth])

    return line


def getOpsTrainList(jmriManifest):
    """
    Makes an OPS train list from an extended JMRI manifest.
    Formatted to JMRI manifest standard.
    """

    trainList = jmriManifest

    locosOnTrain = [] # A list of engine objects that carries over from location to location
    carsOnTrain = [] # A list of car objects that carries over from location to location

    for location in trainList['locations']:
    # Engines
        combinedList = [] # A list of car objects
        pickUp = [] # A list of car objects
        setOut = [] # A list of strings (car name)
        for loco in location['engines']['add']:
            pickUp.append(loco)
        for loco in location['engines']['remove']:
            setOut.append(loco['name'])

        combinedList = locosOnTrain + pickUp
        locosOnTrain = []

        for loco in combinedList:            
            if loco['name'] not in setOut:
                locosOnTrain.append(loco)

        location['engines']['add'] = locosOnTrain
    # Cars
        combinedList = [] # A list of car objects
        pickUp = [] # A list of car objects
        setOut = [] # A list of strings (car name)
        for car in location['cars']['add']:
            if car['isLocal']:
                continue
            newSeq = str(int(car['sequence']) - 1000) # Head end pick up
            car.update({'sequence':newSeq})
            pickUp.append(car)
        for car in location['cars']['remove']:
            if car['isLocal']:
                continue
            setOut.append(car['name'])

        combinedList = carsOnTrain + pickUp
        carsOnTrain = []

        for car in combinedList:            
            if car['name'] not in setOut:
                carsOnTrain.append(car)

        carsOnTrain.sort(key=lambda row: row['sequence'])
        newSeq = 6001
        for car in carsOnTrain:
            car.update({'sequence':str(newSeq)})
            newSeq += 1

        location['cars']['add'] = carsOnTrain

    return trainList