# Comment
# import jmri
# from sys import path as sysPath
#
# fileRoot = jmri.util.FileUtil.getPreferencesPath()
# _currentVersionn = str(jmri.util.FileUtil.findFiles('MainScript.py', fileRoot).pop()).split('\\')
# _currentVersionn.pop(-1)
# _currentVersionn = '\\'.join(_currentVersionn)
#
# sysPath.append(_currentVersionn)
import MainScriptEntities
import PluginLocations


__all__ = ['MainScriptEntities', 'PluginLocations']
