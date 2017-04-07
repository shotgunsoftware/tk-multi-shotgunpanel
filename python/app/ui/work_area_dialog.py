# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'work_area_dialog.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_WorkAreaDialog(object):
    def setupUi(self, WorkAreaDialog):
        WorkAreaDialog.setObjectName("WorkAreaDialog")
        WorkAreaDialog.resize(443, 467)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/tk_multi_infopanel/rings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        WorkAreaDialog.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(WorkAreaDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.top_frame = QtGui.QFrame(WorkAreaDialog)
        self.top_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.top_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.top_frame.setObjectName("top_frame")
        self.horizontalLayout = QtGui.QHBoxLayout(self.top_frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.icon = QtGui.QLabel(self.top_frame)
        self.icon.setMinimumSize(QtCore.QSize(40, 40))
        self.icon.setMaximumSize(QtCore.QSize(40, 40))
        self.icon.setText("")
        self.icon.setPixmap(QtGui.QPixmap(":/tk_multi_infopanel/pin_large.png"))
        self.icon.setScaledContents(True)
        self.icon.setObjectName("icon")
        self.horizontalLayout.addWidget(self.icon)
        self.top_text = QtGui.QLabel(self.top_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.top_text.sizePolicy().hasHeightForWidth())
        self.top_text.setSizePolicy(sizePolicy)
        self.top_text.setObjectName("top_text")
        self.horizontalLayout.addWidget(self.top_text)
        self.verticalLayout.addWidget(self.top_frame)
        self.task_list = QtGui.QListWidget(WorkAreaDialog)
        self.task_list.setObjectName("task_list")
        self.verticalLayout.addWidget(self.task_list)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.cancel = QtGui.QPushButton(WorkAreaDialog)
        self.cancel.setObjectName("cancel")
        self.horizontalLayout_2.addWidget(self.cancel)
        self.ok = QtGui.QPushButton(WorkAreaDialog)
        self.ok.setObjectName("ok")
        self.horizontalLayout_2.addWidget(self.ok)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(WorkAreaDialog)
        QtCore.QObject.connect(self.cancel, QtCore.SIGNAL("clicked()"), WorkAreaDialog.reject)
        QtCore.QObject.connect(self.ok, QtCore.SIGNAL("clicked()"), WorkAreaDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(WorkAreaDialog)

    def retranslateUi(self, WorkAreaDialog):
        WorkAreaDialog.setWindowTitle(QtGui.QApplication.translate("WorkAreaDialog", "Select your work area", None, QtGui.QApplication.UnicodeUTF8))
        self.top_text.setText(QtGui.QApplication.translate("WorkAreaDialog", "Choose a Work Area", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel.setText(QtGui.QApplication.translate("WorkAreaDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.ok.setText(QtGui.QApplication.translate("WorkAreaDialog", "Ok", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
from . import resources_rc
