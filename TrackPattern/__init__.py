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

# 'global' variables for the Track Pattern module
_trackNameClickedOn = None
_carTypeByEmptyDict = {}
_carTypeByLoadDict = {}
_defaultLoadEmpty = u''
_defaultLoadLoad = u''
