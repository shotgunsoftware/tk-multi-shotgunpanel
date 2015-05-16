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
from .model_current_entity import SgCurrentEntityModel


shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")

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
    NOTE_PAGE_IDX = 1
    PUBLISH_PAGE_IDX = 2
    VERSION_PAGE_IDX = 3
    
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
        
        # track the history
        self._history_items = []
        self._history_index = 0
        
        
        self._default_thumb = QtGui.QPixmap(":/tk_multi_infopanel/loading_512x400.png")
        
        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        self._app = sgtk.platform.current_bundle()
        
        
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

        self._entity_model = SgCurrentEntityModel(self.ui.entity_details)
        self._entity_model.data_updated.connect(self._refresh_entity_details)
        self._entity_model.thumbnail_updated.connect(self._refresh_entity_thumbnail)


        # note section
        (model, delegate) = self._make_model(SgReplyModel, ReplyDelegate, self.ui.note_reply_view)
        self._note_reply_model = model
        self._note_reply_delegate = delegate

        self._note_model = SgCurrentEntityModel(self.ui.note_details)
        self._note_model.data_updated.connect(self._refresh_note_details)
        self._note_model.thumbnail_updated.connect(self._refresh_note_thumbnail)



        # publish details
        (model, delegate) = self._make_model(SgPublishModel, PublishDelegate, self.ui.publish_history_view)
        self._publish_history_model = model
        self._publish_history_delegate = delegate
        
        (model, delegate) = self._make_model(SgPublishModel, PublishDelegate, self.ui.publish_upstream_view)
        self._publish_upstream_model = model
        self._publish_upstream_delegate = delegate

        (model, delegate) = self._make_model(SgPublishModel, PublishDelegate, self.ui.publish_downstream_view)
        self._publish_downstream_model = model
        self._publish_downstream_delegate = delegate
        
        self._publish_model = SgCurrentEntityModel(self.ui.publish_details)
        self._publish_model.data_updated.connect(self._refresh_publish_details)
        self._publish_model.thumbnail_updated.connect(self._refresh_publish_thumbnail)

        
        # version details
        (model, delegate) = self._make_model(SgNoteModel, NoteDelegate, self.ui.version_note_view)
        self._version_note_model = model
        self._version_note_delegate = delegate
        
        (model, delegate) = self._make_model(SgPublishModel, PublishDelegate, self.ui.version_publish_view)
        self._version_publish_model = model
        self._version_publish_delegate = delegate        

        self._version_model = SgCurrentEntityModel(self.ui.version_details)
        self._version_model.data_updated.connect(self._refresh_version_details)
        self._version_model.thumbnail_updated.connect(self._refresh_version_thumbnail)



        self.ui.navigation_home.clicked.connect(self._on_home_clicked)
        self.ui.navigation_next.clicked.connect(self._on_next_clicked)
        self.ui.navigation_prev.clicked.connect(self._on_prev_clicked)

        
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


    def focus_entity(self, entity_type, entity_id):
        """
        Move UI to entity mode. Load up tabs.
        """
        
        self.ui.page_stack.setCurrentIndex(self.ENTITY_PAGE_IDX)        
        
        # main info
        fields = ["code", 
                  "description", 
                  "sg_status_list", 
                  "image"]
        
        self._entity_model.load_data(entity_type, entity_id, fields)
        
        # load data for tabs
        self._entity_note_model.load_data({"type": entity_type, "id": entity_id})
        self._entity_version_model.load_data({"type": entity_type, "id": entity_id})        
        self._entity_task_model.load_data({"type": entity_type, "id": entity_id})
        
        publish_filter = [["entity", "is", {"type": entity_type, "id": entity_id}]]
        self._entity_publish_model.load_data(publish_filter)

    def focus_note(self, note_id):
        """
        Move UI to entity mode. Load up tabs.
        """
        
        self.ui.page_stack.setCurrentIndex(self.NOTE_PAGE_IDX)
        
        # main info
        fields = ["content", 
                  "attachments", 
                  "user", 
                  "client_note", 
                  "sg_status_list", 
                  "subject",
                  "created_at", 
                  "addressings_to"]
        
        self._note_model.load_data("Note", note_id, fields)
        
        # load data for tabs
        self._note_reply_model.load_data({"type": "Note", "id": note_id})
        
        

    def focus_publish(self, publish_id):
        """
        Move UI to entity mode. Load up tabs.
        """
        
        self.ui.page_stack.setCurrentIndex(self.PUBLISH_PAGE_IDX)

        # main info
        fields = ["code", 
                  "version_number", 
                  "description", 
                  "published_file_type", 
                  "image",
                  "name", 
                  "created_by",
                  "created_at"]
        
        self._publish_model.load_data("PublishedFile", publish_id, fields)
        
        # load data for tabs
        
        # TODO: FIX
        publish_filter = [["entity", "is", {"type": "PublishedFile", "id": publish_id}]]
        self._publish_history_model.load_data(publish_filter)
        
        publish_filter = [["downstream_published_files", "in", [{"type": "PublishedFile", "id": publish_id}]]]
        self._publish_upstream_model.load_data(publish_filter)
        
        publish_filter = [["upstream_published_files", "in", [{"type": "PublishedFile", "id": publish_id}]]]
        self._publish_downstream_model.load_data(publish_filter)
        
        


    def focus_version(self, version_id):
        """
        Move UI to entity mode. Load up tabs.
        """
        
        self.ui.page_stack.setCurrentIndex(self.VERSION_PAGE_IDX)

        # main info
        fields = ["code", 
                  "sg_department", 
                  "description", 
                  "open_notes_count", 
                  "sg_status_list",
                  "image",
                  "artist",
                  "created_at", 
                  "created_by"]

        self._version_model.load_data("Version", version_id, fields)        
        
        # load data for tabs
        publish_filter = [["version", "is", [{"type": "Version", "id": version_id}]]]
        self._version_publish_model.load_data(publish_filter)
        
        
        self._entity_note_model.load_data({"type": "Version", "id": version_id})




    def _on_entity_clicked(self, model_index):
        """
        Someone clicked an entity
        """
        sg_item = shotgun_model.get_sg_data(model_index)
        sg_location = ShotgunLocation(sg_item["type"], sg_item["id"])
        self._navigate_to(sg_location)





    ###################################################################################################
    # top detail area callbacks


    def _refresh_entity_thumbnail(self):
        self.ui.entity_thumb.setPixmap(self._entity_model.get_pixmap())

    def _refresh_note_thumbnail(self):
        self.ui.note_thumb.setPixmap(self._note_model.get_pixmap())

    def _refresh_version_thumbnail(self):
        self.ui.version_thumb.setPixmap(self._version_model.get_pixmap())

    def _refresh_publish_thumbnail(self):
        self.ui.publish_thumb.setPixmap(self._publish_model.get_pixmap())

        
    def _refresh_entity_details(self):
        sg_data = self._entity_model.get_sg_data()
        
        if sg_data:
            name = sg_data.get("code") or "Unnamed"
            title = "%s %s" % (sg_data.get("type"), name)
            self.ui.entity_text_header.setText(title)
            self.ui.entity_text_bottom.setText(sg_data.get("description") or "No Description")
        
    def _refresh_note_details(self):
        sg_data = self._note_model.get_sg_data()
        

    def _refresh_publish_details(self):
        sg_data = self._publish_model.get_sg_data()

        if sg_data:

            name = sg_data.get("code") or "Unnamed"
            title = "Publish %s" % (name)
            self.ui.publish_text_header.setText(title)


            created_unixtime = sg_data.get("created_at")
            created_datetime = datetime.datetime.fromtimestamp(created_unixtime)
            (human_str, exact_str) = utils.create_human_readable_timestamp(created_datetime)
    
            user = sg_data.get("created_by")        
            
            bottom_str = "Published by <a href='%s:%s' style='text-decoration: none; color: #2C93E2'>%s</a> %s." % (user["type"], user["id"], user["name"], human_str)
            bottom_str += "<br><br><i><b>Comments:</b> %s</i>" % (sg_data.get("description") or "No comments entered.")
            
            
            self.ui.publish_text_bottom.setText(bottom_str)


    def _refresh_version_details(self):
        sg_data = self._version_model.get_sg_data()

        print sg_data
        if sg_data:

            name = sg_data.get("code") or "Unnamed"
            title = "Version %s" % (name)
            self.ui.version_text_header.setText(title)


            created_unixtime = sg_data.get("created_at")
            created_datetime = datetime.datetime.fromtimestamp(created_unixtime)
            (human_str, exact_str) = utils.create_human_readable_timestamp(created_datetime)
    
            user = sg_data.get("artist")
            if user is None:
                # fall back on created by
                user = sg_data.get("created_by")
            
            bottom_str = "Created by <a href='%s:%s' style='text-decoration: none; color: #2C93E2'>%s</a> %s." % (user["type"], user["id"], user["name"], human_str)
            bottom_str += "<br><br><i><b>Comments:</b> %s</i>" % (sg_data.get("description") or "No comments entered.")
            
            
            self.ui.version_text_bottom.setText(bottom_str)

        
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
        shotgun_location.set_up_ui(self)
    
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
        sg_location = ShotgunLocation("Shot", 1660)
        self._navigate_to(sg_location)
        
    def _on_next_clicked(self):
        """
        Navigates to the next item in the history
        """
        self._history_index += 1
        # get the data for this guy (note: index are one based)
        sg_location = self._history_items[self._history_index-1]
        self._compute_history_button_visibility()
        sg_location.set_up_ui(self)
        
    def _on_prev_clicked(self):
        """
        Navigates back in history
        """
        self._history_index += -1
        # get the data for this guy (note: index are one based)
        sg_location = self._history_items[self._history_index-1]
        self._compute_history_button_visibility()
        sg_location.set_up_ui(self)
        

