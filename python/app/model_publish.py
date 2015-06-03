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

class SgPublishModel(ShotgunOverlayModel):

    """
    Model which sets a thumbnail to be a round user icon
    """

    def __init__(self, parent):
        """
        Model which represents the latest publishes for an entity
        """
        self._default_user_pixmap = QtGui.QPixmap(":/tk_multi_infopanel/rect_512x400.png")

        self._app = sgtk.platform.current_bundle()
        
        # figure out our current entity type
        self._publish_entity_type = sgtk.util.get_published_file_entity_type(self._app.sgtk)
        if self._publish_entity_type == "PublishedFile":
            self._publish_type_field = "published_file_type"
        else:
            self._publish_type_field = "tank_type"

        # should the model only show latest publishes?
        self._show_latest_only = False

        # init base class
        ShotgunOverlayModel.__init__(self,
                                     parent,
                                     overlay_widget=parent,
                                     download_thumbs=True,
                                     schema_generation=4)
        
    ############################################################################################
    # public interface

    def get_current_version(self):
        """
        Returns the current version
        """
        return None

    def load_data(self, filters, show_latest_only):
        """
        Clears the model and sets it up for a particular entity.
        Loads any cached data that exists.
        """
        
        fields = ["name", 
                  "version_number", 
                  "description", 
                  self._publish_type_field, 
                  "image",
                  "project",
                  "task",
                  "code", 
                  "created_by",
                  "published_file_type",
                  "created_at"]
        hierarchy = ["code"]
        
        self._show_latest_only = show_latest_only
        
        # note: we add the state of the self._show_latest_only flag to the seed 
        # in order to hint to the model caching system that datasets with and without
        # this flag set are totally different
        
        ShotgunOverlayModel._load_data(self, 
                                       self._publish_entity_type, 
                                       filters, 
                                       hierarchy, 
                                       fields, 
                                       [{"field_name":"created_at", "direction":"asc"}],
                                       seed="%s" % self._show_latest_only)
        self._refresh_data()


    def _populate_default_thumbnail(self, item):
        """
        Called whenever an item needs to get a default thumbnail attached to a node.
        When thumbnails are loaded, this will be called first, when an object is
        either created from scratch or when it has been loaded from a cache, then later
        on a call to _populate_thumbnail will follow where the subclassing implementation
        can populate the real image.
        """
        # set up publishes with a "thumbnail loading" icon
        item.setIcon(self._default_user_pixmap)

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
        
        if field != "image": 
            # there may be other thumbnails being loaded in as part of the data flow
            # (in particular, created_by.HumanUser.image) - these ones we just want to 
            # ignore and not display.
            return
        
        icon = utils.create_rectangular_512x400_thumbnail(path)
        item.setIcon(QtGui.QIcon(icon))




    def _before_data_processing(self, sg_data_list):
        """
        Called just after data has been retrieved from Shotgun but before any processing
        takes place. This makes it possible for deriving classes to perform summaries,
        calculations and other manipulations of the data before it is passed on to the model
        class.

        :param sg_data_list: list of shotgun dictionaries, as retunrned by the find() call.
        :returns: should return a list of shotgun dictionaries, on the same form as the input.
        """
        app = sgtk.platform.current_bundle()

        if not self._show_latest_only:
            # show everything
            return sg_data_list

        # filter the shotgun data so that we only return the latest publish for each file.

        # FIRST PASS!
        # get a dict with only the latest versions, grouped by type and task
        # rely on the fact that versions are returned in asc order from sg.
        # (see filter query above)
        #
        # for example, if there are these publishes:
        # name FOO, version 1, task ANIM, type XXX
        # name FOO, version 2, task ANIM, type XXX
        # name FOO, version 3, task ANIM, type XXX
        # name FOO, version 1, task ANIM, type YYY
        # name FOO, version 2, task ANIM, type YYY
        # name FOO, version 5, task LAY,  type YYY
        # name FOO, version 6, task LAY,  type YYY
        # name FOO, version 7, task LAY,  type YYY
        #
        # three items should show up:
        # - Foo v3 (type XXX)
        # - Foo v2 (type YYY, task ANIM)
        # - Foo v7 (type YYY, task LAY)
                
        unique_data = {}
        
        for sg_item in sg_data_list:
            
            # get the associated type
            type_id = None
            type_link = sg_item[self._publish_type_field]
            if type_link:
                type_id = type_link["id"]

            # also get the associated task
            task_id = None
            task_link = sg_item["task"]
            if task_link:
                task_id = task_link["id"]  

            # key publishes in dict by type and name
            unique_data[ (sg_item["name"], type_id, task_id) ] = sg_item            
        
        # now return this culled data set as our new set of shotgun data, now only
        # including the latest publishes
        return unique_data.values()





