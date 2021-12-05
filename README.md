## JMRI Operations - Pattern Scripts (pre-release)
This is a jython plugin for JMRI Operations Pro that creates track patterns for any single location.  
Track patterns are lists of cars in tracks, essentially an inventory report.  
The user can then directly move selected cars from one track to another at the selected location, without building and terminating trains.   
This is the current version, 2.0, and is under development. Consider it pre-release.  
Version 1.0 was a concept test and is not available.

## Yard Patterns
Yard patterns are track patterns for a yard. They are a useful tool for a yardmaster to use to help manage his/her yard.  
A yardmaster would use a yard pattern to:  
* Check track capacity and verify inventory.  
* Group cars by destination or train.  
* Create switch lists to assign work to crews.  
* Redefine a yard tracks use throughout an operating session.  

## Intra-Plant Switching
Track patterns can also be used for intra-plant switching, which are switching movements confined to a single location.  
Examples of this would include:  
* A mill operator moving coal and coke to and from a furnace.  
* A mine operator loading hoppers from a pool of empties.  
* An inter-modal operator selecting certain types of well cars to load.  
* A grain exchange selling loaded hoppers to grangers.  

## Plugin Notables
Moving cars around a yard, the yard pattern, generally involves working with JMRI 'Yards.'  
Moving cars around a location, Intra-Plant swtiching, generally involves JMRI 'Classification/Interchange' tracks, and 'Spurs.'
Moving cars FROM a spur by using this plugin will apply the spur's schedule, setting the appropriate load and FD.  
If there is no schedule the plugin will attempt to apply the car's RWE or RWL parameters.
If no RWE or RWL, the plugin will then try to load the car with the custom designation for 'Empty' for that cars' load type.  
If none of the above, a car moved from a spur will have the default empty designation applied.  

## How To Use This Plugin
The following are YouTube videos covering the use of this plugin:  
Not Yet But Soon :)  
How to add this plugin to JMRI.  
How to set up and use this plugin.  
Yard pattern example.  
Intra-Plant switching example.
How to modify this plugin  

## Testing
This plugin has been tested with:
* JMRI 4.25.4
* Java 8u301
* Windows 10 Pro and Home

## License
The scripts included in this plugin are © 2021 Greg Ritacco.  
Other then that, there are no restrictions on use.

![GitHub repo file count](https://img.shields.io/github/directory-file-count/GregRitacco/JMRI-Operations---Pattern-Scripts?style=flat-square)
