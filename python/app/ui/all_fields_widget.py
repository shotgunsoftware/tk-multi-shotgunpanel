# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'all_fields_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_AllFieldsWidget(object):
    def setupUi(self, AllFieldsWidget):
        AllFieldsWidget.setObjectName("AllFieldsWidget")
        AllFieldsWidget.resize(337, 645)
        self.verticalLayout = QtGui.QVBoxLayout(AllFieldsWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.all_fields_scroll_area = QtGui.QScrollArea(AllFieldsWidget)
        self.all_fields_scroll_area.setWidgetResizable(True)
        self.all_fields_scroll_area.setObjectName("all_fields_scroll_area")
        self.all_fields_host = QtGui.QWidget()
        self.all_fields_host.setGeometry(QtCore.QRect(0, 0, 335, 643))
        self.all_fields_host.setObjectName("all_fields_host")
        self.all_fields_layout = QtGui.QGridLayout(self.all_fields_host)
        self.all_fields_layout.setContentsMargins(0, 0, 0, 0)
        self.all_fields_layout.setSpacing(0)
        self.all_fields_layout.setObjectName("all_fields_layout")
        self.all_fields_scroll_area.setWidget(self.all_fields_host)
        self.verticalLayout.addWidget(self.all_fields_scroll_area)

        self.retranslateUi(AllFieldsWidget)
        QtCore.QMetaObject.connectSlotsByName(AllFieldsWidget)

    def retranslateUi(self, AllFieldsWidget):
        AllFieldsWidget.setWindowTitle(QtGui.QApplication.translate("AllFieldsWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))

