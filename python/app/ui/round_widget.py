# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'round_widget.ui'
#
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_RoundWidget(object):
    def setupUi(self, RoundWidget):
        RoundWidget.setObjectName("RoundWidget")
        RoundWidget.resize(394, 86)
        self.horizontalLayout_3 = QtGui.QHBoxLayout(RoundWidget)
        self.horizontalLayout_3.setSpacing(1)
        self.horizontalLayout_3.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.box = QtGui.QFrame(RoundWidget)
        self.box.setFrameShape(QtGui.QFrame.StyledPanel)
        self.box.setFrameShadow(QtGui.QFrame.Raised)
        self.box.setObjectName("box")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.box)
        self.horizontalLayout_2.setSpacing(4)
        self.horizontalLayout_2.setContentsMargins(1, 2, 1, 2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.thumbnail = QtGui.QLabel(self.box)
        self.thumbnail.setMinimumSize(QtCore.QSize(75, 75))
        self.thumbnail.setMaximumSize(QtCore.QSize(75, 75))
        self.thumbnail.setStyleSheet("margin: 10px")
        self.thumbnail.setText("")
        self.thumbnail.setPixmap(QtGui.QPixmap(":/tk_multi_infopanel/default_user.png"))
        self.thumbnail.setScaledContents(True)
        self.thumbnail.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnail.setObjectName("thumbnail")
        self.horizontalLayout_2.addWidget(self.thumbnail)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.header_label = QtGui.QLabel(self.box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header_label.sizePolicy().hasHeightForWidth())
        self.header_label.setSizePolicy(sizePolicy)
        self.header_label.setObjectName("header_label")
        self.horizontalLayout.addWidget(self.header_label)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.body_label = QtGui.QLabel(self.box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.body_label.sizePolicy().hasHeightForWidth())
        self.body_label.setSizePolicy(sizePolicy)
        self.body_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.body_label.setWordWrap(True)
        self.body_label.setObjectName("body_label")
        self.verticalLayout.addWidget(self.body_label)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout_3.addWidget(self.box)

        self.retranslateUi(RoundWidget)
        QtCore.QMetaObject.connectSlotsByName(RoundWidget)

    def retranslateUi(self, RoundWidget):
        RoundWidget.setWindowTitle(QtGui.QApplication.translate("RoundWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.header_label.setText(QtGui.QApplication.translate("RoundWidget", "Header", None, QtGui.QApplication.UnicodeUTF8))
        self.body_label.setText(QtGui.QApplication.translate("RoundWidget", "TextLabel\n"
"Foo\n"
"Bar", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
