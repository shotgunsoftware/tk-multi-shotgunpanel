# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'note_widget.ui'
#
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_NoteWidget(object):
    def setupUi(self, NoteWidget):
        NoteWidget.setObjectName("NoteWidget")
        NoteWidget.resize(290, 70)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(NoteWidget)
        self.horizontalLayout_2.setSpacing(8)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.user_thumb = UserLabel(NoteWidget)
        self.user_thumb.setMinimumSize(QtCore.QSize(50, 50))
        self.user_thumb.setMaximumSize(QtCore.QSize(50, 50))
        self.user_thumb.setText("")
        self.user_thumb.setPixmap(QtGui.QPixmap(":/tk_multi_infopanel_activity_stream/default_user.png"))
        self.user_thumb.setScaledContents(True)
        self.user_thumb.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.user_thumb.setObjectName("user_thumb")
        self.verticalLayout_2.addWidget(self.user_thumb)
        spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.frame = QtGui.QFrame(NoteWidget)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.header_left = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header_left.sizePolicy().hasHeightForWidth())
        self.header_left.setSizePolicy(sizePolicy)
        self.header_left.setText("")
        self.header_left.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.header_left.setWordWrap(True)
        self.header_left.setObjectName("header_left")
        self.horizontalLayout.addWidget(self.header_left)
        self.date = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.date.sizePolicy().hasHeightForWidth())
        self.date.setSizePolicy(sizePolicy)
        self.date.setText("")
        self.date.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.date.setWordWrap(True)
        self.date.setObjectName("date")
        self.horizontalLayout.addWidget(self.date)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.footer = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.footer.sizePolicy().hasHeightForWidth())
        self.footer.setSizePolicy(sizePolicy)
        self.footer.setText("")
        self.footer.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.footer.setWordWrap(True)
        self.footer.setObjectName("footer")
        self.verticalLayout.addWidget(self.footer)
        self.horizontalLayout_2.addWidget(self.frame)

        self.retranslateUi(NoteWidget)
        QtCore.QMetaObject.connectSlotsByName(NoteWidget)

    def retranslateUi(self, NoteWidget):
        NoteWidget.setWindowTitle(QtGui.QApplication.translate("NoteWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))

from ..user_label import UserLabel
from . import resources_rc
from . import resources_rc
