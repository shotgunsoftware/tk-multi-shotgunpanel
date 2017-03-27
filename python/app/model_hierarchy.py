# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk

shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
SimpleShotgunHierarchyModel = shotgun_model.SimpleShotgunHierarchyModel


class ShotgunHierarchyModel(SimpleShotgunHierarchyModel):
    """
    Hierarchy navigation model.

    Intended to be attached to a navigation tree view.

    Shows a hierarchy of published files. The rationale here is that
    when you are in a DCC, your primary objective is to publish files, so
    the hierarchy should outline items *for which files can be published.*
    """

    def __init__(self, parent, bg_task_manager):
        """
        Initializes a Shotgun Hierarchy model instance and loads a hierarchy
        that leads to entities that are linked via the ``PublishedFile.entity`` field.

        :param parent: The model parent.
        :type parent: :class:`~PySide.QtGui.QObject`
        :param bg_task_manager: Background task manager to use for any asynchronous work.
        :type bg_task_manager: :class:`~task_manager.BackgroundTaskManager`
        """
        SimpleShotgunHierarchyModel.__init__(self, parent, bg_task_manager=bg_task_manager)

        # We need to provide a dictionary that identifies what additional fields to include
        # for the loaded hierarchy leaf entities in addition to "id" and "type".
        # When they are available for an entity, these fields will be used to add info in the detail panel.
        # TODO: Our entity type list for entities with publishes should be retrieved from somewhere.
        entity_fields = {}
        for entity_type in ["Asset", "Shot"]:
            entity_fields[entity_type] = ["code", "description", "image", "sg_status_list"]

        self._bundle = sgtk.platform.current_bundle()

    def set_location(self, sg_location):
        """
        Clears the model and sets it up for a particular entity.
        Loads any cached data that exists and schedules an async refresh.

        :param sg_location: Location object which should be selected/focused.
        """
        # TODO - when tree system supports entity->path resolution, implement selection

        if self._bundle.context.project:
            # todo - refactor when we have the new entity resolution methods
            path = "/Project/%s" % self._bundle.context.project["id"]
        else:
            path = "/"

        if sgtk.util.get_published_file_entity_type(self._bundle.sgtk) == "PublishedFile":
            seed = "PublishedFile.entity"
        else:
            seed = "TankPublishedFile.entity"

        self.load_data(
            seed,
            path=path,
            entity_fields=self._entity_fields
        )


