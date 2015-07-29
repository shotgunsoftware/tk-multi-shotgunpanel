# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sys

from sgtk.platform.qt import QtCore, QtGui

from .ui.activity_stream_widget import Ui_ActivityStreamWidget

from .widget_loading import LoadingWidget
from .widget_new_item import NewItemWidget
from .widget_note import NoteWidget
from .widget_value_update import ValueUpdateWidget

from .data_manager import ActivityStreamDataHandler
 
class ActivityStreamWidget(QtGui.QWidget):
    """
    Widget that displays a series of replies to a note
    """
    
    MAX_STREAM_LENGTH = 40
    
    # when someone clicks a link or similar
    entity_requested = QtCore.Signal(str, int)
    playback_requested = QtCore.Signal(dict)
        
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """

        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self, parent)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_ActivityStreamWidget() 
        self.ui.setupUi(self)
        
        self._load_stylesheet()

        self.ui.activity_stream_layout.setDirection(QtGui.QBoxLayout.BottomToTop)

        self._data_manager = ActivityStreamDataHandler(self)

        self._data_manager.note_arrived.connect(self._process_new_note)
        self._data_manager.update_arrived.connect(self._process_new_data)
        self._data_manager.thumbnail_arrived.connect(self._process_thumbnail)
        
        self.ui.note_widget.data_updated.connect(self._on_note_submitted)
        
        self._loading_widget = None
        self._expanding_widget = None
        self._widgets = {}
        
        self._entity_type = None
        self._entity_id = None
        
    def set_data_retriever(self, data_retriever):
        self._data_manager.set_data_retriever(data_retriever)
        self.ui.note_widget.set_data_retriever(data_retriever)
        
    def _load_stylesheet(self):
        """
        Loads in a stylesheet from disk
        """
        qss_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.qss")
        try:
            f = open(qss_file, "rt")
            qss_data = f.read()
            # apply to widget (and all its children)
            self.setStyleSheet(qss_data)
        finally:
            f.close()
        
    def set_current_entity(self, entity_type, entity_id):
        
        self._clear()
        
        self._entity_type = entity_type
        self._entity_id = entity_id
        
        self.ui.note_widget.set_current_entity(entity_type, entity_id)

        # now load cached data
        self._data_manager.load_data(entity_type, entity_id)

        # before we begin widget operations, turn off visibility
        # of the whole widget in order to avoid recomputes
        self.setVisible(False)
        try:

            # we are building the widgets bottom up.
            # first of all, insert a widget that will expand so that 
            # it consumes all un-used space. This is to keep other
            # widgets from growing when there are only a few widgets
            # available in the scroll area.
            self._expanding_widget = QtGui.QLabel(self)
            self.ui.activity_stream_layout.addWidget(self._expanding_widget)
            self.ui.activity_stream_layout.setStretchFactor(self._expanding_widget, 1)
    
            # now process activity events
            ids_to_process = self._data_manager.get_activity_ids(self.MAX_STREAM_LENGTH)
        
            # ids are returned in async order. Now pop them onto the activity stream,
            # old items first order...
            for activity_id in ids_to_process:
                self._append_widget(activity_id)      
        
            # last, create "loading" widget
            # to put at the top of the list
            self._loading_widget = LoadingWidget(self)
            self.ui.activity_stream_layout.addWidget(self._loading_widget)
        
        finally:
            # make the window visible again and trigger a redraw
            self.setVisible(True)
        
        # and now request an update check
        self._data_manager.rescan()
    
    def reset(self):
        """
        Reset the widget
        """
        self._clear()
        
        return self.ui.note_widget.reset()
        
    def _clear(self):
        """
        Clear the widget. This will remove all items
        the UI
        """
        
        # before we begin widget operations, turn off visibility
        # of the whole widget in order to avoid recomputes        
        self.setVisible(False)
        
        try:
            self._clear_loading_widget()

            for x in self._widgets.values():
                # remove widget from layout:
                self.ui.activity_stream_layout.removeWidget(x)
                # set it's parent to None so that it is removed from the widget hierarchy
                x.setParent(None)
                # mark it to be deleted when event processing returns to the main loop
                x.deleteLater()
        
            self._widgets = {}
    
            if self._expanding_widget:
                self.ui.activity_stream_layout.removeWidget(self._expanding_widget)
                self._expanding_widget.setParent(None)
                self._expanding_widget.deleteLater()
                self._expanding_widget = None
        
        finally:
            # make the window visible again and trigger a redraw
            self.setVisible(True)
            
        
    def _clear_loading_widget(self):
        
        if self._loading_widget:
            self.ui.activity_stream_layout.removeWidget(self._loading_widget)
            self._loading_widget.setParent(None)
            self._loading_widget.deleteLater()
            self._loading_widget = None
        
    def _append_widget(self, activity_id):
        
        data = self._data_manager.get_activity_data(activity_id)
        
        if data["update_type"] == "create":
            if data["primary_entity"]["type"] != "Note":
                w = NewItemWidget(self)
            else:
                w = NoteWidget(self)
            
        elif data["update_type"] == "create_reply":
            w = NoteWidget(self)
            
        elif data["update_type"] == "update":
            w = ValueUpdateWidget(self)
        
        self.ui.activity_stream_layout.addWidget(w)
        
        # tell the widget which activity stream we
        # are placing it into
        w.set_host_entity(self._entity_type, self._entity_id)
        # add widget to our UI
        w.set_info(data)
        
        self._widgets[activity_id] = w
        
        w.entity_requested.connect(lambda entity_type, entity_id: self.entity_requested.emit(entity_type, entity_id))
        w.playback_requested.connect(lambda sg_data: self.playback_requested.emit(sg_data))
        
        # request thumbs
        self._data_manager.request_thumbnails(activity_id)
        
        return w
        
    def _process_new_data(self, activity_ids):
        
        # remove the "loading please wait .... widget
        self._clear_loading_widget()
        
        # load in the new data
        # the list of ids is delivered in ascending order
        # and we pop them on to the widget
        for activity_id in activity_ids:
            w = self._append_widget(activity_id)
            w.setStyleSheet("QFrame#frame{ border: 1px solid rgba(48, 167, 227, 50%); }")
            

    def _process_thumbnail(self, data):

        activity_id = data["activity_id"]
        thumbnail_type = data["thumbnail_type"]
        image = data["image"]
        
        if activity_id in self._widgets:
            w = self._widgets[activity_id]
            w.set_thumbnail(image, thumbnail_type)

    def _process_new_note(self, note_id):
        
        print "new note arrived! %s" % note_id

    
    def _on_note_submitted(self):
        """
        called when a note has finished submitting
        """
        # kick the data manager to rescan for changes
        self._data_manager.rescan()
