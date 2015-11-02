# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from .shotgun_formatter import ShotgunFormatter

class ShotgunLocation(object):
    """
    Object that wraps around a shotgun entity. This object
    makes it easy to access settings, formatting details around
    for any entity, via the sg_formatter property.
    """
    
    def __init__(self, entity_type, entity_id):
        self._entity_type = entity_type
        self._entity_id = entity_id
        self._formatter = ShotgunFormatter(self._entity_type)
    
        # The ui tab index currently focused on for this location
        self.tab_index = 0
            
    @property
    def entity_type(self):
        """
        Returns the entity type for this object
        """
        return self._entity_type
    
    @property
    def entity_id(self):
        """
        Returns the Shotgun id for this object
        """
        return self._entity_id
    
    @property
    def entity_dict(self):
        """
        Returns an entity dictionary with keys type and id
        to represent the entity. Note that this dict does NOT
        include a name key.
        """
        return {"type": self._entity_type, "id": self._entity_id}
    
    def get_external_url(self):
        """
        Returns the sg webapp url for this entity
        """
        app = sgtk.platform.current_bundle()
        
        if self._entity_type == "Playlist":
            proj_id = app.context.project["id"]
            url = "%s/page/media_center?project_id=%d&entity_type=%s&entity_id=%d" % (app.sgtk.shotgun_url, 
                                                                                      proj_id,
                                                                                      self._entity_type, 
                                                                                      self._entity_id)
        else:
            url = "%s/detail/%s/%s" % (self._entity_type, self._entity_id)
    
        return url    
    
    @property
    def sg_formatter(self):
        """
        Returns a formatter object with details on how 
        this object should be displayed and formatted
        """
        return self._formatter

