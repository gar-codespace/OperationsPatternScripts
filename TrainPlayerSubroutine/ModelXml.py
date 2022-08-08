# coding=utf-8
# © 2021, 2022 Greg Ritacco

"""Manipulates the Operations XML """

from psEntities import PatternScriptEntities
from TrainPlayerSubroutine import ModelEntities

import xml.etree.ElementTree as ET
import xml.dom.minidom as MD
from os import linesep as osLinesep


SCRIPT_NAME = 'OperationsPatternScripts.TrainPlayerSubroutine.ModelXml'
SCRIPT_REV = 20220101


class WrangleXml:
    """Generic queries on any operations xml file"""

    def __init__(self, xmlFile):

        self.xmlFile = xmlFile

        return

    def getXml(self, target):

        filePath = PatternScriptEntities.PROFILE_PATH + '\\operations\\' + self.xmlFile + '.xml'
        if not PatternScriptEntities.JAVA_IO.File(filePath).isFile():
            return False

        with PatternScriptEntities.codecsOpen(filePath, 'r', encoding=PatternScriptEntities.ENCODING) as textWorkFile:
            tree = ET.parse(textWorkFile)

            root = tree.getroot()
            subSection = root.findall(target)

            return subSection


class HackXml:
    """  """

    def __init__(self, xmlFileName):

        self.filePath = PatternScriptEntities.PROFILE_PATH + '\\operations\\' + xmlFileName + '.xml'
        self.tree = MD.parseString("<junk/>")
        self.xmlComment = SCRIPT_NAME + ' - ' + PatternScriptEntities.timeStamp()
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

    def updateXmlLoads(self, elementName, newList):

        root = self.tree.documentElement

        topElement = root.getElementsByTagName(elementName)[0]
        for item in topElement.childNodes:
            if item.nodeType == item.COMMENT_NODE:
                topElement.removeChild(item)
            if item.nodeType == item.ELEMENT_NODE:
                topElement.removeChild(item)
                eName = item.tagName
    # add commend
        xComment = self.tree.createComment(self.xmlComment)
        topElement.appendChild(xComment)
    # add defaults back
        newElement = self.tree.createElement('defaults')
        newElement.setAttribute(u'empty', u'E')
        newElement.setAttribute(u'load', u'L')
        topElement.appendChild(newElement)
    # load matrix
        for item in newList:
            for aar, loads in item.items():
                newElement = self.tree.createElement('load')
                newElement.setAttribute('type', aar)
                topElement.appendChild(newElement)
                emptyElement = self.tree.createElement('carLoad')
                emptyElement.setAttribute(u'name', u'Empty')
                emptyElement.setAttribute(u'loadType', u'Empty')
                newElement.appendChild(emptyElement)
                for load in loads:
                    loadElement = self.tree.createElement('carLoad')
                    loadElement.setAttribute(u'name', load)
                    loadElement.setAttribute(u'loadType', u'Load')
                    newElement.appendChild(loadElement)

        return

    def patchUpDom(self, xmlPatch):
        """Work around mini DOM's limitations"""

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
