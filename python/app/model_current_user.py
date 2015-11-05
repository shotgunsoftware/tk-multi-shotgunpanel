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
from . import utils

# import the shotgun_model module from the shotgun utils framework
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
ShotgunModel = shotgun_model.ShotgunModel

class SgCurrentUserModel(ShotgunModel):
    """
    Model that caches data about the current user.
    
    Emits thumbnail_updated and data_updated signals whenever data 
    arrives from Shotgun.
    
    Data can then be queried via the get_sg_link(), get_sg_data() and 
    get_pixmap() methods
    """
    
    thumbnail_updated = QtCore.Signal()
    data_updated = QtCore.Signal()

    def __init__(self, parent, bg_task_manager):
        """
        Constructor
        
        :param parent: QT parent object
        """
        # init base class
        ShotgunModel.__init__(self, 
                              parent, 
                              bg_load_thumbs=True, 
                              bg_task_manager=bg_task_manager)
        self._app = sgtk.platform.current_bundle()
        self._current_pixmap = None
        self._current_user_sg_dict = None
        self.data_refreshed.connect(self._on_data_refreshed)
        
    def _on_data_refreshed(self):
        """
        Dispatch method that gets called whenever data has been refreshed in the cache
        """
        # broadcast out to listeners that we have new data
        self.data_updated.emit()

    def _populate_thumbnail_image(self, item, field, image, path):
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
        self._current_pixmap = utils.create_round_thumbnail(image)
        self.thumbnail_updated.emit()

    ############################################################################################
    # public interface
    
    def load(self):
        """
        Load data about the current user.
        The user will be picked up from the current context.
        """
        app = sgtk.platform.current_bundle()
        sg_user_data = sgtk.util.get_current_user(app.sgtk)
        
        if sg_user_data is None:
            self._app.log_warning("No current user found! Will continue "
                                  "without a current user.")
        
        else:
            self._current_user_sg_dict = {"type": sg_user_data["type"], 
                                          "id": sg_user_data["id"]}
            hierarchy = ["id"]
            fields = ["image", "login", "name", "department", "firstname", "surname"]
            ShotgunModel._load_data(self, 
                                    sg_user_data["type"],
                                    [["id", "is", sg_user_data["id"]]], 
                                    hierarchy,
                                    fields)
        
            # signal to any views that data now may be available
            self.data_updated.emit()
            self._refresh_data()
    
    def get_sg_link(self):
        """
        Returns the entity link for the current user
        This is always available and doesn't need to be cached
        
        :returns: shotgun link style dictionary with type and id keys
        """
        return self._current_user_sg_dict
    
    def get_sg_data(self):
        """
        Access current user shotgun data.
        
        :returns: The sg data dictionary for the associated item, 
                  None if not available.
        """
        if self.rowCount() == 0:
            data = None
        else:
            data = self.item(0).get_sg_data()
        
        return data
        
    def get_pixmap(self):
        """
        :returns: Current user thumbnail or default one if not yet loaded 
        """
        return self._current_pixmap
        
