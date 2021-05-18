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
import os

HookBaseClass = sgtk.get_hook_baseclass()


class ShotgunFields(HookBaseClass):
    """
    Controls the field configuration for the Shotgun Panel.

    Via this hook, the visual appearance of the Shotgun Panel can be controlled.
    When the shotgun panel displays a UI element, it will call this hook
    in order to determine how that particular object should be formatted.

    Formatting is returned in the form of templated strings, for example::

        <b>By:</b> {created_by}{[<br><b>Description:</b> ]description}

    {dynamic} tokens are on the following form::

        {[preroll]shotgun.field.name|sg_field_name_fallback::directive[postroll]}

    Basic Examples:

        - Simple format: {code}

        - Deep links: {sg_sequence.Sequence.code}

        - If artist is null, use created_by: {artist|created_by}

    Directives are also supported - these are used by the formatting logic
    and include the following:

        - {sg_sequence::showtype} - This will generate a link saying
          'Sequence ABC123' instead of just 'ABC123' like it does by default

        - {sg_sequence::nolink} - No url link will be created

    Optional pre/post roll - if a value is null, pre- and post-strings are
    omitted from the final result. Examples of this syntax:

        - {[Name: ]code} - If code is set, 'Name: xxx' will be
          printed out, otherwise nothing.

        - {[Name: ]code[<br>]} - Same as above but with a post line break

    For a high level reference of the options available,
    see the app documentation.
    """

    def get_list_item_definition(self, entity_type):
        """
        Controls the rendering of items in the various item listings.

        Should return a dictionary with the following keys:

        - top_left: content to display in the top left area of the item
        - top_right: content to display in the top right area of the item
        - body: content to display in the main area of the item

        :param entity_type: Shotgun entity type to provide a template for
        :return: Dictionary containing template strings
        :rtype: dict
        """

        # define a set of defaults
        values = {
            "top_left": "<big>{code}</big>",
            "top_right": "{updated_at}",
            "body": "<b>By:</b> {created_by}{[<br><b>Description:</b> ]description}",
        }

        # override
        if entity_type == "PublishedFile":

            values["top_left"] = "<big>{name} v{version_number}</big>"
            values["top_right"] = "{created_at}"
            values[
                "body"
            ] = """
                {published_file_type} by {created_by}<br>
                <b>Comments:</b> {description}
                """

        elif entity_type == "Note":

            values["top_left"] = "<big>{subject}</big>"
            values["top_right"] = "{sg_status_list}"
            values["body"] = "{content}"

        elif entity_type == "Version":

            values[
                "body"
            ] = """
                <b>By:</b> {user|created_by}<br>
                <b>Comments:</b> {description}
                """

        elif entity_type == "Task":

            values["top_left"] = "<big>{content}</big>"
            values["top_right"] = "{sg_status_list}"
            values[
                "body"
            ] = """
                {[Assigned to ]task_assignees[<br>]}
                {entity::showtype[<br>]}
                {[Starts: ]start_date}{[ Due:]due_date}
                """

        return values

    def get_all_fields(self, entity_type):
        """
        Define which fields should be displayed in the 'info' tab
        for a given entity type.

        :param entity_type: Shotgun entity type to provide a template for
        :return: The Shotgun fields
        :rtype: list
        """

        # supported by all normal fields
        base_values = [
            "id",
            "type",
            "tag_list",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        ]

        # supported by most entities
        std_values = base_values + [
            "code",
            "project",
            "tags",
            "sg_status_list",
            "description",
        ]

        if entity_type == "Shot":
            values = std_values
            values += [
                "assets",
                "sg_cut_duration",
                "sg_cut_in",
                "sg_cut_out",
                "sg_head_in",
                "sg_tail_out",
                "sg_sequence",
                "sg_working_duration",
            ]

        elif entity_type == "Sequence":
            values = std_values + ["shots", "assets"]

        elif entity_type == "Project":
            values = base_values + [
                "sg_description",
                "archived",
                "code",
                "due",
                "name",
                "sg_start",
                "sg_status",
                "tank_name",
                "sg_type",
                "users",
            ]

        elif entity_type == "Asset":
            values = std_values + [
                "sg_asset_type",
                "shots",
                "parents",
                "sequences",
                "assets",
            ]

        elif entity_type == "ClientUser":
            values = base_values + [
                "email",
                "firstname",
                "lastname",
                "name",
                "sg_status_list",
            ]

        elif entity_type == "HumanUser":
            values = base_values + [
                "department",
                "groups",
                "login",
                "email",
                "firstname",
                "lastname",
                "name",
                "sg_status_list",
            ]

        elif entity_type == "ScriptUser":
            values = base_values + ["description", "email", "firstname", "lastname"]

        elif entity_type == "Group":
            values = base_values + ["users"]

        elif entity_type == "Version":
            values = std_values + [
                "user",
                "sg_department",
                "sg_first_frame",
                "frame_count",
                "frame_range",
                "sg_uploaded_movie_frame_rate",
                "sg_path_to_geometry",
                "sg_last_frame",
                "entity",
                "sg_path_to_frames",
                "sg_path_to_movie",
                "playlists",
                "client_approved_by",
                "client_approved_at",
                "client_approved",
                "cuts",
                "delivery_sg_versions_deliveries",
                "sg_department",
                "published_files",
                "sg_task",
                "sg_version_type",
            ]

        elif entity_type == "PublishedFile":
            values = std_values + [
                "entity",
                "name",
                "published_file_type",
                "task",
                "version",
                "version_number",
            ]

        elif entity_type == "Task":
            values = base_values + [
                "task_assignees",
                "est_in_mins",
                "addressings_cc",
                "due_date",
                "duration",
                "entity",
                "step",
                "start_date",
                "sg_status_list",
                "project",
                "content",
            ]

        else:
            values = std_values

        return values

    def get_main_view_definition(self, entity_type):
        """
        Define which info is shown in the top-level detail section
        for an item of a given entity type.

        Should return a dictionary with the following keys:

        - title: top level title string, displayed next to the
                 navigation buttons.
        - body: content to display in the main info area

        :param entity_type: Shotgun entity type to provide a template for
        :return: A mapping of UI field to template string data
        :rtype: dict
        """

        values = {
            "title": "{type} {code}",
            "body": "Status: {sg_status_list}<br>Description: {description}",
        }

        if entity_type == "HumanUser":
            values["title"] = "{name}"

            values[
                "body"
            ] = """
                Login: {login}<br>
                Email: {email}<br>
                Department: {department}
                """

        if entity_type == "ClientUser":
            values["title"] = "{name}"

            values[
                "body"
            ] = """<br>
                <b>Shotgun Client User</b><br><br>
                Email: {email}
                """

        if entity_type == "ApiUser":
            values["title"] = "{firstname}"

            values[
                "body"
            ] = """
                <b>Shotgun Api Script</b><br><br>
                Script Version: {lastname}<br>
                Maintainer: {email}<br>
                Description: {description}
                """

        if entity_type == "Group":
            values["title"] = "{code}"

            values[
                "body"
            ] = """
                <b>Group of users</b><br><br>
                Members: {users}
                """

        elif entity_type == "Shot":
            values[
                "body"
            ] = """
                Sequence: {sg_sequence}<br>
                Status: {sg_status_list}<br>
                {[Cut In: ]sg_cut_in[  ]}{[Cut Out:]sg_cut_out[  ]}{[Duration: ]sg_cut_duration}<br>
                Description: {description}
                """

        elif entity_type == "Task":
            values["title"] = "Task {content}"
            values[
                "body"
            ] = """

                <big>Status: {sg_status_list}</big><br>
                {entity::showtype[<br>]}
                {[Assigned to: ]task_assignees[<br>]}
                {[Starts: ]start_date}{[ Due: ]due_date}
                """

        elif entity_type == "Asset":
            values[
                "body"
            ] = """
                Asset Type: {sg_asset_type}<br>
                Status: {sg_status_list}<br>
                Description: {description}
                """

        elif entity_type == "Project":
            values["title"] = "Project {name}"

            values[
                "body"
            ] = """
                <b>Status: {sg_status}<br>
                {[Start Date: ]start_date[<br>]}
                {[End Date: ]end_date[<br>]}
                Description: {sg_description}
                """

        elif entity_type == "Note":
            values["title"] = "{subject}"

            values[
                "body"
            ] = """
                Note by {created_by} {[(Task ]tasks[)]}<br>
                Written on {created_at}<br>
                {[Addressed to: ]addressings_to}{[, CC: ]addressings_cc}<br>
                <br>
                Associated With:<br>{note_links::showtype}
                """

        elif entity_type == "PublishedFile":
            values["title"] = "{code}"

            values[
                "body"
            ] = """
                <big>{published_file_type}, Version {version_number}</big><br>
                For {entity::showtype}{[, Task ]task} <br>
                Created by {created_by} on {created_at}<br>

                {[<br>Reviewed here: ]version[<br>]}

                <br>
                <b>Comments:</b><br>
                {description}
                """

        elif entity_type == "Version":
            values["title"] = "{code}"

            values[
                "body"
            ] = """
                {entity::showtype}{[, Task ]sg_task} <br>
                Status: {sg_status_list}<br>
                Created by {user|created_by} on {created_at}<br>
                {[<br>Client approved by: ]client_approved_by[<br>]}
                {[<br>In Playlists: ]playlists[<br>]}

                <br>
                <b>Comments: </b>{description}
                """

        return values

    def get_entity_tabs_definition(self, entity_type, shotgun_globals):
        """
        Define which tabs are shown in the Shotgun Panel for an item of a given entity type.

        Returns a dictionary with a key-value pair for each entity tab defined in
        tk-multi-shotgunpanel AppDialog.ENTITY_TABS. Each key-value will be a dictionary
        containing data for the tab.

        The following keys are supported:
            "activity"
            "notes"
            "versions"
            "publishes"
            "publish_history"
            "publish_downstream"
            "publish_upstream"
            "tasks"
            "info

        The following value dict keys are supported:
            name:
                type: str
                description: The text displayed for the tab (e.g. the tab label).
            description:
                type: str
                description: A short description displayed at the top of the entity
                             tab widget.
            enabled:
                type: bool
                description: Set to True to display the tab, or False to hide it.
            enable_checkbox:
                type: bool
                description: Set to True to enable the checkbox filter for this
                            entity (if there is one), else False to hide it.
            tooltip:
                supported entity types: Version only
                type: str
                description: Text to display in tooltip when hovering over an item
                             in the entity list view.
            sort:
                supported entity types: Version only
                type: str
                description: The entity field to sort the entity list view by.

        :param entity_type: Shotgun entity type to provide tab info for.
        :return: The entity tabs definition data used to build the Shotgun panel tab widgets.
        :rtype: dict
        """

        # Default tab config, unless specified otherwise by entity type.
        values = {
            "activity": {"enabled": True, "name": "Activity"},
            "info": {"enabled": True, "name": "Details"},
            "notes": {
                "enabled": True,
                "name": "Notes",
                "description": "Notes associated with this %s, in update order."
                % shotgun_globals.get_type_display_name(entity_type),
            },
            "tasks": {
                "enabled": True,
                "name": "Tasks",
                "description": "All tasks for this %s."
                % shotgun_globals.get_type_display_name(entity_type),
            },
            "versions": {
                "enabled": True,
                "name": "Versions",
                "description": "Review versions for this %s, in creation order."
                % shotgun_globals.get_type_display_name(entity_type),
                "enable_checkbox": True,
            },
            "publishes": {
                "enabled": True,
                "name": "Publishes",
                "description": "Publishes for this %s, in creation order."
                % shotgun_globals.get_type_display_name(entity_type),
                "enable_checkbox": True,
            },
            "publish_history": {
                "enabled": False,
                "name": "Version History",
                "description": "The version history for this publish.",
            },
            "publish_downstream": {
                "enabled": False,
                "name": "Uses",
                "description": "Publishes being referenced by this publish.",
            },
            "publish_upstream": {
                "enabled": False,
                "name": "Used By",
                "description": "Publishes that are referencing this publish.",
            },
        }

        if entity_type == "ApiUser":
            values["activity"]["enabled"] = False
            values["tasks"]["enabled"] = False
            values["notes"][
                "description"
            ] = "Notes that the user has written or replied to, in update order."

        elif entity_type == "ClientUser":
            values["activity"]["enabled"] = False
            values["publishes"]["enabled"] = False
            values["versions"]["enabled"] = False
            values["tasks"]["enabled"] = False
            values["notes"][
                "description"
            ] = "Notes that the user has written or replied to, in update order."

        elif entity_type == "Department":
            values["activity"]["enabled"] = False
            values["notes"]["enabled"] = False
            values["publishes"]["enabled"] = False
            values["versions"]["enabled"] = False
            values["tasks"]["enabled"] = False

        elif entity_type == "Group":
            values["activity"]["enabled"] = False
            values["notes"]["enabled"] = False
            values["publishes"]["enabled"] = False
            values["versions"]["enabled"] = False
            values["tasks"]["enabled"] = False

        elif entity_type == "HumanUser":
            values["activity"]["enabled"] = False
            values["tasks"]["description"] = "Active tasks assigned to this user."
            values["versions"][
                "description"
            ] = "Review versions by this user, in creation order."
            values["publishes"][
                "description"
            ] = "Publishes by this user, in creation order."
            values["notes"][
                "description"
            ] = "Notes that the user has written or replied to, in update order."

        elif entity_type == "ScriptUser":
            values["activity"]["enabled"] = False
            values["tasks"]["enabled"] = False

        elif entity_type == "Project":
            values["info"]["enabled"] = False
            values["tasks"]["description"] = "Your active tasks for this project."
            values["versions"][
                "description"
            ] = "All review versions submitted for this project."
            values["publishes"][
                "description"
            ] = "All publishes for the project, in creation order."
            values["notes"][
                "description"
            ] = "All notes for this project, in update order."

        elif entity_type == "Version":
            values["versions"]["enabled"] = False
            values["tasks"]["enabled"] = False
            values["publishes"]["enable_checkbox"] = False

        elif entity_type in ["PublishedFile", "TankPublishedFile"]:
            values["activity"]["enabled"] = False
            values["notes"]["enabled"] = False
            values["publishes"]["enabled"] = False
            values["versions"]["enabled"] = False
            values["tasks"]["enabled"] = False
            values["publish_history"]["enabled"] = True
            values["publish_downstream"]["enabled"] = True
            values["publish_upstream"]["enabled"] = True

        return values

    def get_entity_default_tab(self, entity_type):
        """
        Return the name of the default tab for this entity type. Tab name should
        be one of the defined tab names in tk-multi-shotgunpanel AppDialog.ENTITY_TABS.

        :param entity_type: Shotgun entity type to get the default for.
        :return: The default tab name
        :rtype str:
        """

        if entity_type == "Project":
            # my tasks is the default tab for projects
            return "tasks"

        if entity_type in ["Group", "Department"]:
            # these items don't have much stuff turned on so show details
            return "info"

        if entity_type in ["ClientUser", "HumanUser", "ScriptUser", "ApiUser"]:
            # these types don't have the activity stream
            return "notes"

        if entity_type in ["PublishedFile", "TankPublishedFile"]:
            return "publish_history"

        # for everything else, default to the activity stream
        return "activity"
