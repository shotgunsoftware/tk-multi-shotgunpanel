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


overlay_module = sgtk.platform.import_framework("tk-framework-qtwidgets", "overlay_widget")

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

        self.__overlay = overlay_module.ShotgunOverlayWidget(self.ui.text_entry)
        
        
        self.ui.screenshot.clicked.connect(self._grab_screen)
        self.ui.submit.clicked.connect(self._submit)
        self.ui.text_entry.on_focus.connect(self._on_focus)

        self.reset()
        
    def reset(self):
        """
        Prompt for confirmation if there is text
        """
        if self.ui.text_entry.toPlainText() != "":
            print "ARE YOU SURE???"
        
        self.ui.screenshot.hide()
        self.ui.submit.hide()
        self.ui.thumbnail.hide()        

    def _grab_screen(self):
        
        pixmap = screen_grab.screen_capture()
        self.ui.thumbnail.setPixmap(pixmap)
        self.ui.thumbnail.show()
        
    def _on_focus(self):
        print "on focus!"
        self.ui.screenshot.show()
        self.ui.submit.show()
        
    def _submit(self):
        print "submit!"
        self.__overlay.start_spin()
        QtCore.QCoreApplication.processEvents()
        print "start spin"
        try:
            import time
            time.sleep(3)
            self.__overlay.hide(hide_errors=False)
        except Exception, e:
            err_str = "Shotgun Error: %s" % e
            self.__overlay.show_error_message(err_str)
        
        self.ui.text_entry.setPlainText("")
        self.reset()
        
        
