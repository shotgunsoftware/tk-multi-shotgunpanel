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


def create_shotgun_location(entity_type, entity_id):
    """
    factory method.
    """
    return ShotgunLocation(entity_type, entity_id)





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
        
    
    @property
    def thumbnail_field(self):
        return "image"
    
    @property
    def entity_type(self):
        return self._entity_type
    
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

    def get_family(self):
        """
        Returns the family that this item belongs to
        """
        return self.ENTITY_FAMILY

    def set_up_thumbnail(self, sg_data, version_label):
        
        version_label.set_playback_icon_active(False)
    
    def render_details(self, sg_data, top_label, middle_label, bottom_label):
        """
        Render details
        """
        name = sg_data.get("code") or "Unnamed"
        title = "%s %s" % (sg_data.get("type"), name)
        top_label.setText(title)
        bottom_label.setText(sg_data.get("description") or "No Description")
    

    
    
