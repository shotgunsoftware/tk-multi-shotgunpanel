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

class SgPublishDependencyUpstreamListingModel(SgEntityListingModel):
    """
    Model which is like the entity listing model
    but taylored for publishes. Also handles a mode
    where only the latest publishes are shown and the
    rest are culled out.
    """
    
    def __init__(self, entity_type, parent):
        """
        Model which represents the latest publishes for an entity
        """
        # init base class
        SgEntityListingModel.__init__(self, entity_type, parent)
        

    def _get_filters(self):
        """
        Return the filter to be used for the current query
        """
        return [["upstream_published_files", "in", [self._sg_location.entity_dict]]]
        

