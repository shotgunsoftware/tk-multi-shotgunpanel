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


class WorkAreaButton(QtGui.QToolButton):
    """
    Work area widget
    """

    def __init__(self, right_side_offset, bottom_offset, parent):
        """
        :param model: Shotgun Model to monitor
        :param view: View to place overlay on top of.
        """
        super(WorkAreaButton, self).__init__(parent)

        self._bundle = sgtk.platform.current_bundle()

        self._right_side_offset = right_side_offset
        self._bottom_offset = bottom_offset

        self.setGeometry(QtCore.QRect(0, 0, 30, 30))

        self.icon = QtGui.QIcon()
        self.icon.addPixmap(
            QtGui.QPixmap(":/tk_multi_infopanel/rings.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.setIcon(self.icon)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)

        # hook up a listener to the parent window so this widget
        # follows along when the parent window changes size
        filter = ResizeEventFilter(parent)
        filter.resized.connect(self._on_parent_resized)
        parent.installEventFilter(filter)

        self._entity_type = None
        self._entity_id = None
        self._is_current = False

        self.clicked.connect(self._on_click)



    def set_up(self, entity_type, entity_id):
        self._entity_id = entity_id
        self._entity_type = entity_type

        # figure out if this is the current project
        context = self._bundle.context

        context_entity = context.task or context.entity or context.project or None

        if context_entity and context_entity["type"] == entity_type and context_entity["id"] == entity_id:
            self._is_current = True
            # button cannot be clicked
            self.setEnabled(False)
        else:
            self._is_current = False
            # button can clicked
            self.setEnabled(True)

    def _on_click(self):

        print "click"


    def leaveEvent(self, evt):
        self.setText("")
        self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.setGeometry(QtCore.QRect(
            self.parentWidget().width() - 30 - self._right_side_offset,
            self.parentWidget().height() - 30 - self._bottom_offset,
            30,
            30
        ))
        return super(WorkAreaButton, self).leaveEvent(evt)

    def enterEvent(self, evt):
        self.setText("Set Work Area")
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.setGeometry(QtCore.QRect(
            self.parentWidget().width() - 100 - self._right_side_offset,
            self.parentWidget().height() - 30 - self._bottom_offset,
            100,
            30
        ))
        return super(WorkAreaButton, self).enterEvent(evt)


    def _on_parent_resized(self):
        """
        Special slot hooked up to the event filter.
        When associated widget is resized this slot is being called.
        """
        # offset the position in such a way that it looks like
        # it is "hanging down" from the adjacent window.
        # these constants are purely aesthetic, decided after some
        # tweaking and trial and error.
        self.move(
            self.parentWidget().width() - self.width() - self._right_side_offset,
            self.parentWidget().height() - self.height() - self._bottom_offset
        )


class WorkAreaButtonDetailsArea(WorkAreaButton):

    def __init__(self, parent):
        """
        :param model: Shotgun Model to monitor
        :param view: View to place overlay on top of.
        """
        super(WorkAreaButtonDetailsArea, self).__init__(10, 10, parent)
        self.setObjectName("work_area_button_details_area")

        self.setStyleSheet("""

            QToolButton {
                color: #fff;
                font-size: 11px;
                font-weight: 100;
                border-radius: 3px;
                background-color: rgba(0, 200, 200, 20%);
            }

            QToolButton:pressed {
                background-color: blue;
                color: #ccc;
            }

            QToolButton:hover
            {
                background-color: #05AB6C;
            }

        """)


class WorkAreaButtonListItem(WorkAreaButton):

    def __init__(self, parent):
        """
        :param model: Shotgun Model to monitor
        :param view: View to place overlay on top of.
        """
        super(WorkAreaButtonListItem, self).__init__(4, 10, parent)
        self.setObjectName("work_area_button_list_item")

        self.setStyleSheet("""

            QToolButton {
                color: #fff;
                font-size: 11px;
                font-weight: 100;
                border-radius: 3px;
                background-color: rgba(200, 200, 200, 0%);
            }

            QToolButton:pressed {
                background-color: blue;
                color: #ccc;
            }

            QToolButton:hover
            {
                background-color: #05AB6C;
            }

        """)


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
