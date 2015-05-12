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
        
        
    def set_up_ui(self, dialog):
        """
        render the UI
        """
        if self._entity_type == "Version":
            dialog.focus_version(self._entity_id)
        elif self._entity_type == "Note":
            dialog.focus_note(self._entity_id)
        elif self._entity_type == "PublishedFile":
            dialog.focus_publish(self._entity_id)
        elif self._entity_type == "Version":
            dialog.focus_version(self._entity_id)
        else:
            dialog.focus_entity(self._entity_type, self._entity_id)
