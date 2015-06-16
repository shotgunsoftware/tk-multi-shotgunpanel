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
 

from .ui.note_input_widget import Ui_NoteInputWidget
from .. import screen_grab  
 
class NoteInputWidget(QtGui.QWidget):
    """
    Widget that can be used for note and thumbnail input and creation.
    """
    
    # emitted when shotgun has been updated
    data_updated = QtCore.Signal()
    
    def __init__(self, parent):
        """
        Constructor
        """
 
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)

        # now load in the UI that was created in the UI designer
        self.ui = Ui_NoteInputWidget() 
        self.ui.setupUi(self)
        
        # set up some handy references
        self._app = sgtk.platform.current_bundle()        
        self._camera_icon = QtGui.QIcon(QtGui.QPixmap(":/tk_multi_infopanel_note_input_widget/camera_hl.png"))
        self._trash_icon = QtGui.QIcon(QtGui.QPixmap(":/tk_multi_infopanel_note_input_widget/trash.png"))
        
        # initialize state variables
        self._processing_id = None      # async task id
        self._entity_link = None        # current associated entity 
        self._pixmap = None             # 

        # set up an overlay that spins when note is submitted
        self.__overlay = overlay_module.ShotgunOverlayWidget(self)
        
        # create a separate sg data handler for submission
        self.__sg_data_retriever = shotgun_data.ShotgunDataRetriever(self)
        self.__sg_data_retriever.work_completed.connect(self.__on_worker_signal)
        self.__sg_data_retriever.work_failure.connect(self.__on_worker_failure)
        self.__sg_data_retriever.start()    
        
        # hook up signals and slots
        self.ui.screenshot.clicked.connect(self._on_screenshot_clicked)
        self.ui.submit.clicked.connect(self._submit)
        self.ui.text_entry.on_focus.connect(self._on_focus)

        # reset state of the UI
        self.reset()
        
    
        
    def reset(self):
        """
        Rest the state of the widget completely.
        Clear any input.
        Prompt for confirmation if there is text.
        
        :returns: true if reset was completed, false if reset couldn't be
                  completed because the user cancelled the operation.
        """
        if self.ui.text_entry.toPlainText() != "":
            # this is similar to what Chrome prompts
            # when you are about to nagivate away from a page
            # where you have entered text 
            status = QtGui.QMessageBox.warning(self, 
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
        
        # reset data state
        self._processing_id = None
        self._pixmap = None
        
        # make sure the screenshot button shows the camera icon
        self.ui.screenshot.setIcon(self._camera_icon)
        self.ui.screenshot.setToolTip("Take Screenshot")
        
        return True
        
    def set_current_entity(self, entity_link):
        """
        Specify the current entity that this widget is linked against
        
        :param entity_link: Std entity link dictionary with type and id
        """
        self._entity_link = entity_link

    def set_placeholder_text(self, msg):
        """
        Sets the placeholder message to display
        
        :param msg: Placeholder text
        """
        self.ui.text_entry.set_placeholder_text(msg)
        

    def _on_screenshot_clicked(self):
        """
        Screenshot button is clicked. This either means that 
        a screenshot should be taken or that it should be cleared.
        """
        if self._pixmap is None:
            # no pixmap exists - screengrab mode
            self._app.log_debug("Prompting for screenshot...")
            self._pixmap = screen_grab.screen_capture()
            self._app.log_debug("Got screenshot %sx%s" % (self._pixmap.width(), 
                                                          self._pixmap.height()))
            
            thumb = self.__format_thumbnail(self._pixmap)
            self.ui.thumbnail.setPixmap(thumb)
            self.ui.thumbnail.show()
            # turn the button into a delete screenshot button
            self.ui.screenshot.setIcon(self._trash_icon)
            self.ui.screenshot.setToolTip("Remove Screenshot")
        
        else:
            # there is a screenshot - that means the user clicked the trash bit 
            self._pixmap = None
            self.ui.thumbnail.hide()
            
            # turn the button into a screenshot button
            self.ui.screenshot.setIcon(self._camera_icon)
            self.ui.screenshot.setToolTip("Take Screenshot")
        
        
    def _on_focus(self):
        """
        Executed when the text editor gets focus.
        Reverals the additional items in the UI, 
        e.g. the buttons. 
        """
        self.ui.screenshot.show()
        self.ui.submit.show()
        
    def _submit(self):
        """
        Creates items in Shotgun and clears the widget.
        """
        self.__overlay.start_spin()
        
        # get all publish details from the UI
        # and submit an async request
        data = {}
        data["pixmap"] = self._pixmap
        data["text"] = self.ui.text_entry.toPlainText()
        data["entity"] = self._entity_link
        data["project"] = self._app.context.project
        # ask the data retriever to execute an async callback
        self._processing_id = self.__sg_data_retriever.execute_method(self._async_submit, data)
        
    def _async_submit(self, sg, data):
        """
        Actual payload for creating things in shotgun.
        Note: This runs in a different thread and cannot access
        any QT UI components.
        
        :param sg: Shotgun instance
        :param data: data dictionary passed in from _submit()
        """
        entity_link = data["entity"]
        if entity_link["type"] == "Note":
            # we are replying to a note - create a reply
            return self._async_submit_reply(sg, data)
        else:
            # create a new note
            return self._async_submit_note(sg, data)
        
    def _async_submit_reply(self, sg, data):
        # create a new reply
        
        note_link = data["entity"]
        
        # this is an entity - so create a note and link it
        sg.create("Reply", {"content": data["text"], "entity": note_link})
        
        if data["pixmap"]:
            
            # save it out to a temp file so we can upload it
            png_path = tempfile.NamedTemporaryFile(suffix=".png",
                                                   prefix="screencapture_",
                                                   delete=False).name
    
            data["pixmap"].save(png_path)
            
            # create file entity and upload file and associate with the NOTE, not the reply!
            sg.upload("Note", note_link["id"], png_path)
            
            if os.path.exists(png_path):
                os.remove(png_path)
                
        
    def _async_submit_note(self, sg, data):
        # note - no logging in here, as I am not sure how all 
        # engines currently react to log_debug() async.
        
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
        
        # step 2 - generate the subject line. The following
        # convention exists for this:
        #
        # Tomoko's Note on aaa_00010_F004_C003_0228F8_v000 and aaa_00010
        # First name's Note on [list of entities]
        current_user = sgtk.util.get_current_user(self._app.sgtk)
        if current_user:
            if current_user.get("firstname"):
                # not all core versions support firstname,
                # so double check that we have that key
                first_name = current_user.get("firstname")
            else:
                # compatibility with older cores
                # for older cores, just split on the first space
                # Sorry Mary Jane Watson!
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
            sg.upload("Note", sg_note_data["id"], png_path)
            
            if os.path.exists(png_path):
                os.remove(png_path)
        
        
    def __on_worker_failure(self, uid, msg):
        """
        Asynchronous callback - the worker thread errored.
        
        :param uid: Unique id for request that failed
        :param msg: Error message
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

        :param uid: Unique id for request
        :param request_type: String indentifying the request class
        :param data: the data that was returned 
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
            
        
    def __format_thumbnail(self, pixmap_obj):
        """
        Given a screengrab, create a thumbnail object, scaled to 96x75 px
        and with a subtle rounded frame.
        
        :param pixmap_obj: input screenshot
        :returns: 96x75px pixmap 
        """
        CANVAS_WIDTH = 96
        CANVAS_HEIGHT = 75
        CORNER_RADIUS = 6
    
        # get the 512 base image
        base_image = QtGui.QPixmap(CANVAS_WIDTH, CANVAS_HEIGHT)
        base_image.fill(QtCore.Qt.transparent)
        
        # scale it down to fit inside a frame of maximum 512x512
        thumb_scaled = pixmap_obj.scaled(CANVAS_WIDTH, 
                                         CANVAS_HEIGHT, 
                                         QtCore.Qt.KeepAspectRatioByExpanding, 
                                         QtCore.Qt.SmoothTransformation)  

        # now composite the thumbnail on top of the base image
        # bottom align it to make it look nice
        thumb_img = thumb_scaled.toImage()
        brush = QtGui.QBrush(thumb_img)
        
        painter = QtGui.QPainter(base_image)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(brush)

        pen = QtGui.QPen(QtGui.QColor("#2C93E2"))
        pen.setWidth(3)
        painter.setPen(pen)
        
        # note how we have to compensate for the corner radius
        painter.drawRoundedRect(0,  
                                0, 
                                CANVAS_WIDTH, 
                                CANVAS_HEIGHT, 
                                CORNER_RADIUS, 
                                CORNER_RADIUS)
        
        painter.end()
        
        return base_image
