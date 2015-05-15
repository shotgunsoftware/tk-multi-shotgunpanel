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

class SgCurrentEntityModel(ShotgunOverlayModel):

    thumbnail_updated = QtCore.Signal()
    data_updated = QtCore.Signal()


    def __init__(self, parent):
        """
        Model which represents the latest publishes for an entity
        """
        # init base class
        ShotgunOverlayModel.__init__(self,
                                     parent,
                                     overlay_widget=parent,
                                     download_thumbs=True,
                                     schema_generation=3)

        self._default_thumb_pixmap = QtGui.QPixmap(":/tk_multi_infopanel/loading_512x400.png")
        self._current_pixmap = self._default_thumb_pixmap
        self.data_refreshed.connect(self._on_data_refreshed)

    ############################################################################################
    # public interface


    def load_data(self, entity_type, entity_id, fields):
        """
        Clears the model and sets it up for a particular entity.
        Loads any cached data that exists.
        """        
        hierarchy = [fields[0]]
        loaded_cache = ShotgunOverlayModel._load_data(self, 
                                                      entity_type, 
                                                      [["id", "is", entity_id]], 
                                                      hierarchy, 
                                                      fields)
        # model data
        self.data_updated.emit()
        self._refresh_data()

    def _on_data_refreshed(self):
        self.data_updated.emit()

    def get_sg_data(self):
        
        if self.rowCount() == 0:
            data = None
        else:
            data = self.item(0).get_sg_data()
        
        return data
        
    def get_pixmap(self):
        return self._current_pixmap
        
    def _populate_default_thumbnail(self, item):
        """
        Called whenever an item needs to get a default thumbnail attached to a node.
        When thumbnails are loaded, this will be called first, when an object is
        either created from scratch or when it has been loaded from a cache, then later
        on a call to _populate_thumbnail will follow where the subclassing implementation
        can populate the real image.
        """
        # set up publishes with a "thumbnail loading" icon
        self._current_pixmap = self._default_thumb_pixmap
        self.thumbnail_updated.emit()

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
        
        self._current_pixmap = utils.create_overlayed_publish_thumbnail(path)
        self.thumbnail_updated.emit()
