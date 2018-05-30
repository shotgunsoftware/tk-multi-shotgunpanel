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
import pprint

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from .ui.dialog import Ui_Dialog

from .shotgun_location import ShotgunLocation
from .delegate_list_item import ListItemDelegate
from .action_manager import ActionManager
from .model_entity_listing import SgEntityListingModel
from .model_version_listing import SgVersionModel
from .model_publish_listing import SgLatestPublishListingModel
from .model_publish_history import SgPublishHistoryListingModel
from .model_task_listing import SgTaskListingModel
from .model_publish_dependency_down import SgPublishDependencyDownstreamListingModel
from .model_publish_dependency_up import SgPublishDependencyUpstreamListingModel
from .model_all_fields import SgAllFieldsModel
from .model_details import SgEntityDetailsModel
from .model_current_user import SgCurrentUserModel
from .not_found_overlay import NotFoundModelOverlay
from .shotgun_formatter import ShotgunTypeFormatter
from .note_updater import NoteUpdater
from .work_area_dialog import WorkAreaDialog

shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
task_manager = sgtk.platform.import_framework("tk-framework-shotgunutils", "task_manager")
settings = sgtk.platform.import_framework("tk-framework-shotgunutils", "settings")
shotgun_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data")
shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")

shotgun_menus = sgtk.platform.import_framework("tk-framework-qtwidgets", "shotgun_menus")
overlay_module = sgtk.platform.import_framework("tk-framework-qtwidgets", "overlay_widget")
ShotgunModelOverlayWidget = overlay_module.ShotgunModelOverlayWidget

# maximum size of the details field in the top part of the UI
MAX_LEN_UPPER_BODY_DETAILS = 1200

# milliseconds to show splash
SPLASH_UI_TIME_MILLISECONDS = 2000

