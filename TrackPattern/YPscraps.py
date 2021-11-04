class yardPattern():
    '''Makes a pattern for a yard location and outputs track lists for some or all tracks in the specified yard'''

# Class variables
    scriptRev = 'ypModelV2 rev.20211015'
    # set logging
    logLevel = 10
    logMode = 'w' # write over the old log
    logName = 'ypLog'

    def __init__(self, yardLoc, tracks):
        '''Set the default yard location for your layout'''

    # script specific
        self.yardLoc = unicode(yardLoc, yUtil.setEncoding())
        self.useTracks = tracks
        self.yardTrackType = None
    # boilerplate
        self.lm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.locations.LocationManager)
        self.cm = jmri.InstanceManager.getDefault(jmri.jmrit.operations.rollingstock.cars.CarManager)
        self.profilePath = jmri.util.FileUtil.getProfilePath()
        return

    def runScript(self):
        '''Run the program'''

    # Load the config file
        configFile = yUtil.readConfigFile()
    # Setup report
        switchlistPath = self.profilePath + 'operations\\switchLists'
        if not (oPath.isdir(switchlistPath)):
            mkdir(switchlistPath)
        yTimeNow = time.time()
        railroadName = unicode(jmri.jmrit.operations.setup.Setup.getRailroadName(), yUtil.setEncoding())
    # Setup gplogging
        gpLogPath = self.profilePath + 'operations\\buildstatus\\Yard Pattern (' + self.yardLoc +').txt'
        ypLog = yUtil.gpLogging(self.logName)
        ypHandle = ypLog.gpStartLogFile(gpLogPath, self.logLevel, self.logMode)
        ypLog.gpInfo(yardPattern.scriptRev)
        ypLog.gpInfo('Built on ' + yUtil.jVT())
    # Validate the yard location
        if (yUtil.checkYard(self.yardLoc, None)): # FIX THIS
            ypLog.gpInfo('Location (' + self.yardLoc + ') is valid')
        else:
            ypLog.gpCritical('Location (' + self.yardLoc + ') is not valid, or has no yard tracks')
            ypLog.gpCritical('Enter a valid location or select use all tracks')
            ypLog.gpCritical('Script stopped')
            ypLog.gpStopLogFile(ypHandle)
            system(yUtil.systemInfo() + gpLogPath)
            return
    # Make a list of the cars at the validated yard/tracks
        ypLog.gpInfo('Get all the cars for the location and tracks')
        carYardPattern = []
        for track in self.useTracks:
            carYardPattern.append(yUtil.getCarObjects(self.yardLoc, track))
        ypLog.gpInfo('Car list created for validated location and tracks')
    # make the pattern
        yardPatternDict = yUtil.makeYardPattern(self.useTracks, self.yardLoc)
        yardPatternDict.update({'RT': u'Yard Pattern for Track'})
        ypLog.gpInfo('Yard pattern created')
    # save the pattern as a json file
        jsonCopyTo = self.profilePath + 'operations\\jsonManifests\\Yard Pattern (' + self.yardLoc + ').json'
        jsonObject = json.dumps(yardPatternDict, indent=2, sort_keys=True) #yardPatternDict
        with cOpen(jsonCopyTo, 'wb', encoding=yUtil.setEncoding()) as jsonWorkFile:
            jsonWorkFile.write(jsonObject)
        ypLog.gpInfo('Yard pattern saved as JSON')
    # save the pattern as a switchlist
        textCopyTo = self.profilePath + 'operations\\switchLists\\Yard Pattern (' + self.yardLoc + ').txt'
        textObject = yUtil.makeSwitchlist(yardPatternDict, True)
        with cOpen(textCopyTo, 'wb', encoding=yUtil.setEncoding()) as textWorkFile:
            textWorkFile.write(textObject)
        system(yUtil.systemInfo() + textCopyTo)
        ypLog.gpInfo('Yard pattern saved as switch list text file')
    # save the pattern as a csv switchlist
        if (jmri.jmrit.operations.setup.Setup.isGenerateCsvSwitchListEnabled()):
            csvSwitchlistPath = self.profilePath + 'operations\\csvSwitchLists'
            if not (oPath.isdir(csvSwitchlistPath)):
                mkdir(csvSwitchlistPath)
            csvCopyTo = self.profilePath + 'operations\\csvSwitchLists\\Yard Pattern (' + self.yardLoc + ').csv'
            csvObject = yUtil.makeCsvSwitchlist(yardPatternDict)
            with cOpen(csvCopyTo, 'wb', encoding=yUtil.setEncoding()) as csvWorkFile:
                csvWorkFile.write(csvObject)
            ypLog.gpInfo('Yard pattern saved as switch list CSV file')
    # All done
        computeTime = 'Yard pattern export (sec): ' + ('%s' % (time.time() - yTimeNow))[:6]
        ypLog.gpInfo('Yard pattern completed')
        ypLog.gpInfo(computeTime)
        ypLog.gpStopLogFile(ypHandle)
        print(yardPattern.scriptRev)
        print(computeTime)
        return
