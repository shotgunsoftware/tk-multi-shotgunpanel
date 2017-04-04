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



class WorkAreaButtonDetailsArea(QtGui.QToolButton):
    """
    UX for switching work area.

    This displays a "change work area" button which a user can interact with
    The button is designed to expand so that it is subtle until a user
    hovers over it.

    :signal clicked(str, int): Fires when someone clicks the change
        work area button. Arguments passed are the entity type and entity id
    """

    WIDGET_WIDTH_COLLAPSED = 30
    WIDGET_HEIGHT = 30

    NON_WORK_AREA_TYPES = [
        "PublishedFile",
        "Project",
        "TankPublishedFile",
        "Version",
        "Note",
        "Group",
        "HumanUser",
        "ScriptUser",
        "ApiUser",
        "ClientUser",
        "Department",
        "Cut",
        "CutItem",
        "Delivery",
        "Playlist",
        "Ticket"
    ]

    change_work_area = QtCore.Signal(str, int)

    def __init__(self, parent):
        """
        :param parent: The model parent.
        :type parent: :class:`~PySide.QtGui.QObject`
        """
        super(WorkAreaButtonDetailsArea, self).__init__(parent)

        self._icon = QtGui.QIcon()
        self._icon.addPixmap(
            QtGui.QPixmap(":/tk_multi_infopanel/pin.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self._icon.addPixmap(
            QtGui.QPixmap(":/tk_multi_infopanel/pin_white.png"),
            QtGui.QIcon.Disabled,
            QtGui.QIcon.Off
        )
        self.setIcon(self._icon)
        self.setIconSize(QtCore.QSize(self.WIDGET_WIDTH_COLLAPSED, self.WIDGET_HEIGHT))

        self._bundle = sgtk.platform.current_bundle()

        self._entity_type = None
        self._entity_id = None
        self._is_current = False

        self._caption = "Set Work Area"
        self._width = 120

        self.clicked.connect(self._on_click)

        self.setVisible(False)


    def set_up(self, entity_type, entity_id):
        """
        Sets up the button for a given entity.
        Typically implemented by subclasses.

        :param entity_type: Entity type to set up button for
        :param entity_id: Entity id to set up button for
        """
        self._entity_id = entity_id
        self._entity_type = entity_type

        if not self._bundle.get_setting("enable_context_switch"):
            # context switch button not enabled
            return

        # figure out if this is the current project
        context = self._bundle.context
        context_entity = context.task or context.entity or context.project or None

        self.setVisible(True)

        if context_entity and context_entity["type"] == entity_type and context_entity["id"] == entity_id:
            self._is_current = True
            self.setPopupMode(QtGui.QToolButton.DelayedPopup)
            self.setToolTip(
                "This is your current work area.\n"
                "The work you do will be associated with this item in Shotgun."
            )

        elif entity_type in self.NON_WORK_AREA_TYPES:
            # don't show the ctx selector for some types
            self.setVisible(False)

        else:
            self._is_current = False

            if entity_type == "Task":
                self._caption = "Set Work Area"
                self.setToolTip("Click to set your work area to the current task.")

            else:
                self._caption = "Pick Work Area"
                self.setToolTip("Click to select a task.")

        # button cannot be clicked
        self.setEnabled(not self._is_current)

        # tell the style sheet to adjust
        self.setProperty("is_current", self._is_current)
        self.style().unpolish(self)
        self.style().polish(self)

        self._init_default_state()

    def _init_default_state(self):
        """
        Sets up the default collapsed state of the button
        """
        self.setText("")
        self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.setMinimumSize(QtCore.QSize(self.WIDGET_WIDTH_COLLAPSED, self.WIDGET_HEIGHT))
        self.setMaximumSize(QtCore.QSize(self.WIDGET_WIDTH_COLLAPSED, self.WIDGET_HEIGHT))
        # tell the style sheet to adjust
        self.setProperty("is_expanded", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def _on_click(self):
        """
        Executed when the button is clicked
        """
        self.change_work_area.emit(self._entity_type, self._entity_id)

    def enterEvent(self, evt):
        """
        QT Mouse enter event
        """
        if not self._is_current:
            # not the current work area. so expand the button
            self.setText(self._caption)
            self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
            self.setMinimumSize(QtCore.QSize(self._width, self.WIDGET_HEIGHT))
            self.setMaximumSize(QtCore.QSize(self._width, self.WIDGET_HEIGHT))
            # tell the style sheet to adjust
            self.setProperty("is_expanded", True)
            self.style().unpolish(self)
            self.style().polish(self)

        return super(WorkAreaButtonDetailsArea, self).enterEvent(evt)

    def leaveEvent(self, evt):
        """
        QT Mouse leave event
        """
        if not self._is_current:
            # collapse button after a delay
            QtCore.QTimer.singleShot(300, self._init_default_state)

        return super(WorkAreaButtonDetailsArea, self).leaveEvent(evt)




class WorkAreaButtonListItem(WorkAreaButtonDetailsArea):
    """
    UX for switching work area.

    This displays a "change work area" button which a user can interact with
    The button is designed to expand so that it is subtle until a user
    hovers over it.

    Derives from :class:`WorkAreaButtonDetailsArea` and positions the widget
    relative to the bottom-right corner of the parent widget.

    :signal clicked(str, int): Fires when someone clicks the change
        work area button. Arguments passed are the entity type and entity id
    """

    RIGHT_OFFSET = 6
    BOTTOM_OFFSET = 6

    def __init__(self, parent):
        """
        :param right_side_offset: Right hand side offset in pixels
        :param bottom_offset: Bottom offset in pixels
        :param parent: The model parent.
        :type parent: :class:`~PySide.QtGui.QObject`
        """
        super(WorkAreaButtonListItem, self).__init__(parent)

        # hook up a listener to the parent window so this widget
        # follows along when the parent window changes size
        filter = ResizeEventFilter(parent)
        filter.resized.connect(self._on_parent_resized)
        parent.installEventFilter(filter)

    def __position_widget(self):
        """
        Moves the widget to the bottom-right corner of the parent widget.
        """
        self.move(
            self.parentWidget().width() - self.width() - self.RIGHT_OFFSET,
            self.parentWidget().height() - self.height() - self.BOTTOM_OFFSET
        )

    def _init_default_state(self):
        """
        Sets up the default collapsed state of the button
        """
        super(WorkAreaButtonListItem, self)._init_default_state()
        self.__position_widget()

    def enterEvent(self, evt):
        """
        QT Mouse enter event
        """
        status = super(WorkAreaButtonListItem, self).enterEvent(evt)

        if not self._is_current:
            self.__position_widget()

        return status

    def _on_parent_resized(self):
        """
        Special slot hooked up to the event filter.
        When associated widget is resized this slot is being called.
        """
        self.__position_widget()


class ResizeEventFilter(QtCore.QObject):
    """
    Utility and helper.

    Event filter which emits a resized signal whenever
    the monitored widget resizes.

    You use it like this:

    # create the filter object. Typically, it's
    # it's easiest to parent it to the object that is
    # being monitored (in this case self.ui.thumbnail)
    filter = ResizeEventFilter(self.ui.thumbnail)

    # now set up a signal/slot connection so that the
    # __on_thumb_resized slot gets called every time
    # the widget is resized
    filter.resized.connect(self.__on_thumb_resized)

    # finally, install the event filter into the QT
    # event system
    self.ui.thumbnail.installEventFilter(filter)
    """
    resized = QtCore.Signal()

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
        if event.type() == QtCore.QEvent.Resize:
            # re-broadcast any resize events
            self.resized.emit()
        # pass it on!
        return False
