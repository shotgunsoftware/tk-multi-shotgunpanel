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
 
class PlainTextEditWithPlaceholderText(QtGui.QPlainTextEdit):
    """
    """
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """
        self._placeholder_text = "Create new Note..." 
        QtGui.QPlainTextEdit.__init__(self, parent)
        
    def set_placeholder_text(self, text):
        self._placeholder_text = text
                
    def paintEvent(self, event):
        """
        Render the UI.
        """
        if self.toPlainText() == "" and not self.hasFocus():
            painter = QtGui.QPainter()
            painter.begin(self.viewport()) 
            try:
                painter.drawText(self.geometry(), QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop, self._placeholder_text)                    
            finally:
                painter.end()
        else:
            QtGui.QPlainTextEdit.paintEvent(self, event)
        
