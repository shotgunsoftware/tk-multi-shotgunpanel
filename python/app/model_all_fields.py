# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform.qt import QtCore, QtGui
import sgtk

# import the shotgun_model module from the shotgun utils framework
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
shotgun_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data")

ShotgunOverlayModel = shotgun_model.ShotgunOverlayModel 

from .modules.schema import CachedShotgunSchema

class SgAllFieldsModel(ShotgunOverlayModel):
    """
    Model that handles the "all fields" tab.
    
    The model wraps around a table model that gets updated with values
    from this shotgun model.
    """

    def __init__(self, parent):
        """
        Model which represents the latest publishes for an entity
        """        
        # current publish we have loaded
        self._sg_location = None
        
        # init base class
        ShotgunOverlayModel.__init__(self,
                                     parent,
                                     overlay_widget=parent,
                                     download_thumbs=False,
                                     schema_generation=6,
                                     bg_load_thumbs=True)

        self._app = sgtk.platform.current_bundle()
        
        # create the coupled model
        self._table_model = QtGui.QStandardItemModel(parent)
        
    def get_table_model(self):
        """
        Returns the embedded table model
        """
        return self._table_model

    ############################################################################################
    # public interface

    def load_data(self, sg_location):
        """
        Clears the model and sets it up for a particular entity.
        Loads any cached data that exists.
        """        
        
        self._sg_location = sg_location
        self._table_model.clear()
        
        filters = [ ["id", "is", sg_location.entity_id ] ]
        hierarchy = ["id"]

        ShotgunOverlayModel._load_data(self, 
                                       sg_location.sg_formatter.entity_type, 
                                       filters,
                                       hierarchy, 
                                       sg_location.sg_formatter.all_fields)
        self._refresh_data()


    def _finalize_item(self, item):
        """
        Called whenever an item is fully constructed, either because a shotgun query returned it
        or because it was loaded as part of a cache load from disk.

        :param item: QStandardItem that is about to be added to the model. This has been primed
                     with the standard settings that the ShotgunModel handles.
        """
        sg_data = item.get_sg_data()
        sg_type = sg_data["type"]
        
        formatter = self._sg_location.sg_formatter

        # populate our table model based on this data
        for field_name in sorted(sg_data.keys()):
            
            # get the human readable field display name
            display_name = CachedShotgunSchema.get_field_display_name(sg_type, field_name)
            display_name_item = QtGui.QStandardItem(display_name)
            
            # set field names to align at the top so that for large values
            # (like descriptions) it won't look strange. Also dial down the color
            # a little bit by adding transparency. 
            display_name_item.setData(QtCore.Qt.AlignTop, QtCore.Qt.TextAlignmentRole)
            field_color = QtGui.QColor(self._app.style_constants["SG_FOREGROUND_COLOR"])
            field_color.setAlpha(120)
            display_name_item.setData(QtGui.QBrush(field_color), QtCore.Qt.ForegroundRole)
            
            # and add the value
            value = formatter.format_raw_value(sg_type, field_name, sg_data[field_name], "nolink")
            display_name_value = QtGui.QStandardItem(value)
            
            self._table_model.appendRow([display_name_item, display_name_value])
            
