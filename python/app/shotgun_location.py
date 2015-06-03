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
    
    elif entity_type in ["HumanUser", "ClientUser", "ApiUser"]:
        return ShotgunUser(entity_type, entity_id)
    
    elif entity_type == "Task":
        return ShotgunTask(entity_type, entity_id)

    elif entity_type == "Asset":
        return ShotgunAsset(entity_type, entity_id)
    
    elif entity_type == "Project":
        return ShotgunProject(entity_type, entity_id)

    elif entity_type == "PublishedFile":
        return ShotgunPublish(entity_type, entity_id)
    
    elif entity_type == "Version":
        return ShotgunVersion(entity_type, entity_id)

    else:
        return ShotgunLocation(entity_type, entity_id)





class ShotgunLocation(object):
    """
    An item representing an item in the history stack
    """
    
    # define the various families of items that the location
    # supports. These corresponds to the different layouts
    # in the UI
    (PUBLISH_FAMILY, VERSION_FAMILY, ENTITY_FAMILY) = range(3)
    
    def __init__(self, entity_type, entity_id):
        """
        Constructor
        """
        self._entity_type = entity_type
        self._entity_id = entity_id
    
    @property
    def use_round_icon(self):
        return False
    
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
    

    
    
class ShotgunShot(ShotgunLocation):
    
    def __init__(self, entity_type, entity_id):
        ShotgunLocation.__init__(self, entity_type, entity_id)
            
    def get_fields(self):        
        fields = ["sg_sequence", "sg_cut_in", "sg_cut_out", "sg_cut_duration"]
        fields += ShotgunLocation.get_fields(self)
        return fields
    
    def render_details(self, sg_data, top_label, middle_label, bottom_label):
        """
        Render details
        """
        ShotgunLocation.render_details(self, sg_data, top_label, middle_label, bottom_label)
                
        middle = "Project: %s" % utils.generate_link(sg_data["project"])
        middle += "<br>Sequence: %s" % utils.generate_link(sg_data["sg_sequence"])
        middle += "<br>Status: %s" % sg_data["sg_status_list"] 
        middle += "<br>Cut in: %s" % (sg_data.get("sg_cut_in") or "Not set")
        middle += "<br>Cut out: %s" % (sg_data.get("sg_cut_out") or "Not set")
        middle += "<br>Cut duration: %s" % (sg_data.get("sg_cut_duration") or "Not set")  
        middle_label.setText(middle)
    

class ShotgunAsset(ShotgunLocation):
    
    def __init__(self, entity_type, entity_id):
        ShotgunLocation.__init__(self, entity_type, entity_id)
            
    def get_fields(self):        
        fields = ["sg_asset_type"]
        fields += ShotgunLocation.get_fields(self)
        return fields
    
    def render_details(self, sg_data, top_label, middle_label, bottom_label):
        """
        Render details
        """
        ShotgunLocation.render_details(self, sg_data, top_label, middle_label, bottom_label)
                
        middle = "Project: %s" % utils.generate_link(sg_data["project"])
        middle += "<br>Asset Type: %s" % sg_data["sg_asset_type"]
        middle += "<br>Status: %s" % sg_data["sg_status_list"] 
        middle_label.setText(middle)



    
    
class ShotgunPublish(ShotgunLocation):
    
    def __init__(self, entity_type, entity_id):
        ShotgunLocation.__init__(self, entity_type, entity_id)
        
    def get_fields(self):
        fields = ["code", 
                  "project",
                  "version_number", 
                  "description", 
                  "published_file_type", 
                  "image",
                  "entity",
                  "task",
                  "name", 
                  "version",
                  "created_by",
                  "created_at"]
        return fields

    def get_family(self):
        """
        Returns the family that this item belongs to
        """
        return self.PUBLISH_FAMILY

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
    
        middle = "Project: %s" % utils.generate_link(sg_data["project"])
        middle += "<br>Associated with: %s" % utils.generate_link(sg_data["entity"])
        middle += "<br>Task: %s" % utils.generate_link(sg_data["task"])
        middle += "<br>Reviewed in: %s" % utils.generate_link(sg_data["version"])
        middle += "<br>Version Number: %s" % (sg_data.get("version_number") or "Not set")
        middle += "<br>File Type: %s" % ((sg_data.get("published_file_type") or {}).get("name") or "Not set")
        
 
         
        middle_label.setText(middle)
    
    


