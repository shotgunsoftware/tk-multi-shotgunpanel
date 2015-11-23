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

class SgEntityDetailsModel(ShotgunModel):
    """
    Model that represents the details data that is 
    displayed in the top section of the UI.
    
    Emits thumbnail_updated and data_updated signals whenever data 
    arrived from Shotgun.
    
    Data can then be queried via the get_sg_data() and get_pixmap() methods.
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
                              download_thumbs=True, 
                              bg_load_thumbs=True,
                              bg_task_manager=bg_task_manager)
        
        self._sg_location = None
        self._current_pixmap = None
        self.data_refreshed.connect(self._on_data_refreshed)

    def _on_data_refreshed(self):
        """
        helper method. dispatches the after-refresh signal
        so that a data_updated signal is consistenntly sent
        out both after the data has been updated and after a cache has been read in
        """
        self.data_updated.emit()

    def _populate_default_thumbnail(self, item):
        """
        Called whenever an item needs to get a default thumbnail attached to a node.
        When thumbnails are loaded, this will be called first, when an object is
        either created from scratch or when it has been loaded from a cache, then later
        on a call to _populate_thumbnail will follow where the subclassing implementation
        can populate the real image.
        """
        self._current_pixmap = self._sg_location.sg_formatter.default_pixmap
        self.thumbnail_updated.emit()

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
        
        if field not in self._sg_location.sg_formatter.thumbnail_fields: 
            # there may be other thumbnails being loaded in as part of the data flow
            # (in particular, created_by.HumanUser.image) - these ones we just want to 
            # ignore and not display.
            return
        
        sg_data = item.get_sg_data()
        self._current_pixmap = self._sg_location.sg_formatter.create_thumbnail(image, sg_data)
        self.thumbnail_updated.emit()

    ############################################################################################
    # public interface

    def load_data(self, sg_location):
        """
        Clears the model and sets it up for a particular entity.
        Loads any cached data that exists and requests an async update.
        
        The fields defined in the sg_location.sg_formatter.fields 
        property will be loaded.
        
        :param sg_location: Shotgun Location object of the object to load.
        """
        # set the current location to represent
        self._sg_location = sg_location
          
        fields = sg_location.sg_formatter.fields + sg_location.sg_formatter.thumbnail_fields

        hierarchy = ["id"]
        
        ShotgunModel._load_data(self, 
                                sg_location.entity_type, 
                                [["id", "is", sg_location.entity_id]], 
                                hierarchy,
                                fields)
        
        # signal to any views that data now may be available
        self.data_updated.emit()
        self._refresh_data()

    
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
        
