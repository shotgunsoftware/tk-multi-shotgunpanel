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
import sgtk

from .ui.work_area_dialog import Ui_WorkAreaDialog


shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


class WorkAreaDialog(QtGui.QDialog):

    def __init__(self, entity_type, entity_id, parent):
        """
        :param model: Shotgun Model to monitor
        :param view: View to place overlay on top of.
        """
        super(WorkAreaDialog, self).__init__(parent)

        # now load in the UI that was created in the UI designer
        self.ui = Ui_WorkAreaDialog()
        self.ui.setupUi(self)

        self._bundle = sgtk.platform.current_bundle()

        main_item = self._bundle.shotgun.find_one(
            entity_type,
            [["id", "is", entity_id]],
            ["code", "description"]
        )

        if main_item.get("code"):
            entity_name = "%s %s" % (shotgun_globals.get_type_display_name(entity_type), main_item.get("code"))
        else:
            entity_name = "Unnamed %s" % shotgun_globals.get_type_display_name(entity_type)

        # insert main item
        self._main_item = QtGui.QListWidgetItem(entity_name, self.ui.task_list)
        self._main_item.setToolTip(main_item.get("description") or "No description found.")

        tasks = self._bundle.shotgun.find(
            "Task",
            [["entity", "is", {"type": entity_type, "id": entity_id}]],
            ["content", "step", "sg_status_list", "task_assignees"]
        )

        for task in tasks:
            task_name = "Task %s on %s" % (task["content"], entity_name)
            if task["task_assignees"]:
                task_name += " (%s)" % ", ".join([x["name"] for x in task["task_assignees"]])
            QtGui.QListWidgetItem(task_name, self.ui.task_list)


        self.new_task = QtGui.QWidget(self)
        self.new_task.setObjectName("new_task")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.new_task)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.task_name = QtGui.QLineEdit(self.new_task)
        self.task_name.setObjectName("task_name")
        self.horizontalLayout_2.addWidget(self.task_name)
        self.step_combo = QtGui.QComboBox(self.new_task)
        self.step_combo.setObjectName("step_combo")
        self.horizontalLayout_2.addWidget(self.step_combo)
        self.task_name.setPlaceholderText("Create new task...")

        self._new_item = QtGui.QListWidgetItem(self.ui.task_list)
        self.ui.task_list.setItemWidget(self._new_item, self.new_task)

        steps = self._bundle.shotgun.find(
            "Step",
            [["entity_type", "is", entity_type]],
            ["code", "id"]
        )

        for step in steps:
            self.step_combo.addItem(step["code"], step["id"])

        self.task_name.installEventFilter(self)


    def eventFilter(self, obj, event):
        """
        Event filter implementation.
        For information, see the QT docs:
        http://doc.qt.io/qt-4.8/qobject.html#eventFilter

        This will emit the resized signal (in this class)
        whenever the linked up object is being resized.

        :param obj: The object that is being watched for events
        :param event: Event object that the object has emitted
        :returns: Always returns False to indicate that no events
                  should ever be discarded by the filter.
        """
        # peek at the message
        if event.type() == QtCore.QEvent.FocusIn:
            # re-broadcast any resize events
            self._new_item.setSelected(True)
        # pass it on!
        return False
