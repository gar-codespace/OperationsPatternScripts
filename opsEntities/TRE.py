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

def translateCarFormat(car):
    """
    For items found in the Setup.get< >ManifestMessageFormat()
    """
                
    newCarFormat = {}

    newCarFormat['Road'] = car['road']
    newCarFormat['Number'] = car['number']
    newCarFormat['Type'] = car['carType']
    newCarFormat['Length'] = car['length']
    newCarFormat['Weight'] = car['weightTons']
    newCarFormat['Load'] = car['load']
    newCarFormat['Load_Type'] = car['loadType']
    newCarFormat['Hazardous'] = car['hazardous']
    newCarFormat['Color'] = car['color']
    newCarFormat['Kernel'] = car['kernel']
    newCarFormat['Kernel_Size'] = car['kernelSize']
    newCarFormat['Owner'] = car['owner']
    newCarFormat['Division'] = car['division']
    newCarFormat['Location'] = car['location']['userName']
    newCarFormat['Track'] = car['location']['track']['userName']
    newCarFormat['Destination'] = car['destination']['userName']
    newCarFormat['Dest&Track'] = '{}-{}'.format(car['destination']['userName'], car['destination']['track']['userName'])
    newCarFormat['Final_Dest'] = car['finalDestination']['userName']
    newCarFormat['FD&Track'] = '{}-{}'.format(car['finalDestination']['userName'], car['finalDestination']['track']['userName'])
    newCarFormat['Comment'] = car['comment']
    newCarFormat['SetOut_Msg'] = car['removeComment']
    newCarFormat['PickUp_Msg'] = car['addComment']
    newCarFormat['RWE'] = car['returnWhenEmpty']

    return newCarFormat

def getShortLoadType(car):
    """
    Replaces empty and load with E, L, or O for occupied.
    JMRI defines custom load type as empty but default load type as E, hence the 'or' statement.
    Load, Empty, Occupied and Unknown are translated by the bundle.
    """

    carObject = PSE.CM.getByRoadAndNumber(car['road'], car['number'])

    lt =  PSE.getBundleItem('Unknown').upper()[0]
    if carObject.getLoadName() == 'E':
        lt = PSE.getBundleItem('Empty').upper()[0]
    if carObject.getLoadName() == 'L':
        lt = PSE.getBundleItem('Load').upper()[0]
    if carObject.getLoadType() == 'empty' or carObject.getLoadType() == 'E':
        lt = PSE.getBundleItem('Empty').upper()[0]

    if carObject.getLoadType() == 'load' or carObject.getLoadType() == 'L':
        lt = PSE.getBundleItem('Load').upper()[0]

    if carObject.isCaboose() or carObject.isPassenger():
        lt = PSE.getBundleItem('Occupied').upper()[0]

    return lt

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
        lineItem = carItems[PSE.ROSETTA[messageItem]]
        lineWidth = PSE.REPORT_ITEM_WIDTH_MATRIX[messageItem] + 1

        if 'Tab' in messageItem:
            continue
    # Special case handling for car load type
        if PSE.ROSETTA[messageItem] == 'Load_Type':
            line += getShortLoadType(car).ljust(1) + ' '
            continue
    # Special case handling for car number
        if PSE.ROSETTA[messageItem] == 'Number':
            line += lineItem.rjust(lineWidth) + ' '
            continue
    # Special case handling for the hazardous flag
        if PSE.ROSETTA[messageItem] == 'Hazardous' and car['hazardous']:
            lineItem = messageItem[0].upper()
            lineWidth = 2
        elif PSE.ROSETTA[messageItem] == 'Hazardous' and not car['hazardous']:
            lineItem = ' '
            lineWidth = 2

        rowItem = lineItem.ljust(lineWidth)[:lineWidth]
        line += rowItem

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
        lineItem = carItems[PSE.ROSETTA[messageItem]]
        lineWidth = PSE.REPORT_ITEM_WIDTH_MATRIX[messageItem] + 1

        if 'Tab' in messageItem:
            continue
    # Special case handling for car load type
        if PSE.ROSETTA[messageItem] == 'Load_Type':
            line += getShortLoadType(car).ljust(1) + ' '
            continue
    # Special case handling for car number
        if PSE.ROSETTA[messageItem] == 'Number':
            line += lineItem.rjust(lineWidth) + ' '
            continue
    # Special case handling for the hazardous flag
        if PSE.ROSETTA[messageItem] == 'Hazardous' and car['hazardous']:
            lineItem = messageItem[0].upper()
            lineWidth = 2
        elif PSE.ROSETTA[messageItem] == 'Hazardous' and not car['hazardous']:
            lineItem = ' '
            lineWidth = 2

        rowItem = lineItem.ljust(lineWidth)[:lineWidth]
        line += rowItem

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
        lineItem = carItems[PSE.ROSETTA[messageItem]]
        lineWidth = PSE.REPORT_ITEM_WIDTH_MATRIX[messageItem]

        if 'Tab' in messageItem:
            continue
    # Special case handling for car load type
        if PSE.ROSETTA[messageItem] == 'Load_Type':
            line += getShortLoadType(car).ljust(1) + ' '
            continue
    # Special case handling for car number
        if PSE.ROSETTA[messageItem] == 'Number':
            line += lineItem.rjust(lineWidth) + ' '
            continue
    # Special case handling for the hazardous flag
        if PSE.ROSETTA[messageItem] == 'Hazardous' and car['hazardous']:
            lineItem = messageItem[0].upper()
            lineWidth = 1
        elif PSE.ROSETTA[messageItem] == 'Hazardous' and not car['hazardous']:
            lineItem = ' '
            lineWidth = 1

        rowItem = lineItem.ljust(lineWidth)[:lineWidth]
        line += rowItem + ' '

    return line


