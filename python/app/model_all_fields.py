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
ShotgunModel = shotgun_model.ShotgunModel

class SgAllFieldsModel(ShotgunModel):
    """
    Model that represents all the fields for an entity, as defined
    by a shotgun location object.
    
    Data is loaded in via the load_data(location_object) method and the
    model will use the sg_location.sg_formatter.all_fields to determine
    which fields to load in.
    
    Once loaded or updated, a data_updated signal is emitted.
    
    :signal data_updated(dict): Signal emitted when shotgun data has arrived.
        the signal carries with it a dictionary of Shotgun data, as specified
        by the location object passed in to :meth:`load_data()`.
    """
    
    data_updated = QtCore.Signal(dict)

    def __init__(self, parent, bg_task_manager):
        """
        Constructor
        
        :param parent: QT parent object.
        """
        # init base class
        ShotgunModel.__init__(self, 
                              parent, 
                              download_thumbs=False, 
                              bg_task_manager=bg_task_manager)
        
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
        Helper method. dispatches the after-refresh signal
        so that a data_updated signal is consistently sent
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

        ShotgunModel._load_data(self, 
                                       sg_location.sg_formatter.entity_type, 
                                       filters,
                                       hierarchy, 
                                       sg_location.sg_formatter.all_fields)
        # signal to any views that data now may be available
        self.data_updated.emit(self._get_sg_data())
        self._refresh_data()
        
        
