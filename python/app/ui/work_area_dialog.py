# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'work_area_dialog.ui'
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
from  . import resources_rc

class Ui_WorkAreaDialog(object):
    def setupUi(self, WorkAreaDialog):
        if not WorkAreaDialog.objectName():
            WorkAreaDialog.setObjectName(u"WorkAreaDialog")
        WorkAreaDialog.resize(443, 467)
        icon1 = QIcon()
        icon1.addFile(u":/tk_multi_infopanel/rings.png", QSize(), QIcon.Normal, QIcon.Off)
        WorkAreaDialog.setWindowIcon(icon1)
        self.verticalLayout = QVBoxLayout(WorkAreaDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.top_frame = QFrame(WorkAreaDialog)
        self.top_frame.setObjectName(u"top_frame")
        self.top_frame.setFrameShape(QFrame.StyledPanel)
        self.top_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.top_frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.icon = QLabel(self.top_frame)
        self.icon.setObjectName(u"icon")
        self.icon.setMinimumSize(QSize(40, 40))
        self.icon.setMaximumSize(QSize(40, 40))
        self.icon.setPixmap(QPixmap(u":/tk_multi_infopanel/pin_large.png"))
        self.icon.setScaledContents(True)

        self.horizontalLayout.addWidget(self.icon)

        self.top_text = QLabel(self.top_frame)
        self.top_text.setObjectName(u"top_text")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.top_text.sizePolicy().hasHeightForWidth())
        self.top_text.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.top_text)

        self.verticalLayout.addWidget(self.top_frame)

        self.task_list = QListWidget(WorkAreaDialog)
        self.task_list.setObjectName(u"task_list")

        self.verticalLayout.addWidget(self.task_list)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.cancel = QPushButton(WorkAreaDialog)
        self.cancel.setObjectName(u"cancel")

        self.horizontalLayout_2.addWidget(self.cancel)

        self.ok = QPushButton(WorkAreaDialog)
        self.ok.setObjectName(u"ok")

        self.horizontalLayout_2.addWidget(self.ok)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(WorkAreaDialog)
        self.cancel.clicked.connect(WorkAreaDialog.reject)
        self.ok.clicked.connect(WorkAreaDialog.accept)

        QMetaObject.connectSlotsByName(WorkAreaDialog)
    # setupUi

    def retranslateUi(self, WorkAreaDialog):
        WorkAreaDialog.setWindowTitle(QCoreApplication.translate("WorkAreaDialog", u"Select your work area", None))
        self.icon.setText("")
        self.top_text.setText(QCoreApplication.translate("WorkAreaDialog", u"Choose a Work Area", None))
        self.cancel.setText(QCoreApplication.translate("WorkAreaDialog", u"Cancel", None))
        self.ok.setText(QCoreApplication.translate("WorkAreaDialog", u"Ok", None))
    # retranslateUi
