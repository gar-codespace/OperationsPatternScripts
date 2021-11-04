# JMRI-Operations---Pattern-Scripts
This is a plugin for JMRI Operations Pro.
The main script is built around the plugin architecture and is designed to run any number of subroutines
Each subroutine is built around the Model, View, Controller architecture.
There is only one subroutine at this time- Track Pattern.
Track Pattern makes a pattern switch list from a set of validated tracks from a validated location.
The switch list print format is taken from Trains/Tools/Manifest Print Options/Local Move Message Format
Optional CSV switch list by checking Trains/Tools/Options/Generate CSV Switch List
Cars listed in the switch lists can be moved to other tracks within the location, subject to track length and other JMRI restrictions.
