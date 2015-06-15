# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'reply_list_widget.ui'
#
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_ReplyListWidget(object):
    def setupUi(self, ReplyListWidget):
        ReplyListWidget.setObjectName("ReplyListWidget")
        ReplyListWidget.resize(418, 401)
        self.verticalLayout = QtGui.QVBoxLayout(ReplyListWidget)
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setContentsMargins(1, 1, 1, 1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.reply_scroll_area = QtGui.QScrollArea(ReplyListWidget)
        self.reply_scroll_area.setWidgetResizable(True)
        self.reply_scroll_area.setObjectName("reply_scroll_area")
        self.reply_widget = QtGui.QWidget()
        self.reply_widget.setGeometry(QtCore.QRect(0, 0, 414, 397))
        self.reply_widget.setObjectName("reply_widget")
        self.verticalLayout_17 = QtGui.QVBoxLayout(self.reply_widget)
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.reply_layout = QtGui.QVBoxLayout()
        self.reply_layout.setObjectName("reply_layout")
        self.verticalLayout_17.addLayout(self.reply_layout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.thumbnail_2 = QtGui.QLabel(self.reply_widget)
        self.thumbnail_2.setMinimumSize(QtCore.QSize(60, 60))
        self.thumbnail_2.setMaximumSize(QtCore.QSize(60, 60))
        self.thumbnail_2.setText("")
        self.thumbnail_2.setPixmap(QtGui.QPixmap(":/tk_multi_infopanel_reply_widget/default_user.png"))
        self.thumbnail_2.setScaledContents(True)
        self.thumbnail_2.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.thumbnail_2.setObjectName("thumbnail_2")
        self.horizontalLayout.addWidget(self.thumbnail_2)
        self.entity_note_input = NoteInputWidget(self.reply_widget)
        self.entity_note_input.setMinimumSize(QtCore.QSize(0, 40))
        self.entity_note_input.setObjectName("entity_note_input")
        self.horizontalLayout.addWidget(self.entity_note_input)
        self.verticalLayout_17.addLayout(self.horizontalLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_17.addItem(spacerItem)
        self.reply_scroll_area.setWidget(self.reply_widget)
        self.verticalLayout.addWidget(self.reply_scroll_area)

        self.retranslateUi(ReplyListWidget)
        QtCore.QMetaObject.connectSlotsByName(ReplyListWidget)

    def retranslateUi(self, ReplyListWidget):
        ReplyListWidget.setWindowTitle(QtGui.QApplication.translate("ReplyListWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))

from ...note_input_widget import NoteInputWidget
from . import resources_rc
