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
import datetime
import os

HookBaseClass = sgtk.get_hook_baseclass()

class GeneralActions(HookBaseClass):
    """
    General Shotgun Panel Actions that apply to all DCCs 
    """
        
    def generate_actions(self, sg_data, actions, ui_area):
        """
        Returns a list of action instances for a particular object.
        The data returned from this hook will be used to populate the 
        actions menu.
    
        The mapping between Shotgun objects and actions are kept in a different place
        (in the configuration) so at the point when this hook is called, the app
        has already established *which* actions are appropriate for this object.
        
        This method needs to return detailed data for those actions, in the form of a list
        of dictionaries, each with name, params, caption and description keys.
        
        The ui_area parameter is a string and indicates where the item is to be shown. 
        
        - If it will be shown in the main browsing area, "main" is passed. 
        - If it will be shown in the details area, "details" is passed.
                
        :param sg_data: Shotgun data dictionary with a set of standard fields.
        :param actions: List of action strings which have been defined in the app configuration.
        :param ui_area: String denoting the UI Area (see above).
        :returns List of dictionaries, each with keys name, params, caption, group and description
        """
        app = self.parent
        app.log_debug("Generate actions called for UI element %s. "
                      "Actions: %s. Shotgun Data: %s" % (ui_area, actions, sg_data))
        
        action_instances = []
        
        if "assign_task" in actions:
            action_instances.append( 
                {"name": "assign_task", 
                  "params": None,
                  "group": "Update task",
                  "caption": "Assign to yourself",
                  "description": "Assign this task to yourself."} )

        if "task_to_ip" in actions:
            action_instances.append( 
                {"name": "task_to_ip", 
                  "params": None,
                  "group": "Update task",
                  "caption": "Set to In Progress", 
                  "description": "Set the task status to In Progress."} )

        if "quicktime_clipboard" in actions:
            
            if sg_data.get("sg_path_to_movie"):
                # path to movie exists, so show the action
                action_instances.append( 
                    {"name": "quicktime_clipboard", 
                      "params": None,
                      "group": "Copy to clipboard",
                      "caption": "Quicktime path",
                      "description": "Copy the quicktime path associated with this version to the clipboard."} )

        if "sequence_clipboard" in actions:

            if sg_data.get("sg_path_to_frames"):
                # path to frames exists, so show the action            
                action_instances.append( 
                    {"name": "sequence_clipboard", 
                      "params": None,
                      "group": "Copy to clipboard",
                      "caption": "Image sequence path",
                      "description": "Copy the image sequence path associated with this version to the clipboard."} )

        if "publish_clipboard" in actions:
            
            if "path" in sg_data and sg_data["path"].get("local_path"): 
                # path field exists and the local path is populated
                action_instances.append( 
                    {"name": "publish_clipboard", 
                      "params": None,
                      "group": "Copy to clipboard",
                      "caption": "Path on disk",
                      "description": "Copy the path associated with this publish to the clipboard."} )

        if "add_to_playlist" in actions and ui_area == "details":
            # retrieve the 10 most recently updated non-closed playlists for this project

            from tank_vendor.shotgun_api3.lib.sgtimezone import LocalTimezone
            datetime_now = datetime.datetime.now(LocalTimezone())

            playlists = self.parent.shotgun.find(
                "Playlist",
                [
                    ["project", "is", sg_data.get("project")],
                    {
                        "filter_operator": "any",
                        "filters": [
                            ["sg_date_and_time", "greater_than", datetime_now],
                            ["sg_date_and_time", "is", None]
                        ]
                    }
                ],
                ["code", "id", "sg_date_and_time"],
                order=[{"field_name": "updated_at", "direction": "desc"}],
                limit=10,
            )

            # playlists this version is already part of
            existing_playlist_ids = [x["id"] for x in sg_data.get("playlists", [])]

            for playlist in playlists:
                if playlist["id"] in existing_playlist_ids:
                    # version already in this playlist so skip
                    continue

                if playlist.get("sg_date_and_time"):
                    # playlist name includes date/time
                    caption = "%s (%s)" % (
                        playlist["code"],
                        self._format_timestamp(playlist["sg_date_and_time"])
                    )
                else:
                    caption = playlist["code"]

                self.logger.debug("Created add to playlist action for playlist %s" % playlist)

                action_instances.append({
                    "name": "add_to_playlist",
                    "group": "Add to playlist",
                    "params": {"playlist_id": playlist["id"]},
                    "caption": caption,
                    "description": "Add the version to this playlist."
                })


        return action_instances

    def execute_action(self, name, params, sg_data):
        """
        Execute a given action. The data sent to this be method will
        represent one of the actions enumerated by the generate_actions method.
        
        :param name: Action name string representing one of the items returned by generate_actions.
        :param params: Params data, as specified by generate_actions.
        :param sg_data: Shotgun data dictionary
        :returns: No return value expected.
        """
        app = self.parent
        app.log_debug("Execute action called for action %s. "
                      "Parameters: %s. Shotgun Data: %s" % (name, params, sg_data))
        
        if name == "assign_task":
            if app.context.user is None:
                raise Exception(
                    "Shotgun Toolkit does not know what Shotgun user you are. "
                    "This can be due to the use of a script key for authentication "
                    "rather than using a user name and password login. To assign a "
                    "Task, you will need to log in using you Shotgun user account."
                )
            
            data = app.shotgun.find_one("Task", [["id", "is", sg_data["id"]]], ["task_assignees"] )
            assignees = data["task_assignees"] or []
            assignees.append(app.context.user)
            app.shotgun.update("Task", sg_data["id"], {"task_assignees": assignees})

        elif name == "add_to_playlist":
            app.shotgun.update(
                "Version",
                sg_data["id"],
                {"playlists": [{"type": "Playlist", "id": params["playlist_id"]}]},
                multi_entity_update_modes={"playlists": "add"}
            )
            self.logger.debug(
                "Updated playlist %s to include version %s" % (
                    params["playlist_id"],
                    sg_data["id"]
                )
            )

        elif name == "task_to_ip":
            app.shotgun.update("Task", sg_data["id"], {"sg_status_list": "ip"})

        elif name == "quicktime_clipboard":
            self._copy_to_clipboard(sg_data["sg_path_to_movie"])
            
        elif name == "sequence_clipboard":
            self._copy_to_clipboard(sg_data["sg_path_to_frames"])
            
        elif name == "publish_clipboard":
            self._copy_to_clipboard(sg_data["path"]["local_path"])

    def _copy_to_clipboard(self, text):
        """
        Helper method - copies the given text to the clipboard
        
        :param text: content to copy
        """
        from sgtk.platform.qt import QtCore, QtGui
        app = QtCore.QCoreApplication.instance()
        app.clipboard().setText(text)

    def _format_timestamp(self, datetime_obj):
        """
        Formats the given datetime object in a short human readable form.

        :param datetime_obj: Datetime obj to format
        :returns: date str
        """
        from tank_vendor.shotgun_api3.lib.sgtimezone import LocalTimezone
        datetime_now = datetime.datetime.now(LocalTimezone())

        datetime_tomorrow = datetime_now + datetime.timedelta(hours=24)

        if datetime_obj.date() == datetime_now.date():
            # today - display timestamp - Today 01:37AM
            return datetime_obj.strftime("Today %I:%M%p")

        elif datetime_obj.date() == datetime_tomorrow.date():
            # tomorrow - display timestamp - Tomorrow 01:37AM
            return datetime_obj.strftime("Tomorrow %I:%M%p")

        else:
            # 24 June 01:37AM
            return datetime_obj.strftime("%d %b %I:%M%p")
