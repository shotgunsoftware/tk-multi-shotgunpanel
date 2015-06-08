# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
import os
import sys
import threading
import datetime
from . import utils

class ShotgunFormatter(object):
    """
    
    """
    
    def __init__(self, entity_type):
        """
        Constructor
        """
        self._entity_type = entity_type
        self._round_default_icon = utils.create_circular_512x400_thumbnail(path)
        self._rect_default_icon = utils.create_rectangular_512x400_thumbnail(path)
    
    ####################################################################################################
    # properties
    
    @property
    def default_pixmap(self):
        """
        Returns the default pixmap associated with this location
        """
        return self._rect_default_icon
            
    @property
    def thumbnail_field(self):
        return "image"
    
    @property
    def entity_type(self):
        return self._entity_type
    
    @property
    def should_open_in_shotgun_web(self):
        if self._entity_type == "Playlist":
            return True
        else:
            return False
    
    @property
    def link_field(self):
        return "entity"

    @property
    def all_fields(self):
        """
        All fields listing
        """


    @property
    def fields(self): 
        """
        fields needed to render list or main details
        """
        fields = ["code", 
                  "project",
                  "created_by",
                  "description", 
                  "sg_status_list",
                  "project" 
                  "image"]
        return fields

    ####################################################################################################
    # methods

    def create_thumbnail(self, path):
        """
        Given a path, create a suitable thumbnail and return a pixmap
        """
        # pass in full sg data here?
        return utils.create_rectangular_512x400_thumbnail(path)


    def get_playback_url(self, sg_data):
        """
        returns a url to be used for playback
        """
        if self._entity_type != "Version":
            return None
        
        url = None
        if sg_data.get("sg_uploaded_movie"):
            # there is a web quicktime available!
            sg_url = sgtk.platform.current_bundle().shotgun.base_url
            url = "%s/page/screening_room?entity_type=%s&entity_id=%d" % (sg_url, sg_data["type"], sg_data["id"])                    
            
        return url

    def format_entity_details(self, sg_data):
        """
        Render details
        
        returns (header, body, footer)
        """
        name = sg_data.get("code") or "Unnamed"
        title = "%s %s" % (sg_data.get("type"), name)
        top_label.setText(title)
        bottom_label.setText(sg_data.get("description") or "No Description")
    
    def format_list_item_details(self, sg_data):
        """
        Render details
        
        returns (header, body) strings
        """
        created_unixtime = sg_data.get("created_at")
        created_datetime = datetime.datetime.fromtimestamp(created_unixtime)
        (human_str, exact_str) = utils.create_human_readable_timestamp(created_datetime)

        user_name = (sg_data.get("artist") or {}).get("name") or "Unknown User"        
        description = sg_data.get("description") or ""
        content = "By %s %s<br><i>%s</i>" % (user_name, human_str, description)

        title = "<b>%s</b>" % sg_data.get("code") or "Untitled Version"

        return (title, content)
    
