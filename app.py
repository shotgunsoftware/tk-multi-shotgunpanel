# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.


from sgtk.platform import Application

class ShotgunPanelApp(Application):
    """
    The app entry point. This class is responsible for registering 
    menu command and panel callbacks.
    """
    
    # window launch mode constants used by the navigate() method
    (PANEL, DIALOG, NEW_DIALOG) = range(3)
    
    def init_app(self):
        """
        Called as the application is being initialized
        """
        # first, we use the special import_module command to access the app module
        # that resides inside the python folder in the app. This is where the actual UI
        # and business logic of the app is kept. By using the import_module command,
        # toolkit's code reload mechanism will work properly.
        app_payload = self.import_module("app")

        # now register a panel, this is to tell the engine about the our panel ui 
        # that the engine can automatically create the panel - this happens for
        # example when a saved window layout is restored in Nuke or at startup.
        self._unique_panel_id = self.engine.register_panel(self.create_panel)
        
        # keep track of the last dialog we have created
        # in order to support the DIALOG mode for the navigate() method
        self._current_dialog = None
        
        # also register a menu entry on the shotgun menu so that users
        # can launch the panel
        self.engine.register_command("Shotgun Panel...", 
                                     self.create_panel, 
                                     {"type": "panel", 
                                      "short_name": "shotgun_panel"})
        
    def navigate(self, entity_type, entity_id, mode):
        """
        API support to start the panel and navigate to a location.
        
        Depending on the mode parameter, the window behavior may 
        differ, but the general idea is that if a panel window doesn't exist
        or isn't in focus, it is created and/or brought to front before navigating
        to the given entity. The new location is added to the existing history stack,
        allowing the user to easily move back again if needed and effectively undo 
        the programmatic navigation.
        
        The following modes exist:
        - PANEL - launch the panel as a panel. Panels are always singleton, so this will start
          the panel if it doesn't already exist. If it exists it will be given user focus. Note that
          on engines without panel support implemented, this flag will be equivalent to DIALOG
          below.
        - DIALOG - launch the panel as a dialog. A dialog may co-exist with a panel. If a dialog
          already exists, it is given focus.
        - NEW_DIALOG - launch the panel as a dialog without attempting to reuse any 
          existing dialogs that may have been created in previous calls.
        
        :param entity_type: Shotgun entity type to navigate to
        :param entity_id: Shotgun entity id 
        :param mode: PANEL, DIALOG or NEW_DIALOG
        """
        if mode == self.NEW_DIALOG:
            # always open a new window
            self.create_dialog()
            self._current_dialog.navigate_to_entity(entity_type, entity_id)
        
        elif mode == self.DIALOG:
            # show panel as dialog and reuse existing window
            if not self._current_dialog:
                self.create_dialog()
            self._current_dialog.navigate_to_entity(entity_type, entity_id)
            # bring window to front
            self._current_dialog.window().raise_()
            self._current_dialog.window().activateWindow()
        
        elif mode == self.PANEL:
            # show panel and navigate
            w = self.create_panel()
            w.navigate_to_entity(entity_type, entity_id)                
    
    def destroy_app(self):
        """
        Called as part engine shutdown
        """
        self.log_debug("Destroying app...")

    def create_panel(self):
        """
        Shows the UI as a panel. 
        Note that since panels are singletons by nature,
        calling this more than once will only result in one panel.
        
        :returns: The widget associated with the panel.
        """
        app_payload = self.import_module("app")
        
        # start the UI
        try:
            widget = self.engine.show_panel(self._unique_panel_id, "Shotgun", self, app_payload.AppDialog)
        except AttributeError, e:
            # just to gracefully handle older engines and older cores
            self.log_warning("Could not execute show_panel method - please upgrade "
                             "to latest core and engine! Falling back on show_dialog. "
                             "Error: %s" % e)
            widget = self.create_dialog()
            
        return widget

    def create_dialog(self):
        """
        Shows the panel as a dialog.
        
        Contrary to the create_panel() method, multiple calls
        to this method will result in multiple windows appearing. 
        
        :returns: The widget associated with the dialog. 
        """
        app_payload = self.import_module("app")
        widget = self.engine.show_dialog("Shotgun", self, app_payload.AppDialog)
        self._current_dialog = widget
        return widget

    def _on_dialog_close(self, dialog):
        """
        Callback called by the panel dialog whenever
        it is about to close.
        """
        if dialog == self._current_dialog:
            self._current_dialog = None