class ShotgunVersion(ShotgunLocation):
    
    def __init__(self, entity_type, entity_id):
        ShotgunLocation.__init__(self, entity_type, entity_id)
        
    def get_fields(self):
        fields = ["code", 
                  "project",
                  "sg_department", 
                  "description", 
                  "open_notes_count",
                  "playlists", 
                  "sg_uploaded_movie",
                  "sg_uploaded_movie",
                  "sg_path_to_frames",
                  "entity",
                  "frame_range",
                  "sg_task",
                  "sg_status_list",
                  "image",
                  "artist",
                  "created_at", 
                  "created_by"]
        return fields
    
    def get_family(self):
        """
        Returns the family that this item belongs to
        """
        return self.VERSION_FAMILY    

    def set_up_thumbnail(self, sg_data, version_label):
        
        if sg_data.get("sg_uploaded_movie"):
            # there is a web quicktime available!
            version_label.set_playback_icon_active(True)
            sg_url = sgtk.platform.current_bundle().shotgun.base_url
            url = "%s/page/screening_room?entity_type=%s&entity_id=%d" % (sg_url, sg_data["type"], sg_data["id"])                    
            version_label.set_plackback_url(url)
        else:
            version_label.set_playback_icon_active(False)
        
    
    
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
    
        middle = "Project: %s" % utils.generate_link(sg_data["project"])
        middle += "<br>Status: %s" % sg_data.get("sg_status_list")
        middle += "<br>Frame Range: %s" % (sg_data.get("frame_range") or "Not set")
        middle += "<br>Associated with: %s" % utils.generate_link(sg_data["entity"])
        middle += "<br>Department: %s" % (sg_data.get("sg_department") or "Not set")
        middle += "<br>Task: %s" % utils.generate_link(sg_data["sg_task"])
        playlist_urls = [ utils.generate_link(x) for x in sg_data["playlists"]]
        middle += "<br>In playlists: %s" % ", ".join(playlist_urls)        
 
         
        middle_label.setText(middle)




class ShotgunUser(ShotgunLocation):
    
    def __init__(self, entity_type, entity_id):
        ShotgunLocation.__init__(self, entity_type, entity_id)
        
    @property
    def use_round_icon(self):
        return True
        
    def get_fields(self):
        fields = ["name",
                  "email", 
                  "department", 
                  "image"]
        return fields

    def render_details(self, sg_data, top_label, middle_label, bottom_label):
        """
        Render details
        """
        name = sg_data.get("name") or "Unnamed"
        title = "User %s" % (name)
        top_label.setText(title)

        middle = "Name: %s" % (sg_data.get("name") or "No name set")
        middle += "<br>Email: %s" % (sg_data.get("email") or "No email set")
        middle += "<br>Department: %s" % (sg_data.get("department") or "No department set")
         
        middle_label.setText(middle)
        
    

class ShotgunProject(ShotgunLocation):
    
    def __init__(self, entity_type, entity_id):
        ShotgunLocation.__init__(self, entity_type, entity_id)
        
    def get_fields(self):
        fields = ["name",
                  "sg_description",
                  "sg_type",
                  "start_date",
                  "end_date",
                  "sg_status",
                  "image"]
        return fields

    def render_details(self, sg_data, top_label, middle_label, bottom_label):
        """
        Render details
        """
        name = sg_data.get("name") or "Unnamed"
        title = "Project %s" % (name)
        top_label.setText(title)

        bottom_label.setText(sg_data.get("sg_description") or "No Description")

        middle = "Name: %s" % (sg_data.get("name") or "No name set")
        middle += "<br>Start Date: %s" % (sg_data.get("start_date") or "No date set")
        middle += "<br>End Date: %s" % (sg_data.get("end_date") or "No date set")
        middle += "<br>Status: %s" % (sg_data.get("sg_status") or "No status set")
         
        middle_label.setText(middle)
        
    

class ShotgunTask(ShotgunLocation):
    
    def __init__(self, entity_type, entity_id):
        ShotgunLocation.__init__(self, entity_type, entity_id)
        
    @property
    def use_round_icon(self):
        return True
        
    def get_fields(self):
        fields = ["task_assignees",
                  "project",
                  "start_date",
                  "due_date",
                  "duration",
                  "step", 
                  "content", 
                  "entity"]
        return fields

    def render_details(self, sg_data, top_label, middle_label, bottom_label):
        """
        Render details
        """
        name = sg_data.get("content") or "Unnamed"
        title = "Task %s" % (name)
        top_label.setText(title)

        middle = "Project: %s" % utils.generate_link(sg_data["project"])
        middle += "<br>Status: %s" % sg_data.get("sg_status_list")
        middle += "<br>Start Date: %s" % (sg_data.get("start_date") or "Not set")
        middle += "<br>Due Date: %s" % (sg_data.get("due_date") or "Not set")
        middle += "<br>Associated with: %s" % utils.generate_link(sg_data["entity"])
        middle += "<br>Pipeline Step: %s" % ((sg_data.get("step") or {}).get("name") or "Not set")
        
        assignee_urls = [ utils.generate_link(x) for x in sg_data["task_assignees"]]
        middle += "<br>Assigned to: %s" % ", ".join(assignee_urls)        
         
        middle_label.setText(middle)




    
