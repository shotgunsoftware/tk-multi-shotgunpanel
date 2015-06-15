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
    Widget that 
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
        # step 1 - extend out the link dictionary according to specific logic.
        # - if link is a version, then also include the item the version is linked to and the version's task
        # - if a link is a task, find its link and use that as the main link. 
        #   set the task to be linked up to the tasks field.
        
        note_tasks = []
        note_links = []
        
        entity_link = data["entity"]
        
        if entity_link["type"] == "Version":
            # if we are adding a note to a version, link it with the version 
            # and the entity that the version is linked to.
            # if the version has a task, link the task to the note too.
            
            sg_version = sg.find_one("Version", 
                                     [["id", "is", entity_link["id"] ]], 
                                     ["entity", "sg_task", "cached_display_name"])
            # first make a std sg link to the current entity - this to ensure we have a name key present
            note_links += [{"id": entity_link["id"], 
                            "type": entity_link["type"], 
                            "name": sg_version["cached_display_name"] }] 
            
            # and now add the linked entity, if there is one
            if sg_version["entity"]:
                note_links += [sg_version["entity"]]
            
            if sg_version["sg_task"]:
                note_tasks += [sg_version["sg_task"]]
            
        elif entity_link["type"] == "Task":
            # if we are adding a note to a task, link the note to the entity that is linked to the
            # task. The link the task to the note via the task link.
            sg_task = sg.find_one("Task", 
                                  [["id", "is", entity_link["id"] ]], 
                                  ["entity"])
            
            if sg_task["entity"]:
                # there is an entity link from this task
                note_links += [sg_task["entity"]]
            
            # lastly, link the note's task link to this task            
            note_tasks += [entity_link]
        
        else:
            # no special logic. Just link the note to the current entity.
            # note that because we don't have the display name for the entity,
            # we need to retrieve this
            sg_entity = sg.find_one(entity_link["type"], [["id", "is", entity_link["id"] ]], ["cached_display_name"])
            note_links += [{"id": entity_link["id"], 
                           "type": entity_link["type"], 
                           "name": sg_entity["cached_display_name"] }] 
        
        # step 2 - generate the subject line. This is done by various shotgun client/server
        # logic which we attempt to emulate here. A typical example is:
        #
        # Tomoko's Note on aaa_00010_F004_C003_0228F8_v000 and aaa_00010
        # First name's Note on [list of entities]
        current_user = sgtk.util.get_current_user(self._app.sgtk)
        if current_user:
            if current_user.get("firstname"):
                first_name = current_user.get("firstname")
            else:
                # compatibility with older cores
                first_name = current_user.get("name").split(" ")[0]
                
            title = "%s's Note" % first_name 
        else:
            title = "Unknown user's Note"
        
        if len(note_links) > 0:
            note_names = [x["name"] for x in note_links]
            title += " on %s" % (", ".join(note_names))

        # this is an entity - so create a note and link it
        sg_note_data = sg.create("Note", {"content": data["text"],
                                          "subject": title, 
                                          "project": data["project"],
                                          "note_links": note_links,
                                          "tasks": note_tasks })
        
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
            
        
