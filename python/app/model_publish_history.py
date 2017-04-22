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

ShotgunModel = shotgun_model.ShotgunModel

from .model_entity_listing import SgEntityListingModel

class SgPublishHistoryListingModel(SgEntityListingModel):
    """
    Model that shows the version history for a publish.
    
    The data fetching pass in this model has a two-pass 
    setup: First, the details for the given publish are fetched:
    version number, type, task etc. Once we have those fields, 
    the shotgun model is updated to retrieve all associated 
    publishes.
    """

    def __init__(self, entity_type, parent, bg_task_manager):
        """
        Constructor.
        
        :param entity_type: The entity type that should be loaded into this model.
                            Needs to be a PublishedFile or TankPublishedFile.        
        :param parent: QT parent object
        :param bg_task_manager: task manager used to process data         
        """
        
        # current publish we have loaded
        self._sg_location = None
        
        # the version number for the current publish
        self._current_version = None
        
        # tracking the background task
        self._sg_query_id = None
        
        # overlay for reporting errors
        self._overlay = None
        
        # init base class
        SgEntityListingModel.__init__(self, entity_type, parent, bg_task_manager)

        self._app = sgtk.platform.current_bundle()
        
        self.__sg_data_retriever = shotgun_data.ShotgunDataRetriever(self, 
                                                                     bg_task_manager=bg_task_manager)        
        self.__sg_data_retriever.start()
        self.__sg_data_retriever.work_completed.connect(self.__on_worker_signal)
        self.__sg_data_retriever.work_failure.connect(self.__on_worker_failure)

    def set_overlay(self, overlay):
        """
        Specify a overlay object for progress reporting
        
        :param overlay: Overlay object
        :type  overlay: :class:`~tk-framework-qtwidgets:overlay_widget.ShotgunOverlayWidget`
        """
        self._overlay = overlay

    ############################################################################################
    # slots

    def __on_worker_failure(self, uid, msg):
        """
        Asynchronous callback - the worker thread errored.
        """
        uid = shotgun_model.sanitize_qt(uid) # qstring on pyqt, str on pyside
        msg = shotgun_model.sanitize_qt(msg)

        if uid == self._sg_query_id: 
            self._app.log_warning("History model query error: %s" % msg)
            full_msg = "Error retrieving data from Shotgun: %s" % msg        
            if self._overlay:
                self._overlay.show_error_message(full_msg)
        
    def __on_worker_signal(self, uid, request_type, data):
        """
        Signaled whenever the worker completes something.
        This method will dispatch the work to different methods
        depending on what async task has completed.
        """        
        uid = shotgun_model.sanitize_qt(uid) # qstring on pyqt, str on pyside
        data = shotgun_model.sanitize_qt(data)

        if self._sg_query_id == uid:
            # hide spinner
            if self._overlay:
                self._overlay.hide()        

            # process the data
            sg_records = data["sg"]
            
            if len(sg_records) != 1 and self._overlay:
                self._overlay.show_error_message("Publish could not be found!")
            
            sg_data = sg_records[0]

            # figure out which publish type we are after
            if self._sg_formatter.entity_type == "PublishedFile":
                publish_type_field = "published_file_type"
            else:
                publish_type_field = "tank_type"

            # when we filter out which other publishes are associated with this one,
            # to effectively get the "version history", we look for items
            # which have the same project, same entity assocation, same name, same type 
            # and the same task.
            filters = [ ["project", "is", sg_data["project"] ],
                        ["name", "is", sg_data["name"] ],
                        ["task", "is", sg_data["task"] ],
                        ["entity", "is", sg_data["entity"] ],
                        [publish_type_field, "is", sg_data[publish_type_field] ],
                      ]

            # the proxy model that is sorting this model will
            # sort based on id (pk), meaning that more recently 
            # commited transactions will appear later in the list.
            # This ensures that publishes with no version number defined
            # (yes, these exist) are also sorted correctly.
            hierarchy = ["created_at"]

            self._current_version = sg_data["version_number"]

            ShotgunModel._load_data(
                self,
                self._sg_formatter.entity_type,
                filters,
                hierarchy,
                self._sg_formatter.fields
            )

            self._refresh_data()

    ############################################################################################
    # public interface

    def load_data(self, sg_location):
        """
        Clears the model and sets it up for a particular entity.
        Loads any cached data that exists.
        
        :param sg_location: Location object representing the *associated*
               object for which items should be loaded. For this class, 
               the location should always represent a published file.
        """        
        self._sg_location = sg_location
        self._current_version = None
        self.__sg_data_retriever.clear()
        
        # figure out which publish type we are after
        if self._sg_formatter.entity_type == "PublishedFile":
            publish_type_field = "published_file_type"
        else:
            publish_type_field = "tank_type"
        
        filters = [["id", "is", sg_location.entity_id]]
        
        fields = ["name", 
                  "version_number",
                  "task", 
                  "entity",
                  "project",
                  publish_type_field]
        
        # get publish details async
        self._sg_query_id = self.__sg_data_retriever.execute_find(self._sg_formatter.entity_type, 
                                                                  filters, 
                                                                  fields)
        
    def is_highlighted(self, model_index):
        """
        Compute if a model index belonging to this model 
        should be highlighted.
        
        In the case of this model, the current version is highlighted
        """
        # see if the model tracks a concept of a current version.
        # this is used for version histories, when we want to highlight 
        # a particular item in a history
        sg_data = shotgun_model.get_sg_data(model_index)
        
        if sg_data.get("version_number") == self._current_version:
            return True
        else:
            return False
