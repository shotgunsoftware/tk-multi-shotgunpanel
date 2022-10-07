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
from sgtk.util import sgre as re
import pprint
import os
import tempfile

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
from .qtwidgets import ActivityStreamWidget
from .shotgun_formatter import ShotgunTypeFormatter
from .note_updater import NoteUpdater
from .widget_all_fields import AllFieldsWidget
from .work_area_dialog import WorkAreaDialog

shotgun_model = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_model"
)
task_manager = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "task_manager"
)
settings = sgtk.platform.import_framework("tk-framework-shotgunutils", "settings")
shotgun_data = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_data"
)
shotgun_globals = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_globals"
)

shotgun_menus = sgtk.platform.import_framework(
    "tk-framework-qtwidgets", "shotgun_menus"
)
overlay_module = sgtk.platform.import_framework(
    "tk-framework-qtwidgets", "overlay_widget"
)
shotgun_fields = sgtk.platform.import_framework(
    "tk-framework-qtwidgets", "shotgun_fields"
)
ShotgunModelOverlayWidget = overlay_module.ShotgunModelOverlayWidget
filtering = sgtk.platform.import_framework("tk-framework-qtwidgets", "filtering")
FilterMenuButton = filtering.FilterMenuButton
ShotgunFilterMenu = filtering.ShotgunFilterMenu
FilterItemProxyModel = filtering.FilterItemProxyModel

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
    NOTE_PAGE_IDX = 1

    # generic entity tabs
    ENTITY_TAB_ACTIVITY_STREAM = "activity"
    ENTITY_TAB_NOTES = "notes"
    ENTITY_TAB_VERSIONS = "versions"
    ENTITY_TAB_PUBLISHES = "publishes"
    ENTITY_TAB_PUBLISH_HISTORY = "publish_history"
    ENTITY_TAB_PUBLISH_DOWNSTREAM = "publish_downstream"
    ENTITY_TAB_PUBLISH_UPSTREAM = "publish_upstream"
    ENTITY_TAB_TASKS = "tasks"
    ENTITY_TAB_INFO = "info"
    # list of available entity tabs in order of display left to right
    ENTITY_TABS = [
        ENTITY_TAB_ACTIVITY_STREAM,
        ENTITY_TAB_NOTES,
        ENTITY_TAB_VERSIONS,
        ENTITY_TAB_PUBLISHES,
        ENTITY_TAB_PUBLISH_HISTORY,
        ENTITY_TAB_PUBLISH_DOWNSTREAM,
        ENTITY_TAB_PUBLISH_UPSTREAM,
        ENTITY_TAB_TASKS,
        ENTITY_TAB_INFO,
    ]

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
        self._action_manager.refresh_request.connect(self.refresh)

        # create a background task manager
        self._task_manager = task_manager.BackgroundTaskManager(
            self, start_processing=True, max_threads=2
        )

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

        # set up action menu. parent it to the action button to prevent cases
        # where it shows up elsewhere on screen (as in Houdini)
        self._menu = shotgun_menus.ShotgunMenu(self.ui.action_button)
        self.ui.action_button.setMenu(self._menu)

        # Last sort menu item selected, by default is sorted 'due_date'
        self._current_menu_sort_item = "due_date"
        self._current_menu_sort_order = "desc"

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
        self._publish_entity_type = sgtk.util.get_published_file_entity_type(
            self._app.sgtk
        )

        # create a settings manager where we can pull and push prefs later
        # prefs in this manager are shared
        self._settings_manager = settings.UserSettings(self._app)

        # navigation
        self.ui.navigation_home.clicked.connect(self._on_home_clicked)
        self.ui.navigation_next.clicked.connect(self._on_next_clicked)
        self.ui.navigation_prev.clicked.connect(self._on_prev_clicked)

        # search
        self.ui.search.clicked.connect(self._on_search_clicked)
        self.ui.cancel_search.clicked.connect(self._cancel_search)
        self.ui.search_input.entity_selected.connect(self._on_search_item_selected)

        # model to get the current user's details
        self._current_user_model = SgCurrentUserModel(self, self._task_manager)
        self._current_user_model.thumbnail_updated.connect(self._update_current_user)
        self._current_user_model.data_updated.connect(self._update_current_user)
        self._current_user_model.load()
        self.ui.current_user.clicked.connect(self._on_user_home_clicked)

        # top detail section
        self._details_model = SgEntityDetailsModel(self, self._task_manager)
        self._details_overlay = ShotgunModelOverlayWidget(
            self._details_model, self.ui.top_group
        )
        self._details_model.data_updated.connect(self._refresh_details)
        self._details_model.thumbnail_updated.connect(self._refresh_details_thumbnail)

        # hyperlink clicking
        self.ui.details_text_header.linkActivated.connect(self._on_link_clicked)
        self.ui.details_text_middle.linkActivated.connect(self._on_link_clicked)
        self.ui.details_thumb.playback_clicked.connect(self._playback_version)

        # notes
        self.ui.note_reply_widget.entity_requested.connect(self.navigate_to_entity)

        # build the tabs for the entity page
        self._entity_tabs = self.build_entity_tabs()
        # The current visible tabs. This will change based on the current entity type
        self._current_entity_tabs = []
        self.ui.entity_tab_widget.currentChanged.connect(self._load_entity_tab_data)

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
        self._overlay.repaint()

        try:

            # register the data fetcher with the global schema manager
            shotgun_globals.unregister_bg_task_manager(self._task_manager)

            # shut down models
            self._details_model.destroy()
            self._current_user_model.destroy()
            for tab_dict in self._entity_tabs.values():
                if tab_dict.get("model", None):
                    tab_dict["model"].destroy()

            # shut down main threadpool
            self._task_manager.shut_down()

        except Exception as e:
            self._app.log_exception("Error running SG Panel App closeEvent()")

        # close splash
        self._overlay.hide()

        # okay to close dialog
        event.accept()

    ##################################################################################################
    # load data and set up UI for a particular state

    def refresh(self, data):
        """
        Refresh the UI based on the incoming data.
        """

        if data and data.get("type", None) and data.get("id", None):
            self.navigate_to_entity(data["type"], data["id"])
        else:
            self.setup_ui()

    def setup_ui(self):
        """
        sets up the UI for the current location
        """

        if self._current_location.entity_type == "Note":
            self.focus_note()

        else:
            self.focus_entity()

        # update the details area
        self._details_model.load_data(self._current_location)

        # update the work area button
        self.ui.set_context.set_up(
            self._current_location.entity_type, self._current_location.entity_id
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
        # tab handling improved with defining ENTITY_TABS and building the tab widgets
        # dynamically instead of directly in the .ui file. Once Qt version has been
        # upgrade to >= 5.15, we can use QTabWidget::setTabVisible instead of clearing
        # and re-adding the tab widgets each time

        # Block signals emitting on the tab widget to avoid triggering unnecessary data loads
        self.ui.entity_tab_widget.blockSignals(True)

        try:
            self.ui.entity_tab_widget.clear()
            self._current_entity_tabs = []
            formatter = self._current_location.sg_formatter
            for tab_name in self.ENTITY_TABS:
                (enabled, text) = formatter.show_entity_tab(tab_name)
                if enabled:
                    tab_widget = self._entity_tabs[tab_name]["widget"]
                    self.ui.entity_tab_widget.addTab(tab_widget, text)
                    self._current_entity_tabs.append(tab_name)

                    if self._entity_tabs[tab_name].get("description", None):
                        text = formatter.get_entity_tab_description(tab_name)
                        self._entity_tabs[tab_name]["description"].setText(text)

                    if self._entity_tabs[tab_name].get("filter_checkbox", None):
                        enabled = formatter.get_tab_data(
                            tab_name, "enable_checkbox", default_value=False
                        )
                        self._entity_tabs[tab_name]["filter_checkbox"].setEnabled(
                            enabled
                        )
                        self._entity_tabs[tab_name]["filter_checkbox"].setVisible(
                            enabled
                        )

        finally:
            self.ui.entity_tab_widget.blockSignals(False)

        # get the tab index associated with the location and
        # show that tab. This means that the 'current tab' is
        # remembered as you step through history
        curr_index = self.ui.entity_tab_widget.currentIndex()

        if self._current_entity_tabs[curr_index] == self._current_location.tab:
            # we are already displaying the right tab
            # kick off a refresh
            self._load_entity_tab_data(curr_index)
        else:
            # navigate to a new tab
            # (note that the navigation will trigger the loading via a signal)
            curr_location_index = self._current_entity_tabs.index(
                self._current_location.tab
            )
            self.ui.entity_tab_widget.setCurrentIndex(curr_location_index)

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

    def _load_entity_tab_data(self, index, sort_by=None, sort_order=None):
        """
        Loads the data for one of the UI tabs in the entity family

        :param index: entity tab index to load
        """
        if index < 0 or index >= len(self._current_entity_tabs):
            # Invalid index, entity tabs may not have been set up just yet
            return

        if not self._navigating:
            self._current_location.tab = self._current_entity_tabs[index]

        tab_name = self._current_entity_tabs[index]
        tab = self._entity_tabs.get(tab_name, None)

        if tab:
            # If the tab has a view, clear the selection to avoid redrawing
            # the ui over and over
            if tab.get("view", None):
                self._entity_tabs[tab_name]["view"].selectionModel().clear()

            if tab.get("model", None):
                args = []
                kwargs = {}

                if tab_name == self.ENTITY_TAB_ACTIVITY_STREAM:
                    args = [self._current_location.entity_dict]

                elif tab_name == self.ENTITY_TAB_VERSIONS:
                    show_pending_only = (
                        tab["filter_checkbox"].isEnabled()
                        and tab["filter_checkbox"].isChecked()
                    )
                    formatter = self._current_location.sg_formatter
                    tooltip = formatter.get_tab_data(tab_name, "tooltip", None)
                    tab["model"].tooltip = tooltip
                    sort_field = formatter.get_tab_data(tab_name, "sort", "id")

                    args = [self._current_location, show_pending_only]
                    kwargs = {"sort_field": sort_field}

                elif tab_name == self.ENTITY_TAB_PUBLISHES:
                    show_latest_only = (
                        tab["filter_checkbox"].isEnabled()
                        and tab["filter_checkbox"].isChecked()
                    )
                    args = [self._current_location, show_latest_only]

                elif tab_name == self.ENTITY_TAB_TASKS:
                    formatter = self._current_location.sg_formatter
                    args = [self._current_location]
                    sort_by = (
                        sort_by if sort_by is not None else self._current_menu_sort_item
                    )
                    sort_order = (
                        sort_order
                        if sort_order is not None
                        else self._current_menu_sort_order
                    )
                    sort_field = formatter.get_tab_data(tab_name, "sort", sort_by)
                    additional_fields = ["step", "id"]
                    kwargs = {
                        "sort_field": sort_field,
                        "additional_fields": additional_fields,
                        "direction": sort_order,
                    }

                else:
                    args = [self._current_location]

                tab["model"].load_data(*args, **kwargs)

        else:
            self._app.log_error(
                "Cannot load data for unknown entity tab %s, index %s."
                % (tab_name, index)
            )

    ###################################################################################################
    # top detail area callbacks

    def _update_current_user(self):
        """
        Update the current user icon
        """
        curr_user_pixmap = self._current_user_model.get_pixmap()

        # QToolbutton needs a QIcon
        self.ui.current_user.setIcon(QtGui.QIcon(curr_user_pixmap))

        # Update the reply icon
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
            self._menu, sg_data, self._action_manager.UI_AREA_DETAILS
        )

    ###################################################################################################
    # UI callbacks
    def _on_entity_doubleclicked(self, model_index):
        """
        Someone double clicked an entity
        """
        sg_item = shotgun_model.get_sg_data(model_index)
        proceed = self._app.execute_hook_method(
            "actions_hook",
            "execute_entity_doubleclicked_action",
            sg_data=sg_item,
        )

        if proceed:
            if sg_item and sg_item.get("type") and sg_item.get("id"):
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
            self._app.log_warning(
                "Cannot play back version %s - "
                "no playback url defined." % version_data["id"]
            )

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

    def _update_note_thumbnail(self, entity):
        """
        :param entity:
        :return:
        """
        if entity["type"] != "Note":
            return

        sg_entity = self._app.shotgun.find_one(
            entity["type"], [["id", "is", entity["id"]]], ["attachments"]
        )

        # be sure to find the right attachment. The screen capture has a "screencapture_" prefix
        pixmap = None
        for a in sg_entity["attachments"]:
            if re.match(r"^screencapture_\w+.png$", a["name"]):
                pixmap = a
                break

        if not pixmap:
            return

        # download the screen capture, upload it as the Note thumbnail and finally delete it from disk
        tmp_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        self._app.shotgun.download_attachment(
            {"type": "Attachment", "id": pixmap["id"]}, tmp_path
        )
        self._app.shotgun.upload_thumbnail(entity["type"], entity["id"], tmp_path)
        os.remove(tmp_path)

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
        self._history_items = self._history_items[: self._history_index]
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
                "the SG user cannot be determined. This is often the "
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
        self._current_location = self._history_items[self._history_index - 1]
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
        self._current_location = self._history_items[self._history_index - 1]
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
                            "SG Toolkit does not know what SG user you are. "
                            "This can be due to the use of a script key for authentication "
                            "rather than using a user name and password login. To create and "
                            "assign a Task, you will need to log in using you SG user "
                            "account."
                        )
                        return

                    # create new task and assign!
                    self._app.log_debug("Resolving SG project...")
                    entity_data = self._app.shotgun.find_one(
                        entity_type, [["id", "is", entity_id]], ["project"]
                    )

                    sg_data = {
                        "content": dialog.new_task_name,
                        "step": {"type": "Step", "id": dialog.new_step_id},
                        "task_assignees": [self._app.context.user],
                        "sg_status_list": "ip",
                        "entity": {"type": entity_type, "id": entity_id},
                        "project": entity_data["project"],
                    }

                    self._app.log_debug(
                        "Creating new task:\n%s" % pprint.pprint(sg_data)
                    )
                    task_data = self._app.shotgun.create("Task", sg_data)
                    (entity_type, entity_id) = (task_data["type"], task_data["id"])

                else:
                    # user selected a task in the UI
                    (entity_type, entity_id) = dialog.selected_entity

                self._do_work_area_switch(entity_type, entity_id)

    def build_entity_tabs(self):
        """
        Build the dictionary data for each entity tab defined in `ENTITY_TABS`. The entity tab
        dictionary data:

            Required:
                'widget': the containing widget for the tab
                'entity_type': the entity type for this tab
                'has_description': indicates whether or not the tab has a description
                'has_view': indicates whether or not the tab has a view
                'has_filter': indicates whether or not the tab has a checkbox filter

            Optional:
                'description': a label to dispaly in the tab
                'filter_checkbox': a checkbox that filters the tab data

            Optional and set in method `setup_entity_model_view`:
                'view': a view to display the tab data
                'model': a data model for the view
                'model_class': the class for the tab 'model'
                'delegate': a delegate to set for the view
                'delegate_class': the class for the tab 'delegate'
                'sort_proxy': a proxy model for the 'model'
                'overlay': an overlay widget that may be used when the tab is loading, not data found, etc.

        :return: The data for each entity tab.
        :rtype: dict
        """

        tab_data = {}

        for entity_tab_name in self.ENTITY_TABS:
            tab_widget = self.create_entity_tab_widget(entity_tab_name)
            data = {
                "has_description": True,
                "has_view": True,
                "has_filter": False,
            }

            if entity_tab_name == self.ENTITY_TAB_NOTES:
                data["model_class"] = SgEntityListingModel
                data["delegate_class"] = ListItemDelegate
                data["entity_type"] = "Note"
                data["filter_fields"] = [
                    "Note.user",
                    "Note.created_at",
                    "Note.addressings_to",
                    "Note.addressings_cc",
                    "Note.tasks",
                ]

            elif entity_tab_name == self.ENTITY_TAB_TASKS:
                data["model_class"] = SgTaskListingModel
                data["delegate_class"] = ListItemDelegate
                data["entity_type"] = "Task"
                data["filter_fields"] = [
                    "Task.sg_status_list",
                    "Task.due_date",
                    "Task.tags",
                    "Task.addressings_cc",
                    "Task.task_assignees",
                    "Task.content",
                ]

            elif entity_tab_name == self.ENTITY_TAB_PUBLISH_HISTORY:
                data["model_class"] = SgPublishHistoryListingModel
                data["delegate_class"] = ListItemDelegate
                data["entity_type"] = self._publish_entity_type

            elif entity_tab_name == self.ENTITY_TAB_PUBLISH_UPSTREAM:
                data["model_class"] = SgPublishDependencyUpstreamListingModel
                data["delegate_class"] = ListItemDelegate
                data["entity_type"] = self._publish_entity_type

            elif entity_tab_name == self.ENTITY_TAB_PUBLISH_DOWNSTREAM:
                data["model_class"] = SgPublishDependencyDownstreamListingModel
                data["delegate_class"] = ListItemDelegate
                data["entity_type"] = self._publish_entity_type

            elif entity_tab_name == self.ENTITY_TAB_VERSIONS:
                data["model_class"] = SgVersionModel
                data["delegate_class"] = ListItemDelegate
                data["entity_type"] = "Version"
                data["has_filter"] = True

                # TODO handle checkbox filters more generically
                checkbox = self.create_entity_tab_checkbox(
                    entity_tab_name,
                    tab_widget,
                    "Only show versions pending review",
                )
                checked = self._settings_manager.retrieve(
                    "pending_versions_only", False
                )
                checkbox.setChecked(checked)
                checkbox.toggled.connect(self._on_pending_versions_toggled)

            elif entity_tab_name == self.ENTITY_TAB_PUBLISHES:
                data["model_class"] = SgLatestPublishListingModel
                data["delegate_class"] = ListItemDelegate
                data["entity_type"] = self._publish_entity_type
                data["has_filter"] = True

                checkbox = self.create_entity_tab_checkbox(
                    entity_tab_name, tab_widget, "Only show latest versions"
                )
                checked = self._settings_manager.retrieve("latest_publishes_only", True)
                checkbox.setChecked(checked)
                checkbox.toggled.connect(self._on_latest_publishes_toggled)

            if entity_tab_name == self.ENTITY_TAB_ACTIVITY_STREAM:
                data["has_description"] = False
                data["has_view"] = False

                activity_widget = ActivityStreamWidget(tab_widget)
                activity_widget.setObjectName("entity_activity_stream")
                activity_widget.set_bg_task_manager(self._task_manager)
                activity_widget.entity_requested.connect(self.navigate_to_entity)
                activity_widget.playback_requested.connect(self._playback_version)
                activity_widget.note_widget.entity_created.connect(
                    self._update_note_thumbnail
                )
                tab_widget.layout().addWidget(activity_widget)
                # The ActivityWStreamWidget is the model in this case (e.g. it implements the necessary
                # `load_data` method).
                data["model"] = activity_widget

            elif entity_tab_name == self.ENTITY_TAB_INFO:
                data["has_description"] = False
                data["has_view"] = False

                info_widget = AllFieldsWidget(tab_widget)
                info_widget.link_activated.connect(self._on_link_clicked)
                tab_widget.layout().addWidget(info_widget)

                model = SgAllFieldsModel(self, self._task_manager)
                model.data_updated.connect(info_widget.set_data)
                data["model"] = model

            if data["has_view"]:
                view = self.create_entity_tab_view(entity_tab_name, tab_widget)
                data["view"] = view

            # Set up the model, view and delegate for the tab. This method will modify the
            # entity data passed in with the created model, view, delegate and other necessary objects
            self.setup_entity_model_view(data)

            # Add the widgets to the layout in this order: description (QLabel),
            # view (QListView), filter (QCheckbox)
            if data["has_description"]:
                label = self.create_entity_tab_label(entity_tab_name, tab_widget)
                data["description"] = label

                # FIXME filters should be added regardless of whether there is a label or not
                data_model = data.get("model")
                proxy_model = data.get("sort_proxy")
                if (
                    data_model
                    and proxy_model
                    and hasattr(data_model, "get_entity_type")
                ):
                    # Add filtering for models
                    filter_menu = ShotgunFilterMenu(data.get("view"))
                    filter_menu.set_visible_fields(data.get("filter_fields"))
                    filter_menu.set_filter_model(proxy_model)

                    # Initialize the menu.
                    filter_menu.initialize_menu()

                    # FIXME add some buffer to the "Filter" text on the button so that it does
                    # not overlap with the menu arrow
                    filter_menu_btn = FilterMenuButton(self)
                    filter_menu_btn.setMenu(filter_menu)
                    filter_menu_btn.setStyleSheet("QToolButton {padding-right:0.5em;}")
                    data["filter_menu"] = filter_menu

                    layout = QtGui.QHBoxLayout()
                    layout.addWidget(label)
                    layout.addStretch()
                    # If is a Task entity type, add the sort menu to the layout
                    if data["entity_type"] == "Task":
                        self._sort_menu_setup(data)
                        layout.addWidget(self.sort_menu_button)
                    layout.addWidget(filter_menu_btn)
                    tab_widget.layout().addLayout(layout)
                else:
                    tab_widget.layout().addWidget(label)

            if data.get("view"):
                tab_widget.layout().addWidget(data.get("view"))

            if data["has_filter"]:
                tab_widget.layout().addWidget(checkbox)
                data["filter_checkbox"] = checkbox

            data["widget"] = tab_widget

            tab_data[entity_tab_name] = data

        return tab_data

    def create_entity_tab_widget(self, name):
        """
        Create a QWidget to be used by an entity tab.

        :param name: The name of the entity tab. This will be used to set the QWidget object name.
        :type name: str
        :return: A widget intended to be used for an entity tab.
        :rtype: :class:`sgtk.platform.qt.QtGui.QWidget`
        """

        widget = QtGui.QWidget()
        widget.setObjectName("entity_" + name + "_tab")
        vlayout = QtGui.QVBoxLayout(widget)
        vlayout.setObjectName(name + "_vlayout")
        vlayout.setContentsMargins(0, 0, 0, 0)
        return widget

    def create_entity_tab_label(self, name, parent):
        """
        Create a QLabel to be used by an entity tab.

        :param name: The name of the entity tab. This will be used to set the QLabel object name.
        :type name: str
        :param parent: The QLabel parent widget. This should be the entity tab widget.
        :type parent: :class:`sgtk.platform.qt.QtGui.QWidget`
        :return: A label intended to be used for an entity tab.
        :rtype: :class:`sgtk.platform.qt.QtGui.QLabel`
        """

        label = QtGui.QLabel(parent)
        label.setObjectName("entity_" + name + "_label")
        label.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        label.setStyleSheet(
            """
            font-size: 10px;
            font-weight: 100;
            font-style: italic;
            """
        )
        return label

    def create_entity_tab_view(self, name, parent):
        """
        Create a QListView to be used by an entity tab.

        :param name: The name of the entity tab. This will be used to set the QListView object name.
        :type name: str
        :param parent: The QListView parent widget. This should be the entity tab widget.
        :type parent: :class:`sgtk.platform.qt.QtGui.QWidget`
        :return: A view intended to be used for an entity tab.
        :rtype: :class:`sgtk.platform.qt.QtGui.QListView`
        """

        view = QtGui.QListView(parent)
        view.setObjectName("entity_" + name + "_view")
        view.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        view.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        view.setUniformItemSizes(True)
        return view

    def create_entity_tab_checkbox(self, name, parent, text=""):
        """
        Create a QCheckBox to be used by an entity tab.

        :param name: The name of the entity tab. This will be used to set the QCheckBox object name.
        :type name: str
        :param parent: The QCheckBox parent widget. This should be the entity tab widget.
        :type parent: :class:`sgtk.platform.qt.QtGui.QWidget`
        :param text: Optional text to dispaly with the checkbox. Defaults to the empty string.
        :type text: str
        :return: A checkbox intended to be used for an entity tab.
        :rtype: :class:`sgtk.platform.qt.QtGui.QCheckBox`
        """

        checkbox = QtGui.QCheckBox(text, parent)
        checkbox.setObjectName("entity_" + name + "_checkbox")
        return checkbox

    def setup_entity_model_view(self, entity_data):
        """
        Given the entity tab data, set up a model and view for the tab. This method
        will modify the `entity_data` dict passed in with the created model and view.

        :param entity_data:
        :type entity_data: dict
        :return: None
        """

        # Check for the required entity data to set up the model and view.
        if not (
            entity_data.get("model_class", None)
            and entity_data.get("delegate_class", None)
            and entity_data.get("entity_type", None)
            and entity_data.get("view", None)
        ):
            return

        ModelClass = entity_data["model_class"]
        DelegateClass = entity_data["delegate_class"]

        self._app.log_debug("Creating %r..." % ModelClass)

        # create model
        entity_data["model"] = ModelClass(
            entity_data["entity_type"], entity_data["view"], self._task_manager
        )

        # create proxy for sorting
        entity_data["sort_proxy"] = FilterItemProxyModel(self)
        entity_data["sort_proxy"].setSourceModel(entity_data["model"])

        # now use the proxy model to sort the data to ensure
        # higher version numbers appear earlier in the list
        # the history model is set up so that the default display
        # role contains the version number field in shotgun.
        # This field is what the proxy model sorts by default
        # We set the dynamic filter to true, meaning QT will keep
        # continuously sorting. And then tell it to use column 0
        # (we only have one column in our models) and descending order.
        entity_data["sort_proxy"].setDynamicSortFilter(True)

        # set up model
        entity_data["view"].setModel(entity_data["sort_proxy"])
        # set up a global on-click handler for
        entity_data["view"].doubleClicked.connect(self._on_entity_doubleclicked)
        # create delegate
        entity_data["delegate"] = DelegateClass(
            entity_data["view"], self._action_manager
        )
        entity_data["delegate"].change_work_area.connect(self._change_work_area)
        # hook up delegate renderer with view
        entity_data["view"].setItemDelegate(entity_data["delegate"])
        # and set up a spinner overlay
        entity_data["overlay"] = NotFoundModelOverlay(
            entity_data["model"], entity_data["view"]
        )

        if ModelClass == SgPublishHistoryListingModel:
            # this class needs special access to the overlay
            entity_data["model"].set_overlay(entity_data["overlay"])

    def _sort_menu_setup(self, task_tab_data):
        """
        Configure a new Menu for
        sorting the Task tab.
        :param task_tab_data:
        :type task_tab_data: dict
        :return: None
        """

        # Build the sort menu to display entity fields
        self._entity_type = task_tab_data["entity_type"]
        project_id = self._app.context.project["id"]

        self._entity_field_menu = shotgun_menus.EntityFieldMenu(
            self._entity_type,
            self,
            bg_task_manager=self._task_manager,
            project_id=project_id,
        )

        self.sort_menu_button = QtGui.QPushButton("Sort")
        self.sort_menu_button.setObjectName("sort_menu_button")
        self.sort_menu_button.setStyleSheet("border :None")

        # show the sort menu when the button is clicked
        self.sort_menu_button.clicked.connect(
            lambda: self._entity_field_menu.exec_(QtGui.QCursor.pos())
        )

        # Set the sort menu icon
        icon_path = self._switch_sort_icon()
        self.sort_menu_button.setIcon(QtGui.QIcon(icon_path))

        # the fields manager is used to query which fields are supported
        # for display. it can also be used to find out which fields are
        # visible to the user and editable by the user. the fields manager
        # needs time to initialize itself. once that's done, the widgets can
        # begin to be populated.
        fields_manager = shotgun_fields.ShotgunFieldManager(
            self, bg_task_manager=self._task_manager
        )
        fields_manager.initialized.connect(self._field_filters)
        fields_manager.initialize()
        self._sort_menu_actions()

    def _field_filters(self):

        # ---- define a few simple filter methods for use by the menu

        def field_filter(field):
            # none of the fields are included
            return False

        def checked_filter(field):
            # none of the fields are checked
            return False

        def disabled_filter(field):
            # none of the fields are disabled
            return False

        # attach the filters
        self._entity_field_menu.set_field_filter(field_filter)
        self._entity_field_menu.set_checked_filter(checked_filter)
        self._entity_field_menu.set_disabled_filter(disabled_filter)

    def _sort_menu_actions(self):
        """
        Populate the sort menu with actions.
        """

        # Create Sort Menu actions
        sort_asc = self._entity_field_menu._get_qaction("ascending", "Ascending")
        sort_desc = self._entity_field_menu._get_qaction("descending", "Descending")
        separator = self._entity_field_menu.addSeparator()
        status_action = self._entity_field_menu._get_qaction("sg_status_list", "Status")
        step_action = self._entity_field_menu._get_qaction("step", "Step")
        start_date_action = self._entity_field_menu._get_qaction(
            "start_date", "Start date"
        )
        due_date_action = self._entity_field_menu._get_qaction("due_date", "Due date")

        # Actions group list ordered
        sort_actions = [
            due_date_action,
            start_date_action,
            status_action,
            separator,
            sort_asc,
            sort_desc,
        ]

        # By default it sort Tasks due date in descending order
        sort_desc.setChecked(True)
        due_date_action.setChecked(True)
        # Menu sort order actions
        sort_asc.triggered[()].connect(
            lambda: self.load_sort_data(
                "ascending", sort_asc, sort_actions, sort_order="asc"
            )
        )
        sort_desc.triggered[()].connect(
            lambda: self.load_sort_data(
                "descending", sort_desc, sort_actions, sort_order="desc"
            )
        )
        # Menu sort field actions
        status_action.triggered[()].connect(
            lambda: self.load_sort_data("sg_status_list", status_action, sort_actions)
        )
        step_action.triggered[()].connect(
            lambda: self.load_sort_data("step", step_action, sort_actions)
        )
        start_date_action.triggered[()].connect(
            lambda: self.load_sort_data("start_date", start_date_action, sort_actions)
        )
        due_date_action.triggered[()].connect(
            lambda: self.load_sort_data("due_date", due_date_action, sort_actions)
        )
        # Add actions to the entity Menu
        self._entity_field_menu.add_group(sort_actions, "Sort menu")
        # Remove the separator from the list
        sort_actions.remove(separator)

    def load_sort_data(self, field, sort_action, actions_list, **sort_order):
        """
        Loads the data for MyTasks UI tab according to the selected
        menu sort option.

        :param field: task field string.
        :param sort_action: selected task QAction object.
        :param action_list: Dict of task QAction objects.
        :param sort_order: Selected sort order.
        """

        sort_order = (
            sort_order.get("sort_order", None)
            if sort_order
            else self._current_menu_sort_order
        )

        # Change the sort icon in the menu button according the sort direction
        icon_path = self._switch_sort_icon(sort_order)
        self.sort_menu_button.setIcon(QtGui.QIcon(icon_path))

        for action in actions_list:
            if action == sort_action:
                sort_action.setChecked(True)
            else:
                if sort_action.data().get("field", None) in ["ascending", "descending"]:
                    # If the current list element is equal to the latest field selected
                    # Check it True
                    if action.data().get("field", None) == self._current_menu_sort_item:
                        sort_action.setChecked(True)
                    else:
                        continue
                else:
                    action.setChecked(False)

        # Last menu field item selected
        field = (
            field
            if not (field in ["ascending", "descending"])
            else self._current_menu_sort_item
        )

        if field:
            self._load_entity_tab_data(
                self.ui.entity_tab_widget.currentIndex(),
                sort_by=field,
                sort_order=sort_order,
            )

        # Set checked the current sort order in the Menu
        if sort_order == "asc":
            actions_list[3].setChecked(True)
            actions_list[4].setChecked(False)
        elif sort_order == "desc":
            actions_list[4].setChecked(True)
            actions_list[3].setChecked(False)

        # Save the last menu item selected
        self._current_menu_sort_item = field
        # Save the Last sort item selected
        self._current_menu_sort_order = sort_order

    def _switch_sort_icon(self, sort_order="desc"):
        """
        Return the sort Icon path according to the sort direction
        selected.
        :param sort_order: Selected sort order, "desc" by default.
        :return: Sort icon path.
        """
        if sort_order == "asc":
            image_path = QtGui.QPixmap(
                ":/tk_multi_infopanel/icon_my_tasks_sort_asc_dark.png"
            )
        else:
            image_path = QtGui.QPixmap(
                ":/tk_multi_infopanel/icon_my_tasks_sort_desc_dark.png"
            )

        return image_path
