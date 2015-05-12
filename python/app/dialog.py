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
import threading

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from .ui.dialog import Ui_Dialog

from .shotgun_location import ShotgunLocation

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
        
        
        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        self._app = sgtk.platform.current_bundle()
        
        
        # entity section
        self._entity_note_model = shotgun_model.SimpleShotgunModel(self.ui.entity_note_view)
        self.ui.entity_note_view.setModel(self._entity_note_model)
        self.ui.entity_note_view.clicked.connect(self._on_note_clicked)
        
        self._entity_version_model = shotgun_model.SimpleShotgunModel(self.ui.entity_version_view)
        self.ui.entity_version_view.setModel(self._entity_version_model)
        self.ui.entity_version_view.clicked.connect(self._on_version_clicked)
        
        self._entity_publish_model = shotgun_model.SimpleShotgunModel(self.ui.entity_publish_view)
        self.ui.entity_publish_view.setModel(self._entity_publish_model)
        self.ui.entity_publish_view.clicked.connect(self._on_publish_clicked)
        
        self._entity_task_model = shotgun_model.SimpleShotgunModel(self.ui.entity_task_view)
        self.ui.entity_task_view.setModel(self._entity_task_model)
        
        self._entity_model = shotgun_model.SimpleShotgunModel(self.ui.entity_details)


        # note section
        self._note_reply_model = shotgun_model.SimpleShotgunModel(self.ui.note_reply_view)
        self.ui.note_reply_view.setModel(self._note_reply_model)

        self._note_model = shotgun_model.SimpleShotgunModel(self.ui.note_details)


        # publish details
        self._publish_publish_model = shotgun_model.SimpleShotgunModel(self.ui.publish_publish_view)
        self.ui.publish_publish_view.setModel(self._publish_publish_model)
        self.ui.publish_publish_view.clicked.connect(self._on_publish_clicked)

        self._publish_model = shotgun_model.SimpleShotgunModel(self.ui.publish_details)
        
        # version details
        self._version_note_model = shotgun_model.SimpleShotgunModel(self.ui.version_note_view)
        self.ui.version_note_view.setModel(self._version_note_model)
        self.ui.version_note_view.clicked.connect(self._on_note_clicked)

        self._version_publish_model = shotgun_model.SimpleShotgunModel(self.ui.version_publish_view)
        self.ui.version_publish_view.setModel(self._version_publish_model)
        self.ui.version_publish_view.clicked.connect(self._on_publish_clicked)
        

        self._version_model = shotgun_model.SimpleShotgunModel(self.ui.version_details)


        self.ui.navigation_home.clicked.connect(self._on_home_clicked)
        self.ui.navigation_next.clicked.connect(self._on_next_clicked)
        self.ui.navigation_prev.clicked.connect(self._on_prev_clicked)

        
        
        self._on_home_clicked()



    def focus_entity(self, entity_type, entity_id):
        """
        Move UI to entity mode. Load up tabs.
        """
        
        self.ui.page_stack.setCurrentIndex(self.ENTITY_PAGE_IDX)
        
        
        # main info
        self._entity_model.load_data(entity_type, [["id", "is", entity_id]], ["code", "description"])
        self.ui.title_label.setText("%s %s" % (entity_type, entity_id))
        
        # load data for tabs
        self._entity_note_model.load_data("Note", 
                                          [["note_links", "in", {"type": entity_type, "id": entity_id}]], 
                                          ["content"])
        
        self._entity_version_model.load_data("Version", 
                                             [["entity", "is", {"type": entity_type, "id": entity_id}]],
                                             ["code"])
        
        self._entity_publish_model.load_data("PublishedFile", 
                                             [["entity", "is", {"type": entity_type, "id": entity_id}]],
                                             ["code"])
        
        self._entity_task_model.load_data("Task", 
                                          [["entity", "is", {"type": entity_type, "id": entity_id}]],
                                          ["content"])
        
        
        
        

    def focus_note(self, note_id):
        """
        Move UI to entity mode. Load up tabs.
        """
        
        self.ui.page_stack.setCurrentIndex(self.NOTE_PAGE_IDX)
        
        # main info
        self._publish_model.load_data("Note", [["id", "is", note_id]], ["content"])
        self.ui.title_label.setText("Note %s" % note_id)
        
        # load data for tabs
        self._note_reply_model.load_data("Reply", [["entity", "is", {"type": "Note", "id": note_id}]], ["content"])
        
        

    def focus_publish(self, publish_id):
        """
        Move UI to entity mode. Load up tabs.
        """
        
        self.ui.page_stack.setCurrentIndex(self.PUBLISH_PAGE_IDX)

        # main info
        self._publish_model.load_data("PublishedFile", [["id", "is", publish_id]], ["code", "description"])
        self.ui.title_label.setText("Publish %s" % publish_id)
        
        # load data for tabs
        self._publish_publish_model.load_data("PublishedFile", 
                                              [["upstream_published_files", "is", {"type": "PublishedFile", "id": publish_id}]], 
                                              ["code"])


    def focus_version(self, version_id):
        """
        Move UI to entity mode. Load up tabs.
        """
        
        self.ui.page_stack.setCurrentIndex(self.VERSION_PAGE_IDX)

        # main info
        self._version_model.load_data("Version", [["id", "is", version_id]], ["code", "description"])
        self.ui.title_label.setText("Version %s" % version_id)
        
        # load data for tabs
        self._version_publish_model.load_data("PublishedFile", 
                                              [["version", "is",{"type": "Version", "id":version_id}]], 
                                              ["code"])

        self._entity_note_model.load_data("Note", 
                                          [["note_links", "in", {"type": "Version", "id": version_id}]], 
                                          ["content"])










    def _on_note_clicked(self, model_index):
        """
        Someone clicked a note
        """
        sg_item = shotgun_model.get_sg_data(model_index)
        sg_location = ShotgunLocation("Note", sg_item["id"])
        self._navigate_to(sg_location)
        

    def _on_publish_clicked(self, model_index):
        """
        Someone clicked a publish
        """
        sg_item = shotgun_model.get_sg_data(model_index)
        sg_location = ShotgunLocation("PublishedFile", sg_item["id"])
        self._navigate_to(sg_location)

    def _on_version_clicked(self, model_index):
        """
        Someone clicked a version
        """
        sg_item = shotgun_model.get_sg_data(model_index)
        sg_location = ShotgunLocation("Version", sg_item["id"])
        self._navigate_to(sg_location)
        
        
        
    
    
    def _navigate_to(self, shotgun_location):
        
        
        # chop off history at the point we are currently
        self._history_items = self._history_items[:self._history_index]
        # add new record
        self._history_index += 1
        self._history_items.append(shotgun_location)
        self._compute_history_button_visibility()
        shotgun_location.set_up_ui(self)
    
        
    def _compute_history_button_visibility(self):        
        self.ui.navigation_next.setEnabled(True)
        self.ui.navigation_prev.setEnabled(True)
        if self._history_index == len(self._history_items):
            self.ui.navigation_next.setEnabled(False)
        if self._history_index == 1:
            self.ui.navigation_prev.setEnabled(False)
        
    def _on_home_clicked(self):
        sg_location = ShotgunLocation("Shot", 1660)
        self._navigate_to(sg_location)
        
    def _on_next_clicked(self):
        self._app.log_debug("Next")
        self._history_index += 1
        # get the data for this guy (note: index are one based)
        sg_location = self._history_items[self._history_index-1]
        self._compute_history_button_visibility()
        sg_location.set_up_ui(self)
        
    def _on_prev_clicked(self):
        self._app.log_debug("Prev")
        self._history_index += -1
        # get the data for this guy (note: index are one based)
        sg_location = self._history_items[self._history_index-1]
        self._compute_history_button_visibility()
        sg_location.set_up_ui(self)
        

