# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sgtk
import datetime
import tempfile


overlay_module = sgtk.platform.import_framework("tk-framework-qtwidgets", "overlay_widget")
shotgun_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data")
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
ShotgunDataRetriever = shotgun_data.ShotgunDataRetriever

from sgtk.platform.qt import QtCore, QtGui
 

from ...ui.note_input_widget import Ui_NoteInputWidget
from .. import screen_grab  
 
class NoteInputWidget(QtGui.QWidget):
    """
    """
    
    # emitted when shotgun has been updated
    data_updated = QtCore.Signal()
    
    def __init__(self, parent):
 
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)
        
        self._app = sgtk.platform.current_bundle()
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_NoteInputWidget() 
        self.ui.setupUi(self)

        self._processing_id = None
        self._entity_link = None
        self._pixmap = None

        self.__overlay = overlay_module.ShotgunOverlayWidget(self.ui.text_entry)
        
        # create a separate sg data fetcher for submission
        self.__sg_data_retriever = shotgun_data.ShotgunDataRetriever(self)
        self.__sg_data_retriever.work_completed.connect(self.__on_worker_signal)
        self.__sg_data_retriever.work_failure.connect(self.__on_worker_failure)
        self.__sg_data_retriever.start()        
        
        self.ui.screenshot.clicked.connect(self._grab_screen)
        self.ui.submit.clicked.connect(self._submit)
        self.ui.text_entry.on_focus.connect(self._on_focus)

        self.reset()
        
    def reset(self):
        """
        Prompt for confirmation if there is text.
        
        :returns: true if reset was completed, false if reset couldn't be
                  completed because the user cancelled the operation.
        """
        if self.ui.text_entry.toPlainText() != "":
            status =QtGui.QMessageBox.warning(self, 
                                              "Confirm Navigation", 
                                              """<b>Confirm Navigation</b><br><br>
                                              You haven't submitted your Note yet.<br>
                                              Do you want to leave without finishing?""", 
                                              QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if status == QtGui.QMessageBox.No:
                return False
        
        self.ui.text_entry.setPlainText("")
        self.ui.screenshot.hide()
        self.ui.submit.hide()
        self.ui.thumbnail.hide()
        # clear focus to show the hint text
        self.ui.text_entry.clearFocus()
        
        self._processing_id = None
        self._pixmap = None
        
        return True
        
    def set_current_entity(self, entity_link):
        """
        Specify the current entity
        """
        self._entity_link = entity_link

    def _grab_screen(self):
        
        self._pixmap = screen_grab.screen_capture()
        self.ui.thumbnail.setPixmap(self._pixmap)
        self.ui.thumbnail.show()
        
    def _on_focus(self):
        """
        Slot for when the text editor gets focus. 
        """
        self.ui.screenshot.show()
        self.ui.submit.show()
        
    def _submit(self):
        """
        Creates items in Shotgun and clears the widget.
        """
        self.__overlay.start_spin()
        
        # get publish details async
        data = {}
        data["pixmap"] = self._pixmap
        data["text"] = self.ui.text_entry.toPlainText()
        data["entity"] = self._entity_link
        data["project"] = self._app.context.project
        self._processing_id = self.__sg_data_retriever.execute_method(self._async_submit, data)
        
    def _async_submit(self, sg, data):
        """
        Actual payload for creating things in shotgun.
        This runs in a different thread and cannot access
        any QT UI components.
        
        """
        

        if self._entity_link["type"] == "Note":
            # this is a reply that should be linked up to a note 
            raise Exception("Replies not supported yet!")
        
        else:
            # this is an entity - so create a note and link it
            sg_note_data = sg.create("Note", {"content": data["text"], 
                                         "project": data["project"],
                                         "note_links": [self._entity_link]})
            
            if data["pixmap"]:
                
                # save it out to a temp file so we can upload it
                png_path = tempfile.NamedTemporaryFile(suffix=".png",
                                                       prefix="screencapture_",
                                                       delete=False).name
        
         
                data["pixmap"].save(png_path)
                
                # create file entity and upload file
                sg_upload_data = sg.upload("Note", sg_note_data["id"], png_path)
                
                if os.path.exists(png_path):
                    self._app.log_debug("Deleting temp file %s" % png_path)
                    os.remove(png_path)
        
        
    def __on_worker_failure(self, uid, msg):
        """
        Asynchronous callback - the worker thread errored.
        """
        uid = shotgun_model.sanitize_qt(uid) # qstring on pyqt, str on pyside
        msg = shotgun_model.sanitize_qt(msg)

        if self._processing_id == uid:        
            self._app.log_error("Could not create note/reply for %s: %s" % (self._entity_link, msg))
            full_msg = "Shotgun Error: %s" % msg
            self.__overlay.show_error_message(full_msg)
    

    def __on_worker_signal(self, uid, request_type, data):
        """
        Signaled whenever the worker completes something.
        This method will dispatch the work to different methods
        depending on what async task has completed.
        """
        uid = shotgun_model.sanitize_qt(uid) # qstring on pyqt, str on pyside
        data = shotgun_model.sanitize_qt(data)

        if self._processing_id == uid:
            # all done!
            self.__overlay.hide()
            self.ui.text_entry.setPlainText("")
            self.reset()
            self._app.log_debug("Update call complete! Return data: %s" % data)
            self.data_updated.emit()
            
        
