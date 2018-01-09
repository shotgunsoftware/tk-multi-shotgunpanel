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

from .model_entity_listing import SgEntityListingModel

class SgVersionModel(SgEntityListingModel):
    """
    Special model for versions so that we can control
    how to display items with different review status.
    """
    def __init__(self, entity_type, parent, bg_task_manager):
        """
        Constructor.
        
        :param entity_type: The entity type that should be loaded into this model.
                            Needs to be a PublishedFile or TankPublishedFile.
        :param parent: QT parent object
        """
        self._show_pending_only = False
        
        # init base class
        SgEntityListingModel.__init__(self, entity_type, parent, bg_task_manager)

    def _get_filters(self):
        """
        Return the filter to be used for the current query
        """
        # get base class filters
        filters = SgEntityListingModel._get_filters(self)
        
        if self._show_pending_only:
            # limit based on status
            filters.append(["sg_status_list", "is", "rev"])
        
        return filters
    
    ############################################################################################
    # public interface

    def load_data(self, sg_location, show_pending_only):
        """
        Clears the model and sets it up for a particular entity.
        
        :param sg_location: Location object representing the *associated*
               object for which items should be loaded. 
               
        :param show_pending_only: If true, the listing will be culled so that
               only items pending review are shown
        """
        # figure out our current entity type
        self._show_pending_only = show_pending_only
        
        # make sure that we include the status regardless of how the
        # ui is configured - this is so we can do a status comparison
        # later in the _get_filters method.
        SgEntityListingModel.load_data(
            self,
            sg_location,
            additional_fields=["sg_status_list"],
            sort_field="id"
        )

