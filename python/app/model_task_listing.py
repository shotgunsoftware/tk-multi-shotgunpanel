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

from .model_entity_listing import SgEntityListingModel

class SgTaskListingModel(SgEntityListingModel):
    """
    Model to list tasks
    """

    def __init__(self, entity_type, parent):
        """
        Model which represents the latest publishes for an entity
        """
        # init base class
        SgEntityListingModel.__init__(self, entity_type, parent)
        
#     ############################################################################################
#     # public interface
# 
#     def load_data(self, sg_location, show_latest_only):
#         """
#         Clears the model and sets it up for a particular entity.
#         Loads any cached data that exists.
#         """
#         # figure out our current entity type
#         
#         SgEntityListingModel.load_data(self, 
#                                        sg_location, 
#                                        additional_fields=["version", "task", self._publish_type_field])
# 
#     def _populate_default_thumbnail(self, item):
#         """
#         Called whenever an item needs to get a default thumbnail attached to a node.
#         When thumbnails are loaded, this will be called first, when an object is
#         either created from scratch or when it has been loaded from a cache, then later
#         on a call to _populate_thumbnail will follow where the subclassing implementation
#         can populate the real image.
#         """
#         if self._sg_location.entity_type == "HumanUser":
#             # when showing 
#         
#         # set up publishes with a "thumbnail loading" icon
#         item.setIcon(self._sg_formatter.default_pixmap)
# 
#     def _populate_thumbnail_image(self, item, field, image, path):
#         """
#         Called whenever a thumbnail for an item has arrived on disk. In the case of
#         an already cached thumbnail, this may be called very soon after data has been
#         loaded, in cases when the thumbs are downloaded from Shotgun, it may happen later.
# 
#         This method will be called only if the model has been instantiated with the
#         download_thumbs flag set to be true. It will be called for items which are
#         associated with shotgun entities (in a tree data layout, this is typically
#         leaf nodes).
# 
#         This method makes it possible to control how the thumbnail is applied and associated
#         with the item. The default implementation will simply set the thumbnail to be icon
#         of the item, but this can be altered by subclassing this method.
# 
#         Any thumbnails requested via the _request_thumbnail_download() method will also
#         resurface via this callback method.
# 
#         :param item: QStandardItem which is associated with the given thumbnail
#         :param field: The Shotgun field which the thumbnail is associated with.
#         :param path: A path on disk to the thumbnail. This is a file in jpeg format.
#         """        
#         if field != self._sg_formatter.thumbnail_field: 
#             # there may be other thumbnails being loaded in as part of the data flow
#             # (in particular, created_by.HumanUser.image) - these ones we just want to 
#             # ignore and not display.
#             return
#         
#         sg_data = item.get_sg_data()
#         icon = self._sg_formatter.create_thumbnail(image, sg_data)
#         item.setIcon(QtGui.QIcon(icon))
