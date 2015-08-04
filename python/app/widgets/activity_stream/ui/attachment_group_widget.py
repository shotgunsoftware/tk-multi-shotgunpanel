# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'attachment_group_widget.ui'
#
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_AttachmentGroupWidget(object):
    def setupUi(self, AttachmentGroupWidget):
        AttachmentGroupWidget.setObjectName("AttachmentGroupWidget")
        AttachmentGroupWidget.resize(217, 27)
        self.verticalLayout = QtGui.QVBoxLayout(AttachmentGroupWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.load_more = QtGui.QToolButton(AttachmentGroupWidget)
        self.load_more.setObjectName("load_more")
        self.verticalLayout.addWidget(self.load_more)
        self.attachment_layout = QtGui.QVBoxLayout()
        self.attachment_layout.setContentsMargins(2, 2, 2, 2)
        self.attachment_layout.setObjectName("attachment_layout")
        self.verticalLayout.addLayout(self.attachment_layout)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(AttachmentGroupWidget)
        QtCore.QMetaObject.connectSlotsByName(AttachmentGroupWidget)

    def retranslateUi(self, AttachmentGroupWidget):
        AttachmentGroupWidget.setWindowTitle(QtGui.QApplication.translate("AttachmentGroupWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.load_more.setText(QtGui.QApplication.translate("AttachmentGroupWidget", "...", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
from . import resources_rc
