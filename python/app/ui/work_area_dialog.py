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
        self.icon.setPixmap(QtGui.QPixmap(":/tk_multi_infopanel/rings_large.png"))
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
        self.buttonBox = QtGui.QDialogButtonBox(WorkAreaDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(WorkAreaDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), WorkAreaDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), WorkAreaDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(WorkAreaDialog)

    def retranslateUi(self, WorkAreaDialog):
        WorkAreaDialog.setWindowTitle(QtGui.QApplication.translate("WorkAreaDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.top_text.setText(QtGui.QApplication.translate("WorkAreaDialog", "Choose your work area", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
from . import resources_rc
