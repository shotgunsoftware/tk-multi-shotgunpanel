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

from . import utils

import sgtk

class AttachmentLabel(QtGui.QLabel):
    """
    Subclassed QLabel to represent a shotgun user.
    """
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """
        QtGui.QLabel.__init__(self, parent)
        
        self.setMinimumSize(QtCore.QSize(256, 144))
        self.setMaximumSize(QtCore.QSize(256, 144))
        self.setText("")
        self.setPixmap(QtGui.QPixmap(":/tk_multi_infopanel_activity_stream/rect_256x144.png"))
        # make this user clickable
        self.setCursor(QtCore.Qt.PointingHandCursor)

        self._data = None
        
    def set_data(self, data):
        self._data = data

    def set_thumbnail(self, image):
        print "thumb!"
        thumb = utils.create_rectangular_256x144_thumbnail(image)
        self.setPixmap(thumb)

    def mousePressEvent(self, event):
        """
        Fires when the mouse is pressed
        """
        QtGui.QLabel.mousePressEvent(self, event)        
        print "click attachment!"
        
