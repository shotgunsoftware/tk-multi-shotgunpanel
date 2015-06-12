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
 
from ...ui.note_input_widget import Ui_NoteInputWidget
from .. import screen_grab  
 
class NoteInputWidget(QtGui.QWidget):
    """
    """
    
    def __init__(self, parent):
 
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_NoteInputWidget() 
        self.ui.setupUi(self)
        
        self.ui.screenshot.clicked.connect(self._grab_screen)


    def _grab_screen(self):
        
        pixmap = screen_grab.screen_capture()
        self.ui.thumbnail.setPixmap(pixmap)
        
