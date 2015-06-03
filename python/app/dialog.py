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

from .shotgun_location import create_shotgun_location

from .delegate_task import TaskDelegate
from .delegate_note import NoteDelegate
from .delegate_reply import ReplyDelegate
from .delegate_publish import PublishDelegate
from .delegate_version import VersionDelegate

from .model_note import SgNoteModel
from .model_reply import SgReplyModel
from .model_task import SgTaskModel
from .model_version import SgVersionModel
from .model_publish import SgPublishModel
from .model_publish_history import SgPublishHistoryModel
from .model_current_entity import SgCurrentEntityModel


shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
settings = sgtk.platform.import_framework("tk-framework-shotgunutils", "settings")

def show_dialog(app_instance):
    """
    Shows the main dialog window.
    """
    # in order to handle UIs seamlessly, each toolkit engine has methods for launching
    # different types of windows. By using these methods, your windows will be correctly
    # decorated and handled in a consistent fashion by the system. 
    
    # we pass the dialog class to this method and leave the actual construction
    # to be carried out by toolkit.
    app_instance.engine.show_dialog("Info Panel", app_instance, AppDialog)
    


class AppDialog(QtGui.QWidget):
    """
    Main application dialog window
    """
    
    # page indices
    ENTITY_PAGE_IDX = 0
    PUBLISH_PAGE_IDX = 1
    VERSION_PAGE_IDX = 2
    
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
        self._details_model = SgCurrentEntityModel(self.ui.details)
        self._details_model.data_updated.connect(self._refresh_details)
        self._details_model.thumbnail_updated.connect(self._refresh_details_thumbnail)


        # hyperlink clicking
        self.ui.details_text_header.linkActivated.connect(self._on_link_clicked)
        self.ui.details_text_middle.linkActivated.connect(self._on_link_clicked)
        self.ui.details_text_bottom.linkActivated.connect(self._on_link_clicked)
        self.ui.details_thumb.playback_clicked.connect(self._on_link_clicked)

        
        # entity section
        (model, delegate) = self._make_model(SgNoteModel, NoteDelegate, self.ui.entity_note_view)
        self._entity_note_model = model
        self._entity_note_delegate = delegate
                
        (model, delegate) = self._make_model(SgVersionModel, VersionDelegate, self.ui.entity_version_view)
        self._entity_version_model = model
        self._entity_version_delegate = delegate

        (model, delegate) = self._make_model(SgPublishModel, PublishDelegate, self.ui.entity_publish_view)
        self._entity_publish_model = model
        self._entity_publish_delegate = delegate
        
        (model, delegate) = self._make_model(SgTaskModel, TaskDelegate, self.ui.entity_task_view)
        self._entity_task_model = model
        self._entity_task_delegate = delegate


        # publish details
        (model, delegate) = self._make_model(SgPublishHistoryModel, PublishDelegate, self.ui.publish_history_view)
        self._publish_history_model = model
        self._publish_history_delegate = delegate
        
        (model, delegate) = self._make_model(SgPublishModel, PublishDelegate, self.ui.publish_upstream_view)
        self._publish_upstream_model = model
        self._publish_upstream_delegate = delegate

        (model, delegate) = self._make_model(SgPublishModel, PublishDelegate, self.ui.publish_downstream_view)
        self._publish_downstream_model = model
        self._publish_downstream_delegate = delegate
        
        
        # version details
        (model, delegate) = self._make_model(SgNoteModel, NoteDelegate, self.ui.version_note_view)
        self._version_note_model = model
        self._version_note_delegate = delegate
        
        (model, delegate) = self._make_model(SgPublishModel, PublishDelegate, self.ui.version_publish_view)
        self._version_publish_model = model
        self._version_publish_delegate = delegate  

        # kick off
        self._on_home_clicked()

    def _make_model(self, ModelClass, DelegateClass, parent_view):
        """
        Helper method
        
        :returns: (model, delegate)
        """
        model = ModelClass(parent_view)
        parent_view.setModel(model)
        parent_view.clicked.connect(self._on_entity_clicked)
        delegate = DelegateClass(parent_view)
        parent_view.setItemDelegate(delegate)
        return (model, delegate)


    ##################################################################################################
    # load data and set up UI for a particular state
    def setup_ui(self):
        """
        sets up the UI for the current location
        """
        if self._current_location.get_family() == ShotgunLocation.ENTITY_FAMILY:
            self.focus_entity(self._current_location)
        
        elif self._current_location.get_family() == ShotgunLocation.VERSION_FAMILY:
            self.focus_version(self._current_location)
            
        elif self._current_location.get_family() == ShotgunLocation.PUBLISH_FAMILY:
            self.focus_publish(self._current_location)
        
        else:
            self._app.log_error("Cannot set up UI for unknown item family!")

    def focus_entity(self, sg_location):
        """
        Move UI to entity mode. Load up tabs.
        """
        # set the right widget to show
        self.ui.page_stack.setCurrentIndex(self.ENTITY_PAGE_IDX)        
        
        # detail area info
        self._details_model.load_data(sg_location.entity_type, 
                                     sg_location.entity_id, 
                                     sg_location.get_fields(),
                                     sg_location.use_round_icon)
        
        # reset to the default tab
        self.ui.entity_tab_widget.setCurrentIndex(self.ENTITY_TAB_NOTES)
        self._load_entity_tab_data(self.ENTITY_TAB_NOTES)


    def focus_publish(self, sg_location):
        """
        Move UI to entity mode. Load up tabs.
        """
        self.ui.page_stack.setCurrentIndex(self.PUBLISH_PAGE_IDX)

        # main info
        self._details_model.load_data(sg_location.entity_type, 
                                     sg_location.entity_id, 
                                     sg_location.get_fields(),
                                     sg_location.use_round_icon)
        
        # reset to the default tab
        self.ui.publish_tab_widget.setCurrentIndex(self.PUBLISH_TAB_HISTORY)
        self._load_publish_tab_data(self.PUBLISH_TAB_HISTORY)
        


    def focus_version(self, sg_location):
        """
        Move UI to entity mode. Load up tabs.
        """
        self.ui.page_stack.setCurrentIndex(self.VERSION_PAGE_IDX)

        # main info
        self._details_model.load_data(sg_location.entity_type, 
                                     sg_location.entity_id, 
                                     sg_location.get_fields(),
                                     sg_location.use_round_icon)        
        
        # reset to the default tab
        self.ui.version_tab_widget.setCurrentIndex(self.VERSION_TAB_NOTES)
        self._load_version_tab_data(self.VERSION_TAB_NOTES)
        

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
        
        self._app.log_debug("Entity tab clicked - index: %s" % index)

        curr_entity_dict = self._current_location.entity_dict

        if index == self.ENTITY_TAB_NOTES:        
            self._entity_note_model.load_data(curr_entity_dict)
            
        elif index == self.ENTITY_TAB_VERSIONS:
            self._entity_version_model.load_data(curr_entity_dict)
        
        elif index == self.ENTITY_TAB_PUBLISHES:
            publish_filter = [["entity", "is", curr_entity_dict]]
            show_latest_only = self.ui.latest_publishes_only.isChecked()
            self._entity_publish_model.load_data(publish_filter, show_latest_only)
            
        elif index == self.ENTITY_TAB_TASKS:
            self._entity_task_model.load_data(curr_entity_dict)
        
        elif index == self.ENTITY_TAB_INFO:
            pass
        
        else:
            self._app.log_error("Cannot load data for unknown entity tab.")
        
        
    def _load_version_tab_data(self, index):
        """
        Load the data for one of the tabs in the version family
        """
        self._app.log_debug("Version tab clicked - index: %s" % index)

        curr_entity_dict = self._current_location.entity_dict

        if index == self.VERSION_TAB_NOTES:
            publish_filter = [["version", "is", [curr_entity_dict]]]
            self._version_publish_model.load_data(publish_filter, show_latest_only=False)

        elif index == self.VERSION_TAB_PUBLISHES:        
            self._version_note_model.load_data(curr_entity_dict)
            
        else:
            self._app.log_error("Cannot load data for unknown version tab.")
    
    
    def _load_publish_tab_data(self, index):
        """
        Load the data for one of the tabs in the publish family.
        """
        self._app.log_debug("Publish tab clicked - index: %s" % index)
        
        curr_entity_dict = self._current_location.entity_dict
        
        if index == self.PUBLISH_TAB_HISTORY:
            self._publish_history_model.load_data(curr_entity_dict)

        elif index == self.PUBLISH_TAB_CONTAINS:        
            publish_filter = [["downstream_published_files", "in", [curr_entity_dict]]]
            self._publish_upstream_model.load_data(publish_filter, show_latest_only=False)
        
        elif index == self.PUBLISH_TAB_USED_IN:
            publish_filter = [["upstream_published_files", "in", [curr_entity_dict]]]
            self._publish_downstream_model.load_data(publish_filter, show_latest_only=False)
        
        else:
            self._app.log_error("Cannot load data for unknown publish tab.")
        



    ###################################################################################################
    # top detail area callbacks

    def _refresh_details_thumbnail(self):        
        self.ui.details_thumb.setPixmap(self._details_model.get_pixmap())


    def _refresh_details(self):
        
        # first clear UI
        self.ui.details_text_header.setText("")
        self.ui.details_text_middle.setText("")
        self.ui.details_text_bottom.setText("")
        
        
        sg_data = self._details_model.get_sg_data()                
        if sg_data:
            sg_loc = create_shotgun_location(sg_data["type"], sg_data["id"])
            sg_loc.render_details(sg_data, 
                                  self.ui.details_text_header, 
                                  self.ui.details_text_middle, 
                                  self.ui.details_text_bottom)
            sg_loc.set_up_thumbnail(sg_data, self.ui.details_thumb)


    ###################################################################################################
    # UI callbacks

    def _on_entity_clicked(self, model_index):
        """
        Someone clicked an entity
        """
        sg_item = shotgun_model.get_sg_data(model_index)
        sg_location = create_shotgun_location(sg_item["type"], sg_item["id"])
        self._navigate_to(sg_location)


    def _on_link_clicked(self, url):
        """
        When someone clicks a url
        """
        self._app.log_debug("Url clicked: '%s'" % url)
        if url is None:
            return
        if url.startswith("http"):
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
            
        else:
            (entity_type, entity_id) = url.split(":")
            entity_id = int(entity_id)
            
            if entity_type == "Playlist":
                
                sg_url = sgtk.platform.current_bundle().shotgun.base_url
                proj_id = self._app.context.project["id"]
                url = "%s/page/media_center?project_id=%d&entity_type=Playlist&entity_id=%d" % (sg_url, 
                                                                                                proj_id, 
                                                                                                entity_id)
                QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
                                    
            else:
                sg_location = create_shotgun_location(entity_type, entity_id)
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
            sg_location = create_shotgun_location(ctx.entity["type"], ctx.entity["id"])
                    
        else:
            sg_location = create_shotgun_location(ctx.project["type"], ctx.project["id"])
            
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
        

