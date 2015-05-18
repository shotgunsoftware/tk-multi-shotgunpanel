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
 
class VersionLabel(QtGui.QLabel):
    """
    """
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """
        QtGui.QLabel.__init__(self, parent)
        self._play_icon = QtGui.QPixmap(":/tk_multi_infopanel/play_icon.png")
        self._play_icon_inactive = QtGui.QPixmap(":/tk_multi_infopanel/play_icon_inactive.png")
        self._hover = False
        self._active = False

    def set_playback_icon_active(self, status):
        self._active = status

    def enterEvent(self, event):
        if self._active:
            self._hover = True
            self.setCursor(QtCore.Qt.PointingHandCursor)
            self.repaint()
        
    def leaveEvent(self, event):
        if self._active:
            self._hover = False
            self.unsetCursor()
            self.repaint()

    def paintEvent(self, event):
        """
        Render the UI.
        """
        
        # first render the label
        QtGui.QLabel.paintEvent(self, event)
        
        if self._active:
            # now render a pixmap on top
            painter = QtGui.QPainter()
            painter.begin(self)
            try:
                # set up semi transparent backdrop
                painter.setRenderHint(QtGui.QPainter.Antialiasing)
                
                # draw image
                painter.translate((painter.device().width() / 2) - (self._play_icon.width()/2), 
                                  (painter.device().height() / 2) - (self._play_icon.height()/2) )
                
                if self._hover:
                    painter.drawPixmap( QtCore.QPoint(0, 0), self._play_icon)
                else:
                    painter.drawPixmap( QtCore.QPoint(0, 0), self._play_icon_inactive)
                    
            finally:
                painter.end()
 
