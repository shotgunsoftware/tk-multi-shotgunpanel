# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'list_item_widget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from tank.platform.qt import QtCore
for name, cls in QtCore.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls

from tank.platform.qt import QtGui
for name, cls in QtGui.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls


from  . import resources_rc

class Ui_ListItemWidget(object):
    def setupUi(self, ListItemWidget):
        if not ListItemWidget.objectName():
            ListItemWidget.setObjectName(u"ListItemWidget")
        ListItemWidget.resize(355, 105)
        self.horizontalLayout_3 = QHBoxLayout(ListItemWidget)
        self.horizontalLayout_3.setSpacing(1)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(8, 4, 8, 4)
        self.box = QFrame(ListItemWidget)
        self.box.setObjectName(u"box")
        self.box.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_2 = QHBoxLayout(self.box)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(4, 8, 4, 8)
        self.thumbnail = QLabel(self.box)
        self.thumbnail.setObjectName(u"thumbnail")
        self.thumbnail.setMinimumSize(QSize(96, 75))
        self.thumbnail.setMaximumSize(QSize(96, 75))
        self.thumbnail.setPixmap(QPixmap(u":/tk_multi_infopanel/rect_512x400.png"))
        self.thumbnail.setScaledContents(True)
        self.thumbnail.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.thumbnail)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.list_item_top_left = QLabel(self.box)
        self.list_item_top_left.setObjectName(u"list_item_top_left")

        self.horizontalLayout.addWidget(self.list_item_top_left)

        self.list_item_top_right = QLabel(self.box)
        self.list_item_top_right.setObjectName(u"list_item_top_right")
        self.list_item_top_right.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout.addWidget(self.list_item_top_right)

        self.button = QPushButton(self.box)
        self.button.setObjectName(u"button")
        self.button.setMaximumSize(QSize(16, 16))
        self.button.setIconSize(QSize(10, 10))

        self.horizontalLayout.addWidget(self.button)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.list_item_body = QLabel(self.box)
        self.list_item_body.setObjectName(u"list_item_body")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_item_body.sizePolicy().hasHeightForWidth())
        self.list_item_body.setSizePolicy(sizePolicy)
        self.list_item_body.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.list_item_body.setWordWrap(True)

        self.verticalLayout.addWidget(self.list_item_body)

        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.horizontalLayout_3.addWidget(self.box)

        self.retranslateUi(ListItemWidget)

        QMetaObject.connectSlotsByName(ListItemWidget)
    # setupUi

    def retranslateUi(self, ListItemWidget):
        ListItemWidget.setWindowTitle(QCoreApplication.translate("ListItemWidget", u"Form", None))
        self.thumbnail.setText("")
        self.list_item_top_left.setText(QCoreApplication.translate("ListItemWidget", u"Hello World", None))
        self.list_item_top_right.setText(QCoreApplication.translate("ListItemWidget", u"3 days ago", None))
        self.list_item_body.setText(QCoreApplication.translate("ListItemWidget", u"Body text\n"
"hello", None))
    # retranslateUi
