## JMRI-Operations - Pattern-Scripts (pre-release)
This is a jython plugin for JMRI Operations Pro that creates track patterns for any single location.  
The user can then set selected cars from one track to another at the selected location.  
This is the current version, 2.0, and is under development. Consider it pre-release.  
Version 1.0 is a prototype concept test and is not available.

## About This Plugin
Track patterns are lists of cars in tracks, essentially an inventory report.  
A yardmaster would use a track pattern to:  
* Check track capacity  
* Group cars by destination or train  
* Verify inventory  
* Create switch lists to assign work to crews  

This plugin allows the above. Thus a yard location can be inventoried and organized by a yardmaster and work can be done by switch crews without the need to build and terminate trains. This offers additional flexibility in yard utilization in that tracks do not have to be pre-defined to serve particular needs, those needs can shift with changing demand.  

## Important Limitations
JMRI has two types of yard locations, one is called 'Yards' and the other is called 'Classification/Interchange'  
This plugin is designed to work with the type of yard location defined as 'Yards'  
However, I have expanded the scope of this plugin to work with all types of tracks.  
It is important to differentiate between the words 'move' and 'set'  
When JMRI moves a car, it applies the spurs' schedule.  
When this plugin sets a car, the spurs' schedule is not applied.  
Accordingly, I would not recommend using this plugin to do 'intra plant' switching, I hope to cover that in version 2.1.  

## How To Use This Plugin
The following are YouTube videos covering the use of this plugin:  
Not Yet But Soon :)  
How to add this plugin to JMRI  
How to use this plugin  
Real world example  
How to modify this plugin  

## Testing
This plugin has been tested with:
* Windows 10 Pro and Home
* JMRI 4.25.4
* Java 8u301

![GitHub repo file count](https://img.shields.io/github/directory-file-count/GregRitacco/JMRI-Operations---Pattern-Scripts?style=flat-square)
