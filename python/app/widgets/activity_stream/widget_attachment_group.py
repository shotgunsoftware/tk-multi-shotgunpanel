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

from .thumbnail_widgets import LargeAttachmentThumbnail, SmallAttachmentThumbnail
from .data_manager import ActivityStreamDataHandler

from .ui.attachment_group_widget import Ui_AttachmentGroupWidget

class AttachmentGroupWidget(QtGui.QWidget):
    """
    Subclassed QLabel to represent a shotgun user.
    """
    
    def __init__(self, parent, attachment_data):
        """
        Constructor
        
        :param parent: QT parent object
        """
        QtGui.QWidget.__init__(self, parent)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_AttachmentGroupWidget() 
        self.ui.setupUi(self)
        
        
        self._large_thumbnails = {}
        self._small_thumbnails = {}
        self._other_widgets = []
        
        self._attachment_data = attachment_data
        
        self.ui.attachment_frame.setVisible(False)
        
        current_row = 0
        current_col = 0
        max_col = 0
        
        for data in self._attachment_data:
            obj = SmallAttachmentThumbnail(self.ui.preview_frame)
            obj.set_data(data)
            obj.clicked.connect(self._toggle_large_thumbnails)            
            self.ui.preview_layout.addWidget(obj, current_row, current_col)
            self._small_thumbnails[data["id"]] = obj
            
            
            if current_col > 4:
                current_col = 0
                current_row += 1
            else:
                current_col += 1
                
            # track the max column used so far
            max_col = max(current_col, max_col)
            
        
        # and have everything pushed to the left        
        self.ui.preview_layout.setColumnStretch(max_col+1, 1)
        
        for data in self._attachment_data:
            obj = LargeAttachmentThumbnail(self)
            obj.set_data(data)
            obj.clicked.connect(self._toggle_small_thumbnails)
            self.ui.attachment_layout.addWidget(obj)
            self._large_thumbnails[data["id"]] = obj
        
        

    def set_thumbnail(self, data):
        """
        set thumbnail
        """
        if data["thumbnail_type"] != ActivityStreamDataHandler.THUMBNAIL_ATTACHMENT:
            return
        attachment_id = data["entity"]["id"]
        if attachment_id in self._large_thumbnails:
            attachment_obj = self._large_thumbnails[attachment_id]
            attachment_obj.set_thumbnail(data["image"])
            
        if attachment_id in self._small_thumbnails:
            attachment_obj = self._small_thumbnails[attachment_id]
            attachment_obj.set_thumbnail(data["image"])

    def _toggle_large_thumbnails(self):
        
        self.ui.attachment_frame.setVisible(True)
        self.ui.preview_frame.setVisible(False)
        
    def _toggle_small_thumbnails(self):
        
        self.ui.attachment_frame.setVisible(False)
        self.ui.preview_frame.setVisible(True)
                
        
    def get_data(self):
        return self._attachment_data
            
        
