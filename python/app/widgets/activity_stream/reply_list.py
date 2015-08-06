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
import os
import sys
from sgtk.platform.qt import QtCore, QtGui
from ... import utils

from .dialog_reply import ReplyDialog

from .ui.reply_list_widget import Ui_ReplyListWidget

from .label_widgets import ClickableTextLabel
 
from .data_manager import ActivityStreamDataHandler
from .widget_attachment_group import AttachmentGroupWidget
from .widget_reply import ReplyWidget
from .overlaywidget import SmallOverlayWidget
 
overlay_module = sgtk.platform.import_framework("tk-framework-qtwidgets", "overlay_widget")
 
class ReplyListWidget(QtGui.QWidget):
    """
    Widget that displays a series of replies to a note
    """
    
    # when someone clicks a link or similar
    entity_requested = QtCore.Signal(str, int)
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """

        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self, parent)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_ReplyListWidget() 
        self.ui.setupUi(self)
        
        self._note_id = None
        self._sg_entity_dict = None
        self._data_retriever = None
        self._general_widgets = []
        self._reply_widgets = []
        self._attachment_group_widgets = {}
        
        self._app = sgtk.platform.current_bundle()
        
        # apply styling
        self._load_stylesheet()
        
        # small overlay
        self.__small_overlay = SmallOverlayWidget(self)
        self.__overlay = overlay_module.ShotgunOverlayWidget(self)
        
        # create a data manager to handle backend
        self._data_manager = ActivityStreamDataHandler(self)
        
        self._data_manager.thumbnail_arrived.connect(self._process_thumbnail)
        self._data_manager.note_arrived.connect(self._process_new_note)
        

    def _process_new_note(self, activity_id, note_id):
        """
        New thumbnail has arrived from the data manager
        """
        self.__overlay.hide()
        self.load_data(self._sg_entity_dict)
            
        # set note content            
        note_thread_data = self._data_manager.get_note(note_id)
        
        if note_thread_data is None:            
            # anomaly - there should be data at this point.
            self._app.log_warning("Could not get note data from Shotgun!")
        else:
            self._build_replies(note_thread_data)
            

    def set_data_retriever(self, data_retriever):
        """
        Set an async data retreiver object to use with this 
        widget.
        """
        self._data_manager.set_data_retriever(data_retriever)
        self._data_retriever = data_retriever
        

          
    ##########################################################################################
    # public interface
        
    def load_data(self, sg_entity_dict):
        """
        Load replies for a given entity.
        
        :param sg_entity_dict: Shotgun link dictionary with keys type and id.
        """
        self._app.log_debug("Loading replies for %s" % sg_entity_dict)
        
        if sg_entity_dict["type"] != "Note":
            self._app.log_error("Cannot only show replies for Notes.")
            return

        self._sg_entity_dict = sg_entity_dict
        note_id = self._sg_entity_dict["id"]

        # init data store        
        self._app.log_debug("Setting up db manager....")
        self._data_manager.load_data("Note", note_id)
        
        # set note content            
        note_thread_data = self._data_manager.get_note(note_id)
        
        if note_thread_data is None:
            
            # no data yet!
            self.__overlay.show_message("Loading Shotgun Data...")
            self._data_manager.rescan()
        
        else:
            
            self._build_replies(note_thread_data)

    def _build_replies(self, note_thread_data):

        # before we begin widget operations, turn off visibility
        # of the whole widget in order to avoid recomputes
        self.setVisible(False)
        
        try:


            self._clear()
    
            note_id = self._sg_entity_dict["id"]
            
            attachment_requests = []
            
            # we have cached note data
            replies_and_attachments = note_thread_data[1:] 
                        
            # now add replies
            self._add_replies(replies_and_attachments)
            
            # add a reply button and connect it
            reply_button = self._add_reply_button()
            reply_button.clicked.connect(lambda : self._on_reply_clicked(note_id))
    
            # add a proxy widget that should expand to fill all white
            # space available
            expanding_widget = QtGui.QLabel(self)
            self.ui.reply_layout.addWidget(expanding_widget)
            self.ui.reply_layout.setStretchFactor(expanding_widget, 1)
            self._general_widgets.append(expanding_widget)
    
            # get all attachment data
            # can request thumbnails post UI build
            for attachment_group_id in self._attachment_group_widgets.keys():
                agw = self._attachment_group_widgets[attachment_group_id]
                for attachment_data in agw.get_data():                        
                    ag_request = {"attachment_group_id": attachment_group_id, 
                                  "attachment_data": attachment_data}
                    attachment_requests.append(ag_request)
    
            self._app.log_debug("Request thumbnails...")
            
            for attachment_req in attachment_requests:
                self._data_manager.request_attachment_thumbnail(-1, 
                                                                attachment_req["attachment_group_id"], 
                                                                attachment_req["attachment_data"])
            
            for (entity_type, entity_id) in self._get_reply_users():
                self._data_manager.request_user_thumbnail(entity_type, entity_id)
            
        finally:
            # make the window visible again and trigger a redraw
            self.setVisible(True)
            
        
        self._app.log_debug("...done")






    ##########################################################################################
    # internal methods
        
    def _clear(self):
        """
        Clear the widget. This will remove all items from the UI
        """
        self._app.log_debug("Clearing UI...")
        
        for x in self._general_widgets + self._reply_widgets + self._attachment_group_widgets.values():
            # remove widget from layout:
            self.ui.reply_layout.removeWidget(x)
            # set it's parent to None so that it is removed from the widget hierarchy
            x.setParent(None)
            # mark it to be deleted when event processing returns to the main loop
            x.deleteLater()
    
        self._general_widgets = []
        self._reply_widgets = []
        self._attachment_group_widgets = {}    
        
        
        
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
            
        
    def _get_reply_users(self):
        """
        Returns a list of users who have created replies
        
        :returns: tuple with (entity_type, entity_id)
        """
        users = []
        for reply_widget in self._reply_widgets:
            created_by_tuple = (reply_widget.created_by["type"], 
                                reply_widget.created_by["id"])
            users.append(created_by_tuple)
        return set(users)    
    
    def _add_reply_button(self):

        reply_button = ClickableTextLabel(self)
        reply_button.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        reply_button.setText("Reply to this Note")
        reply_button.setObjectName("reply_button")
        self.ui.reply_layout.addWidget(reply_button)
        self._general_widgets.append(reply_button)
        return reply_button


    def _add_attachment_group(self, attachments, after_note):
        
        curr_attachment_group_widget_id = len(self._attachment_group_widgets)
        attachment_group = AttachmentGroupWidget(self, attachments)        
        # show an ATTACHMENTS header
        attachment_group.show_attachments_label(True)        
        
        
        offset = attachment_group.OFFSET_NONE if after_note else attachment_group.OFFSET_LARGE_THUMB        
        attachment_group.adjust_left_offset(offset)
        
        self.ui.reply_layout.addWidget(attachment_group)
        
        # add it to our mapping dict and increment the counter
        self._attachment_group_widgets[curr_attachment_group_widget_id] = attachment_group
        
        

    def _add_replies(self, replies_and_attachments):
        """
        Add replies and attachment widgets
        """
        
        current_attachments = []
        attachment_is_directly_after_note = True
        
        for item in replies_and_attachments:

            if item["type"] == "Reply":
                                
                # first, wrap up attachments
                if len(current_attachments) > 0:                    
                    self._add_attachment_group(current_attachments, attachment_is_directly_after_note)
                    current_attachments = []
                                                
                w = ReplyWidget(self)
                w.adjust_thumb_style(w.LARGE_USER_THUMB)
                self.ui.reply_layout.addWidget(w)
                w.set_info(item)
                self._reply_widgets.append(w)
                # ensure navigation requests from replies bubble up
                w.entity_requested.connect(self.entity_requested.emit)
                # next bunch of attachments will be after a reply
                # rather than directly under the note
                # (this affects the visual style)
                attachment_is_directly_after_note = False
                
            if item["type"] == "Attachment" and item["this_file"]["link_type"] == "upload":
                current_attachments.append(item)
        
        # see if there are still open attachments
        if len(current_attachments) > 0:
            self._add_attachment_group(current_attachments, attachment_is_directly_after_note)
            current_attachments = []            


    def _process_thumbnail(self, data):
        """
        Populate the UI with the given thumbnail
        
        :param image: QImage with thumbnail data
        :param thumbnail_type: thumbnail enum constant:
            ActivityStreamDataHandler.THUMBNAIL_CREATED_BY
            ActivityStreamDataHandler.THUMBNAIL_ENTITY
            ActivityStreamDataHandler.THUMBNAIL_ATTACHMENT
        """        
        thumbnail_type = data["thumbnail_type"]
        activity_id = data["activity_id"]
        image = data["image"]
        
        if thumbnail_type == ActivityStreamDataHandler.THUMBNAIL_ATTACHMENT and activity_id == -1:
            group_id = data["attachment_group_id"]
            attachment_group = self._attachment_group_widgets[group_id]
            attachment_group.set_thumbnail(data)

        elif thumbnail_type == ActivityStreamDataHandler.THUMBNAIL_USER:
            # a thumbnail for a user possibly for one of our replies
            for reply_widget in self._reply_widgets:
                if reply_widget.thumbnail_populated:
                    # already set
                    continue
                if data["entity"] == reply_widget.created_by:
                    reply_widget.set_thumbnail(image)


    def _on_reply_clicked(self, note_id):
        
        # TODO - refactor to not have dupe code
        
        reply_dialog = ReplyDialog(self, self._data_retriever, note_id)
        
        #position the reply modal dialog above the activity stream scroll area
        pos = self.mapToGlobal(self.ui.reply_scroll_area.pos())
        x_pos = pos.x() + (self.ui.reply_scroll_area.width() / 2) - (reply_dialog.width() / 2) - 10         
        y_pos = pos.y() + (self.ui.reply_scroll_area.height() / 2) - (reply_dialog.height() / 2) - 20
        reply_dialog.move(x_pos, y_pos)
        
        # and pop it
        try:
            self.__small_overlay.show()
        
            if reply_dialog.exec_() == QtGui.QDialog.Accepted:
                self._data_manager.rescan()
        finally:
            self.__small_overlay.hide()
        
        
