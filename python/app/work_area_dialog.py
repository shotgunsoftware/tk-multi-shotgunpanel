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
from .ui.work_area_dialog import Ui_WorkAreaDialog

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


class WorkAreaDialog(QtGui.QDialog):
    """
    Task selector and creator dialog
    """
    ENTITY_TYPE_ROLE = QtCore.Qt.UserRole + 1001
    ENTITY_ID_ROLE = QtCore.Qt.UserRole + 1002

    def __init__(self, entity_type, entity_id, parent):
        """
        :param entity_type: Entity type to display tasks for
        :param entity_id: Entity id to display tasks for
        :param parent: The model parent.
        :type parent: :class:`~PySide.QtGui.QObject`
        """
        super(WorkAreaDialog, self).__init__(parent)

        # now load in the UI that was created in the UI designer
        self.ui = Ui_WorkAreaDialog()
        self.ui.setupUi(self)

        # double clicking an item in the list closes the dialog
        self.ui.task_list.itemDoubleClicked.connect(self.accept)

        self._bundle = sgtk.platform.current_bundle()

        # find information about the main item
        main_item = self._bundle.shotgun.find_one(
            entity_type,
            [["id", "is", entity_id]],
            ["code", "description"]
        )

        if main_item.get("code"):
            entity_name = "%s %s" % (shotgun_globals.get_type_display_name(entity_type), main_item.get("code"))
        else:
            entity_name = "Unnamed %s" % shotgun_globals.get_type_display_name(entity_type)

        # # insert main item
        # self._main_item = QtGui.QListWidgetItem(entity_name, self.ui.task_list)
        # self._main_item.setToolTip(main_item.get("description") or "No description found.")
        # self._main_item.setData(self.ENTITY_TYPE_ROLE, entity_type)
        # self._main_item.setData(self.ENTITY_ID_ROLE, entity_id)
        #
        # # make this selected by default
        # self._main_item.setSelected(True)

        # now get all tasks from Shotgun
        tasks = self._bundle.shotgun.find(
            "Task",
            [["entity", "is", {"type": entity_type, "id": entity_id}]],
            ["content", "step", "sg_status_list", "task_assignees"]
        )

        # insert into list
        for task in tasks:
            task_name = "Task %s on %s" % (task["content"], entity_name)
            # indicate users assigned
            if task["task_assignees"]:
                task_name += " (%s)" % ", ".join([x["name"] for x in task["task_assignees"]])
            task_item = QtGui.QListWidgetItem(task_name, self.ui.task_list)
            task_item.setData(self.ENTITY_TYPE_ROLE, task["type"])
            task_item.setData(self.ENTITY_ID_ROLE, task["id"])

        # as the last item, create the "create new task widget"
        # embedded into a list widget
        self.new_task = QtGui.QWidget(self)
        self.new_task.setObjectName("new_task")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.new_task)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.task_name = QtGui.QLineEdit(self.new_task)
        self.task_name.setObjectName("task_name")
        self.horizontalLayout_2.addWidget(self.task_name)
        self.step_combo = QtGui.QComboBox(self.new_task)
        self.step_combo.setObjectName("step_combo")
        self.horizontalLayout_2.addWidget(self.step_combo)
        self.task_name.setPlaceholderText("Create new task...")

        self._new_item = QtGui.QListWidgetItem(self.ui.task_list)
        self.ui.task_list.setItemWidget(self._new_item, self.new_task)

        # find the steps for this entity type
        steps = self._bundle.shotgun.find(
            "Step",
            [["entity_type", "is", entity_type]],
            ["code", "id"]
        )

        # populate combo box
        for step in steps:
            self.step_combo.addItem(step["code"], step["id"])

        # install filter so that when the task name is clicked
        # the list widget is selected
        self.task_name.installEventFilter(self)

    @property
    def is_new_task(self):
        """
        Returns true if the selected object is a new task
        """
        return self._new_item.isSelected()

    @property
    def new_task_name(self):
        """
        The new task name for new tasks or "" if not set
        """
        return self.task_name.text()

    @property
    def new_step_id(self):
        """
        Step if for new task or None if not set
        """
        return self.step_combo.itemData(self.step_combo.currentIndex())

    @property
    def selected_entity(self):
        """
        The selected (entity_type, entity_id) or
        (None, None) if a new task is selected
        """
        if self.is_new_task:
            return None, None
        else:
            current_item = self.ui.task_list.currentItem()
            return (
                current_item.data(self.ENTITY_TYPE_ROLE),
                current_item.data(self.ENTITY_ID_ROLE)
            )

    def eventFilter(self, obj, event):
        """
        Event filter implementation.
        For information, see the QT docs:
        http://doc.qt.io/qt-4.8/qobject.html#eventFilter

        Will select the "new item" listitem if someone
        clicks on the task name widget.

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
