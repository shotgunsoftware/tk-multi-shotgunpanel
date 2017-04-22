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

class SgLatestPublishListingModel(SgEntityListingModel):
    """
    Model which fetches publish objects with the option to collapse
    the list of returned data so that only the latest version of each
    publish is shown.
    """

    def __init__(self, entity_type, parent, bg_task_manager):
        """
        Constructor.
        
        :param entity_type: The entity type that should be loaded into this model.
                            Needs to be a PublishedFile or TankPublishedFile.
        :param parent: QT parent object
        """
        # should the model only show latest publishes?
        self._show_latest_only = False
        self._publish_type_field = None

        # init base class
        SgEntityListingModel.__init__(self, entity_type, parent, bg_task_manager)
        

    def load_data(self, sg_location, show_latest_only):
        """
        Clears the model and sets it up for a particular entity.
        
        :param sg_location: Location object representing the *associated*
               object for which items should be loaded. 
               
        :param show_latest_only: If true, the listing will be culled so that
               only latest items are shown.
        """
        # figure out our current entity type
        if self._sg_formatter.entity_type == "PublishedFile":
            self._publish_type_field = "published_file_type"
        else:
            self._publish_type_field = "tank_type"
        
        self._show_latest_only = show_latest_only
        
        SgEntityListingModel.load_data(
            self,
            sg_location,
            additional_fields=["version", "task", self._publish_type_field],
            sort_field="created_at"
        )



    def _before_data_processing(self, sg_data_list):
        """
        Called just after data has been retrieved from Shotgun but before any processing
        takes place. This makes it possible for deriving classes to perform summaries,
        calculations and other manipulations of the data before it is passed on to the model
        class.

        :param sg_data_list: list of shotgun dictionaries, as returned by the find() call.
        :returns: should return a list of shotgun dictionaries, on the same form as the input.
        """
        if not self._show_latest_only:
            # show everything
            new_sg_data_list = sg_data_list

        else:

            # filter the shotgun data so that we only return the latest publish for each file.
    
            # FIRST PASS!
            # get a dict with only the latest versions, grouped by type and task
            # rely on the fact that versions are returned in desc order from sg.
            # (this is defined in SgEntityListingModel)
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
            
            # the data is passed from sg in desc order, with the highest version
            # first.
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
    
                # get a unique key to track this publish group
                unique_key = (sg_item["name"], type_id, task_id)
    
                # add records only if a record doesn't already exist
                # the data arrives in desc order, so we know that
                # if a record already exists, it must have a higher 
                # version than the current one. So skip current one.
                if unique_key not in unique_data: 
                    unique_data[unique_key] = sg_item            
            
            new_sg_data_list = unique_data.values()
        
        # now return this culled data set as our new set of shotgun data, now only
        # including the latest publishes
        return SgEntityListingModel._before_data_processing(self, new_sg_data_list) 
                                       
        
        
