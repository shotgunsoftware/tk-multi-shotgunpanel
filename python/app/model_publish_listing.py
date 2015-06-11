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

class SgLatestPublishListingModel(SgEntityListingModel):
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
        # should the model only show latest publishes?
        self._show_latest_only = False
        self._publish_type_field = None

        # init base class
        SgEntityListingModel.__init__(self, entity_type, parent)
        
    ############################################################################################
    # public interface

    def load_data(self, sg_location, show_latest_only):
        """
        Clears the model and sets it up for a particular entity.
        Loads any cached data that exists.
        """
        # figure out our current entity type
        if self._sg_formatter.entity_type == "PublishedFile":
            self._publish_type_field = "published_file_type"
        else:
            self._publish_type_field = "tank_type"
        
        self._show_latest_only = show_latest_only
        
        SgEntityListingModel.load_data(self, 
                                       sg_location, 
                                       additional_fields=["version", "task", self._publish_type_field])



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
            new_sg_data_list = sg_data_list

        else:

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
            
            new_sg_data_list = unique_data.values()
        
        # now return this culled data set as our new set of shotgun data, now only
        # including the latest publishes
        return SgEntityListingModel._before_data_processing(self, new_sg_data_list) 
                                       
        
        
