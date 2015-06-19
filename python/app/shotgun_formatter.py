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
from sgtk import TankError
from sgtk.platform.qt import QtCore, QtGui
import os
import re
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
        self._round_default_icon = QtGui.QPixmap(":/tk_multi_infopanel/round_512x400.png")
        self._rect_default_icon = QtGui.QPixmap(":/tk_multi_infopanel/rect_512x400.png")
        
        self._app = sgtk.platform.current_bundle()
        
        # read in the hook data into a dict
        self._hook_data = {}
        
        self._hook_data["get_thumbnail_settings"] = self._app.execute_hook_method("shotgun_fields_hook", 
                                                                                  "get_thumbnail_settings", 
                                                                                  entity_type=entity_type)

        self._hook_data["get_list_item_definition"] = self._app.execute_hook_method("shotgun_fields_hook", 
                                                                                  "get_list_item_definition", 
                                                                                  entity_type=entity_type)
        
        self._hook_data["get_all_fields"] = self._app.execute_hook_method("shotgun_fields_hook", 
                                                                          "get_all_fields", 
                                                                          entity_type=entity_type)
        
        self._hook_data["get_tab_visibility"] = self._app.execute_hook_method("shotgun_fields_hook", 
                                                                              "get_tab_visibility", 
                                                                              entity_type=entity_type)
        
        self._hook_data["get_main_view_definition"] = self._app.execute_hook_method("shotgun_fields_hook", 
                                                                                    "get_main_view_definition", 
                                                                                    entity_type=entity_type)        
        
        # extract a list of fields given all the different {tokens} defined
        fields = []
        fields += self._resolve_sg_fields( self._get_hook_value("get_list_item_definition", "top_left") )
        fields += self._resolve_sg_fields( self._get_hook_value("get_list_item_definition", "top_right") )
        fields += self._resolve_sg_fields( self._get_hook_value("get_list_item_definition", "body") )
        fields += self._resolve_sg_fields( self._get_hook_value("get_main_view_definition", "title") )
        fields += self._resolve_sg_fields( self._get_hook_value("get_main_view_definition", "body") )
        fields += self._resolve_sg_fields( self._get_hook_value("get_main_view_definition", "footer") )
        
        # also include the thumbnail field so that it gets retrieved as part of the general 
        # query payload
        fields.append(self.thumbnail_field)
        
        
        
        # include the special quicktime field for versions
        if entity_type == "Version":
            fields.append("sg_uploaded_movie")
        if entity_type == "Note":
            fields.append("read_by_current_user")
        
        self._token_fields = set(fields)
        
    def __repr__(self):
        return "<Shotgun '%s' formatter>" % self._entity_type
        
    def _resolve_sg_fields(self, token_str):
        """
        Convenience method. Returns the sg fields for all tokens.
        """
        return [sg_field for (_, sg_field, _) in self._resolve_tokens(token_str)]
        
    def _resolve_tokens(self, token_str):
        """
        given a string with {tokens} or {deep.linktokens} return a list
        of tokens.
        
        retrurns: a list of tuples with (full_token, sg_field, directive)
        """    
    
        try:
            # find all field names ["xx", "yy", "zz.xx"] from "{xx}_{yy}_{zz.xx}"
            raw_tokens = set(re.findall('{([^}^{]*)}', token_str))
        except Exception, error:
            raise TankError("Could not parse '%s' - Error: %s" % (token_str, error) )
    
        fields = []
        for raw_token in raw_tokens:
    
            if "::" in raw_token:
                # we have a special formatting directive
                # e.g. created_at::ago
                (sg_field, directive) = raw_token.split("::")
            else:
                sg_field = raw_token
                directive = None
        
            fields.append( (raw_token, sg_field, directive) )
    
        return fields
    
    def _get_hook_value(self, method_name, hook_key):
        """
        Validate that value is correct and return it
        """
        
        if method_name not in self._hook_data:
            raise TankError("Unknown shotgun_fields hook method %s" % method_name)
        
        data = self._hook_data[method_name]

        if hook_key not in data:
            raise TankError("Hook shotgun_fields.%s does not return "
                            "required dictionary key '%s'!" % (method_name, hook_key))
        
        return data[hook_key]
    
    def _sg_field_to_str(self, sg_type, sg_field, value, directive=None):
        """
        Convert to string
        """         
        str_val = ""
        
        if value is None:
            return "No value set"        
        
        elif isinstance(value, dict) and set(["type", "id", "name"]) == set(value.keys()):
            # entity link
            
            if directive == "showtype":
                # links are displayed as "Shot ABC123"
                
                # get the nice name from our schema
                # this is so that it says "Level" instead of "CustomEntity013"
                entity_info = self._app.metaschema.get_type_info(value["type"])
                if entity_info:
                    entity_type_display_name = entity_info["name"]["value"]
                else:
                    entity_type_display_name = value["type"]
                
                link_name = "%s %s" % (entity_type_display_name, value["name"])
            else:
                # links are just "ABC123"
                link_name = value["name"]
            
            if not self._generates_links(value["type"]) or directive == "nolink":
                str_val = link_name
            else:
                str_val = "<a href='%s:%s' style='text-decoration: none; color: #2C93E2'>%s</a>" % (value["type"], 
                                                                                             value["id"], 
                                                                                             link_name)
        
        elif isinstance(value, list):
            # list of items
            link_urls = []
            for list_item in value:
                link_urls.append( self._sg_field_to_str(sg_type, sg_field, list_item, directive))
            str_val = ", ".join(link_urls)
            
        elif sg_field in ["created_at", "updated_at"]:
            created_datetime = datetime.datetime.fromtimestamp(value)
            (human_str, exact_str) = utils.create_human_readable_timestamp(created_datetime) 

            if directive == "ago":
                str_val = human_str
            else:
                str_val = exact_str
            
            
        else:
            str_val = str(value)  
            
        return str_val
    
    def _generates_links(self, entity_type):
        """
        Returns true if the given entity type
        should be hyperlinked to, false if not
        """
        if entity_type in ["Step", "TankType", "PublishedFileType"]:
            return False
        else:
            return True
        
    
    ####################################################################################################
    # properties
    
    @property
    def default_pixmap(self):
        """
        Returns the default pixmap associated with this location
        """
        thumb_style = self._get_hook_value("get_thumbnail_settings", "style")
        
        if thumb_style == "rect":
            return self._rect_default_icon
        elif thumb_style == "round":
            return self._round_default_icon
        else:
            raise TankError("Unknown thumbnail style defined in hook!")
            
    @property
    def thumbnail_field(self):
        """
        Returns the field name to use when look for thumbnails
        """
        return self._get_hook_value("get_thumbnail_settings", "sg_field")
    
    @property
    def entity_type(self):
        return self._entity_type
    
    @property
    def should_open_in_shotgun_web(self):
        
        # TODO - we might want to expose this in the hook at some point
        if self._entity_type == "Playlist":
            return True
        else:
            return False
    
    @property
    def all_fields(self):
        """
        All fields listing
        """
        return self._hook_data["get_all_fields"]

    @property
    def fields(self): 
        """
        fields needed to render list or main details
        """
        return list(self._token_fields)

    @property
    def show_notes_tab(self):
        """
        Should the note tab be shown for this
        """
        return self._get_hook_value("get_tab_visibility", "notes_tab")

    @property
    def show_publishes_tab(self):
        """
        Should the publishes tab be shown for this
        """
        return self._get_hook_value("get_tab_visibility", "publishes_tab")

    @property
    def show_versions_tab(self):
        """
        Should the publishes tab be shown for this
        """
        return self._get_hook_value("get_tab_visibility", "versions_tab")

    @property
    def show_tasks_tab(self):
        """
        Should the tasks tab be shown for this
        """
        return self._get_hook_value("get_tab_visibility", "tasks_tab")

    ####################################################################################################
    # methods

    def get_link_filters(self, sg_location):
        """
        Returns a filter string which links this type up to a particular 
        location
        """ 
        # TODO - we might want to expose this in the hook at some point
        link_filters = []
        
        if sg_location.entity_type in ["HumanUser", "ClientUser"]:
            # the logic for users is different
            # here we want give an overview of their work
            # for the current project 
            link_filters.append(["project", "is", self._app.context.project])
            
            if self._entity_type == "Task":
                # show tasks i am assigned to
                link_filters.append(["task_assignees", "in", [sg_location.entity_dict]])
                link_filters.append(["sg_status_list", "is_not", "final"])
                
            elif self._entity_type == "Note":
                # show notes that are TO me, CC me or on tasks which I have been
                # assigned. Use advanced filters for this one so we can use OR
                
                link_filters = {
                    "logical_operator": "or", 
                    "conditions": [
                        {"path": "addressings_cc.Group.users", "values": [sg_location.entity_dict], "relation": "in"},
                        {"path": "addressings_to.Group.users", "values": [sg_location.entity_dict], "relation": "in"},
                        {"path": "replies.Reply.user", "values": [sg_location.entity_dict], "relation": "is"},
                        {"path": "addressings_cc", "values": [sg_location.entity_dict], "relation": "in"},                       
                        {"path": "addressings_to", "values": [sg_location.entity_dict], "relation": "in"},
                        {"path": "tasks.Task.task_assignees", "values": [sg_location.entity_dict], "relation": "in"} 
                        ] }                
                
            else:
                # for other things, show items created by me
                link_filters.append(["created_by", "is", sg_location.entity_dict])
            
        elif sg_location.entity_type in ["Task"]:
            
            # tasks are usually associated via a task field rather than via a link field
            if self._entity_type == "Note":
                link_filters.append(["tasks", "in", [sg_location.entity_dict]])
            
            elif self._entity_type == "Version":
                link_filters.append(["sg_task", "is", sg_location.entity_dict])
            
            elif self._entity_type in ["PublishedFile", "TankPublishedFile"]:
                link_filters.append(["task", "is", sg_location.entity_dict])

            else:
                link_filters.append(["entity", "is", sg_location.entity_dict])
            
            
        else:
            
            if self._entity_type == "Note":
                link_filters.append(["note_links", "in", [sg_location.entity_dict]])
            else:
                link_filters.append(["entity", "is", sg_location.entity_dict])
            
        return link_filters     
            
        

    def create_thumbnail(self, path, sg_data):
        """
        Given a path, create a suitable thumbnail and return a pixmap
        """
        
        thumb_style = self._get_hook_value("get_thumbnail_settings", "style")
        
        if thumb_style == "rect":
            return utils.create_rectangular_512x400_thumbnail(path)
        elif sg_data["type"] == "Note":
            # handle read/unread as a special case for notes
            if sg_data["read_by_current_user"] == "unread":
                return utils.create_circular_512x400_thumbnail(path, accent=True)
            else:
                return utils.create_circular_512x400_thumbnail(path, accent=False)
            
        
        elif thumb_style == "round": 
            return utils.create_circular_512x400_thumbnail(path)
        else:
            raise TankError("Unknown thumbnail style defined in hook!")        


    def get_playback_url(self, sg_data):
        """
        returns a url to be used for playback
        """
        
        # TODO - we might want to expose this in the hook at some point
        if self._entity_type != "Version":
            return None
        
        url = None
        if sg_data.get("sg_uploaded_movie"):
            # there is a web quicktime available!
            sg_url = sgtk.platform.current_bundle().shotgun.base_url
            url = "%s/page/screening_room?entity_type=%s&entity_id=%d" % (sg_url, sg_data["type"], sg_data["id"])                    

        return url

    def _parse_token(self, token_str):
        """
        Parse a token (" {foo::directive}
        """
        

    def _convert_token_string(self, token_str, sg_data):
        """
        Convert a string with {tokens} given a shotgun data dict
        """
        # extract all tokens and process them one after the other
        for (full_token, sg_field, directive) in self._resolve_tokens(token_str):
            # get sg data
            sg_value = sg_data.get(sg_field)
            # resolve value 
            resolved_value = self._sg_field_to_str(sg_data["type"], sg_field, sg_value, directive)
            # and replace the token with the value
            token_str = token_str.replace("{%s}" % full_token, resolved_value)
        
        return token_str
        

    def format_raw_value(self, entity_type, field_name, value, directive):
        """
        Format a raw shotgun value
        """
        return self._sg_field_to_str(entity_type, field_name, value, directive)

    def format_entity_details(self, sg_data):
        """
        Render details
        
        returns (header, body, footer)
        """
        title = self._get_hook_value("get_main_view_definition", "title")
        body = self._get_hook_value("get_main_view_definition", "body")
        footer = self._get_hook_value("get_main_view_definition", "footer")
        
        title_converted = self._convert_token_string(title, sg_data)
        body_converted = self._convert_token_string(body, sg_data)
        footer_converted = self._convert_token_string(footer, sg_data)
        
        return (title_converted, body_converted, footer_converted)
        
    def format_list_item_details(self, sg_data):
        """
        Render details
        
        returns (top_left, top_right, body) strings
        """

        top_left = self._get_hook_value("get_list_item_definition", "top_left")
        top_right = self._get_hook_value("get_list_item_definition", "top_right")
        body = self._get_hook_value("get_list_item_definition", "body")
        
        top_left_converted = self._convert_token_string(top_left, sg_data)
        top_right_converted = self._convert_token_string(top_right, sg_data)
        body_converted = self._convert_token_string(body, sg_data)
        
        return (top_left_converted, top_right_converted, body_converted)
    
