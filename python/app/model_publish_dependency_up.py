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

class SgPublishDependencyUpstreamListingModel(SgEntityListingModel):
    """
    Model which is like the entity listing model
    but tailored for displaying upstream dependencies for a given publish
    """
    
    # note: no constructor implemented - use base class version
    
    def load_data(self, sg_location):
        """
        Clears the model and sets it up for a particular entity.
        Loads any cached data that exists and schedules an async refresh.
        
        :param sg_location: Location object representing the *associated*
               object for which items should be loaded. NOTE! If the model is
               configured to display tasks, this sg_location could for example
               point to a Shot for which we want to display tasks.
        """        
        # for publishes, sort them by id (e.g. creation date) rather than
        # by update date.
        SgEntityListingModel.load_data(self, sg_location, sort_field="id")

    def _get_filters(self):
        """
        Return the filter to be used for the current query
        """
        return [["upstream_published_files", "in", [self._sg_location.entity_dict]]]
        

