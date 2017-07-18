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
from sgtk.platform.qt import QtGui

HookBaseClass = sgtk.get_hook_baseclass()


class NukeActions(HookBaseClass):
    """
    Shotgun Panel Actions for Nuke
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
                
        :param sg_data: Shotgun data dictionary.
        :param actions: List of action strings which have been defined in the app configuration.
        :param ui_area: String denoting the UI Area (see above).
        :returns List of dictionaries, each with keys name, params, caption and description
        """
        app = self.parent
        app.log_debug("Generate actions called for UI element %s. "
                      "Actions: %s. Shotgun Data: %s" % (ui_area, actions, sg_data))
        
        action_instances = []
        
        try:
            # call base class first
            action_instances += HookBaseClass.generate_actions(self, sg_data, actions, ui_area)
        except AttributeError, e:
            # base class doesn't have the method, so ignore and continue
            pass        
        
        if "read_node" in actions:
            action_instances.append( {"name": "read_node", 
                                      "params": None,
                                      "caption": "Create Read Node", 
                                      "description": "This will add a read node to the current scene."} )

        if "script_import" in actions:        
            action_instances.append( {"name": "script_import",
                                      "params": None, 
                                      "caption": "Import Contents", 
                                      "description": "This will import all the nodes into the current scene."} )

        if "open_project" in actions:
            action_instances.append( {"name": "open_project",
                                      "params": None,
                                      "caption": "Open Project",
                                      "description": "This will open the Nuke Studio project in the current session."} )

        if "submit_for_review" in actions:

            # Based on the config, we know this is a rendered image publish.
            # ensure we're only adding this action if the publish does not have
            # a linked Version.
            if not sg_data.get("version"):
                action_instances.append({
                    "name": "submit_for_review",
                    "params": None,
                    "caption": "Submit for Review",
                    "description": "Submit the Publish to SG for review."
                })

        if "download" in actions:
            action_instances.append({
                "name": "download",
                "params": None,
                "caption": "Download",
                "description": "Ensure the publish exists locally."
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

        # resolve path - forward slashes on all platforms in Nuke
        path = self.get_publish_path(sg_data).replace(os.path.sep, "/")

        if name == "read_node":
            self._create_read_node(path, sg_data)
        
        elif name == "script_import":
            self._import_script(path, sg_data)

        elif name == "open_project":
            self._open_project(path, sg_data)

        elif name == "submit_for_review":
            self._submit_for_review(path, sg_data)

        elif name == "download":
            self._download(path, sg_data)

        else:
            try:
                HookBaseClass.execute_action(self, name, params, sg_data)
            except AttributeError, e:
                # base class doesn't have the method, so ignore and continue
                pass            
            
           
    ##############################################################################################################
    # helper methods which can be subclassed in custom hooks to fine tune the behavior of things
    
    def _import_script(self, path, sg_publish_data):
        """
        Import contents of the given file into the scene.
        
        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        """
        import nuke
        if not os.path.exists(path):
            raise Exception("File not found on disk - '%s'" % path)
        
        nuke.nodePaste(path)

    def _open_project(self, path, sg_publish_data):
        """
        Open the nuke studio project.

        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        """

        if not os.path.exists(path):
            raise Exception("File not found on disk - '%s'" % path)

        import nuke

        if not nuke.env.get("studio"):
            # can't import the project unless nuke studio is running
            raise Exception("Nuke Studio is required to open the project.")

        import hiero
        hiero.core.openProject(path)

    def _create_read_node(self, path, sg_publish_data):
        """
        Create a read node representing the publish.
        
        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.        
        """        
        import nuke
        
        (_, ext) = os.path.splitext(path)

        # If this is an Alembic cache, use a ReadGeo2 and we're done.
        if ext.lower() == '.abc':
            nuke.createNode('ReadGeo2', 'file {%s}' % path)
            return

        valid_extensions = [".png", 
                            ".jpg", 
                            ".jpeg", 
                            ".exr", 
                            ".cin", 
                            ".dpx", 
                            ".tiff", 
                            ".tif", 
                            ".mov", 
                            ".psd",
                            ".tga",
                            ".ari",
                            ".gif",
                            ".iff"]

        if ext.lower() not in valid_extensions:
            raise Exception("Unsupported file extension for '%s'!" % path)

        # `nuke.createNode()` will extract the format and frame range from the
        # file itself (if possible), whereas `nuke.nodes.Read()` won't. We'll
        # also check to see if there's a matching template and override the
        # frame range, but this should handle the zero config case. This will
        # also automatically extract the format and frame range for movie files.
        read_node = nuke.createNode("Read")
        read_node["file"].fromUserText(path)

        # find the sequence range if it has one:
        seq_range = self._find_sequence_range(path)

        if seq_range:
            # override the detected frame range.
            read_node["first"].setValue(seq_range[0])
            read_node["last"].setValue(seq_range[1])

    def _find_sequence_range(self, path):
        """
        Helper method attempting to extract sequence information.
        
        Using the toolkit template system, the path will be probed to 
        check if it is a sequence, and if so, frame information is
        attempted to be extracted.
        
        :param path: Path to file on disk.
        :returns: None if no range could be determined, otherwise (min, max)
        """
        # find a template that matches the path:
        template = None
        try:
            template = self.parent.sgtk.template_from_path(path)
        except sgtk.TankError:
            pass
        
        if not template:
            return None
            
        # get the fields and find all matching files:
        fields = template.get_fields(path)
        if not "SEQ" in fields:
            return None
        
        files = self.parent.sgtk.paths_from_template(template, fields, ["SEQ", "eye"])
        
        # find frame numbers from these files:
        frames = []
        for file in files:
            fields = template.get_fields(file)
            frame = fields.get("SEQ")
            if frame != None:
                frames.append(frame)
        if not frames:
            return None
        
        # return the range
        return (min(frames), max(frames))

    def _submit_for_review(self, path, sg_publish_data):
        """
        Submit the publish for review in SG

        :param path: Path to the publish file
        :param sg_publish_data: Shotgun data dictionary with all the standard
            publish fields.
        """

        app = self.parent

        app.log_debug("Loading RAAS framework...")
        raas_fw = self.load_framework("tk-framework-raas_v0.x.x")
        raas_actions = raas_fw.import_module("actions")

        review_submit_dialog = raas_actions.review_submit.ReviewSubmitDialog(
            QtGui.QApplication.activeWindow(),
            sg_publish_data
        )
        review_submit_dialog.show()

    def _download(self, path, sg_publish_data):
        """
        Ensure the publish exists locally

        :param path: Path to the publish file
        :param sg_publish_data: Shotgun data dictionary with all the standard
            publish fields.
        """

        app = self.parent

        app.log_debug("Loading RAAS framework...")
        raas_fw = self.load_framework("tk-framework-raas_v0.x.x")
        raas_actions = raas_fw.import_module("actions")

        raas_actions.ensure_local(sg_publish_data)
