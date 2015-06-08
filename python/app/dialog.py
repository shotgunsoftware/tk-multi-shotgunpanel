# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
import tank
import os
import sys
import datetime
import threading

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from .ui.dialog import Ui_Dialog

from . import utils

from .shotgun_location import ShotgunLocation

from .delegate_list_item import ListItemDelegate

from .model_entity_listing import SgEntityListingModel
from .model_publish_listing import SgLatestPublishListingModel
from .model_publish_history import SgPublishHistoryModel
from .model_all_fields import SgAllFieldsModel
from .model_details import SgEntityDetailsModel

shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
settings = sgtk.platform.import_framework("tk-framework-shotgunutils", "settings")

def show_dialog(app_instance):
    """
    Shows the main dialog window.
    """
    # in order to handle UIs seamlessly, each toolkit engine has methods for launching
    # different types of windows. By using these methods, your windows will be correctly
    # decorated and handled in a consistent fashion by the system. 
    
    # Create and display the splash screen
    splash_pix = QtGui.QPixmap(":/res/splash.png") 
    splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    QtCore.QCoreApplication.processEvents()

    # start the UI
    app_instance.engine.show_dialog("Info Panel", app_instance, AppDialog)
    
    # attach splash screen to the main window to help GC
    w.__splash_screen = splash
    
    # hide splash screen after loader UI show
    splash.finish(w.window())
        
    
    
    
    
    
    
    


