# coding=utf-8
# No restrictions on use
# © 2021 Greg Ritacco

'''Track Pattern imports and global variables'''

import TrackPattern.Model as Model
import TrackPattern.View as View
import TrackPattern.Controller as Controller
import TrackPattern.ModelEntities as ModelEntities
import TrackPattern.ViewEntities as ViewEntities
import TrackPattern.ModelSetCarsForm as ModelSetCarsForm
import TrackPattern.ViewSetCarsForm as ViewSetCarsForm
import TrackPattern.ControllerSetCarsForm as ControllerSetCarsForm

__all__ = ['Model', 'View', 'Controller', 'ModelEntities', 'ViewEntities', 'ModelSetCarsForm', 'ViewSetCarsForm', 'ControllerSetCarsForm']

_trackNameClickedOn = None
_carTypeByEmptyDict = {}
_carTypeByLoadDict = {}
_defaultLoadEmpty = u''
_defaultLoadLoad = u''
