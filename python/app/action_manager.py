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
import sys
from sgtk.platform.qt import QtCore, QtGui
from tank_vendor import shotgun_api3
from sgtk import TankError


class ActionManager(object):
    """
    Manager class that is used to generate action menus and dispatch action
    exeuction into the various action hooks. This provides an interface between
    the action hooks, action defs in the config, and the rest ot the app.
    """
    
    # the area of the UI that an action is being requested/run for.
    UI_AREA_MAIN = 0x1
    UI_AREA_DETAILS = 0x2
    
    def __init__(self, main_dialog):
        """
        Constructor
        
        :param main_dialog: Main sg panel dialog object
        """        
        self._app = sgtk.platform.current_bundle()
        self._dialog = main_dialog
    
    def get_actions(self, sg_data, ui_area):
        """
        Returns a list of actions for an entity
        
        :param sg_data: Shotgun data for a publish
        :param ui_area: Indicates which part of the UI the request is coming from. 
                        Currently one of UI_AREA_MAIN, UI_AREA_DETAILS and UI_AREA_HISTORY
        :returns: List of QAction objects, ready to be parented to some QT Widgetry.
        """
        if sg_data is None:
            return []
        
        # check if we have logic configured to handle this
        action_defs = []
        all_mappings = self._app.get_setting("action_mappings")
        if all_mappings.get(sg_data["type"]):
            
            mappings = all_mappings[ sg_data["type"] ]

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
        actions = []
        for action_def in action_defs:
            name = action_def["name"]
            caption = action_def["caption"]
            params = action_def["params"]
            description = action_def["description"]
            
            a = QtGui.QAction(caption, None)
            a.setToolTip(description)
            a.triggered[()].connect(lambda n=name, sg=sg_data, p=params: self._execute_hook(n, sg, p))
            actions.append(a)
            
        if ui_area == self.UI_AREA_DETAILS:
            actions = self._get_default_detail_actions(sg_data) + actions
            
        return actions

    def _get_default_detail_actions(self, sg_data):
        """
        Returns a list of default actions for the detail area
        """
        refresh = QtGui.QAction("Refresh", None)
        refresh.triggered[()].connect(lambda f=sg_data: self._refresh(f))

        view_in_sg = QtGui.QAction("View in Shotgun", None)
        view_in_sg.triggered[()].connect(lambda f=sg_data: self._show_in_sg(f))

        copy_url = QtGui.QAction("Copy Shotgun url to clipboard", None)
        copy_url.triggered[()].connect(lambda f=sg_data: self._copy_to_clipboard(f))

        separator = QtGui.QAction(None)
        separator.setSeparator(True)
        
        return [refresh, view_in_sg, copy_url, separator]
    
    ########################################################################################
    # callbacks
    
    def _execute_hook(self, action_name, sg_data, params):
        """
        callback - executes a hook
        """
        self._app.log_debug("Calling scene load hook for %s. Params: %s. Sg data: %s" % (action_name, params, sg_data))
        
        try:
            self._app.execute_hook_method("actions_hook", 
                                          "execute_action", 
                                          name=action_name, 
                                          params=params, 
                                          sg_data=sg_data)
        except Exception, e:
            self._app.log_exception("Could not execute execute_action hook.")
            QtGui.QMessageBox.critical(None, "Hook Error", "Error: %s" % e)

    def _refresh(self, entity):
        """
        Internal action callback - refreshes the main dialog UI
        
        :param entity: std sg entity dict with keys type, id and name
        """
        self._dialog.setup_ui()
        
    def _show_in_sg(self, entity):
        """
        Internal action callback - Shows a shotgun entity in the web browser
        
        :param entity: std sg entity dict with keys type, id and name
        """
        url = "%s/detail/%s/%d" % (self._app.sgtk.shotgun.base_url, entity["type"], entity["id"])                    
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def _copy_to_clipboard(self, entity):
        """
        Internal action callback - Shows a shotgun entity in the web browser
        
        :param entity: std sg entity dict with keys type, id and name
        """
        url = "%s/detail/%s/%d" % (self._app.sgtk.shotgun.base_url, entity["type"], entity["id"])        
        app = QtCore.QCoreApplication.instance()
        app.clipboard().setText(url)
