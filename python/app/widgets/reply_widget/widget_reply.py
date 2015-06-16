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
import datetime

from sgtk.platform.qt import QtCore, QtGui
 
from .ui.reply_widget import Ui_ReplyWidget
 
class ReplyWidget(QtGui.QWidget):
    """
    """
    
    def __init__(self, parent):
 
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_ReplyWidget() 
        self.ui.setupUi(self)
        
        # hide attachments for now - TODO : add support for this
        self.ui.attachment_scrollarea.hide()
        self.ui.attachment_header.hide()
        
    def set_content(self, user, date, body):
        self.ui.reply.setText(body)
        self.ui.user.setText(user)
        self.ui.date.setText(user)

    def set_thumbnail(self, pixmap):
        self.ui.thumbnail.setPixmap(pixmap)
