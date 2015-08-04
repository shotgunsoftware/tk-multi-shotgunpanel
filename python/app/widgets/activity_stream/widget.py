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
import sgtk

from sgtk.platform.qt import QtCore, QtGui

from .ui.activity_stream_widget import Ui_ActivityStreamWidget

from .widget_loading import LoadingWidget
from .widget_new_item import NewItemWidget, SimpleNewItemWidget
from .widget_note import NoteWidget
from .widget_value_update import ValueUpdateWidget

from .data_manager import ActivityStreamDataHandler
 
class ActivityStreamWidget(QtGui.QWidget):
    """
    Widget that displays a series of replies to a note
    """
    
    MAX_STREAM_LENGTH = 20
    
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
        self._app = sgtk.platform.current_bundle()
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_ActivityStreamWidget() 
        self.ui.setupUi(self)
        
        # apply styling
        self._load_stylesheet()

        # set insertion order into list to be bottom-up
        self.ui.activity_stream_layout.setDirection(QtGui.QBoxLayout.BottomToTop)

        # create a data manager to handle backend
        self._data_manager = ActivityStreamDataHandler(self)

        # set up signals
        self._data_manager.note_arrived.connect(self._process_new_note)
        self._data_manager.update_arrived.connect(self._process_new_data)
        self._data_manager.thumbnail_arrived.connect(self._process_thumbnail)
        self.ui.note_widget.data_updated.connect(self._on_note_submitted)
        
        # keep handles to all widgets to be nice to the GC
        self._loading_widget = None
        self._other_widgets = []
        self._widgets = {}
                
        # state management
        self._data_retriever = None
        self._entity_type = None
        self._entity_id = None
        
        
    def set_data_retriever(self, data_retriever):
        """
        Set an async data retreiver object to use with this 
        widget.
        """
        self._data_retriever = data_retriever
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
        """
        Reset the state of the widget and then load up the data
        for the given entity.
        """
        self._app.log_debug("Setting up activity stream for entity %s %s" % (entity_type, entity_id))
        # clean up everything first
        self._clear()
        
        # change the state
        self._entity_type = entity_type
        self._entity_id = entity_id
        
        # tell our "new note" widget which entity it should link up against 
        self.ui.note_widget.set_current_entity(self._entity_type, 
                                               self._entity_id)

        # now load cached data for the given entity
        self._app.log_debug("Setting up db manager....")
        self._data_manager.load_data(self._entity_type, self._entity_id)

        # get list of activity events that are already cached locally
        ids_to_process = self._data_manager.get_activity_ids(self.MAX_STREAM_LENGTH)
        self._app.log_debug("Db returned %s events" % len(ids_to_process))

        reply_users = set()
        
        # before we begin widget operations, turn off visibility
        # of the whole widget in order to avoid recomputes
        self._app.log_debug("Start building widgets based on cached data...")
        self.setVisible(False)
        try:

            # we are building the widgets bottom up.
            # first of all, insert a widget that will expand so that 
            # it consumes all un-used space. This is to keep other
            # widgets from growing when there are only a few widgets
            # available in the scroll area.
            self._app.log_debug("Adding expanding base widget...")            
            
            expanding_widget = QtGui.QLabel(self)
            self.ui.activity_stream_layout.addWidget(expanding_widget)
            self.ui.activity_stream_layout.setStretchFactor(expanding_widget, 1)
            self._other_widgets.append(expanding_widget)

            sg_stream_button = QtGui.QPushButton(self)
            sg_stream_button.setText("Click here to see the Activity stream in Shotgun.")
            sg_stream_button.setObjectName("full_shotgun_stream_button")
            sg_stream_button.setCursor(QtCore.Qt.PointingHandCursor)
            sg_stream_button.setFocusPolicy(QtCore.Qt.NoFocus)
            sg_stream_button.clicked.connect(self._load_shotgun_activity_stream)
            
            
            self.ui.activity_stream_layout.addWidget(sg_stream_button)
            self._other_widgets.append(sg_stream_button)
    
            # ids are returned in async order. Now pop them onto the activity stream,
            # old items first order...
            self._app.log_debug("Adding activity widgets...")
            for activity_id in ids_to_process:
                w = self._create_activity_widget(activity_id)      
                self._widgets[activity_id] = w
                self.ui.activity_stream_layout.addWidget(w)        
        
                # run extra init for notes
                if isinstance(w, NoteWidget):
                    data = self._data_manager.get_activity_data(activity_id)
                    note_id = data["primary_entity"]["id"]
                    self._populate_note_widget(w, activity_id, note_id)            
                    # request a list of users that have replied
                    reply_users |= w.get_reply_users()
        
            # last, create "loading" widget
            # to put at the top of the list
            self._app.log_debug("Adding loading widget...")
            self._loading_widget = LoadingWidget(self)
            self.ui.activity_stream_layout.addWidget(self._loading_widget)
        
        finally:
            # make the window visible again and trigger a redraw
            self.setVisible(True)
            self._app.log_debug("...UI building complete!")
                
        # request thumbs
        self._app.log_debug("Request thumbnails...")
        for activity_id in ids_to_process:
            self._data_manager.request_activity_thumbnails(activity_id)
        
        for (entity_type, entity_id) in reply_users:
            self._data_manager.request_user_thumbnail(entity_type, entity_id)
        
        self._app.log_debug("...done")
        
        
        
        # and now request an update check
        self._app.log_debug("Ask db manager to ask shotgun for updates...")
        self._data_manager.rescan()
        self._app.log_debug("...done")
        
    
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
        self._app.log_debug("Clearing UI...")
        # before we begin widget operations, turn off visibility
        # of the whole widget in order to avoid recomputes        
        self.setVisible(False)
        
        try:
            self._app.log_debug("Clear loading widget")
            self._clear_loading_widget()

            self._app.log_debug("Removing all widget items")
            for x in self._widgets.values():
                # remove widget from layout:
                self.ui.activity_stream_layout.removeWidget(x)
                # set it's parent to None so that it is removed from the widget hierarchy
                x.setParent(None)
                # mark it to be deleted when event processing returns to the main loop
                x.deleteLater()
        
            self._app.log_debug("Clearing python data structures")
            self._widgets = {}
    
            self._app.log_debug("Removing expanding widget")
            for w in self._other_widgets:
                self.ui.activity_stream_layout.removeWidget(w)
                w.setParent(None)
                w.deleteLater()
            self._other_widgets = []
        
        finally:
            # make the window visible again and trigger a redraw
            self.setVisible(True)
            
    def _clear_loading_widget(self):
        """
        Remove the loading widget from the widget list
        """
        if self._loading_widget:
            self._app.log_debug("Cleaning the loading widget")
            self.ui.activity_stream_layout.removeWidget(self._loading_widget)
            self._loading_widget.setParent(None)
            self._loading_widget.deleteLater()
            self._loading_widget = None
            self._app.log_debug("...done")
        
    def _populate_note_widget(self, activity_widget, activity_id, note_id):
        """
        Load note content and replies into a note widget
        """
        # set note content            
        note_thread_data = self._data_manager.get_note(note_id)
        if note_thread_data:
            # we have cached note data
            note_data = note_thread_data[0]
            replies_and_attachments = note_thread_data[1:] 
            
            # set up the note data first
            activity_widget.set_note_info(note_data)
            
            # now add replies
            attachment_group_ids = activity_widget.add_replies(replies_and_attachments)
            
            # finally hook up expand events on the attachmen groups to a callback
            for attachment_group_id in attachment_group_ids:
                attachment_group_widget = activity_widget.get_attachment_group_widget(attachment_group_id)
                attachment_group_widget.expanded.connect(lambda : self._on_attachment_group_expanded(activity_id, attachment_group_id))
        
            # lastly, add a reply button
            reply_button = activity_widget.add_reply_button()
            # connect reply click
            reply_button.clicked.connect(lambda : self._on_reply_clicked(note_id))
        
        
    def _create_activity_widget(self, activity_id):
        """
        Create a widget for a given activity id
        """
        data = self._data_manager.get_activity_data(activity_id)
        
        # factory logic
        if data["update_type"] == "create":
            
            if data["primary_entity"]["type"] in ["Version", "PublishedFile", "TankPublishedFile"]:
                # full on 'new item' widget with thumbnail, description etc.
                w = NewItemWidget(self)
            
            elif data["primary_entity"]["type"] == "Note":
                # new note
                w = NoteWidget(self)
                
            else:
                # minimalistic 'new' widget for all other cases
                w = SimpleNewItemWidget(self)
                            
        elif data["update_type"] == "create_reply":
            w = NoteWidget(self)
            
        elif data["update_type"] == "update":
            w = ValueUpdateWidget(self)
        
        # initialize the widget
        w.set_host_entity(self._entity_type, self._entity_id)
        w.set_info(data)
        w.entity_requested.connect(lambda entity_type, entity_id: self.entity_requested.emit(entity_type, entity_id))
        w.playback_requested.connect(lambda sg_data: self.playback_requested.emit(sg_data))
                    
        return w
        
    def _process_new_data(self, activity_ids):
        """
        New activity items have arrived from from the data manager
        """
        self._app.log_debug("Process new data slot called for %s events" % len(activity_ids))
        # remove the "loading please wait .... widget
        self._clear_loading_widget()
        
        reply_users = set()
        
        # load in the new data
        # the list of ids is delivered in ascending order
        # and we pop them on to the widget
        for activity_id in activity_ids:
            self._app.log_debug("Creating new widget...")
            w = self._create_activity_widget(activity_id)
            
            # run extra init for notes
            if isinstance(w, NoteWidget):
                data = self._data_manager.get_activity_data(activity_id)
                note_id = data["primary_entity"]["id"]
                self._populate_note_widget(w, activity_id, note_id)
                # request a list of users that have replied
                reply_users |= w.get_reply_users()
            
            
            self._widgets[activity_id] = w
            self._app.log_debug("Adding %s to layout" % w)
            self.ui.activity_stream_layout.addWidget(w)        
            # add special blue border to indicate that this is a new arrival
            w.setStyleSheet("QFrame#frame{ border: 1px solid rgba(48, 167, 227, 50%); }")
        
        # when everything is loaded in, load the thumbs
        self._app.log_debug("Requesting thumbnails")
        for activity_id in activity_ids:
            self._data_manager.request_activity_thumbnails(activity_id)

        for (entity_type, entity_id) in reply_users:
            self._data_manager.request_user_thumbnail(entity_type, entity_id)
        
        self._app.log_debug("Process new data complete.")
            

    def _process_thumbnail(self, data):
        """
        New thumbnail has arrived from the data manager
        """
        # broadcast to all activity widgets
        for widget in self._widgets.values():
            widget.set_thumbnail(data)

    def _process_new_note(self, activity_id, note_id):
        """
        New thumbnail has arrived from the data manager
        """
        if activity_id in self._widgets:
            widget = self._widgets[activity_id]
            self._populate_note_widget(widget, activity_id, note_id)

    def _on_reply_clicked(self, note_id):
        print "REPLY FOR NOTE ID %s" % note_id
    
    def _on_attachment_group_expanded(self, activity_id, attachment_group_id):
        """
        Someone clicked an attachment group
        """

        widget = self._widgets[activity_id]
        attachment_group_widget = widget.get_attachment_group_widget(attachment_group_id)
        for attachment_data in attachment_group_widget.get_data():
            self._data_manager.request_attachment_thumbnail(activity_id, 
                                                            attachment_group_id, 
                                                            attachment_data)
        
    
    def _on_note_submitted(self):
        """
        called when a note has finished submitting
        """
        # kick the data manager to rescan for changes
        self._data_manager.rescan()

    def _load_shotgun_activity_stream(self):
        
        url = "%s/detail/%s/%s" % (self._app.sgtk.shotgun_url, self._entity_type, self._entity_id)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
