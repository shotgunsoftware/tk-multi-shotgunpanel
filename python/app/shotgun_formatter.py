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
        fields += self._resolve_fields( self._get_hook_value("get_list_item_definition", "top_left") )
        fields += self._resolve_fields( self._get_hook_value("get_list_item_definition", "top_right") )
        fields += self._resolve_fields( self._get_hook_value("get_list_item_definition", "body") )
        fields += self._resolve_fields( self._get_hook_value("get_main_view_definition", "title") )
        fields += self._resolve_fields( self._get_hook_value("get_main_view_definition", "body") )
        fields += self._resolve_fields( self._get_hook_value("get_main_view_definition", "footer") )
        self._token_fields = set(fields)
        
    def _resolve_fields(self, token_str):
        """
        given a string with {tokens} or {deep.linktokens} return a list
        of tokens.
        """    
    
        try:
            # find all field names ["xx", "yy", "zz.xx"] from "{xx}_{yy}_{zz.xx}"
            fields = set(re.findall('{([^}^{]*)}', token_str))
        except Exception, error:
            raise TankError("Could not parse '%s' - Error: %s" % (token_str, error) )
    
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
    
    def _sg_field_to_str(self, sg_field, value):
        """
        Convert to string
        """
        return str(value)
    
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
        return self._hook_data["get_all_fields"]

    @property
    def fields(self): 
        """
        fields needed to render list or main details
        """
        return list(self._token_fields)

    ####################################################################################################
    # methods

    def create_thumbnail(self, path):
        """
        Given a path, create a suitable thumbnail and return a pixmap
        """
        
        thumb_style = self._get_hook_value("get_thumbnail_settings", "style")
        
        if thumb_style == "rect":
            return utils.create_rectangular_512x400_thumbnail(path)
        elif thumb_style == "round":
            return utils.create_circular_512x400_thumbnail(path)
        else:
            raise TankError("Unknown thumbnail style defined in hook!")        


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
        title = self._get_hook_value("get_main_view_definition", "title")
        body = self._get_hook_value("get_main_view_definition", "body")
        footer = self._get_hook_value("get_main_view_definition", "footer")
        
        # run replacements of the strings
        for (field_name, value) in sg_data.iteritems():
            token = "{%s}" % field_name
            str_value = self._sg_field_to_str(field_name, value)
            title = title.replace(token, str_value)
            body = body.replace(token, str_value)
            footer = footer.replace(token, str_value)
        
        return (title, body, footer)
        
#         name = sg_data.get("code") or "Unnamed"
#         title = "%s %s" % (sg_data.get("type"), name)
#         top_label.setText(title)
#         bottom_label.setText(sg_data.get("description") or "No Description")
    
    def format_list_item_details(self, sg_data):
        """
        Render details
        
        returns (top_left, top_right, body) strings
        """

        top_left = self._get_hook_value("get_list_item_definition", "top_left")
        top_right = self._get_hook_value("get_list_item_definition", "top_right")
        body = self._get_hook_value("get_list_item_definition", "body")
        
        # run replacements of the strings
        for (field_name, value) in sg_data.iteritems():
            token = "{%s}" % field_name
            str_value = self._sg_field_to_str(field_name, value)
            top_left = top_left.replace(token, str_value)
            top_right = top_right.replace(token, str_value)
            body = body.replace(token, str_value)
        
        
#         created_unixtime = sg_data.get("created_at")
#         created_datetime = datetime.datetime.fromtimestamp(created_unixtime)
#         (human_str, exact_str) = utils.create_human_readable_timestamp(created_datetime)
# 
#         user_name = (sg_data.get("artist") or {}).get("name") or "Unknown User"        
#         description = sg_data.get("description") or ""
#         content = "By %s %s<br><i>%s</i>" % (user_name, human_str, description)
# 
#         title = "<b>%s</b>" % sg_data.get("code") or "Untitled Version"

        return (top_left, top_right, body)
    
