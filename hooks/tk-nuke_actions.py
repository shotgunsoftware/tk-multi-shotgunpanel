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
import re
import glob

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
        app.log_debug(
            "Generate actions called for UI element %s. "
            "Actions: %s. SG Data: %s" % (ui_area, actions, sg_data)
        )

        action_instances = []

        try:
            # call base class first
            action_instances += HookBaseClass.generate_actions(
                self, sg_data, actions, ui_area
            )
        except AttributeError as e:
            # base class doesn't have the method, so ignore and continue
            pass

        if "read_node" in actions:
            action_instances.append(
                {
                    "name": "read_node",
                    "params": None,
                    "caption": "Create Read Node",
                    "description": "This will add a read node to the current scene.",
                }
            )

        if "script_import" in actions:
            action_instances.append(
                {
                    "name": "script_import",
                    "params": None,
                    "caption": "Import Contents",
                    "description": "This will import all the nodes into the current scene.",
                }
            )

        if "open_project" in actions:
            action_instances.append(
                {
                    "name": "open_project",
                    "params": None,
                    "caption": "Open Project",
                    "description": "This will open the Nuke Studio project in the current session.",
                }
            )

        if "clip_import" in actions:
            action_instances.append(
                {
                    "name": "clip_import",
                    "params": None,
                    "caption": "Import Clip",
                    "description": "This will add a Clip to the current project.",
                }
            )

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
        app.log_debug(
            "Execute action called for action %s. "
            "Parameters: %s. SG Data: %s" % (name, params, sg_data)
        )

        if name == "read_node":
            # resolve path - forward slashes on all platforms in Nuke
            path = self.get_publish_path(sg_data).replace(os.path.sep, "/")
            self._create_read_node(path, sg_data)

        elif name == "script_import":
            # resolve path - forward slashes on all platforms in Nuke
            path = self.get_publish_path(sg_data).replace(os.path.sep, "/")
            self._import_script(path, sg_data)

        elif name == "open_project":
            # resolve path - forward slashes on all platforms in Nuke
            path = self.get_publish_path(sg_data).replace(os.path.sep, "/")
            self._open_project(path, sg_data)

        elif name == "clip_import":
            # resolve path - forward slashes on all platforms in Nuke
            path = self.get_publish_path(sg_data).replace(os.path.sep, "/")
            self._import_clip(path, sg_data)

        else:
            try:
                HookBaseClass.execute_action(self, name, params, sg_data)
            except AttributeError as e:
                # base class doesn't have the method, so ignore and continue
                pass

    ##############################################################################################################
    # helper methods which can be subclassed in custom hooks to fine tune the behavior of things

    def _import_clip(self, path, sg_publish_data):
        """
        Imports the given publish data into Nuke Studio or Hiero as a clip.

        :param str path: Path to the file(s) to import.
        :param dict sg_publish_data: Shotgun data dictionary with all of the standard publish
            fields.
        """
        if (
            not self.parent.engine.studio_enabled
            and not self.parent.engine.hiero_enabled
        ):
            raise Exception(
                "Importing shot clips is only supported in Hiero and Nuke Studio."
            )

        import hiero
        from hiero.core import (
            BinItem,
            MediaSource,
            Clip,
        )

        if not hiero.core.projects():
            raise Exception("An active project must exist to import clips into.")

        project = hiero.core.projects()[-1]
        bins = project.clipsBin().bins()
        media_source = MediaSource(path)
        clip = Clip(media_source)
        project.clipsBin().addItem(BinItem(clip))

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
        if ext.lower() == ".abc":
            nuke.createNode("ReadGeo2", "file {%s}" % path)
            return

        valid_extensions = [
            ".png",
            ".jpg",
            ".jpeg",
            ".exr",
            ".cin",
            ".dpx",
            ".tiff",
            ".tif",
            ".mov",
            ".mp4",
            ".psd",
            ".tga",
            ".ari",
            ".gif",
            ".iff",
        ]

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

    def _sequence_range_from_path(self, path):
        """
        Parses the file name in an attempt to determine the first and last
        frame number of a sequence. This assumes some sort of common convention
        for the file names, where the frame number is an integer at the end of
        the basename, just ahead of the file extension, such as
        file.0001.jpg, or file_001.jpg. We also check for input file names with
        abstracted frame number tokens, such as file.####.jpg, or file.%04d.jpg.

        :param str path: The file path to parse.

        :returns: None if no range could be determined, otherwise (min, max)
        :rtype: tuple or None
        """
        # This pattern will match the following at the end of a string and
        # retain the frame number or frame token as group(1) in the resulting
        # match object:
        #
        # 0001
        # ####
        # %04d
        #
        # The number of digits or hashes does not matter; we match as many as
        # exist.
        frame_pattern = re.compile(r"([0-9#]+|[%]0\dd)$")
        root, ext = os.path.splitext(path)
        match = re.search(frame_pattern, root)

        # If we did not match, we don't know how to parse the file name, or there
        # is no frame number to extract.
        if not match:
            return None

        # We need to get all files that match the pattern from disk so that we
        # can determine what the min and max frame number is.
        glob_path = "%s%s" % (
            re.sub(frame_pattern, "*", root),
            ext,
        )
        files = glob.glob(glob_path)

        # Our pattern from above matches against the file root, so we need
        # to chop off the extension at the end.
        file_roots = [os.path.splitext(f)[0] for f in files]

        # We know that the search will result in a match at this point, otherwise
        # the glob wouldn't have found the file. We can search and pull group 1
        # to get the integer frame number from the file root name.
        frames = [int(re.search(frame_pattern, f).group(1)) for f in file_roots]
        return (min(frames), max(frames))

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
            # If we don't have a template to take advantage of, then
            # we are forced to do some rough parsing ourself to try
            # to determine the frame range.
            return self._sequence_range_from_path(path)

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
