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
from collections import defaultdict
from sgtk.platform.qt import QtCore, QtGui
from tank_vendor import shotgun_api3
from sgtk import TankError

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")

logger = sgtk.platform.get_logger(__name__)

class ActionManager(QtCore.QObject):
    """
    Manager class that is used to generate action menus and dispatch action
    execution into the various action hooks. This provides an interface between
    the action hooks, action defs in the config, and the rest of the app.
    """
    
    # emitted when the user requests a refresh via the actions system
    refresh_request = QtCore.Signal()
    
    # the area of the UI that an action is being requested/run for.
    UI_AREA_MAIN = 0x1
    UI_AREA_DETAILS = 0x2
    
    def __init__(self, parent):
        """
        Constructor
        """
        QtCore.QObject.__init__(self, parent)
        
        self._app = sgtk.platform.current_bundle()
        self._actions = []

    def populate_menu(self, shotgun_menu, sg_data, ui_area):
        """
        Populate the given shotgun menu with actions,
        organized in groups. Existing menu items will
        be cleared out and replaced with new ones.

        :param shotgun_menu: ShotgunMenu instance to operate on.
        :param sg_data: Shotgun data to generate actions for
        :param ui_area: Indicates which part of the UI the request is coming from.
                        Currently one of UI_AREA_MAIN, UI_AREA_DETAILS and UI_AREA_HISTORY
        :returns: Number of actions added
        """
        shotgun_menu.clear()
        shotgun_menu.action_handles = None
        all_actions = []

        # get built in actions
        if ui_area == self.UI_AREA_DETAILS:
            actions = self._get_default_detail_actions(sg_data)
            shotgun_menu.add_group(actions, "General")
            all_actions.extend(actions)

        # get dynamic actions
        for group_name, actions in self._get_actions(sg_data, ui_area).iteritems():
            shotgun_menu.add_group(actions, group_name)
            all_actions.extend(actions)

        # for GC purposes, store python pointers to all QActions on
        # the menu instance.
        shotgun_menu.action_handles = all_actions
        return len(all_actions)

    def _get_actions(self, sg_data, ui_area):
        """
        Returns a list of actions for an entity
        
        :param sg_data: Shotgun data
        :param ui_area: Indicates which part of the UI the request is coming from. 
                        Currently one of UI_AREA_MAIN, UI_AREA_DETAILS and UI_AREA_HISTORY
        :returns: Dict of QAction objects, keyed by group.
        """
        if sg_data is None:
            return {}
        
        # check if we have logic configured to handle this
        action_defs = []
        all_mappings = self._app.get_setting("action_mappings")

        if all_mappings.get(sg_data["type"]):
            
            mappings = all_mappings[sg_data["type"] ]

            # this is now a list of items, each a dictioary
            # with keys filters and actions
            # [{'filters': {}, 'actions': ['assign_task']}]

            # now cull out actions that don't match our filters
            actions_to_evaluate = []
            for mapping in mappings:
                actions_def = mapping["actions"]
                filters_def = mapping["filters"]
                if filters_def is None or len(filters_def) == 0:
                    # no filters to consider 
                    actions_to_evaluate.extend(actions_def)
                else:
                    # filters are on the form 
                    # field_name: value
                    for (field_name, field_value) in filters_def.iteritems():
                        
                        # resolve linked fields into a string value                        
                        sg_value = sg_data.get(field_name)
                        if isinstance(sg_value, dict):
                            sg_value = sg_value.get("name")
                        
                        # check if the filter is valid
                        if sg_value == field_value:
                            actions_to_evaluate.extend(actions_def)
                            
            if len(actions_to_evaluate) > 0:
                # no actions to run through the hook
        
                # cool so we have one or more actions
                # call out to hook to give us the specifics.
                
                # resolve UI area
                if ui_area == self.UI_AREA_DETAILS:
                    ui_area_str = "details"
                elif ui_area == self.UI_AREA_MAIN:
                    ui_area_str = "main"
                else:
                    raise TankError("Unsupported UI_AREA. Contact support.")
        
                # convert created_at unix time stamp to shotgun std time stamp
                unix_timestamp = sg_data.get("created_at")
                if unix_timestamp:
                    sg_timestamp = datetime.datetime.fromtimestamp(unix_timestamp, 
                                                                   shotgun_api3.sg_timezone.LocalTimezone())
                    sg_data["created_at"] = sg_timestamp
                            
                action_defs = []
                try:
                    action_defs = self._app.execute_hook_method("actions_hook", 
                                                                "generate_actions", 
                                                                sg_data=sg_data, 
                                                                actions=actions_to_evaluate,
                                                                ui_area=ui_area_str)
                except Exception:
                    self._app.log_exception("Could not execute generate_actions hook.")
            
        # create QActions
        default_group = "%s Actions" % shotgun_globals.get_type_display_name(sg_data["type"])
        actions = defaultdict(list)

        for action_def in action_defs:
            name = action_def["name"]
            caption = action_def["caption"]
            params = action_def["params"]
            description = action_def["description"]

            action = QtGui.QAction(caption, None)
            action.setToolTip(description)
            action.triggered[()].connect(
                lambda n=name, sg=sg_data, p=params: self._execute_hook(n, sg, p)
            )

            if "group" in action_def:
                # action belongs to a specific group
                actions[action_def["group"]].append(action)
            else:
                # put action in general group
                actions[default_group].append(action)

        return actions

    def _get_default_detail_actions(self, sg_data):
        """
        Returns a list of default actions for the detail area
        
        :param sg_data: Shotgun data directory
        """
        refresh = QtGui.QAction("Refresh", None)
        refresh.triggered[()].connect(lambda f=sg_data: self._refresh(f))

        view_in_sg = QtGui.QAction("View in Shotgun", None)
        view_in_sg.triggered[()].connect(lambda f=sg_data: self._show_in_sg(f))

        copy_url = QtGui.QAction("Copy Shotgun url to clipboard", None)
        copy_url.triggered[()].connect(lambda f=sg_data: self._copy_to_clipboard(f))

        show_docs = QtGui.QAction("Documentation", None)
        show_docs.triggered[()].connect(self._show_docs)

        separator = QtGui.QAction(None)
        separator.setSeparator(True)
        
        return [refresh, view_in_sg, copy_url, show_docs, separator]
    
    ########################################################################################
    # callbacks
    
    def _execute_hook(self, action_name, sg_data, params):
        """
        callback - executes a hook
        
        :param action_name: Name of action to execute
        :param sg_data: Shotgun data dictionary
        :param params: action parameters passed in from the hook
        """
        self._app.log_debug("Calling action hook for %s. "
                            "Params: %s. Sg data: %s" % (action_name, params, sg_data))
        
        try:
            self._app.execute_hook_method("actions_hook", 
                                          "execute_action", 
                                          name=action_name, 
                                          params=params, 
                                          sg_data=sg_data)
            
            # refresh UI
            self.refresh_request.emit()
            
        except Exception, e:
            self._app.log_exception("Could not execute execute_action hook.")
            QtGui.QMessageBox.critical(None, "Action Error", "Error: %s" % e)
        else:
            self._app._log_metric_launched_action(action_name)

    def _show_docs(self):
        """
        Internal action callback - Launch app documentation
        """        
        self._app.log_debug("Opening url %s..." % self._app.documentation_url)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(self._app.documentation_url))

    def _refresh(self, entity):
        """
        Internal action callback - refreshes the main dialog UI
        
        :param entity: std sg entity dict with keys type, id and name
        """
        self.refresh_request.emit()
        
    def _show_in_sg(self, entity):
        """
        Internal action callback - Shows a shotgun entity in the web browser
        
        :param entity: std sg entity dict with keys type, id and name
        """
        url = "%s/detail/%s/%d" % (self._app.sgtk.shotgun.base_url, entity["type"], entity["id"])                    
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def _copy_to_clipboard(self, entity):
        """
        Internal action callback - copy shotgun url to clipboard
        
        :param entity: std sg entity dict with keys type, id and name
        """
        url = "%s/detail/%s/%d" % (self._app.sgtk.shotgun.base_url, entity["type"], entity["id"])        
        app = QtCore.QCoreApplication.instance()
        app.clipboard().setText(url)
