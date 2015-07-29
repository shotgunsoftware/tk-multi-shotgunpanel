# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'loading_widget.ui'
#
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_LoadingWidget(object):
    def setupUi(self, LoadingWidget):
        LoadingWidget.setObjectName("LoadingWidget")
        LoadingWidget.resize(336, 16)
        self.horizontalLayout = QtGui.QHBoxLayout(LoadingWidget)
        self.horizontalLayout.setSpacing(8)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.filler = QtGui.QLabel(LoadingWidget)
        self.filler.setMinimumSize(QtCore.QSize(60, 0))
        self.filler.setMaximumSize(QtCore.QSize(60, 16777215))
        self.filler.setText("")
        self.filler.setScaledContents(True)
        self.filler.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.filler.setObjectName("filler")
        self.horizontalLayout.addWidget(self.filler)
        self.loading_frame = QtGui.QFrame(LoadingWidget)
        self.loading_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.loading_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.loading_frame.setObjectName("loading_frame")
        self.verticalLayout = QtGui.QVBoxLayout(self.loading_frame)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.loading_label = QtGui.QLabel(self.loading_frame)
        self.loading_label.setAlignment(QtCore.Qt.AlignCenter)
        self.loading_label.setObjectName("loading_label")
        self.verticalLayout.addWidget(self.loading_label)
        self.horizontalLayout.addWidget(self.loading_frame)

        self.retranslateUi(LoadingWidget)
        QtCore.QMetaObject.connectSlotsByName(LoadingWidget)

    def retranslateUi(self, LoadingWidget):
        LoadingWidget.setWindowTitle(QtGui.QApplication.translate("LoadingWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.loading_label.setText(QtGui.QApplication.translate("LoadingWidget", "<i><small>Getting the latest updates...</small></i>", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
