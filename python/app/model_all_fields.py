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
ShotgunOverlayModel = shotgun_model.ShotgunOverlayModel

class SgAllFieldsModel(ShotgunOverlayModel):
    """
    Model that represents the details data that is 
    displayed in the main section of the UI.
    """
    data_updated = QtCore.Signal(dict)

    def __init__(self, parent):
        """
        Model which represents the latest publishes for an entity
        """
        # init base class
        ShotgunOverlayModel.__init__(self,
                                     parent,
                                     overlay_widget=parent,
                                     download_thumbs=False,
                                     schema_generation=3)
        
        self._sg_location = None                
        self.data_refreshed.connect(self._on_data_refreshed)

    def _get_sg_data(self):
        """
        Returns the sg data dictionary for the associated item
        None if not available.
        """
        if self.rowCount() == 0:
            data = {}
        else:
            data = self.item(0).get_sg_data()
        
        return data

    def _on_data_refreshed(self):
        """
        helper method. dispatches the after-refresh signal
        so that a data_updated signal is consistenntly sent
        out both after the data has been updated and after a cache has been read in
        """
        sg_data = self._get_sg_data()
        self.data_updated.emit(sg_data)

    ############################################################################################
    # public interface


    def load_data(self, sg_location):
        """
        Clears the model and sets it up for a particular entity.
        Loads any cached data that exists.
        """
        # set the current location to represent
        self._sg_location = sg_location
          
        filters = [ ["id", "is", self._sg_location.entity_id ] ]
        hierarchy = ["id"]

        ShotgunOverlayModel._load_data(self, 
                                       sg_location.sg_formatter.entity_type, 
                                       filters,
                                       hierarchy, 
                                       sg_location.sg_formatter.all_fields)
        # signal to any views that data now may be available
        self.data_updated.emit(self._get_sg_data())
        self._refresh_data()
        
        
