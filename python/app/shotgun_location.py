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
from .shotgun_formatter import ShotgunEntityFormatter

class ShotgunLocation(object):
    """
    Object that wraps around a shotgun entity. This object
    makes it easy to access settings, formatting details around
    for any entity, via the sg_formatter property.
    """
    
    def __init__(self, entity_type, entity_id):
        self._entity_type = entity_type
        self._entity_id = entity_id
        self._formatter = ShotgunEntityFormatter(self._entity_type, entity_id)
    
        # The ui tab index currently focused on for this location
        self._tab_index = self._formatter.default_tab

    def __repr__(self):
        """
        String representation
        """
        return "<ShotgunLocation %s %s tab index %s>" % (
            self._entity_type,
            self._entity_id,
            self._tab_index
        )

    @classmethod
    def from_context(cls, ctx):
        """
        Interprets the given Context and constructs the apporpriate
        ShotgunLocation for it.

        :param ctx: The Context to interpret.

        :returns: The resulting ShotgunLocation.
        """
        # determine home by looking at various locations
        # - first look for a current task
        # - then a current entity
        # - failing that a project
        # - as a last fallback (for site contexts) use the user

        if ctx.task:
            sg_location = cls(ctx.task["type"], ctx.task["id"])

        elif ctx.entity:
            sg_location = cls(ctx.entity["type"], ctx.entity["id"])
                    
        elif ctx.project:
            sg_location = cls(ctx.project["type"], ctx.project["id"])

        elif ctx.user:
            sg_location = cls(ctx.user["type"], ctx.user["id"])

        else:
            raise NotImplementedError("The Shotgun panel requires a non-empty context.")

        return sg_location

    def set_tab_index(self, index):
        """
        Update the associated tab index
        :param int index: tab index
        """
        self._tab_index = index

    @property
    def tab_index(self):
        """
        The tab index associated with this location
        """
        return self._tab_index

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
            url = "%s/detail/%s/%s" % (app.sgtk.shotgun_url, self._entity_type, self._entity_id)
    
        return url    
    
    @property
    def sg_formatter(self):
        """
        Returns a formatter object with details on how 
        this object should be displayed and formatted

        :returns: :class:`ShotgunEntityFormatter` instance
        """
        return self._formatter

