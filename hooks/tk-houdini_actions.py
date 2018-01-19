# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Hook that loads defines all the available actions, broken down by publish type. 
"""
import os
import re
import sgtk

HookBaseClass = sgtk.get_hook_baseclass()


class HoudiniActions(HookBaseClass):
    """
    Shotgun Panel Actions for Maya
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

        :param sg_data: Shotgun data dictionary with all the standard shotgun fields.
        :param actions: List of action strings which have been defined in the app configuration.
        :param ui_area: String denoting the UI Area (see above).
        :returns List of dictionaries, each with keys name, params, caption and description
        """
        app = self.parent
        app.log_debug("Generate actions called for UI element %s. "
                      "Actions: %s. Publish Data: %s" % (ui_area, actions, sg_data))
        
        action_instances = []

        try:
            # call base class first
            action_instances += HookBaseClass.generate_actions(self, sg_data, actions, ui_area)
        except AttributeError, e:
            # base class doesn't have the method, so ignore and continue
            pass

        if "merge" in actions:
            action_instances.append( {"name": "merge", 
                                      "params": None,
                                      "caption": "Merge", 
                                      "description": "This will merge the item into the scene."} )        
        if "import" in actions:
            action_instances.append({
                "name": "import",
                "params": None,
                "caption": "Import",
                "description": "Import the Alembic cache file into a geometry network.",
            })

        if "file_cop" in actions:
            action_instances.append({
                "name": "file_cop",
                "params": None,
                "caption": "File COP",
                "description": "Load an image or image sequence via File COP.",
            })

        return action_instances

    def execute_action(self, name, params, sg_data):
        """
        Execute a given action. The data sent to this be method will
        represent one of the actions enumerated by the generate_actions method.
        
        :param name: Action name string representing one of the items returned by generate_actions.
        :param params: Params data, as specified by generate_actions.
        :param sg_data: Shotgun data dictionary with all the standard publish fields.
        :returns: No return value expected.
        """
        app = self.parent
        app.log_debug("Execute action called for action %s. "
                      "Parameters: %s. Publish Data: %s" % (name, params, sg_data))
        
        # resolve path
        path = self.get_publish_path(sg_data)
        
        if name == "merge":
            self._merge(path, sg_data)

        elif name == "import":
            self._import(path, sg_data)

        elif name == "file_cop":
            self._file_cop(path, sg_data)

        else:
            try:
                HookBaseClass.execute_action(self, name, params, sg_data)
            except AttributeError, e:
                # base class doesn't have the method, so ignore and continue
                pass

    ##############################################################################################################
    # helper methods which can be subclassed in custom hooks to fine tune the behaviour of things
    
    def _merge(self, path, sg_publish_data):
        """
        Merge a published hip file into the working hip file with
        the default settings Houdini would use if you did it in the UI.
        
        :param path: Path to file.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        """
        import hou

        if not os.path.exists(path):
            raise Exception("File not found on disk - '%s'" % path)
        
        # use the default settings, which tries to merge all nodes
        # and is conservative about overwriting and errors                
        
        hou.hipFile.merge(path,
                          node_pattern="*",
                          overwrite_on_conflict=False,
                          ignore_load_warnings=False) 


    ##############################################################################################################
    def _import(self, path, sg_publish_data):
        """Import the supplied path as a geo/alembic sop.
        
        :param str path: The path to the file to import.
        :param dict sg_publish_data: The publish data for the supplied path.
        
        """

        import hou
        app = self.parent

        name = sg_publish_data.get("name", "alembic")
        path = self.get_publish_path(sg_publish_data)

        # houdini doesn't like UNC paths.
        path = path.replace("\\", "/")

        obj_context = _get_current_context("/obj")

        try:
            geo_node = obj_context.createNode("geo", name)
        except hou.OperationFailed:
            # failed to create the node in this context, create at top-level
            obj_context = hou.node("/obj")
            geo_node = obj_context.createNode("geo", name)

        app.log_debug("Created geo node: %s" % (geo_node.path(),))

        # delete the default nodes created in the geo
        for child in geo_node.children():
            child.destroy()

        alembic_sop = geo_node.createNode("alembic", name)
        alembic_sop.parm("fileName").set(path)
        app.log_debug(
            "Creating alembic sop: %s\n  path: '%s' " % 
            (alembic_sop.path(), path)
        )
        alembic_sop.parm("reload").pressButton()

        _show_node(alembic_sop)

    ##############################################################################################################
    def _file_cop(self, path, sg_publish_data):
        """Read the supplied path as a file COP.

        :param str path: The path to the file to import.
        :param dict sg_publish_data: The publish data for the supplied path.

        """

        import hou
        app = self.parent

        publish_name = sg_publish_data.get("name", "published_file")

        # we'll use the publish name for the file cop node name, but we need to
        # remove non alphanumeric characers from the string (houdini node names
        # must be alphanumeric). first, build a regex to match non alpha-numeric
        # characters. Then use it to replace any matches with an underscore
        pattern = re.compile('[\W_]+', re.UNICODE)
        publish_name = pattern.sub('_', publish_name)

        # get the publish path
        path = self.get_publish_path(sg_publish_data)

        # houdini doesn't like UNC paths.
        path = path.replace("\\", "/")

        img_context = _get_current_context("/img")

        try:
            file_cop = img_context.createNode("file", publish_name)
        except hou.OperationFailed:
            # failed to create the node in the current context.
            img_context = hou.node("/img")

            comps = [c for c in img_context.children()
                     if c.type().name() == "img"]

            if comps:
                # if there are comp networks, just pick the first one
                img_network = comps[0]
            else:
                # if not, create one at the /img and then add the file cop
                img_network = img_context.createNode("img", "comp1")

            file_cop = img_network.createNode("file", publish_name)

        # replace any %0#d format string with the corresponding houdini frame
        # env variable. example %04d => $F4
        frame_pattern = re.compile("(%0(\d)d)")
        frame_match = re.search(frame_pattern, path)
        if frame_match:
            full_frame_spec = frame_match.group(1)
            padding = frame_match.group(2)
            path = path.replace(full_frame_spec, "$F%s" % (padding,))

        file_cop.parm("filename1").set(path)
        app.log_debug(
            "Created file COP: %s\n  path: '%s' " % (file_cop.path(), path))
        file_cop.parm("reload").pressButton()

        _show_node(file_cop)


##############################################################################################################
def _get_current_context(context_type):
    """Attempts to return the current node context.

    :param str context_type: Return a full context under this context type.
        Example: "/obj"

    Looks for a current network pane tab displaying the supplied context type.
    Returns the full context being displayed in that network editor.

    """

    import hou

    # default to the top level context type
    context = hou.node(context_type)

    network_tab = _get_current_network_panetab(context_type)
    if network_tab:
        context = network_tab.pwd()
    
    return context


##############################################################################################################
def _get_current_network_panetab(context_type):
    """Attempt to retrieve the current network pane tab.

    :param str context_type: Search for a network pane showing this context
        type. Example: "/obj"

    """
    
    import hou
    network_tab = None

    # there doesn't seem to be a way to know the current context "type" since
    # there could be multiple network panels open with different contexts
    # displayed. so for now, loop over pane tabs and find a network editor in
    # the specified context type that is the current tab in its pane. hopefully
    # that's the one the user is looking at.
    for panetab in hou.ui.paneTabs():
        if (isinstance(panetab, hou.NetworkEditor) and
            panetab.pwd().path().startswith(context_type) and
            panetab.isCurrentTab()):

            network_tab = panetab
            break

    return network_tab


##############################################################################################################
def _show_node(node):
    """Frame the supplied node in the current network pane.
    
    :param hou.Node node: The node to frame in the current network pane.
    
    """

    context_type = "/" + node.path().split("/")[0] 
    network_tab = _get_current_network_panetab(context_type)

    if not network_tab:
        return

    # select the node and frame it
    node.setSelected(True, clear_all_selected=True)
    network_tab.cd(node.parent().path())
    network_tab.frameSelection()

    
