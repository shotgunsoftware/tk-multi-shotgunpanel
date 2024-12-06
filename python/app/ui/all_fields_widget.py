# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'all_fields_widget.ui'
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


class Ui_AllFieldsWidget(object):
    def setupUi(self, AllFieldsWidget):
        if not AllFieldsWidget.objectName():
            AllFieldsWidget.setObjectName(u"AllFieldsWidget")
        AllFieldsWidget.resize(337, 645)
        self.verticalLayout = QVBoxLayout(AllFieldsWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.all_fields_scroll_area = QScrollArea(AllFieldsWidget)
        self.all_fields_scroll_area.setObjectName(u"all_fields_scroll_area")
        self.all_fields_scroll_area.setWidgetResizable(True)
        self.all_fields_host = QWidget()
        self.all_fields_host.setObjectName(u"all_fields_host")
        self.all_fields_host.setGeometry(QRect(0, 0, 335, 643))
        self.all_fields_layout = QGridLayout(self.all_fields_host)
        self.all_fields_layout.setSpacing(0)
        self.all_fields_layout.setContentsMargins(0, 0, 0, 0)
        self.all_fields_layout.setObjectName(u"all_fields_layout")
        self.all_fields_scroll_area.setWidget(self.all_fields_host)

        self.verticalLayout.addWidget(self.all_fields_scroll_area)

        self.retranslateUi(AllFieldsWidget)

        QMetaObject.connectSlotsByName(AllFieldsWidget)
    # setupUi

    def retranslateUi(self, AllFieldsWidget):
        AllFieldsWidget.setWindowTitle(QCoreApplication.translate("AllFieldsWidget", u"Form", None))
    # retranslateUi