class AppDialog(QtGui.QWidget):
    """
    Main application dialog window. This defines the top level UI
    and binds all UI objects together.
    """

    # header indices
    NAVIGATION_MODE_IDX = 0
    SEARCH_MODE_IDX = 1
    
    # page indices
    ENTITY_PAGE_IDX = 0
    PUBLISH_PAGE_IDX = 1
    VERSION_PAGE_IDX = 2
    NOTE_PAGE_IDX = 3
    
    # tab indices
    ENTITY_TAB_ACTIVITY_STREAM = 0
    ENTITY_TAB_NOTES = 1
    ENTITY_TAB_VERSIONS = 2
    ENTITY_TAB_PUBLISHES = 3
    ENTITY_TAB_TASKS = 4
    ENTITY_TAB_INFO = 5
    
    PUBLISH_TAB_HISTORY = 0
    PUBLISH_TAB_CONTAINS = 1
    PUBLISH_TAB_USED_IN = 2
    PUBLISH_TAB_INFO = 3
    
    VERSION_TAB_ACTIVITY_STREAM = 0
    VERSION_TAB_NOTES = 1 
    VERSION_TAB_PUBLISHES = 2
    VERSION_TAB_INFO = 3
    
    @property
    def hide_tk_title_bar(self):
        """
        Tell the system to not show the std toolbar
        """
        return True
    
    def __init__(self, parent=None):
        """
        Constructor
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self, parent)
        
        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        self._app = sgtk.platform.current_bundle()
        
        self._action_manager = ActionManager(self)
        self._action_manager.refresh_request.connect(self.setup_ui)

        # create a background task manager
        self._task_manager = task_manager.BackgroundTaskManager(self, 
                                                                start_processing=True, 
                                                                max_threads=2)

        # register the data fetcher with the global schema manager
        shotgun_globals.register_bg_task_manager(self._task_manager)
                
        # now load in the UI that was created in the UI designer
        self.ui = Ui_Dialog() 
        self.ui.setupUi(self)

        # create a note updater to run operations on notes in the db
        self._note_updater = NoteUpdater(self._task_manager, self)

        # flag to keep track of when we are navigating
        self._navigating = False

        # hook up a data retriever with all objects needing to talk to sg
        self.ui.search_input.set_bg_task_manager(self._task_manager)
        self.ui.note_reply_widget.set_bg_task_manager(self._task_manager)    
        self.ui.entity_activity_stream.set_bg_task_manager(self._task_manager)
        self.ui.version_activity_stream.set_bg_task_manager(self._task_manager)

        # set up action menu. parent it to the action button to prevent cases
        # where it shows up elsewhere on screen (as in Houdini)
        self._menu = shotgun_menus.ShotgunMenu(self.ui.action_button)
        self.ui.action_button.setMenu(self._menu)        

        # this forces the menu to be right aligned with the button. This is
        # preferable since many DCCs show the embed panel on the far right. In
        # houdini at least, before forcing this layout direction, the menu was
        # showing up partially offscreen.
        self.ui.action_button.setLayoutDirection(QtCore.Qt.RightToLeft)
        
        # our current object we are currently displaying
        self._current_location = None
        
        # track the history
        self._history_items = []
        self._history_index = 0
        
        # overlay to show messages                        
        self._overlay = overlay_module.ShotgunOverlayWidget(self)

        # figure out which type of publish this toolkit project is using
        self._publish_entity_type = sgtk.util.get_published_file_entity_type(self._app.sgtk)

        # create a settings manager where we can pull and push prefs later
        # prefs in this manager are shared
        self._settings_manager = settings.UserSettings(self._app)
        
        # set previously stored value for "show latest"
        latest_pubs_only = self._settings_manager.retrieve("latest_publishes_only", True)
        self.ui.latest_publishes_only.setChecked(latest_pubs_only)

        # set previously stored value for "show pending"
        pending_versions_only = self._settings_manager.retrieve("pending_versions_only", False)
        self.ui.pending_versions_only.setChecked(pending_versions_only)
        
        # navigation
        self.ui.navigation_home.clicked.connect(self._on_home_clicked)
        self.ui.navigation_next.clicked.connect(self._on_next_clicked)
        self.ui.navigation_prev.clicked.connect(self._on_prev_clicked)
        
        # search
        self.ui.search.clicked.connect(self._on_search_clicked)
        self.ui.cancel_search.clicked.connect(self._cancel_search)
        self.ui.search_input.entity_selected.connect(self._on_search_item_selected)

        # latest publishes only
        self.ui.latest_publishes_only.toggled.connect(self._on_latest_publishes_toggled)
        self.ui.pending_versions_only.toggled.connect(self._on_pending_versions_toggled)
        
        # tabs
        self.ui.entity_tab_widget.currentChanged.connect(self._load_entity_tab_data)
        self.ui.version_tab_widget.currentChanged.connect(self._load_version_tab_data)
        self.ui.publish_tab_widget.currentChanged.connect(self._load_publish_tab_data)
        
        # model to get the current user's details
        self._current_user_model = SgCurrentUserModel(self, self._task_manager)        
        self._current_user_model.thumbnail_updated.connect(self._update_current_user)        
        self._current_user_model.data_updated.connect(self._update_current_user)        
        self._current_user_model.load()
        self.ui.current_user.clicked.connect(self._on_user_home_clicked)
        
        # top detail section
        self._details_model = SgEntityDetailsModel(self, self._task_manager)
        self._details_overlay = ShotgunModelOverlayWidget(self._details_model, 
                                                          self.ui.top_group)
        
        self._details_model.data_updated.connect(self._refresh_details)
        self._details_model.thumbnail_updated.connect(self._refresh_details_thumbnail)

        # hyperlink clicking
        self.ui.details_text_header.linkActivated.connect(self._on_link_clicked)
        self.ui.details_text_middle.linkActivated.connect(self._on_link_clicked)
        self.ui.details_thumb.playback_clicked.connect(self._playback_version)
        
        self.ui.note_reply_widget.entity_requested.connect(self.navigate_to_entity)
        self.ui.entity_activity_stream.entity_requested.connect(self.navigate_to_entity)
        self.ui.version_activity_stream.entity_requested.connect(self.navigate_to_entity)

        self.ui.entity_activity_stream.playback_requested.connect(self._playback_version)
        self.ui.version_activity_stream.playback_requested.connect(self._playback_version)

        
        # set up the UI tabs. Each tab has a model, a delegate, a view and 
        # an associated enity type
        
        self._detail_tabs = {}
        
        # tabs on entity view
        idx = (self.ENTITY_PAGE_IDX, self.ENTITY_TAB_NOTES)
        self._detail_tabs[idx] = {"model_class": SgEntityListingModel,
                                  "delegate_class": ListItemDelegate,
                                  "view": self.ui.entity_note_view,
                                  "entity_type": "Note"}
        
        idx = (self.ENTITY_PAGE_IDX, self.ENTITY_TAB_VERSIONS)
        self._detail_tabs[idx] = {"model_class": SgVersionModel,
                                  "delegate_class": ListItemDelegate,
                                  "view": self.ui.entity_version_view,
                                  "entity_type": "Version"}

        idx = (self.ENTITY_PAGE_IDX, self.ENTITY_TAB_PUBLISHES)
        self._detail_tabs[idx] = {"model_class": SgLatestPublishListingModel,
                                  "delegate_class": ListItemDelegate,
                                  "view": self.ui.entity_publish_view,
                                  "entity_type": self._publish_entity_type}

        idx = (self.ENTITY_PAGE_IDX, self.ENTITY_TAB_TASKS)
        self._detail_tabs[idx] = {"model_class": SgTaskListingModel,
                                  "delegate_class": ListItemDelegate,
                                  "view": self.ui.entity_task_view,
                                  "entity_type": "Task"}

        # tabs on publish view
        idx = (self.PUBLISH_PAGE_IDX, self.PUBLISH_TAB_HISTORY)
        self._detail_tabs[idx] = {"model_class": SgPublishHistoryListingModel,
                                  "delegate_class": ListItemDelegate,
                                  "view": self.ui.publish_history_view,
                                  "entity_type": self._publish_entity_type}

        idx = (self.PUBLISH_PAGE_IDX, self.PUBLISH_TAB_CONTAINS)
        self._detail_tabs[idx] = {"model_class": SgPublishDependencyDownstreamListingModel,
                                  "delegate_class": ListItemDelegate,
                                  "view": self.ui.publish_upstream_view,
                                  "entity_type": self._publish_entity_type}

        idx = (self.PUBLISH_PAGE_IDX, self.PUBLISH_TAB_USED_IN)
        self._detail_tabs[idx] = {"model_class": SgPublishDependencyUpstreamListingModel,
                                  "delegate_class": ListItemDelegate,
                                  "view": self.ui.publish_downstream_view,
                                  "entity_type": self._publish_entity_type}

        # tabs on version view
        idx = (self.VERSION_PAGE_IDX, self.VERSION_TAB_NOTES)
        self._detail_tabs[idx] = {"model_class": SgEntityListingModel,
                                  "delegate_class": ListItemDelegate,
                                  "view": self.ui.version_note_view,
                                  "entity_type": "Note"}

        idx = (self.VERSION_PAGE_IDX, self.VERSION_TAB_PUBLISHES)
        self._detail_tabs[idx] = {"model_class": SgLatestPublishListingModel,
                                  "delegate_class": ListItemDelegate,
                                  "view": self.ui.version_publish_view,
                                  "entity_type": self._publish_entity_type}

        
        # now initialize all tabs. This will add two model and delegate keys
        # to all the dicts
        
        for (idx, tab_dict) in self._detail_tabs.iteritems():
            
            ModelClass = tab_dict["model_class"]
            DelegateClass = tab_dict["delegate_class"] 
                    
            self._app.log_debug("Creating %r..." % ModelClass)
            
            # create model 
            tab_dict["model"] = ModelClass(tab_dict["entity_type"], 
                                           tab_dict["view"],
                                           self._task_manager)
                
            # create proxy for sorting
            tab_dict["sort_proxy"] = QtGui.QSortFilterProxyModel(self)
            tab_dict["sort_proxy"].setSourceModel(tab_dict["model"])
                        
            # now use the proxy model to sort the data to ensure
            # higher version numbers appear earlier in the list
            # the history model is set up so that the default display
            # role contains the version number field in shotgun.
            # This field is what the proxy model sorts by default
            # We set the dynamic filter to true, meaning QT will keep
            # continously sorting. And then tell it to use column 0
            # (we only have one column in our models) and descending order.
            tab_dict["sort_proxy"].setDynamicSortFilter(True)
            tab_dict["sort_proxy"].sort(0, QtCore.Qt.DescendingOrder)
    
            # set up model
            tab_dict["view"].setModel(tab_dict["sort_proxy"])            
            # set up a global on-click handler for
            tab_dict["view"].doubleClicked.connect(self._on_entity_doubleclicked)
            # create delegate
            tab_dict["delegate"] = DelegateClass(tab_dict["view"], self._action_manager)
            tab_dict["delegate"].change_work_area.connect(self._change_work_area)
            # hook up delegate renderer with view
            tab_dict["view"].setItemDelegate(tab_dict["delegate"])
            # and set up a spinner overlay
            tab_dict["overlay"] = NotFoundModelOverlay(tab_dict["model"], tab_dict["view"])
        
            if ModelClass == SgPublishHistoryListingModel:
                # this class needs special access to the overlay
                tab_dict["model"].set_overlay(tab_dict["overlay"])
        
        # set up the all fields tabs
        self._entity_details_model = SgAllFieldsModel(self, self._task_manager)
        self._entity_details_overlay = ShotgunModelOverlayWidget(
            self._entity_details_model,
            self.ui.entity_info_widget
        )
             
        self._entity_details_model.data_updated.connect(self.ui.entity_info_widget.set_data)
        self.ui.entity_info_widget.link_activated.connect(self._on_link_clicked)
           
        self._version_details_model = SgAllFieldsModel(self.ui.version_info_widget, self._task_manager)        
        self._version_details_model.data_updated.connect(self.ui.version_info_widget.set_data)
        self.ui.version_info_widget.link_activated.connect(self._on_link_clicked)
        
        self._publish_details_model = SgAllFieldsModel(self.ui.publish_info_widget, self._task_manager)
        self._publish_details_model.data_updated.connect(self.ui.publish_info_widget.set_data)
        self.ui.publish_info_widget.link_activated.connect(self._on_link_clicked)

        # the set work area overlay
        self.ui.set_context.change_work_area.connect(self._change_work_area)

        # kick off
        self._on_home_clicked()

        # register a startup splash screen
        splash_pix = QtGui.QPixmap(":/tk_multi_infopanel/splash.png")
        self._overlay.show_message_pixmap(splash_pix)
        QtCore.QCoreApplication.processEvents()
        QtCore.QTimer.singleShot(SPLASH_UI_TIME_MILLISECONDS, self._overlay.hide)


    def closeEvent(self, event):
        """
        Executed when the main dialog is closed.
        All worker threads and other things which need a proper shutdown
        need to be called here.
        """        
        
        self._app.log_debug("CloseEvent Received. Begin shutting down UI.")

        # tell main app instance that we are closing
        self._app._on_dialog_close(self)

        # register a shutdown overlay
        splash_pix = QtGui.QPixmap(":/tk_multi_infopanel/bye_for_now.png")
        self._overlay.show_message_pixmap(splash_pix)
        QtCore.QCoreApplication.processEvents()

        try:
            
            # register the data fetcher with the global schema manager
            shotgun_globals.unregister_bg_task_manager(self._task_manager)
                                    
            # shut down main details model
            self._details_model.destroy()
            self._current_user_model.destroy()
            
            # and the all fields model
            self._entity_details_model.destroy()
            self._version_details_model.destroy()
            self._publish_details_model.destroy()
            
            # gracefully close all tab model connections
            for tab_dict in self._detail_tabs.values():
                tab_dict["model"].destroy()            

            # shut down main threadpool
            self._task_manager.shut_down()                

        except Exception, e:
            self._app.log_exception("Error running Shotgun Panel App closeEvent()")
                
        # close splash
        self._overlay.hide()

        # okay to close dialog
        event.accept()


    ##################################################################################################
    # load data and set up UI for a particular state
    
    def setup_ui(self):
        """
        sets up the UI for the current location
        """
        if self._current_location.entity_type == "Version":
            self.focus_version()
            
        elif self._current_location.entity_type in ["PublishedFile", "TankPublishedFile"]:
            self.focus_publish()
        
        elif self._current_location.entity_type == "Note":
            self.focus_note()
        
        else:            
            self.focus_entity()

        # update the details area
        self._details_model.load_data(self._current_location)

        # update the work area button
        self.ui.set_context.set_up(
            self._current_location.entity_type,
            self._current_location.entity_id
        )
        

    def focus_entity(self):
        """
        Move UI to entity mode. Load up tabs.
        Based on the current location, focus in on the current tab
        """
        # set the right widget to show
        self.ui.page_stack.setCurrentIndex(self.ENTITY_PAGE_IDX)

        #################################################################################
        # temp tab handling! Replace with smarter, better solution!
        
        formatter = self._current_location.sg_formatter

        (enabled, caption) = formatter.show_activity_tab
        self.ui.entity_tab_widget.setTabEnabled(self.ENTITY_TAB_ACTIVITY_STREAM, enabled)
        self.ui.entity_tab_widget.setTabText(self.ENTITY_TAB_ACTIVITY_STREAM, caption)

        (enabled, caption) = formatter.show_notes_tab
        self.ui.entity_tab_widget.setTabEnabled(self.ENTITY_TAB_NOTES, enabled)
        self.ui.entity_tab_widget.setTabText(self.ENTITY_TAB_NOTES, caption)

        (enabled, caption) = formatter.show_versions_tab
        self.ui.entity_tab_widget.setTabEnabled(self.ENTITY_TAB_VERSIONS, enabled)
        self.ui.entity_tab_widget.setTabText(self.ENTITY_TAB_VERSIONS, caption)

        (enabled, caption) = formatter.show_publishes_tab
        self.ui.entity_tab_widget.setTabEnabled(self.ENTITY_TAB_PUBLISHES, enabled)
        self.ui.entity_tab_widget.setTabText(self.ENTITY_TAB_PUBLISHES, caption)

        (enabled, caption) = formatter.show_tasks_tab
        self.ui.entity_tab_widget.setTabEnabled(self.ENTITY_TAB_TASKS, enabled)
        self.ui.entity_tab_widget.setTabText(self.ENTITY_TAB_TASKS, caption)

        (enabled, caption) = formatter.show_info_tab
        self.ui.entity_tab_widget.setTabEnabled(self.ENTITY_TAB_INFO, enabled)
        self.ui.entity_tab_widget.setTabText(self.ENTITY_TAB_INFO, caption)

        # set the description
        self.ui.entity_note_label.setText(formatter.notes_description)
        self.ui.entity_task_label.setText(formatter.tasks_description)
        self.ui.entity_version_label.setText(formatter.versions_description)
        self.ui.entity_publish_label.setText(formatter.publishes_description)

        # get the tab index associated with the location and
        # show that tab. This means that the 'current tab' is
        # remembered as you step through history
        curr_index = self.ui.entity_tab_widget.currentIndex()
        if self._current_location.tab_index == curr_index:
            # we are already displaying the right tab
            # kick off a refresh
            self._load_entity_tab_data(curr_index)
        else:
            # navigate to a new tab
            # (note that the navigation will trigger the loading via a signal)
            self.ui.entity_tab_widget.setCurrentIndex(self._current_location.tab_index)


    def focus_publish(self):
        """
        Move UI to entity mode. Load up tabs.
        Based on the current location, focus in on the current tab
        """
        # set the right widget to show
        self.ui.page_stack.setCurrentIndex(self.PUBLISH_PAGE_IDX)

        # get the tab index associated with the location and
        # show that tab. This means that the 'current tab' is
        # remembered as you step through history
        tab_idx_for_location = self._current_location.tab_index
        self.ui.publish_tab_widget.setCurrentIndex(tab_idx_for_location)
        self._load_publish_tab_data(tab_idx_for_location)

    def focus_version(self):
        """
        Move UI to entity mode. Load up tabs.
        Based on the current location, focus in on the current tab
        """
        # set the right widget to show
        self.ui.page_stack.setCurrentIndex(self.VERSION_PAGE_IDX)

        # get the tab index associated with the location and
        # show that tab. This means that the 'current tab' is
        # remembered as you step through history
        tab_idx_for_location = self._current_location.tab_index
        self.ui.version_tab_widget.setCurrentIndex(tab_idx_for_location)
        self._load_version_tab_data(tab_idx_for_location)

        # set the description
        formatter = self._current_location.sg_formatter
        self.ui.version_note_label.setText(formatter.notes_description)
        self.ui.version_publish_label.setText(formatter.publishes_description)

    def focus_note(self):
        """
        Move UI to note mode. Load up tabs.
        """
        # set the right widget to show
        self.ui.page_stack.setCurrentIndex(self.NOTE_PAGE_IDX)
        # tell note reply widget to rebuild itself
        self.ui.note_reply_widget.load_data(self._current_location.entity_dict)
        # check if the note is unread and in that case mark it as read
        self._note_updater.mark_note_as_read(self._current_location.entity_id)

    ###################################################################################################
    # tab callbacks

    def _on_latest_publishes_toggled(self, checked):
        """
        Executed when the latest publishes checkbox is toggled
        
        :param checked: boolean indicating if the latest publishes box is checked.
        """
        # store setting
        self._settings_manager.store("latest_publishes_only", checked)
        
        # refresh the publishes tab
        self._load_entity_tab_data(self.ui.entity_tab_widget.currentIndex())

    def _on_pending_versions_toggled(self, checked):
        """
        Executed when the 'pending versions only' is toggled
        
        :param checked: boolean indicating if the pending versions only box is checked.
        """
        # store setting
        self._settings_manager.store("pending_versions_only", checked)
        
        # refresh the versions tab
        self._load_entity_tab_data(self.ui.entity_tab_widget.currentIndex())

    def _load_entity_tab_data(self, index):
        """
        Loads the data for one of the UI tabs in the entity family
        
        :param index: entity tab index to load
        """
        if not self._navigating:
            self._current_location.set_tab_index(index)
        
        if index == self.ENTITY_TAB_ACTIVITY_STREAM:
            self.ui.entity_activity_stream.load_data(self._current_location.entity_dict)

        elif index == self.ENTITY_TAB_NOTES:
            # clear selection to avoid redrawing the ui over and over
            self._detail_tabs[(self.ENTITY_PAGE_IDX, index)]["view"].selectionModel().clear()
            self._detail_tabs[(self.ENTITY_PAGE_IDX, index)]["model"].load_data(self._current_location)
            
        elif index == self.ENTITY_TAB_VERSIONS:
            # clear selection to avoid redrawing the ui over and over
            self._detail_tabs[(self.ENTITY_PAGE_IDX, index)]["view"].selectionModel().clear()
            show_pending_only = self.ui.pending_versions_only.isChecked()
            self._detail_tabs[(self.ENTITY_PAGE_IDX, index)]["model"].load_data(
                self._current_location,
                show_pending_only
            )
        
        elif index == self.ENTITY_TAB_PUBLISHES:
            # clear selection to avoid redrawing the ui over and over
            self._detail_tabs[(self.ENTITY_PAGE_IDX, index)]["view"].selectionModel().clear()
            show_latest_only = self.ui.latest_publishes_only.isChecked()
            self._detail_tabs[(self.ENTITY_PAGE_IDX, index)]["model"].load_data(
                self._current_location,
                show_latest_only
            )
            
        elif index == self.ENTITY_TAB_TASKS:
            # clear selection to avoid redrawing the ui over and over
            self._detail_tabs[(self.ENTITY_PAGE_IDX, index)]["view"].selectionModel().clear()
            self._detail_tabs[(self.ENTITY_PAGE_IDX, index)]["model"].load_data(self._current_location)
        
        elif index == self.ENTITY_TAB_INFO:
            self._entity_details_model.load_data(self._current_location)
        
        else:
            self._app.log_error("Cannot load data for unknown entity tab index %s." % index)
        
    def _load_version_tab_data(self, index):
        """
        Load the data for one of the tabs in the version family
        
        :param index: version tab index to load
        """
        if not self._navigating:
            self._current_location.set_tab_index(index)

        if index == self.VERSION_TAB_ACTIVITY_STREAM:
            self.ui.version_activity_stream.load_data(self._current_location.entity_dict)
        
        elif index == self.VERSION_TAB_NOTES:
            self._detail_tabs[(self.VERSION_PAGE_IDX, index)]["model"].load_data(self._current_location)

        elif index == self.VERSION_TAB_PUBLISHES:        
            self._detail_tabs[(self.VERSION_PAGE_IDX, index)]["model"].load_data(
                self._current_location,
                show_latest_only=False
            )
            
        elif index == self.VERSION_TAB_INFO:
            self._version_details_model.load_data(self._current_location)
            
        else:
            self._app.log_error("Cannot load data for unknown version tab.")
    
    def _load_publish_tab_data(self, index):
        """
        Load the data for one of the tabs in the publish family.
        
        :param index: publish tab index to load
        """
        if not self._navigating:
            self._current_location.set_tab_index(index)
        
        if index == self.PUBLISH_TAB_HISTORY:
            self._detail_tabs[(self.PUBLISH_PAGE_IDX, index)]["model"].load_data(self._current_location)

        elif index == self.PUBLISH_TAB_CONTAINS:        
            self._detail_tabs[(self.PUBLISH_PAGE_IDX, index)]["model"].load_data(self._current_location)
        
        elif index == self.PUBLISH_TAB_USED_IN:
            self._detail_tabs[(self.PUBLISH_PAGE_IDX, index)]["model"].load_data(self._current_location)
        
        elif index == self.PUBLISH_TAB_INFO:
            self._publish_details_model.load_data(self._current_location)
            
        else:
            self._app.log_error("Cannot load data for unknown publish tab.")
        

    ###################################################################################################
    # top detail area callbacks

    def _update_current_user(self):        
        """        
        Update the current user icon     
        """
        curr_user_pixmap = self._current_user_model.get_pixmap()        
                
        # QToolbutton needs a QIcon      
        self.ui.current_user.setIcon(QtGui.QIcon(curr_user_pixmap))        
                
        # updat the reply icon                
        sg_data = self._current_user_model.get_sg_data()        
        if sg_data:
            first_name = sg_data.get("firstname") or "Noname"
            self.ui.current_user.setToolTip("%s's Home" % first_name.capitalize())

    def _refresh_details_thumbnail(self):
        """
        Callback called when the details thumbnail is available
        """ 
        self.ui.details_thumb.setPixmap(self._details_model.get_pixmap())

    def _refresh_details(self):
        """
        Callback called when data for the top details section has arrived
        """
        formatter = self._current_location.sg_formatter        
        sg_data = self._details_model.get_sg_data()
        
        # set up the thumbnail
        self.ui.details_thumb.set_shotgun_data(sg_data)
        
        # populate the text with data
        if sg_data:
            (header, body) = formatter.format_entity_details(sg_data) 
            self.ui.details_text_header.setText(header)
            self.ui.details_text_header.setToolTip(header)
            
            # if the body text is extremely long, cap it forceully
            # this is so that the header portion of the UI doesn't grow
            # indefinitely
            if len(body) > MAX_LEN_UPPER_BODY_DETAILS:
                body = body[:MAX_LEN_UPPER_BODY_DETAILS]
                body += "..."
                tooltip = """<b>Capped Content</b><br>
                             The contents of this field was very long 
                             and has therefore been capped. For full details, 
                             please jump to Shotgun via the actions menu.""" 
                self.ui.details_text_middle.setToolTip(tooltip)
            
            self.ui.details_text_middle.setText(body)
            
        else:
            self.ui.details_text_header.setText("")
            self.ui.details_text_header.setToolTip("")
            self.ui.details_text_middle.setText("")
            
        # load actions
        self._action_manager.populate_menu(
            self._menu,
            sg_data,
            self._action_manager.UI_AREA_DETAILS
        )

    ###################################################################################################
    # UI callbacks
    def _on_entity_doubleclicked(self, model_index):
        """
        Someone double clicked an entity
        """
        sg_item = shotgun_model.get_sg_data(model_index)
        sg_location = ShotgunLocation(sg_item["type"], sg_item["id"])
        self._navigate_to(sg_location)

    def navigate_to_entity(self, entity_type, entity_id):
        """
        Navigate to a particular entity.
        A history entry will be created and inserted into the
        history navigation stack. 
        
        :param entity_type: Shotgun entity type
        :param entity_id: Shotgun entity id
        """
        sg_location = ShotgunLocation(entity_type, entity_id)
        if sg_location.sg_formatter.should_open_in_shotgun_web:
            sg_url = sg_location.get_external_url()
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(sg_url))            
        else:
            self._navigate_to(sg_location)
        
    def _playback_version(self, version_data):
        """
        Given version data, play back a version
        
        :param version_data: A version dictionary containing version data
        """
        url = ShotgunTypeFormatter.get_playback_url(version_data)
        if url:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
        else:
            self._app.log_warning("Cannot play back version %s - "
                                  "no playback url defined." % version_data["id"])
        
    def _on_link_clicked(self, url):
        """
        Callback called when someone clicks a url.
        
        Urls for internal navigation are on the form 'Shot:123', 
        e.g. EntityType:entity_id  
        
        :param url: Url to navigate to.
        """
        if url is None:
            return
        
        if url.startswith("sgtk:"):
            # this is an internal url on the form sgtk:EntityType:entity_id
            (_, entity_type, entity_id) = url.split(":")
            entity_id = int(entity_id)
            self.navigate_to_entity(entity_type, entity_id)            
            
        else:
            # all other links are dispatched to the OS
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
            


    ###################################################################################################
    # navigation

    def navigate_to_context(self, context):
        """
        Navigates to the given context.

        :param context: The context to navigate to.
        """
        self._navigate_to(ShotgunLocation.from_context(context))
    
    def _navigate_to(self, shotgun_location):
        """
        Update the UI to point at the given shotgun location object
        
        :param shotgun_location: Shotgun location object
        """        
        # chop off history at the point we are currently
        self._history_items = self._history_items[:self._history_index]
        # add new record
        self._history_index += 1
        self._history_items.append(shotgun_location)
        self._compute_history_button_visibility()
        
        # set the current location
        self._current_location = shotgun_location 
        self._app._log_metric_viewed_panel(shotgun_location.entity_type)

        # and set up the UI for this new location
        self._navigating = True
        try:
            self.setup_ui()
        finally:
            self._navigating = False
    
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
        
    def _on_current_user_clicked(self):
        """
        Navigates to the current user
        """
        sg_data = self._current_user_model.get_sg_link()
        sg_location = ShotgunLocation(sg_data["type"], sg_data["id"])
        self._navigate_to(sg_location)
        
    def _on_user_home_clicked(self):
        """
        Navigate to current user
        """
        sg_user_data = sgtk.util.get_current_user(self._app.sgtk)
        if sg_user_data:
            sg_location = ShotgunLocation(sg_user_data["type"], sg_user_data["id"])
            self._navigate_to(sg_location)
        else:
            self._app.log_warning(
                "Navigation to the current user is not supported when "
                "the Shotgun user cannot be determined. This is often the "
                "case when Toolkit has been authenticated using a script key "
                "rather than with a user name and password."
            )
        
    def _on_home_clicked(self):
        """
        Navigate home
        """
        sg_location = ShotgunLocation.from_context(self._app.context)
        self._navigate_to(sg_location)
        
    def _on_next_clicked(self):
        """
        Navigate to the next item in the history
        """
        self._history_index += 1
        # get the data for this guy (note: index are one based)
        self._current_location = self._history_items[self._history_index-1]
        self._compute_history_button_visibility()

        # and set up the UI for this new location
        self._navigating = True
        try:
            self.setup_ui()
        finally:
            self._navigating = False

    def _on_prev_clicked(self):
        """
        Navigate back in history
        """
        self._history_index += -1
        # get the data for this guy (note: index are one based)
        self._current_location = self._history_items[self._history_index-1]
        self._compute_history_button_visibility()

        # and set up the UI for this new location
        self._navigating = True
        try:
            self.setup_ui()
        finally:
            self._navigating = False

    def _on_search_clicked(self):
        """
        Reveals the search button
        """
        self.ui.header_stack.setCurrentIndex(self.SEARCH_MODE_IDX)
        self.ui.search_input.setFocus()

    def _cancel_search(self):
        """
        Cancels the search, resets the search and returns to
        the normal navigation
        """
        self.ui.header_stack.setCurrentIndex(self.NAVIGATION_MODE_IDX)
        self.ui.search_input.setText("")

    def _on_search_item_selected(self, entity_type, entity_id):
        """
        Navigate based on the selection in the global search
        """
        self.ui.header_stack.setCurrentIndex(self.NAVIGATION_MODE_IDX)
        self.ui.search_input.setText("")
        sg_location = ShotgunLocation(entity_type, entity_id)
        self._navigate_to(sg_location)


    ###################################################################################################
    # context switch

    def _do_work_area_switch(self, entity_type, entity_id):
        """
        Switches context and navigates to the new context.
        If the context is a task, the current user is assigned
        and the task is set to IP.

        :param entity_type: Entity type to switch to
        :param entity_id: Entity id to switch to
        """
        self._app.log_debug("Switching context to %s %s" % (entity_type, entity_id))
        ctx = self._app.sgtk.context_from_entity(entity_type, entity_id)
        sgtk.platform.change_context(ctx)
        self._on_home_clicked()


    def _change_work_area(self, entity_type, entity_id):
        """
        High level context switch ux logic.

        If the entity type is a Task, the context switch
        happens immediately.

        For all other cases, a UI is displayed, allowing
        the user to select or create a new task.

        :param entity_type: Entity type to switch to
        :param entity_id: Entity id to switch to
        """
        if entity_type == "Task":
            # for tasks, switch context directly
            self._do_work_area_switch(entity_type, entity_id)

        else:
            # display the task selection/creation UI
            dialog = WorkAreaDialog(entity_type, entity_id, self)

            # show modal
            res = dialog.exec_()

            if res == QtGui.QDialog.Accepted:

                if dialog.is_new_task:
                    # user wants to create a new task

                    # basic validation
                    if not dialog.new_task_name:
                        self._app.log_error("Please name your task!")
                        return

                    if self._app.context.user is None:
                        self._app.log_error(
                            "Shotgun Toolkit does not know what Shotgun user you are. "
                            "This can be due to the use of a script key for authentication "
                            "rather than using a user name and password login. To create and "
                            "assign a Task, you will need to log in using you Shotgun user "
                            "account."
                        )
                        return

                    # create new task and assign!
                    self._app.log_debug("Resolving shotgun project...")
                    entity_data = self._app.shotgun.find_one(
                        entity_type,
                        [["id", "is", entity_id]],
                        ["project"]
                    )

                    sg_data = {
                        "content": dialog.new_task_name,
                        "step": {"type": "Step", "id": dialog.new_step_id},
                        "task_assignees": [self._app.context.user],
                        "sg_status_list": "ip",
                        "entity": {"type": entity_type, "id": entity_id},
                        "project": entity_data["project"]
                    }

                    self._app.log_debug("Creating new task:\n%s" % pprint.pprint(sg_data))
                    task_data = self._app.shotgun.create("Task", sg_data)
                    (entity_type, entity_id) = (task_data["type"], task_data["id"])

                else:
                    # user selected a task in the UI
                    (entity_type, entity_id) = dialog.selected_entity

                self._do_work_area_switch(entity_type, entity_id)

