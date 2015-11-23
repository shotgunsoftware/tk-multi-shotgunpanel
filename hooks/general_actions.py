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
                
        :param sg_data: Shotgun data dictionary with all the standard publish fields.
        :param actions: List of action strings which have been defined in the app configuration.
        :param ui_area: String denoting the UI Area (see above).
        :returns List of dictionaries, each with keys name, params, caption and description
        """
        app = self.parent
        app.log_debug("Generate actions called for UI element %s. "
                      "Actions: %s. Shotgun Data: %s" % (ui_area, actions, sg_data))
        
        action_instances = []
        
        if "assign_task" in actions:
            action_instances.append( 
                {"name": "assign_task", 
                  "params": None,
                  "caption": "Assign Task to yourself", 
                  "description": "Assign this task to yourself."} )

        if "task_to_ip" in actions:
            action_instances.append( 
                {"name": "task_to_ip", 
                  "params": None,
                  "caption": "Set to In Progress", 
                  "description": "Set the task status to In Progress."} )

        if "quicktime_clipboard" in actions:
            
            if sg_data.get("sg_path_to_movie"):
                # path to movie exists, so show the action
                action_instances.append( 
                    {"name": "quicktime_clipboard", 
                      "params": None,
                      "caption": "Copy quicktime path to clipboard", 
                      "description": "Copy the quicktime path associated with this version to the clipboard."} )

        if "sequence_clipboard" in actions:

            if sg_data.get("sg_path_to_frames"):
                # path to frames exists, so show the action            
                action_instances.append( 
                    {"name": "sequence_clipboard", 
                      "params": None,
                      "caption": "Copy image sequence path to clipboard", 
                      "description": "Copy the image sequence path associated with this version to the clipboard."} )

        if "publish_clipboard" in actions:
            
            if "path" in sg_data and sg_data["path"].get("local_path"): 
                # path field exists and the local path is populated
                action_instances.append( 
                    {"name": "publish_clipboard", 
                      "params": None,
                      "caption": "Copy path to clipboard", 
                      "description": "Copy the path associated with this publish to the clipboard."} )


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
                raise Exception("Cannot establish current user!")
            
            data = app.shotgun.find_one("Task", [["id", "is", sg_data["id"]]], ["task_assignees"] )
            assignees = data["task_assignees"] or []
            assignees.append(app.context.user)
            app.shotgun.update("Task", sg_data["id"], {"task_assignees": assignees})

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
        
           

    

        
