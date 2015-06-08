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
ShotgunModel = shotgun_model.ShotgunModel

class SgCurrentUserModel(ShotgunModel):
    """
    Model that represents the details data that is 
    displayed in the main section of the UI.
    """
    thumbnail_updated = QtCore.Signal()
    data_updated = QtCore.Signal()

    def __init__(self, parent):
        """
        Model which represents the latest publishes for an entity
        """
        # init base class
        ShotgunModel.__init__(self, parent)
        self._current_pixmap = None
        self.data_refreshed.connect(self._on_data_refreshed)
        
    def load(self):
        
        app = sgtk.platform.current_bundle()
        sg_user_data = sgtk.util.get_current_user(app.sgtk)
        hierarchy = ["id"]
        fields = ["image", "login", "name", "department"]
        ShotgunModel._load_data(self, 
                                sg_user_data["type"],
                                [["id", "is", sg_user_data["id"]]], 
                                hierarchy,
                                fields)
        
        # signal to any views that data now may be available
        self.data_updated.emit()
        self._refresh_data()
        

    def _on_data_refreshed(self):
        """
        helper method. dispatches the after-refresh signal
        so that a data_updated signal is consistenntly sent
        out both after the data has been updated and after a cache has been read in
        """
        self.data_updated.emit()

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
            
        self._current_pixmap = utils.create_round_thumbnail(path)
        self.thumbnail_updated.emit()

    ############################################################################################
    # public interface


    def get_sg_data(self):
        """
        Returns the sg data dictionary for the associated item
        None if not available.
        """
        if self.rowCount() == 0:
            data = None
        else:
            data = self.item(0).get_sg_data()
        
        return data
        
    def get_pixmap(self):
        """
        Returns the thumbnail currently associated with the item.
        If no pixmap has been loaded for the item yet, a default icon is returned.
        """
        return self._current_pixmap
        
