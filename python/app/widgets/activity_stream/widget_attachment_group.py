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

from .attachment_label import AttachmentLabel
from .data_manager import ActivityStreamDataHandler

from .ui.attachment_group_widget import Ui_AttachmentGroupWidget

class AttachmentGroupWidget(QtGui.QWidget):
    """
    Subclassed QLabel to represent a shotgun user.
    """
    
    expanded = QtCore.Signal()
    
    def __init__(self, parent, attachment_data):
        """
        Constructor
        
        :param parent: QT parent object
        """
        QtGui.QWidget.__init__(self, parent)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_AttachmentGroupWidget() 
        self.ui.setupUi(self)
        
        self._widgets = {}
        
        self._attachment_data = attachment_data
        self.ui.load_more.setText("%s Attachments" % len(attachment_data))        
        self.ui.load_more.clicked.connect(self._show_attachments)
        

    def set_thumbnail(self, data):
        """
        set thumbnail
        """
        if data["thumbnail_type"] != ActivityStreamDataHandler.THUMBNAIL_ATTACHMENT:
            return
        attachment_id = data["entity"]["id"]
        if attachment_id in self._widgets:
            attachment_obj = self._widgets[attachment_id]
            attachment_obj.set_thumbnail(data["image"])
            
        
    def _show_attachments(self):
        
        self.expanded.emit()
        
        self.ui.load_more.setVisible(False)
        
        for data in self._attachment_data:
            attachment_obj = AttachmentLabel(self)
            attachment_obj.set_data(data)
            self.ui.attachment_layout.addWidget(attachment_obj)
            self._widgets[data["id"]] = attachment_obj
                
        
    def get_data(self):
        return self._attachment_data
            
        
