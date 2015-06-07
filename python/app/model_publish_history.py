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

class SgPublishHistoryModel(ShotgunOverlayModel):
    """
    Model that shows the version history for a publish.
    
    The data fetching pass in this model has a two-pass 
    setup: First, the list of publishes that are part of the 
    history for a given publish are fetched. Then, in a second 
    pass
    """

    def __init__(self, parent):
        """
        constructor
        """
        
        # current publish we have loaded
        self._sg_location = None
        
        # the version number for the current publish
        self._current_version = None
        
        self._sg_query_id = None
        
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

        self._app.log_warning("History model query error: %s" % msg)
        
        full_msg = "Error retrieving data from Shotgun: %s" % msg        
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
            # process the data
            sg_records = data["sg"]
            
            if len(sg_records) != 1:
                self._show_overlay_error_message("Publish could not be found!")
            
            sg_data = sg_records[0]

            # figure out which publish type we are after
            if sg_location.entity_type == "PublishedFile":
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


            hierarchy = ["name"]

            self._current_version = sg_data["version_number"]

            ShotgunOverlayModel._load_data(self, 
                                           sg_location.entity_type, 
                                           self._sg_location.sg_fields, 
                                           hierarchy, 
                                           fields, 
                                           [{"field_name":"created_at", "direction":"desc"}])
            self._refresh_data()



    ############################################################################################
    # public interface

    def load_data(self, sg_location):
        """
        Clears the model and sets it up for a particular entity.
        Loads any cached data that exists.
        """        
        self._sg_location = sg_location
        self._current_version = None
        self.__sg_data_retriever.clear()
        
        # figure out which publish type we are after
        if sg_location.entity_type == "PublishedFile":
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
        
        hierarchy = ["code"]
        
        # start spinning
        self._show_overlay_spinner()
        
        # get publish details async
        self._sg_query_id = self.__sg_data_retriever.execute_find(sg_location.entity_type, filters, fields)
        
    def _populate_default_thumbnail(self, item):
        """
        Called whenever an item needs to get a default thumbnail attached to a node.
        When thumbnails are loaded, this will be called first, when an object is
        either created from scratch or when it has been loaded from a cache, then later
        on a call to _populate_thumbnail will follow where the subclassing implementation
        can populate the real image.
        """
        # set up publishes with a "thumbnail loading" icon
        item.setIcon(self._sg_location.get_default_pixmap())

    def _populate_thumbnail(self, item, field, path):
        """
        Called whenever a thumbnail for an item has arrived on disk. In the case of
        an already cached thumbnail, this may be called very soon after data has been
        loaded, in cases when the thumbs are downloaded from Shotgun, it may happen later.

        This method will be called only if the model has been instantiated with the
        download_thumbs flag set to be true. It will be called for items which are
        associated with shotgun entities (in a tree data layout, this is typically
        leaf nodes).

        This method makes it possible to control how the thumbnail is applied and associated
        with the item. The default implementation will simply set the thumbnail to be icon
        of the item, but this can be altered by subclassing this method.

        Any thumbnails requested via the _request_thumbnail_download() method will also
        resurface via this callback method.

        :param item: QStandardItem which is associated with the given thumbnail
        :param field: The Shotgun field which the thumbnail is associated with.
        :param path: A path on disk to the thumbnail. This is a file in jpeg format.
        """
        
        if field != self._sg_location.thumbnail_field: 
            # there may be other thumbnails being loaded in as part of the data flow
            # (in particular, created_by.HumanUser.image) - these ones we just want to 
            # ignore and not display.
            return
        
        icon = self._sg_location.create_thumbnail(path)
        item.setIcon(QtGui.QIcon(icon))

