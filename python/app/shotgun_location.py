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
    if entity_type == "Shot":
        return ShotgunShot(entity_type, entity_id)
    
    elif entity_type == "PublishedFile":
        return ShotgunPublish(entity_type, entity_id)
    
    elif entity_type == "Version":
        return ShotgunVersion(entity_type, entity_id)

    else:
        return ShotgunLocationGeneral(entity_type, entity_id)





class ShotgunLocation(object):
    """
    An item representing an item in the history stack
    """
    
    def __init__(self, entity_type, entity_id):
        """
        Constructor
        """
        self._entity_type = entity_type
        self._entity_id = entity_id
        
    @property
    def entity_type(self):
        return self._entity_type
    
    @property
    def entity_id(self):
        return self._entity_id
    
    @property
    def entity_dict(self):
        return {"type": self._entity_type, "id": self._entity_id}

    def get_fields(self):
        raise NotImplementedError

    def set_up_ui(self, dialog):
        raise NotImplementedError
    
    def render_details(self, sg_data, top_label, middle_label, bottom_label):
        raise NotImplementedError
    


class ShotgunLocationGeneral(ShotgunLocation):
    
    def __init__(self, entity_type, entity_id):
        ShotgunLocation.__init__(self, entity_type, entity_id)
        
    def get_fields(self):        
        fields = ["code", 
                  "created_by",
                  "description", 
                  "sg_status_list", 
                  "image"]
        return fields

    def set_up_ui(self, dialog):
        """
        render the UI
        """
        dialog.focus_entity(self)
    
    def render_details(self, sg_data, top_label, middle_label, bottom_label):
        """
        Render details
        """
        name = sg_data.get("code") or "Unnamed"
        title = "%s %s" % (sg_data.get("type"), name)
        top_label.setText(title)
        bottom_label.setText(sg_data.get("description") or "No Description")
    
    
class ShotgunShot(ShotgunLocationGeneral):
    
    def __init__(self, entity_type, entity_id):
        ShotgunLocationGeneral.__init__(self, entity_type, entity_id)
            
    def get_fields(self):        
        fields = ["sg_sequence"]
        fields += ShotgunLocationGeneral.get_fields(self)
        return fields
    
    def render_details(self, sg_data, top_label, middle_label, bottom_label):
        """
        Render details
        """
        ShotgunLocationGeneral.render_details(self, sg_data, top_label, middle_label, bottom_label)
                
        middle = ""            
        middle_label.setText(middle)
    
    
    
class ShotgunPublish(ShotgunLocation):
    
    def __init__(self, entity_type, entity_id):
        ShotgunLocation.__init__(self, entity_type, entity_id)
        
    def get_fields(self):
        fields = ["code", 
                  "version_number", 
                  "description", 
                  "published_file_type", 
                  "image",
                  "name", 
                  "created_by",
                  "created_at"]
        return fields

    def set_up_ui(self, dialog):
        """
        render the UI
        """
        dialog.focus_publish(self)
    
    def render_details(self, sg_data, top_label, middle_label, bottom_label):
        """
        Render details
        """
        name = sg_data.get("code") or "Unnamed"
        title = "Publish %s" % (name)
        top_label.setText(title)


        created_unixtime = sg_data.get("created_at")
        created_datetime = datetime.datetime.fromtimestamp(created_unixtime)
        (human_str, exact_str) = utils.create_human_readable_timestamp(created_datetime)

        user = sg_data.get("created_by")
        
        bottom_str = "Published by %s %s." % (utils.generate_link(user), human_str)
        bottom_str += "<br><br><i><b>Comments:</b> %s</i>" % (sg_data.get("description") or "No comments entered.")
        
        bottom_label.setText(bottom_str)
    
    


class ShotgunVersion(ShotgunLocation):
    
    def __init__(self, entity_type, entity_id):
        ShotgunLocation.__init__(self, entity_type, entity_id)
        
    def get_fields(self):
        fields = ["code", 
                  "sg_department", 
                  "description", 
                  "open_notes_count", 
                  "sg_status_list",
                  "image",
                  "artist",
                  "created_at", 
                  "created_by"]
        return fields

    def set_up_ui(self, dialog):
        """
        render the UI
        """
        dialog.focus_version(self)
    
    def render_details(self, sg_data, top_label, middle_label, bottom_label):
        """
        Render details
        """
        name = sg_data.get("code") or "Unnamed"
        title = "Version %s" % (name)
        top_label.setText(title)

        created_unixtime = sg_data.get("created_at")
        created_datetime = datetime.datetime.fromtimestamp(created_unixtime)
        (human_str, exact_str) = utils.create_human_readable_timestamp(created_datetime)

        user = sg_data.get("artist")
        if user is None:
            # fall back on created by
            user = sg_data.get("created_by")
        
        bottom_str = "Created by %s %s." % (utils.generate_link(user), human_str)
        bottom_str += "<br><br><i><b>Comments:</b> %s</i>" % (sg_data.get("description") or "No comments entered.")
        
        bottom_label.setText(bottom_str)
    









    
