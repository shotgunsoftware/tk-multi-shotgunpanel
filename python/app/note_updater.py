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
from sgtk.platform.qt import QtCore, QtGui

shotgun_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data")
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")

class NoteUpdater(QtCore.QObject):
    """
    Class that operates asynchronously on notes.
    """
    def __init__(self, task_manager, parent):
        """
        Constructor
        
        :param data_retriever: Task manager to use for background work
        :param parent: QT parent object 
        """     
        QtCore.QObject.__init__(self, parent)   
        
        self._guids = []
        
        self._app = sgtk.platform.current_bundle()
        self.__sg_data_retriever = shotgun_data.ShotgunDataRetriever(self, 
                                                                     bg_task_manager=task_manager)        
        self.__sg_data_retriever.start()
        self.__sg_data_retriever.work_completed.connect(self.__on_worker_signal)
        self.__sg_data_retriever.work_failure.connect(self.__on_worker_failure)      

    def __on_worker_failure(self, uid, msg):
        """
        Asynchronous callback - the worker thread errored.
        
        :param uid: Unique id for request that failed
        :param msg: Error message
        """
        uid = shotgun_model.sanitize_qt(uid) # qstring on pyqt, str on pyside
        msg = shotgun_model.sanitize_qt(msg)
        if uid in self._guids:
            self._app.log_warning("Could not update note: %s" % msg)
            self._guids.remove(uid)
    
    def __on_worker_signal(self, uid, request_type, data):
        """
        Signaled whenever the worker completes something.
        This method will dispatch the work to different methods
        depending on what async task has completed.

        :param uid: Unique id for request
        :param request_type: String identifying the request class
        :param data: the data that was returned 
        """
        uid = shotgun_model.sanitize_qt(uid) # qstring on pyqt, str on pyside
        data = shotgun_model.sanitize_qt(data)
        if uid in self._guids:
            self._app.log_debug("Note update complete: %s" % data)
            self._guids.remove(uid)

    def mark_note_as_read(self, note_id):
        """
        Mark the note as read if it's unread.
        
        :param note_id: Shotgun note id to operate on
        """
        data = {"note_id": note_id }
        uid = self.__sg_data_retriever.execute_method(self._mark_note_as_read, data)
        self._guids.append(uid)
        
    def _mark_note_as_read(self, sg, data):
        """
        Async callback called by the data retriever.
        Sets the note read status to read in case the status is set to unread.
        """
        note_id = data["note_id"]
        
        sg_data = sg.find_one("Note", [["id", "is", note_id]], ["read_by_current_user"])
        if sg_data and sg_data["read_by_current_user"] == "unread":
            sg.update("Note", note_id, {"read_by_current_user": "read"})
        
