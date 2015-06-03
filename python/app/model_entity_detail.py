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

class SgEntityDetailsModel(ShotgunOverlayModel):
    """
    Model which shows the publish history
    """

    def __init__(self, parent):
        """
        Model which represents the latest publishes for an entity
        """
        
        # current publish we have loaded
        self._curr_entity_dict = None
        self._sg_query_id = None
        
        self._sg_schema = None
        
        # init base class
        ShotgunOverlayModel.__init__(self,
                                     parent,
                                     overlay_widget=parent,
                                     download_thumbs=True,
                                     schema_generation=5)

        self._app = sgtk.platform.current_bundle()
        
        # create a separate sg data fetcher for this model so that we can read in separate 
        # shotgun data asynchronously
        self.__sg_data_retriever = shotgun_data.ShotgunDataRetriever(self)
        self.__sg_data_retriever.work_completed.connect(self.__on_worker_signal)
        self.__sg_data_retriever.work_failure.connect(self.__on_worker_failure)
        self.__sg_data_retriever.start()

        # create the coupled model
        self._table_model = QtGui.QStandardItemModel(parent) 
        
    def get_table_model(self):
        """
        Returns the embedded table model
        """
        return self._table_model
        

    def destroy(self):
        """
        Call this method prior to destroying this object.
        This will ensure all worker threads etc are stopped.
        """
        # first disconnect our worker completely
        self.__sg_data_retriever.work_completed.disconnect(self.__on_worker_signal)
        self.__sg_data_retriever.work_failure.disconnect(self.__on_worker_failure)
        # gracefully stop thread
        self.__sg_data_retriever.stop()
        # call base class
        ShotgunOverlayModel.destroy(self)


    ############################################################################################
    # slots


    def __on_worker_failure(self, uid, msg):
        """
        Asynchronous callback - the worker thread errored.
        """
        uid = shotgun_model.sanitize_qt(uid) # qstring on pyqt, str on pyside
        msg = shotgun_model.sanitize_qt(msg)

        self._app.log_warning("Could not load sg schema: %s" % msg)
        
        full_msg = "Error retrieving Shotgun schema: %s" % msg        
        self._show_overlay_error_message(full_msg)
        

    def __on_worker_signal(self, uid, request_type, data):
        """
        Signaled whenever the worker completes something.
        This method will dispatch the work to different methods
        depending on what async task has completed.
        """
        
        # hide spinner
        self._hide_overlay_info()        
        
        uid = shotgun_model.sanitize_qt(uid) # qstring on pyqt, str on pyside
        data = shotgun_model.sanitize_qt(data)

        if self._sg_query_id == uid:
            # cache the schema
            self._sg_schema  = data["sg"]
            import pprint
            print "schema %s" % pprint.pformat(self._sg_schema)
            
            # and proceed to main loading code
            self._load_detail_data()


    ############################################################################################
    # public interface

    def load_data(self, sg_entity_dict):
        """
        Clears the model and sets it up for a particular entity.
        Loads any cached data that exists.
        """        
        self._table_model.clear()
        self._curr_entity_dict = sg_entity_dict
        self.__sg_data_retriever.clear()
        
        if self._sg_schema is None:
            # read in the schema before we load the data
            # this is then cached in memory
            self._show_overlay_spinner()
            sg_project_id = self._app.context.project["id"]
            self._sg_query_id = self.__sg_data_retriever.get_schema(sg_project_id)
            
        else:
            # got the schema, jump straight to main data load
            self._load_detail_data()
        

    def _load_detail_data(self):
        """
        Loads the actual detail data given schema data
        """
        # at this point we can assume that we have cached the schema
        
        # get schema subset for this entity type
        curr_entity_schema = self._sg_schema.get(self._curr_entity_dict["type"])

        curr_entity_fields = curr_entity_schema.keys() 

        filters = [ ["id", "is", self._curr_entity_dict["id"] ] ]
        hierarchy = ["id"]

        ShotgunOverlayModel._load_data(self, 
                                       self._curr_entity_dict["type"], 
                                       filters, 
                                       hierarchy, 
                                       curr_entity_fields)
        self._refresh_data()


    def _finalize_item(self, item):
        """
        Called whenever an item is fully constructed, either because a shotgun query returned it
        or because it was loaded as part of a cache load from disk.

        :param item: QStandardItem that is about to be added to the model. This has been primed
                     with the standard settings that the ShotgunModel handles.
        """
        sg_data = item.get_sg_data()
        
        curr_entity_schema = self._sg_schema.get(self._curr_entity_dict["type"])
        
        # populate our table model based on this data
        for field_name in sorted(sg_data.keys()):
            
            # get the display name
            field_data = curr_entity_schema.get(field_name)
            
            if field_data:
                display_name = field_data["name"]["value"]
            else:
                # something missing from metaschema. Go with default
                display_name = field_name
            
            display_name_item = QtGui.QStandardItem(display_name)
            
            value = "%s" % sg_data[field_name]
            display_name_value = QtGui.QStandardItem(value)
            
            self._table_model.appendRow([display_name_item, display_name_value])
            
            
        
