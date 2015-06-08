# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from collections import defaultdict
from sgtk.platform.qt import QtCore, QtGui

import sgtk
from . import utils

# import the shotgun_model module from the shotgun utils framework
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
shotgun_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data")

ShotgunOverlayModel = shotgun_model.ShotgunOverlayModel
ShotgunDataRetriever = shotgun_data.ShotgunDataRetriever 

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
                                     download_thumbs=True,
                                     schema_generation=5)

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

        # populate our table model based on this data
        for field_name in sorted(sg_data.keys()):
            
            # todo: add human readable entity types
            field_data = curr_entity_schema.get(field_name)
            
            display_name_item = QtGui.QStandardItem(display_name)
            
            # todo: add formatting
            value = "%s" % sg_data[field_name]
            display_name_value = QtGui.QStandardItem(value)
            
            self._table_model.appendRow([display_name_item, display_name_value])
            
            
        
