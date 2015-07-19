# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'note_input_widget.ui'
#
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_NoteInputWidget(object):
    def setupUi(self, NoteInputWidget):
        NoteInputWidget.setObjectName("NoteInputWidget")
        NoteInputWidget.resize(537, 80)
        NoteInputWidget.setMinimumSize(QtCore.QSize(0, 80))
        NoteInputWidget.setMaximumSize(QtCore.QSize(16777215, 80))
        self.horizontalLayout = QtGui.QHBoxLayout(NoteInputWidget)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.text_entry = NoteEditor(NoteInputWidget)
        self.text_entry.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.text_entry.setObjectName("text_entry")
        self.horizontalLayout.addWidget(self.text_entry)
        self.thumbnail = QtGui.QLabel(NoteInputWidget)
        self.thumbnail.setEnabled(True)
        self.thumbnail.setMinimumSize(QtCore.QSize(96, 75))
        self.thumbnail.setMaximumSize(QtCore.QSize(96, 75))
        self.thumbnail.setText("")
        self.thumbnail.setPixmap(QtGui.QPixmap(":/tk_multi_infopanel/rect_512x400.png"))
        self.thumbnail.setScaledContents(True)
        self.thumbnail.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnail.setObjectName("thumbnail")
        self.horizontalLayout.addWidget(self.thumbnail)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.screenshot = QtGui.QToolButton(NoteInputWidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/tk_multi_infopanel_note_input_widget/camera_hl.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.screenshot.setIcon(icon)
        self.screenshot.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.screenshot.setAutoRaise(True)
        self.screenshot.setObjectName("screenshot")
        self.verticalLayout.addWidget(self.screenshot)
        self.submit = QtGui.QToolButton(NoteInputWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.submit.sizePolicy().hasHeightForWidth())
        self.submit.setSizePolicy(sizePolicy)
        self.submit.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/tk_multi_infopanel_note_input_widget/tick.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.submit.setIcon(icon1)
        self.submit.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.submit.setAutoRaise(True)
        self.submit.setObjectName("submit")
        self.verticalLayout.addWidget(self.submit)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(NoteInputWidget)
        QtCore.QMetaObject.connectSlotsByName(NoteInputWidget)

    def retranslateUi(self, NoteInputWidget):
        NoteInputWidget.setWindowTitle(QtGui.QApplication.translate("NoteInputWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.screenshot.setToolTip(QtGui.QApplication.translate("NoteInputWidget", "Take a screenshot", None, QtGui.QApplication.UnicodeUTF8))
        self.screenshot.setText(QtGui.QApplication.translate("NoteInputWidget", "Attach Screenshot", None, QtGui.QApplication.UnicodeUTF8))
        self.submit.setToolTip(QtGui.QApplication.translate("NoteInputWidget", "Create Note", None, QtGui.QApplication.UnicodeUTF8))

from ..note_editor import NoteEditor
from . import resources_rc