class AppDialog(QtGui.QWidget):
    """
    Main application dialog window
    """
    
    # page indices
    ENTITY_PAGE_IDX = 0
    PUBLISH_PAGE_IDX = 1
    VERSION_PAGE_IDX = 2
    NOTE_PAGE_IDX = 3
    
    # tab indices
    ENTITY_TAB_NOTES = 0
    ENTITY_TAB_VERSIONS = 1
    ENTITY_TAB_PUBLISHES = 2
    ENTITY_TAB_TASKS = 3
    ENTITY_TAB_INFO = 4
    
    PUBLISH_TAB_HISTORY = 0
    PUBLISH_TAB_CONTAINS = 1
    PUBLISH_TAB_USED_IN = 2
    
    VERSION_TAB_NOTES = 0 
    VERSION_TAB_PUBLISHES = 1
    
    
    @property
    def hide_tk_title_bar(self):
        """
        Tell the system to not show the std toolbar
        """
        return True    
    
    def __init__(self):
        """
        Constructor
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_Dialog() 
        self.ui.setupUi(self)
        
        # our current object we are currently displaying
        self._current_location = None
        
        # track the history
        self._history_items = []
        self._history_index = 0
                
        # track all model instances so that we can shut
        # them down easily later on
        self._model_instances = []
                
        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        self._app = sgtk.platform.current_bundle()

        # create a settings manager where we can pull and push prefs later
        # prefs in this manager are shared
        self._settings_manager = settings.UserSettings(self._app)
        
        # set previously stored value for "show latest"
        latest_pubs_only = self._settings_manager.retrieve("latest_publishes_only", True)
        self.ui.latest_publishes_only.setChecked(latest_pubs_only)
        
        # navigation
        self.ui.navigation_home.clicked.connect(self._on_home_clicked)
        self.ui.navigation_next.clicked.connect(self._on_next_clicked)
        self.ui.navigation_prev.clicked.connect(self._on_prev_clicked)

        # latest publishes only
        self.ui.latest_publishes_only.toggled.connect(self._on_latest_publishes_toggled)
        
        # tabs
        self.ui.entity_tab_widget.currentChanged.connect(self._load_entity_tab_data)
        self.ui.version_tab_widget.currentChanged.connect(self._load_version_tab_data)
        self.ui.publish_tab_widget.currentChanged.connect(self._load_publish_tab_data)
        
        # top detail section
        self._details_model = SgEntityDetailsModel(self.ui.details)
        self._details_model.data_updated.connect(self._refresh_details)
        self._details_model.thumbnail_updated.connect(self._refresh_details_thumbnail)

        # hyperlink clicking
        self.ui.details_text_header.linkActivated.connect(self._on_link_clicked)
        self.ui.details_text_middle.linkActivated.connect(self._on_link_clicked)
        self.ui.details_text_bottom.linkActivated.connect(self._on_link_clicked)
        self.ui.details_thumb.playback_clicked.connect(self._on_link_clicked)

        
        # entity section
        (model, delegate) = self._make_model(SgEntityListingModel, ListItemDelegate, self.ui.entity_note_view)
        self._entity_note_model = model
        self._entity_note_delegate = delegate
                
        (model, delegate) = self._make_model(SgEntityListingModel, ListItemDelegate, self.ui.entity_version_view)
        self._entity_version_model = model
        self._entity_version_delegate = delegate

        (model, delegate) = self._make_model(SgLatestPublishListingModel, ListItemDelegate, self.ui.entity_publish_view)
        self._entity_publish_model = model
        self._entity_publish_delegate = delegate
        
        (model, delegate) = self._make_model(SgEntityListingModel, ListItemDelegate, self.ui.entity_task_view)
        self._entity_task_model = model
        self._entity_task_delegate = delegate
        
        self._entity_details_model = SgAllFieldsModel(self.ui.entity_info_view)
        self._model_instances.append(self._entity_details_model)        
        self.ui.entity_info_view.setModel(self._entity_details_model.get_table_model())

        self.ui.entity_info_view.verticalHeader().hide()
        self.ui.entity_info_view.horizontalHeader().hide()


        # publish details
        (model, delegate) = self._make_model(SgPublishHistoryModel, ListItemDelegate, self.ui.publish_history_view)
        self._publish_history_model = model
        self._publish_history_delegate = delegate
        
        (model, delegate) = self._make_model(SgPublishDependencyListingModel, 
                                             ListItemDelegate, 
                                             self.ui.publish_upstream_view,
                                             direction=SgPublishDependencyListingModel.UPSTREAM)
        self._publish_upstream_model = model
        self._publish_upstream_delegate = delegate

        (model, delegate) = self._make_model(SgPublishDependencyListingModel, 
                                             ListItemDelegate, 
                                             self.ui.publish_downstream_view,
                                             direction=SgPublishDependencyListingModel.DOWNSTREAM)
        self._publish_downstream_model = model
        self._publish_downstream_delegate = delegate
        
        
        # version details
        (model, delegate) = self._make_model(SgEntityListingModel, ListItemDelegate, self.ui.version_note_view)
        self._version_note_model = model
        self._version_note_delegate = delegate
        
        (model, delegate) = self._make_model(SgEntityListingModel, ListItemDelegate, self.ui.version_publish_view)
        self._version_publish_model = model
        self._version_publish_delegate = delegate  

        # kick off
        self._on_home_clicked()


    def _make_model(self, ModelClass, DelegateClass, parent_view, **kwargs):
        """
        Helper method
        
        :returns: (model, delegate)
        """
        model = ModelClass(parent_view, **kwargs)
        parent_view.setModel(model)
        parent_view.clicked.connect(self._on_entity_clicked)
        delegate = DelegateClass(parent_view)
        parent_view.setItemDelegate(delegate)
        self._model_instances.append(model)
        return (model, delegate)



    def closeEvent(self, event):
        """
        Executed when the main dialog is closed.
        All worker threads and other things which need a proper shutdown
        need to be called here.
        """        
        # display exit splash screen
        splash_pix = QtGui.QPixmap(":/res/exit_splash.png")
        splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
        splash.setMask(splash_pix.mask())
        splash.show()
        QtCore.QCoreApplication.processEvents()

        try:
            # clear the selection in the main views. 
            # this is to avoid re-triggering selection
            # as items are being removed in the models
            #
            # TODO: might have to clear selection models here
            
            # gracefully close all connections
            for m in self._model_instances:
                m.destroy()

        except:
            self._app.log_exception("Error running Info panel App closeEvent()")

        # close splash
        splash.close()

        # okay to close dialog
        event.accept()




    ##################################################################################################
    # load data and set up UI for a particular state
    def setup_ui(self):
        """
        sets up the UI for the current location
        """
        if sg_location.family == ShotgunLocation.ENTITY_FAMILY:
            self.focus_entity()
        
        elif sg_location.family == ShotgunLocation.VERSION_FAMILY:
            self.focus_version()
            
        elif sg_location.family == ShotgunLocation.PUBLISH_FAMILY:
            self.focus_publish()
        
        elif sg_location.family == ShotgunLocation.NOTE_FAMILY:
            self.focus_note()

        else:
            self._app.log_error("Cannot set up UI for unknown item family!")

        # update the details area
        self._details_model.load_data(self._current_location)


    def focus_entity(self):
        """
        Move UI to entity mode. Load up tabs.
        """
        # set the right widget to show
        self.ui.page_stack.setCurrentIndex(self.ENTITY_PAGE_IDX)        
        
        # reset to the default tab
        self.ui.entity_tab_widget.setCurrentIndex(self.ENTITY_TAB_NOTES)
        
        # load up tab data
        self._load_entity_tab_data(self.ENTITY_TAB_NOTES)


    def focus_publish(self):
        """
        Move UI to entity mode. Load up tabs.
        """
        # set the right widget to show
        self.ui.page_stack.setCurrentIndex(self.PUBLISH_PAGE_IDX)
        
        # reset to the default tab
        self.ui.publish_tab_widget.setCurrentIndex(self.PUBLISH_TAB_HISTORY)
        
        # load up tab data
        self._load_publish_tab_data(self.PUBLISH_TAB_HISTORY)

    def focus_version(self):
        """
        Move UI to entity mode. Load up tabs.
        """
        # set the right widget to show
        self.ui.page_stack.setCurrentIndex(self.VERSION_PAGE_IDX)

        # reset to the default tab
        self.ui.version_tab_widget.setCurrentIndex(self.VERSION_TAB_NOTES)
        
        # load up tab data
        self._load_version_tab_data(self.VERSION_TAB_NOTES)
        
    def focus_note(self):
        """
        Move UI to note mode. Load up tabs.
        """
        # set the right widget to show
        self.ui.page_stack.setCurrentIndex(self.NOTE_PAGE_IDX)        
        

    ###################################################################################################
    # tab callbacks

    def _on_latest_publishes_toggled(self, checked):
        """
        Executed when the latest publishes checkbox is toggled
        """
        # store setting
        self._settings_manager.store("latest_publishes_only", checked)
        
        # refresh the publishes tab
        self._load_entity_tab_data(self.ui.entity_tab_widget.currentIndex())

    def _load_entity_tab_data(self, index):
        """
        Loads the data for one of the UI tabs in the entity family
        """        
        if index == self.ENTITY_TAB_NOTES:        
            self._entity_note_model.load_data(self._current_location)
            
        elif index == self.ENTITY_TAB_VERSIONS:
            self._entity_version_model.load_data(self._current_location)
        
        elif index == self.ENTITY_TAB_PUBLISHES:
            show_latest_only = self.ui.latest_publishes_only.isChecked()
            self._entity_publish_model.load_data(self._current_location, show_latest_only)
            
        elif index == self.ENTITY_TAB_TASKS:
            self._entity_task_model.load_data(self._current_location)
        
        elif index == self.ENTITY_TAB_INFO:
            self._entity_details_model.load_data(self._current_location)
        
        else:
            self._app.log_error("Cannot load data for unknown entity tab.")
        
        
    def _load_version_tab_data(self, index):
        """
        Load the data for one of the tabs in the version family
        """
        self._app.log_debug("Version tab clicked - index: %s" % index)

        if index == self.VERSION_TAB_NOTES:
            self._version_publish_model.load_data(self._current_location, show_latest_only=False)

        elif index == self.VERSION_TAB_PUBLISHES:        
            self._version_note_model.load_data(self._current_location)
            
        else:
            self._app.log_error("Cannot load data for unknown version tab.")
    
    
    def _load_publish_tab_data(self, index):
        """
        Load the data for one of the tabs in the publish family.
        """
        if index == self.PUBLISH_TAB_HISTORY:
            self._publish_history_model.load_data(self._current_location)

        elif index == self.PUBLISH_TAB_CONTAINS:        
            self._publish_upstream_model.load_data(self._current_location)
        
        elif index == self.PUBLISH_TAB_USED_IN:
            self._publish_downstream_model.load_data(self._current_location)
        
        else:
            self._app.log_error("Cannot load data for unknown publish tab.")
        

    ###################################################################################################
    # top detail area callbacks

    def _refresh_details_thumbnail(self):        
        self.ui.details_thumb.setPixmap(self._details_model.get_pixmap())

    def _refresh_details(self):
        
        sg_data = self._details_model.get_sg_data()                
        if sg_data:

            (header, body, footer) = self._current_location.format_entity_details(sg_data) 

            self.ui.details_text_header.setText(header)
            self.ui.details_text_middle.setText(body)
            self.ui.details_text_bottom.setText(footer)
            
        else:
            self.ui.details_text_header.setText("")
            self.ui.details_text_middle.setText("")
            self.ui.details_text_bottom.setText("")        
            
        playback_url = self._current_location.get_playback_url(sg_data)
        if playback_url:
            self.ui.details_thumb.set_playback_icon_active(True)
            self.ui.details_thumb.set_plackback_url(playback_url)
        else:
            self.ui.details_thumb.set_playback_icon_active(False)
            
            
    ###################################################################################################
    # UI callbacks

    def _on_entity_clicked(self, model_index):
        """
        Someone clicked an entity
        """
        sg_item = shotgun_model.get_sg_data(model_index)
        sg_location = ShotgunLocation(sg_item["type"], sg_item["id"])
        self._navigate_to(sg_location)


    def _on_link_clicked(self, url):
        """
        When someone clicks a url
        """
        if url is None:
            return
        
        if url.startswith("http"):
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
            
        else:
            (entity_type, entity_id) = url.split(":")
            entity_id = int(entity_id)
            
            sg_location = ShotgunLocation(entity_type, entity_id)
            if sg_location.should_open_in_shotgun_web:
                sg_url = location.get_external_url()
                QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
                                                
            else:
                self._navigate_to(sg_location)

    ###################################################################################################
    # navigation
    
    def _navigate_to(self, shotgun_location):
        """
        Update the UI to point at the given shotgun location object
        """
        
        # chop off history at the point we are currently
        self._history_items = self._history_items[:self._history_index]
        # add new record
        self._history_index += 1
        self._history_items.append(shotgun_location)
        self._compute_history_button_visibility()
        
        # set the current location
        self._current_location = shotgun_location 
        
        # and set up the UI for this new location
        self.setup_ui()
    
    def _compute_history_button_visibility(self):
        """
        Helper method which ensures history buttons are rendered correctly
        """        
        self.ui.navigation_next.setEnabled(True)
        self.ui.navigation_prev.setEnabled(True)
        if self._history_index == len(self._history_items):
            self.ui.navigation_next.setEnabled(False)
        if self._history_index == 1:
            self.ui.navigation_prev.setEnabled(False)
        
    def _on_home_clicked(self):
        """
        Navigates home
        """
        # get entity portion of context
        ctx = self._app.context
        if ctx.entity:
            sg_location = ShotgunLocation(ctx.entity["type"], ctx.entity["id"])
                    
        else:
            sg_location = ShotgunLocation(ctx.project["type"], ctx.project["id"])
            
        self._navigate_to(sg_location)
        
    def _on_next_clicked(self):
        """
        Navigates to the next item in the history
        """
        self._history_index += 1
        # get the data for this guy (note: index are one based)
        self._current_location = self._history_items[self._history_index-1]
        self._compute_history_button_visibility()

        # and set up the UI for this new location
        self.setup_ui()

        
    def _on_prev_clicked(self):
        """
        Navigates back in history
        """
        self._history_index += -1
        # get the data for this guy (note: index are one based)
        self._current_location = self._history_items[self._history_index-1]
        self._compute_history_button_visibility()

        # and set up the UI for this new location
        self.setup_ui()
        

