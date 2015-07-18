# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk import TankError
from sgtk.platform.qt import QtCore, QtGui
import os
import re
import sys
import threading
import datetime
from . import utils

shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
shotgun_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data")
ShotgunDataRetriever = shotgun_data.ShotgunDataRetriever 

class CachedShotgunSchema(QtCore.QObject):
    """
    Wraps around the shotgun schema and caches it for fast lookups.
    """
    
    def __init__(self, parent=None):
        
        QtCore.QObject.__init__(self, parent)
        
        self._app = sgtk.platform.current_bundle()
        
        self._field_schema = {}
        self._type_schema = {}
        self._sg_query_id = None
        
        self._load_cached_schema()
        
        # create a separate sg data fetcher for this model so that we can read in separate 
        # shotgun data asynchronously
        self.__sg_data_retriever = shotgun_data.ShotgunDataRetriever(self)
        self.__sg_data_retriever.work_completed.connect(self.__on_worker_signal)
        self.__sg_data_retriever.work_failure.connect(self.__on_worker_failure)
        self.__sg_data_retriever.start()        
        
        
    def _load_cached_schema(self):
        self._app.log_debug("Loading cached metaschema...")
        # TODO - save/load schema on disk. This needs to be saved per user because
        # the schema is affected by permissions
        return {}
    
    
    def _cache_schema(self):
        self._app.log_debug("Saving metaschema to disk...")
        # TODO - save/load schema on disk. This needs to be saved per user because
        # the schema is affected by permissions
        pass
        
        
    def _refresh_cache(self):
        """
        Request a new fresh cache from shotgun, asynchronously
        """
        self._app.log_debug("Starting to download new metaschema from Shotgun...")
        self.__sg_data_retriever.clear()
        sg_project_id = self._app.context.project["id"]
        self._sg_query_id = self.__sg_data_retriever.get_schema(sg_project_id)
            
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

    def __on_worker_failure(self, uid, msg):
        """
        Asynchronous callback - the worker thread errored.
        """
        msg = shotgun_model.sanitize_qt(msg) # qstring on pyqt, str on pyside
        self._app.log_warning("Could not load sg schema: %s" % msg)        
        
    def __on_worker_signal(self, uid, request_type, data):
        """
        Signaled whenever the worker completes something.
        This method will dispatch the work to different methods
        depending on what async task has completed.
        """
        self._app.log_debug("Metaschema arrived from Shotgun...")
        uid = shotgun_model.sanitize_qt(uid) # qstring on pyqt, str on pyside
        data = shotgun_model.sanitize_qt(data)

        if self._sg_query_id == uid:
            # cache the schema
            self._field_schema = data["fields"]
            self._type_schema = data["types"]
            
            # and write out the data to disk
            self._cache_schema()

    ##########################################################################################
    # public methods

    def request_cache(self):
        """
        Requests that the metaschema is refreshed
        """
        self._refresh_cache()

    def get_type_info(self, sg_entity_type):
        """
        Returns the schema info for an entity type.
        If no data is known for this object, None is returned.
        """
        if sg_entity_type in self._type_schema:
            data = self._type_schema[sg_entity_type]
        else:
            self._refresh_cache()
            data = None
        
        return data
        
    def get_field_info(self, sg_entity_type, field_name):
        """
        Returns the info for a field
        """
        
        # hack - type doesn't seem to be returned in the fields schema
        if field_name == "type":
            # don't trigger a reload = it won't help
            return None
        
        elif sg_entity_type not in self._field_schema:
            self._refresh_cache()
            data = None 
        
        elif field_name not in self._field_schema[sg_entity_type]:
            self._refresh_cache()
            data = None 

        else:
            data = self._field_schema[sg_entity_type][field_name]
        
        return data
        
