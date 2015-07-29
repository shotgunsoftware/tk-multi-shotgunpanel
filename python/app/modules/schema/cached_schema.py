# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

# make sure that py25 has access to with statement
from __future__ import with_statement

import os
import sgtk
from sgtk import TankError
from sgtk.platform.qt import QtCore, QtGui
import cPickle as pickle

shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
shotgun_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data") 

class CachedShotgunSchema(object):
    """
    Wraps around the shotgun schema and caches it for fast lookups.
    """
    __instance = None
    
    @classmethod
    def __get_instance(cls):
        """
        Singleton access
        """
        if cls.__instance is None:
            cls.__instance = CachedShotgunSchema()
        return cls.__instance
    
    def __init__(self):
        """
        Constructor
        """
        self._app = sgtk.platform.current_bundle()
        self._field_schema = {}
        self._type_schema = {}
        self.__sg_data_retrievers = {}
        self._status_data = {}
        
        self._sg_schema_query_id = None
        self._sg_status_query_id = None
        
        self._schema_cache_path = os.path.join(self._app.cache_location, "sg_schema.pickle")
        self._status_cache_path = os.path.join(self._app.cache_location, "sg_status.pickle")

        self._schema_loaded = self._load_cached_schema()
        self._status_loaded = self._load_cached_status()        
        
        
    def _load_cached_status(self):
        """
        Load cached status from disk if it exists
        """
        cache_loaded = False
        if os.path.exists(self._status_cache_path):
            try:
                self._app.log_debug("Loading cached status from '%s'" % self._status_cache_path)
                with open(self._status_cache_path, "rb") as fh:
                    self._status_data = pickle.load(fh)
                    cache_loaded = True
            except Exception, e:
                self._app.log_warning("Could not open cached status "
                                      "file '%s': %s" % (self._status_cache_path, e))       
        return cache_loaded
        
    def _load_cached_schema(self):
        """
        Load cached metaschema from disk if it exists
        
        :returns: true if cache was loaded, false if not
        """
        cache_loaded = False
        if os.path.exists(self._schema_cache_path):
            try:
                self._app.log_debug("Loading cached schema from '%s'" % self._schema_cache_path)
                with open(self._schema_cache_path, "rb") as fh:
                    data = pickle.load(fh)
                    self._field_schema = data["field_schema"]
                    self._type_schema = data["type_schema"]
                    cache_loaded = True
            except Exception, e:
                self._app.log_warning("Could not open cached schema "
                                      "file '%s': %s" % (self._schema_cache_path, e))
        return cache_loaded            
    
    def _cache_schema(self):
        """
        Write schema cache to disk
        """
        self._app.log_debug("Saving schema to '%s'..." % self._schema_cache_path)
        try:
            with open(self._schema_cache_path, "wb") as fh:
                data = {"field_schema": self._field_schema, 
                        "type_schema": self._type_schema}
                pickle.dump(data, fh)
        except Exception, e:
            self._app.log_warning("Could not write schema "
                                  "file '%s': %s" % (self._schema_cache_path, e))            
        
    def _cache_status(self):
        """
        Write status cache to disk
        """
        self._app.log_debug("Saving status to '%s'..." % self._status_cache_path)
        try:
            with open(self._status_cache_path, "wb") as fh:
                pickle.dump(self._status_data, fh)
        except Exception, e:
            self._app.log_warning("Could not write status "
                                  "file '%s': %s" % (self._status_cache_path, e))            

    def _refresh_schema(self):
        """
        Request a new fresh cache from shotgun, asynchronously
        """
        sg_project_id = self._app.context.project["id"]
                
        self._app.log_debug("Starting to download new metaschema from Shotgun...")
        
        if len(self.__sg_data_retrievers) == 0:
            self._app.log_warning("No data retrievers registered with this " 
                                  "schema manager. Cannot load shotgun schema.")
        else:
            # pick the first one
            dr = self.__sg_data_retrievers.values()[0]
            self._sg_schema_query_id = dr.get_schema(sg_project_id)

    def _check_schema_refresh(self, entity_type, field_name=None):
        """
        Check and potentially trigger a cache refresh
        """
        refresh_needed = False
        if entity_type not in self._field_schema:
            self._app.log_debug("Schema cache check: Type '%s' "
                                "triggered a cache refresh" % entity_type)        
            self._refresh_schema()
            refresh_needed = True

        elif field_name and field_name != "type" and field_name not in self._field_schema[entity_type]:
            self._app.log_debug("Schema cache check: Field '%s.%s' "
                                "triggered a cache refresh" % (entity_type, field_name))        
            self._refresh_schema()
            refresh_needed = True
        
        return refresh_needed
        
    def _refresh_status(self):
        """
        Request status data from shotgun
        """
        fields = ["bg_color", "code", "name"]

        self._app.log_debug("Starting to download status list from Shotgun...")
        
        if len(self.__sg_data_retrievers) == 0:
            self._app.log_warning("No data retrievers registered with this " 
                                  "schema manager. Cannot load shotgun status.")
        else:
            # pick the first one
            dr = self.__sg_data_retrievers.values()[0]
            self._sg_status_query_id = dr.execute_find("Status", [], fields)        
        
    def _on_worker_failure(self, uid, msg):
        """
        Asynchronous callback - the worker thread errored.
        """
        if uid == self._sg_schema_query_id:
            msg = shotgun_model.sanitize_qt(msg) # qstring on pyqt, str on pyside
            self._app.log_warning("Could not load sg schema: %s" % msg)
        
        elif uid == self._sg_status_query_id:
            msg = shotgun_model.sanitize_qt(msg) # qstring on pyqt, str on pyside
            self._app.log_warning("Could not load sg status: %s" % msg)
        
    def _on_worker_signal(self, uid, request_type, data):
        """
        Signaled whenever the worker completes something.
        This method will dispatch the work to different methods
        depending on what async task has completed.
        """
        uid = shotgun_model.sanitize_qt(uid) # qstring on pyqt, str on pyside
        data = shotgun_model.sanitize_qt(data)

        if self._sg_schema_query_id == uid:
            self._app.log_debug("Metaschema arrived from Shotgun...")
            # store the schema
            self._field_schema = data["fields"]
            self._type_schema = data["types"]
            # and write out the data to disk
            self._cache_schema()
        
        elif uid == self._sg_status_query_id:
            self._app.log_debug("Status list arrived from Shotgun...")
            # store status
            self._status_data = {}
            for x in data["sg"]:
                self._status_data[ x["code"] ] = x
            # and write out the data to disk
            self._cache_status()

    ##########################################################################################
    # public methods
    
    @classmethod
    def register_data_retriever(cls, data_retriever):
        """
        Register a data retriever with the singleton.
        Once a data retriever has been registered, the schema singleton
        can refresh its cache.
        
        :data_retriever: shotgun data retriever object to register
        """
        self = cls.__get_instance()
        
        # add to dict of registered data retrievers
        obj_hash = id(data_retriever)
        self.__sg_data_retrievers[obj_hash] = data_retriever
        data_retriever.work_completed.connect(self._on_worker_signal)
        data_retriever.work_failure.connect(self._on_worker_failure)
        
        if not self._status_loaded:
            self._status_loaded = True
            self._refresh_status()
        
        if not self._schema_loaded:
            self._schema_loaded = True
            self._refresh_schema()
        
    @classmethod
    def unregister_data_retriever(cls, data_retriever):
        """
        Unregister a previously registered data retriever with the singleton.
        
        :data_retriever: shotgun data retriever object to unregister
        """     
        self = cls.__get_instance()
        
        obj_hash = id(data_retriever)
        if obj_hash in self.__sg_data_retrievers:
            self._app.log_debug("Unregistering %r from schema manager" % data_retriever)
            data_retriever = self.__sg_data_retrievers[obj_hash]
            del self.__sg_data_retrievers[obj_hash]
            data_retriever.work_completed.disconnect(self._on_worker_signal)
            data_retriever.work_failure.disconnect(self._on_worker_failure)
        else:
            self._app.log_warning("Could not unregister unknown data "
                                  "retriever %r with schema manager" %  data_retriever)

    @classmethod
    def get_type_display_name(cls, sg_entity_type):
        """
        Returns the schema info for an entity type.
        If no data is known for this object, None is returned.
        
        If the entity type is not known to the system, a cache reload
        will be triggered, meaning that subsequent cache requests may
        return valid data.
        
        :param sg_entity_type: Shotgun entity type
        :returns: schema information dict if entity type is known, None if not.
        """
        
        self = cls.__get_instance()
        
        display_name = sg_entity_type
            
        if not self._check_schema_refresh(sg_entity_type):
            # cache contains our item
            data = self._type_schema[sg_entity_type]
            display_name = data["name"]["value"]            
        
        return display_name
        
    @classmethod
    def get_field_display_name(cls, sg_entity_type, field_name):
        """
        Returns the display name for a given field. If the field
        cannot be found or the value is not yet cached, 
        the field name is returned.
        """
        self = cls.__get_instance()
        
        display_name = field_name

        if field_name == "type":
            # type doesn't seem to exist in the schema
            # so treat as a special case
            display_name = "Type"
        
        elif not self._check_schema_refresh(sg_entity_type, field_name):
            # cache contains our item
            data = self._field_schema[sg_entity_type][field_name]
            display_name = data["name"]["value"]

        return display_name
        

    @classmethod
    def get_empty_phrase(cls, sg_entity_type, field_name):
        """
        Get an appropriate phrase to describe the fact that 
        a field is empty. The phrase will differ depending on 
        the data type of the field.
        """
        self = cls.__get_instance()
        
        empty_value = "Not set"
        
        if not self._check_schema_refresh(sg_entity_type, field_name):
            # cache contains our item
            data = self._field_schema[sg_entity_type][field_name]
            data_type = data["data_type"]["value"]
            
            if data_type == "Entity":
                empty_value = "Not set"

        return empty_value

    @classmethod
    def get_status_display_name(cls, status_code, name_only=False):
        """
        Returns the display name for a given status code.
        If the status code cannot be found or haven't been loaded,
        the code is returned back.
        
        :param status_code: Status short code (e.g 'ip')
        :param name_only: If True, the long status name will be returned
                          as a string (e.g. 'In Progress'). If false, 
                          additional html decoration may be returned.
        :returns: string with descriptive status name 
        """
        self = cls.__get_instance()
        
        display_name = status_code
        
        if status_code not in self._status_data:
            # unknown status. Most likely our cache is out of date
            self._refresh_status()
        
        else:
            data = self._status_data[status_code]
        
            display_name = data.get("name") or status_code

            status_color = data.get("bg_color")
            if status_color and not name_only:
                display_name = "%s&nbsp;<span style='color: rgb(%s)'>&#9608;</span>" % (display_name, status_color)
        
        return display_name
