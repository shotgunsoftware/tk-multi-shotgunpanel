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
from .shotgun_formatter import ShotgunTypeFormatter

# import the shotgun_model module from the shotgun utils framework
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
ShotgunModel = shotgun_model.ShotgunModel

class SgEntityListingModel(ShotgunModel):
    """
    Model used to display long listings of data in the tabs.
    
    Each model represents for example all publishes, versions notes etc
    that are associated with a particular object.
    
    The associated object is defined in the shotgun location.
    
    The returned data in this model is capped so that it will at
    the most contain SG_RECORD_LIMIT items.
    """
    
    # maximum number of items to show in the listings
    SG_RECORD_LIMIT = 50
    
    def __init__(self, entity_type, parent, bg_task_manager):
        """
        Constructor.
        
        :param entity_type: The entity type that should be loaded into this model.
        :param parent: QT parent object
        """
        self._sg_location = None
        self._sg_formatter = ShotgunTypeFormatter(entity_type)
        
        # init base class
        ShotgunModel.__init__(self,
                              parent,
                              download_thumbs=True,
                              bg_load_thumbs=True,
                              bg_task_manager=bg_task_manager)

    ############################################################################################
    # public interface

    def get_formatter(self):
        """
        Returns the shotgun location associated with this model.
        This formatter object describes the properties of the items
        that are being displayed by this model.
        """
        return self._sg_formatter

    def is_highlighted(self, model_index):
        """
        Compute if a model index belonging to this model 
        should be highlighted.
        
        This can be subclassed by models that have a special
        concept which defines highlighting.
        """
        return False

    def load_data(self, sg_location, additional_fields=None, sort_field=None):
        """
        Clears the model and sets it up for a particular entity.
        Loads any cached data that exists and schedules an async refresh.
        
        :param sg_location: Location object representing the *associated*
               object for which items should be loaded. NOTE! If the model is
               configured to display tasks, this sg_location could for example
               point to a Shot for which we want to display tasks.
        :param additional_fields: Additional fields to load apart from those 
               defined in the sg formatter object associated with the entity 
               type.
        :param sort_field: Field to use to sort the data. The data will be 
               sorted in descending order (this happens in a proxy model 
               outside the model itself, so not strictly part of this class, 
               but rather defined outside in the main dialog). The sort field
               is the main 'text' field in the model that is set.
        """
        self._sg_location = sg_location
        
        # if a sort field has not been specified, default to 
        # update date (unix time), in descending order
        sort_field = sort_field or "updated_at"
        
        fields = self._sg_formatter.fields
        if additional_fields:
            fields += additional_fields
            
        hierarchy = [sort_field]

        # This is wrapped here to account for the situation where we can't
        # query for the My Tasks tab if we don't have a Shotgun user. This
        # is the case when a script key is used for auth and we can't 
        # determine a Shotgun human user by other means.
        try:
            filters = self._get_filters()
        except sgtk.TankError as exc:
            self.data_refresh_fail.emit(exc.message)
            return

        ShotgunModel._load_data(self, 
                                self._sg_formatter.entity_type, 
                                filters, 
                                hierarchy, 
                                fields, 
                                [{"field_name": sort_field, 
                                  "direction": "desc"}],
                                limit=self.SG_RECORD_LIMIT)
        self._refresh_data()

    ############################################################################################
    # protected methods
    
    def _get_filters(self):
        """
        Return the filter to be used for the current query
        """
        return self._sg_formatter.get_link_filters(self._sg_location)

    def _populate_default_thumbnail(self, item):
        """
        Called whenever an item needs to get a default thumbnail attached to a node.
        When thumbnails are loaded, this will be called first, when an object is
        either created from scratch or when it has been loaded from a cache, then later
        on a call to _populate_thumbnail will follow where the subclassing implementation
        can populate the real image.
        """
        # set up publishes with a "thumbnail loading" icon
        item.setIcon(self._sg_formatter.default_pixmap)

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
        if field not in self._sg_formatter.thumbnail_fields: 
            # there may be other thumbnails being loaded in as part of the data flow
            # (in particular, created_by.HumanUser.image) - these ones we just want to 
            # ignore and not display.
            return
        
        sg_data = item.get_sg_data()
        icon = self._sg_formatter.create_thumbnail(image, sg_data)
        item.setIcon(QtGui.QIcon(icon))
