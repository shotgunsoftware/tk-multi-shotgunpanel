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

class UserLabel(QtGui.QLabel):
    """
    Subclassed QLabel to represent a shotgun user.
    """
    
    # signal that fires on click
    clicked = QtCore.Signal(str, int)
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """
        QtGui.QLabel.__init__(self, parent)
        # make this user clickable
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self._sg_data = None
            
    def set_shotgun_data(self, sg_data):
        """
        Set the shotgun data associated with this user
        
        :param sg_data: Shotgun user data
        """
        self._sg_data = sg_data
        user_name = sg_data.get("name") or "Unknown User"
        self.setToolTip(user_name)

    def mousePressEvent(self, event):
        """
        Fires when the mouse is pressed
        """
        QtGui.QLabel.mousePressEvent(self, event)
        
        if self._sg_data:
            self.clicked.emit(self._sg_data["type"], 
                              self._sg_data["id"])
        
