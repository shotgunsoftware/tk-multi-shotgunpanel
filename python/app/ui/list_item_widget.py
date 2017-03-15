# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'list_item_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_ListItemWidget(object):
    def setupUi(self, ListItemWidget):
        ListItemWidget.setObjectName("ListItemWidget")
        ListItemWidget.resize(355, 105)
        self.horizontalLayout_3 = QtGui.QHBoxLayout(ListItemWidget)
        self.horizontalLayout_3.setSpacing(1)
        self.horizontalLayout_3.setContentsMargins(8, 4, 8, 4)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.box = QtGui.QFrame(ListItemWidget)
        self.box.setFrameShape(QtGui.QFrame.NoFrame)
        self.box.setObjectName("box")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.box)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setContentsMargins(4, 8, 4, 8)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.thumbnail = QtGui.QLabel(self.box)
        self.thumbnail.setMinimumSize(QtCore.QSize(96, 75))
        self.thumbnail.setMaximumSize(QtCore.QSize(96, 75))
        self.thumbnail.setText("")
        self.thumbnail.setPixmap(QtGui.QPixmap(":/tk_multi_infopanel/rect_512x400.png"))
        self.thumbnail.setScaledContents(True)
        self.thumbnail.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnail.setObjectName("thumbnail")
        self.horizontalLayout_2.addWidget(self.thumbnail)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.list_item_top_left = QtGui.QLabel(self.box)
        self.list_item_top_left.setObjectName("list_item_top_left")
        self.horizontalLayout.addWidget(self.list_item_top_left)
        self.list_item_top_right = QtGui.QLabel(self.box)
        self.list_item_top_right.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.list_item_top_right.setObjectName("list_item_top_right")
        self.horizontalLayout.addWidget(self.list_item_top_right)
        self.button = QtGui.QPushButton(self.box)
        self.button.setMaximumSize(QtCore.QSize(16, 16))
        self.button.setIconSize(QtCore.QSize(10, 10))
        self.button.setObjectName("button")
        self.horizontalLayout.addWidget(self.button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.list_item_body = QtGui.QLabel(self.box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_item_body.sizePolicy().hasHeightForWidth())
        self.list_item_body.setSizePolicy(sizePolicy)
        self.list_item_body.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.list_item_body.setWordWrap(True)
        self.list_item_body.setObjectName("list_item_body")
        self.verticalLayout.addWidget(self.list_item_body)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout_3.addWidget(self.box)

        self.retranslateUi(ListItemWidget)
        QtCore.QMetaObject.connectSlotsByName(ListItemWidget)

    def retranslateUi(self, ListItemWidget):
        ListItemWidget.setWindowTitle(QtGui.QApplication.translate("ListItemWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.list_item_top_left.setText(QtGui.QApplication.translate("ListItemWidget", "Hello World", None, QtGui.QApplication.UnicodeUTF8))
        self.list_item_top_right.setText(QtGui.QApplication.translate("ListItemWidget", "3 days ago", None, QtGui.QApplication.UnicodeUTF8))
        self.list_item_body.setText(QtGui.QApplication.translate("ListItemWidget", "Body text\n"
"hello", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
