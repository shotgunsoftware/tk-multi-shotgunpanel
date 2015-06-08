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
from .shotgun_formatter import ShotgunFormatter

class ShotgunLocation(object):
    """
    """
    
    def __init__(self, entity_type, entity_id):
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
    def sg_formatter(self):
        return ShotgunFormatter(self._entity_type)

