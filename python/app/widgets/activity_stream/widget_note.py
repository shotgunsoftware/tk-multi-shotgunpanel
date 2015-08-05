# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform.qt import QtCore, QtGui

import sgtk

from .widget_activity_stream_base import ActivityStreamBaseWidget
from .ui.note_widget import Ui_NoteWidget

shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")

from .widget_reply import ReplyWidget

from .widget_attachment_group import AttachmentGroupWidget
from ...modules.schema import CachedShotgunSchema

from .data_manager import ActivityStreamDataHandler
from ... import utils

class NoteWidget(ActivityStreamBaseWidget):
    """
    Widget that replies event stream details for a note
    """
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """
        # first, call the base class and let it do its thing.
        ActivityStreamBaseWidget.__init__(self, parent)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_NoteWidget() 
        self.ui.setupUi(self)
        
        self._note_id = None
        self._general_widgets = []
        self._reply_widgets = []
        self._attachment_group_widgets = {}
                
        # make sure clicks propagate upwards in the hierarchy
        self.ui.links.linkActivated.connect(self._entity_request_from_url)
        self.ui.content.linkActivated.connect(self._entity_request_from_url)
        self.ui.header_left.linkActivated.connect(self._entity_request_from_url)    
        self.ui.user_thumb.clicked.connect(lambda entity_type, entity_id: self.entity_requested.emit(entity_type, entity_id))    

    ##############################################################################
    # public interface
    
    def set_info(self, data):
        """
        Populate text fields for this widget
        
        :param data: data dictionary with activity stream info. 
        """        
        # call base class
        ActivityStreamBaseWidget.set_info(self, data)
        
        # most of the info will appear later, as part of the note
        # data being loaded, so add placeholder
        self.ui.content.setText("Hang on, loading note content...")
        
    def set_thumbnail(self, data):
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
        
        if thumbnail_type == ActivityStreamDataHandler.THUMBNAIL_CREATED_BY and activity_id == self.activity_id:
            thumb = utils.create_round_thumbnail(image)          
            self.ui.user_thumb.setPixmap(thumb)
        
        elif thumbnail_type == ActivityStreamDataHandler.THUMBNAIL_ATTACHMENT and activity_id == self.activity_id:
            group_id = data["attachment_group_id"]
            attachment_group = self.get_attachment_group_widget(group_id)
            attachment_group.set_thumbnail(data)

        elif thumbnail_type == ActivityStreamDataHandler.THUMBNAIL_USER:
            # a thumbnail for a user possibly for one of our replies
            for reply_widget in self._reply_widgets:
                if reply_widget.thumbnail_populated:
                    # already set
                    continue
                if data["entity"] == reply_widget.created_by:
                    reply_widget.set_thumbnail(image)


    def add_reply_button(self):
        reply_button = QtGui.QToolButton(self)
        reply_button.setText("Reply")
        reply_button.setObjectName("reply_button")
        self.ui.reply_layout.addWidget(reply_button)
        self._general_widgets.append(reply_button)
        return reply_button

    def get_attachment_group_widget_ids(self):
        return self._attachment_group_widgets.keys()
    
    def get_attachment_group_widget(self, attachment_group_id):
        """
        Returns an attachment group widget given its id
        """
        return self._attachment_group_widgets[attachment_group_id]
    
    def add_replies(self, replies_and_attachments):
        """
        Add replies and attachment widgets
        """
        
        curr_attachment_group_widget_id = len(self._attachment_group_widgets)
        
        current_attachments = []
        attachment_is_directly_after_note = True
        
        for item in replies_and_attachments:
            
            if item["type"] == "Reply":
                                
                # first, wrap up attachments
                if len(current_attachments) > 0:
                    attachment_group = AttachmentGroupWidget(self, current_attachments)
                    
                    if attachment_is_directly_after_note:
                        attachment_group.adjust_ui_for_note()
                        
                    self.ui.reply_layout.addWidget(attachment_group)
                    current_attachments = []
                    
                    # add it to our mapping dict and increment the counter
                    self._attachment_group_widgets[curr_attachment_group_widget_id] = attachment_group
                    curr_attachment_group_widget_id += 1
                                                
                w = ReplyWidget(self)
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
            
            attachment_group = AttachmentGroupWidget(self, current_attachments)
            if attachment_is_directly_after_note:
                attachment_group.adjust_ui_for_note()
            
            self._attachment_group_widgets[curr_attachment_group_widget_id] = attachment_group
            self.ui.reply_layout.addWidget(attachment_group)
            print self._attachment_group_widgets
        
    def get_reply_users(self):
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
        
        
    def __generate_note_links_table(self, links):
        """
        Make a html table that contains links different items
        """
        # format note links
        html_chunks = []
        for link in links:
            entity_type_display_name = CachedShotgunSchema.get_type_display_name(link["type"])
            chunk = """
                <tr><td bgcolor=#666666>
                    <a href='%s:%s' style='text-decoration: none; color: #dddddd'>%s <b>%s</b></a>
                </td></tr>
                """ % (link["type"], link["id"], entity_type_display_name, link["name"])
            html_chunks.append(chunk)

        html = """
        <table cellpadding=5 cellspacing=2 >
        %s
        </table>
        """ % "\n".join(html_chunks)
        
        return html
        
        
    def set_note_info(self, data):
        """
        update with new note data
        """
        
        self._note_id = data["id"]
        
        # make the thumbnail clickable
        self.ui.user_thumb.set_shotgun_data(data["created_by"])
        
        # the top left part of the note is the name of the author
        entity_url = self._generate_entity_url(data["created_by"], 
                                               this_syntax=False,
                                               display_type=False)        
        self.ui.header_left.setText("<big>%s</big>" % entity_url)
        
        # top right is the date of the note (rather than 
        # date of activity)
        self._set_timestamp(data, self.ui.date)
        
        # set the main note text
        self.ui.content.setText(data["content"])
        
        # format note links
        links_html = self.__generate_note_links_table(data["note_links"])

        self.ui.links.setText(links_html)

