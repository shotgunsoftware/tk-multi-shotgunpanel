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



class ShotgunLocation(object):
    """
    An item representing an item in the history stack
    """
    
    # define the various families of items that the location
    # supports. These corresponds to the different layouts
    # in the UI
    (PUBLISH_FAMILY, VERSION_FAMILY, ENTITY_FAMILY, NOTE_FAMILY) = range(4)
    
    def __init__(self, entity_type, entity_id):
        """
        Constructor
        """
        self._entity_type = entity_type
        self._entity_id = entity_id
    
        self._round_default_icon = utils.create_circular_512x400_thumbnail(path)
        self._rect_default_icon = utils.create_rectangular_512x400_thumbnail(path)
    
    def get_default_pixmap(self):
        """
        Returns the default pixmap associated with this location
        """
        return self._rect_default_icon
    
    def create_thumbnail(self, path):
        """
        Given a path, create a suitable thumbnail and return a pixmap
        """
        return utils.create_rectangular_512x400_thumbnail(path)
    
    def get_playback_url(self, sg_data):
        """
        returns a url to be used for playback
        """
        url = None
        if sg_data.get("sg_uploaded_movie"):
            # there is a web quicktime available!
            sg_url = sgtk.platform.current_bundle().shotgun.base_url
            url = "%s/page/screening_room?entity_type=%s&entity_id=%d" % (sg_url, sg_data["type"], sg_data["id"])                    
            
        return url
        
    def get_external_url(self):
        """
        returns the sg url for this entity
        """
        sg_url = sgtk.platform.current_bundle().shotgun.base_url
        
        if self._entity_type == "Playlist":
            proj_id = self._app.context.project["id"]
            url = "%s/page/media_center?project_id=%d&entity_type=%s&entity_id=%d" % (sg_url, 
                                                                                      proj_id,
                                                                                      self._entity_type, 
                                                                                      self._entity_id)
        
        else:
            url = "%s/detail/%s/%s" % (self._entity_type, self._entity_id)
    
        return url
    
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
    def entity_id(self):
        return self._entity_id
    
    @property
    def entity_dict(self):
        return {"type": self._entity_type, "id": self._entity_id}

    @property
    def link_field(self):
        return "entity"

    @property
    def sg_fields(self): 
        """
        todo: read from hook
        """
               
        fields = ["code", 
                  "project",
                  "created_by",
                  "description", 
                  "sg_status_list",
                  "project" 
                  "image"]
        return fields

    @property
    def family(self):
        """
        Returns the family that this item belongs to
        """
        return self.ENTITY_FAMILY

    def set_up_thumbnail(self, sg_data, version_label):
        
        version_label.set_playback_icon_active(False)
    
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
    
