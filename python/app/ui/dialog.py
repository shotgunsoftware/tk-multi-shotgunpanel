# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(451, 863)
        self.verticalLayout_7 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.navigation_home = QtGui.QToolButton(Dialog)
        self.navigation_home.setMinimumSize(QtCore.QSize(40, 40))
        self.navigation_home.setMaximumSize(QtCore.QSize(40, 40))
        self.navigation_home.setStyleSheet("QToolButton{\n"
"   border: none;\n"
"   background-color: none;\n"
"   background-repeat: no-repeat;\n"
"   background-position: center center;\n"
"   background-image: url(:/tk_multi_infopanel/home.png);\n"
"}\n"
"\n"
"QToolButton:hover{\n"
"background-image: url(:/tk_multi_infopanel/home_hover.png);\n"
"}\n"
"\n"
"QToolButton:Pressed {\n"
"background-image: url(:/tk_multi_infopanel/home_pressed.png);\n"
"}\n"
"")
        self.navigation_home.setObjectName("navigation_home")
        self.horizontalLayout_2.addWidget(self.navigation_home)
        self.navigation_prev = QtGui.QToolButton(Dialog)
        self.navigation_prev.setMinimumSize(QtCore.QSize(40, 40))
        self.navigation_prev.setMaximumSize(QtCore.QSize(40, 40))
        self.navigation_prev.setStyleSheet("QToolButton{\n"
"   border: none;\n"
"   background-color: none;\n"
"   background-repeat: no-repeat;\n"
"   background-position: center center;\n"
"   background-image: url(:/tk_multi_infopanel/left_arrow.png);\n"
"}\n"
"\n"
"QToolButton:disabled{\n"
"   background-image: url(:/tk_multi_infopanel/left_arrow_disabled.png);\n"
"}\n"
"\n"
"QToolButton:hover{\n"
"background-image: url(:/tk_multi_infopanel/left_arrow_hover.png);\n"
"}\n"
"\n"
"QToolButton:Pressed {\n"
"background-image: url(:/tk_multi_infopanel/left_arrow_pressed.png);\n"
"}\n"
"")
        self.navigation_prev.setObjectName("navigation_prev")
        self.horizontalLayout_2.addWidget(self.navigation_prev)
        self.navigation_next = QtGui.QToolButton(Dialog)
        self.navigation_next.setMinimumSize(QtCore.QSize(40, 40))
        self.navigation_next.setMaximumSize(QtCore.QSize(40, 40))
        self.navigation_next.setStyleSheet("QToolButton{\n"
"   border: none;\n"
"   background-color: none;\n"
"   background-repeat: no-repeat;\n"
"   background-position: center center;\n"
"   background-image: url(:/tk_multi_infopanel/right_arrow.png);\n"
"}\n"
"\n"
"QToolButton:disabled{\n"
"   background-image: url(:/tk_multi_infopanel/right_arrow_disabled.png);\n"
"}\n"
"\n"
"\n"
"QToolButton:hover{\n"
"background-image: url(:/tk_multi_infopanel/right_arrow_hover.png);\n"
"}\n"
"\n"
"QToolButton:Pressed {\n"
"background-image: url(:/tk_multi_infopanel/right_arrow_pressed.png);\n"
"}\n"
"")
        self.navigation_next.setObjectName("navigation_next")
        self.horizontalLayout_2.addWidget(self.navigation_next)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout_7.addLayout(self.horizontalLayout_2)
        self.line = QtGui.QFrame(Dialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_7.addWidget(self.line)
        self.details = QtGui.QWidget(Dialog)
        self.details.setObjectName("details")
        self.gridLayout = QtGui.QGridLayout(self.details)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.details_thumb = VersionLabel(self.details)
        self.details_thumb.setMinimumSize(QtCore.QSize(192, 150))
        self.details_thumb.setMaximumSize(QtCore.QSize(192, 150))
        self.details_thumb.setText("")
        self.details_thumb.setPixmap(QtGui.QPixmap(":/tk_multi_infopanel/rect_512x400.png"))
        self.details_thumb.setScaledContents(True)
        self.details_thumb.setObjectName("details_thumb")
        self.gridLayout.addWidget(self.details_thumb, 2, 0, 1, 1)
        self.details_action_btn = QtGui.QToolButton(self.details)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/tk_multi_infopanel/down_arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.details_action_btn.setIcon(icon)
        self.details_action_btn.setObjectName("details_action_btn")
        self.gridLayout.addWidget(self.details_action_btn, 1, 2, 1, 1)
        self.details_text_header = QtGui.QLabel(self.details)
        self.details_text_header.setStyleSheet("font-size: 16px; color: #2C93E2")
        self.details_text_header.setWordWrap(True)
        self.details_text_header.setObjectName("details_text_header")
        self.gridLayout.addWidget(self.details_text_header, 1, 0, 1, 2)
        self.details_text_middle = QtGui.QLabel(self.details)
        self.details_text_middle.setWordWrap(True)
        self.details_text_middle.setObjectName("details_text_middle")
        self.gridLayout.addWidget(self.details_text_middle, 2, 1, 1, 2)
        self.details_text_bottom = QtGui.QLabel(self.details)
        self.details_text_bottom.setWordWrap(True)
        self.details_text_bottom.setObjectName("details_text_bottom")
        self.gridLayout.addWidget(self.details_text_bottom, 3, 0, 1, 3)
        self.verticalLayout_7.addWidget(self.details)
        self.page_stack = QtGui.QStackedWidget(Dialog)
        self.page_stack.setObjectName("page_stack")
        self.entity_page = QtGui.QWidget()
        self.entity_page.setObjectName("entity_page")
        self.verticalLayout = QtGui.QVBoxLayout(self.entity_page)
        self.verticalLayout.setObjectName("verticalLayout")
        self.entity_tab_widget = QtGui.QTabWidget(self.entity_page)
        self.entity_tab_widget.setObjectName("entity_tab_widget")
        self.entity_note_tab = QtGui.QWidget()
        self.entity_note_tab.setObjectName("entity_note_tab")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.entity_note_tab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.entity_note_view = QtGui.QListView(self.entity_note_tab)
        self.entity_note_view.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.entity_note_view.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.entity_note_view.setUniformItemSizes(True)
        self.entity_note_view.setObjectName("entity_note_view")
        self.verticalLayout_2.addWidget(self.entity_note_view)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label = QtGui.QLabel(self.entity_note_tab)
        self.label.setMinimumSize(QtCore.QSize(65, 65))
        self.label.setMaximumSize(QtCore.QSize(65, 65))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/tk_multi_infopanel/default_user.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout_8.addWidget(self.label)
        self.plainTextEdit = QtGui.QPlainTextEdit(self.entity_note_tab)
        self.plainTextEdit.setMaximumSize(QtCore.QSize(16777215, 60))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.horizontalLayout_8.addWidget(self.plainTextEdit)
        self.verticalLayout_2.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem1)
        self.pushButton = QtGui.QPushButton(self.entity_note_tab)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_6.addWidget(self.pushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        self.entity_tab_widget.addTab(self.entity_note_tab, "")
        self.entity_version_tab = QtGui.QWidget()
        self.entity_version_tab.setObjectName("entity_version_tab")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.entity_version_tab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.entity_version_view = QtGui.QListView(self.entity_version_tab)
        self.entity_version_view.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.entity_version_view.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.entity_version_view.setUniformItemSizes(True)
        self.entity_version_view.setObjectName("entity_version_view")
        self.verticalLayout_3.addWidget(self.entity_version_view)
        self.entity_tab_widget.addTab(self.entity_version_tab, "")
        self.entity_publish_tab = QtGui.QWidget()
        self.entity_publish_tab.setObjectName("entity_publish_tab")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.entity_publish_tab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.entity_publish_view = QtGui.QListView(self.entity_publish_tab)
        self.entity_publish_view.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.entity_publish_view.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.entity_publish_view.setUniformItemSizes(True)
        self.entity_publish_view.setObjectName("entity_publish_view")
        self.verticalLayout_4.addWidget(self.entity_publish_view)
        self.latest_publishes_only = QtGui.QCheckBox(self.entity_publish_tab)
        self.latest_publishes_only.setChecked(True)
        self.latest_publishes_only.setObjectName("latest_publishes_only")
        self.verticalLayout_4.addWidget(self.latest_publishes_only)
        self.entity_tab_widget.addTab(self.entity_publish_tab, "")
        self.entity_tasks_tab = QtGui.QWidget()
        self.entity_tasks_tab.setObjectName("entity_tasks_tab")
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.entity_tasks_tab)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.entity_task_view = QtGui.QListView(self.entity_tasks_tab)
        self.entity_task_view.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.entity_task_view.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.entity_task_view.setUniformItemSizes(True)
        self.entity_task_view.setObjectName("entity_task_view")
        self.verticalLayout_8.addWidget(self.entity_task_view)
        self.entity_tab_widget.addTab(self.entity_tasks_tab, "")
        self.entity_info_tab = QtGui.QWidget()
        self.entity_info_tab.setObjectName("entity_info_tab")
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.entity_info_tab)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.entity_info_view = QtGui.QTableView(self.entity_info_tab)
        self.entity_info_view.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.entity_info_view.setAlternatingRowColors(True)
        self.entity_info_view.setSortingEnabled(True)
        self.entity_info_view.setObjectName("entity_info_view")
        self.entity_info_view.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_9.addWidget(self.entity_info_view)
        self.entity_tab_widget.addTab(self.entity_info_tab, "")
        self.verticalLayout.addWidget(self.entity_tab_widget)
        self.page_stack.addWidget(self.entity_page)
        self.publish_page = QtGui.QWidget()
        self.publish_page.setObjectName("publish_page")
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.publish_page)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.publish_tab_widget = QtGui.QTabWidget(self.publish_page)
        self.publish_tab_widget.setObjectName("publish_tab_widget")
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.verticalLayout_15 = QtGui.QVBoxLayout(self.tab_3)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.publish_history_view = QtGui.QListView(self.tab_3)
        self.publish_history_view.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.publish_history_view.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.publish_history_view.setUniformItemSizes(True)
        self.publish_history_view.setObjectName("publish_history_view")
        self.verticalLayout_15.addWidget(self.publish_history_view)
        self.publish_tab_widget.addTab(self.tab_3, "")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_13 = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.publish_upstream_view = QtGui.QListView(self.tab)
        self.publish_upstream_view.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.publish_upstream_view.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.publish_upstream_view.setUniformItemSizes(True)
        self.publish_upstream_view.setObjectName("publish_upstream_view")
        self.verticalLayout_13.addWidget(self.publish_upstream_view)
        self.publish_tab_widget.addTab(self.tab, "")
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_14 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.publish_downstream_view = QtGui.QListView(self.tab_2)
        self.publish_downstream_view.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.publish_downstream_view.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.publish_downstream_view.setUniformItemSizes(True)
        self.publish_downstream_view.setObjectName("publish_downstream_view")
        self.verticalLayout_14.addWidget(self.publish_downstream_view)
        self.publish_tab_widget.addTab(self.tab_2, "")
        self.verticalLayout_6.addWidget(self.publish_tab_widget)
        self.page_stack.addWidget(self.publish_page)
        self.version_page = QtGui.QWidget()
        self.version_page.setObjectName("version_page")
        self.verticalLayout_10 = QtGui.QVBoxLayout(self.version_page)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.version_tab_widget = QtGui.QTabWidget(self.version_page)
        self.version_tab_widget.setObjectName("version_tab_widget")
        self.version_note_tab = QtGui.QWidget()
        self.version_note_tab.setObjectName("version_note_tab")
        self.verticalLayout_11 = QtGui.QVBoxLayout(self.version_note_tab)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.version_note_view = QtGui.QListView(self.version_note_tab)
        self.version_note_view.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.version_note_view.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.version_note_view.setUniformItemSizes(True)
        self.version_note_view.setObjectName("version_note_view")
        self.verticalLayout_11.addWidget(self.version_note_view)
        self.horizontalLayout_11 = QtGui.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.label_3 = QtGui.QLabel(self.version_note_tab)
        self.label_3.setMinimumSize(QtCore.QSize(60, 60))
        self.label_3.setMaximumSize(QtCore.QSize(60, 60))
        self.label_3.setText("")
        self.label_3.setPixmap(QtGui.QPixmap(":/tk_multi_infopanel/default_user.png"))
        self.label_3.setScaledContents(True)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_11.addWidget(self.label_3)
        self.plainTextEdit_3 = QtGui.QPlainTextEdit(self.version_note_tab)
        self.plainTextEdit_3.setMaximumSize(QtCore.QSize(16777215, 60))
        self.plainTextEdit_3.setObjectName("plainTextEdit_3")
        self.horizontalLayout_11.addWidget(self.plainTextEdit_3)
        self.verticalLayout_11.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_12 = QtGui.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem2)
        self.pushButton_3 = QtGui.QPushButton(self.version_note_tab)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_12.addWidget(self.pushButton_3)
        self.verticalLayout_11.addLayout(self.horizontalLayout_12)
        self.version_tab_widget.addTab(self.version_note_tab, "")
        self.version_publish_tab = QtGui.QWidget()
        self.version_publish_tab.setObjectName("version_publish_tab")
        self.verticalLayout_12 = QtGui.QVBoxLayout(self.version_publish_tab)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.version_publish_view = QtGui.QListView(self.version_publish_tab)
        self.version_publish_view.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.version_publish_view.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.version_publish_view.setUniformItemSizes(True)
        self.version_publish_view.setObjectName("version_publish_view")
        self.verticalLayout_12.addWidget(self.version_publish_view)
        self.version_tab_widget.addTab(self.version_publish_tab, "")
        self.verticalLayout_10.addWidget(self.version_tab_widget)
        self.page_stack.addWidget(self.version_page)
        self.verticalLayout_7.addWidget(self.page_stack)

        self.retranslateUi(Dialog)
        self.page_stack.setCurrentIndex(0)
        self.entity_tab_widget.setCurrentIndex(4)
        self.publish_tab_widget.setCurrentIndex(0)
        self.version_tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Shotgun Browser", None, QtGui.QApplication.UnicodeUTF8))
        self.navigation_home.setToolTip(QtGui.QApplication.translate("Dialog", "Clicking the <i>home button</i> will take you to the location that best matches your current work area.", None, QtGui.QApplication.UnicodeUTF8))
        self.navigation_prev.setToolTip(QtGui.QApplication.translate("Dialog", "<i>Go back</i> in the folder history.", None, QtGui.QApplication.UnicodeUTF8))
        self.navigation_next.setToolTip(QtGui.QApplication.translate("Dialog", "<i>Go forward</i> in the folder history.", None, QtGui.QApplication.UnicodeUTF8))
        self.details_text_header.setText(QtGui.QApplication.translate("Dialog", "Header Text", None, QtGui.QApplication.UnicodeUTF8))
        self.details_text_middle.setText(QtGui.QApplication.translate("Dialog", "Middle Text", None, QtGui.QApplication.UnicodeUTF8))
        self.details_text_bottom.setText(QtGui.QApplication.translate("Dialog", "Bottom Text", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Dialog", "Create Note", None, QtGui.QApplication.UnicodeUTF8))
        self.entity_tab_widget.setTabText(self.entity_tab_widget.indexOf(self.entity_note_tab), QtGui.QApplication.translate("Dialog", "Notes", None, QtGui.QApplication.UnicodeUTF8))
        self.entity_tab_widget.setTabText(self.entity_tab_widget.indexOf(self.entity_version_tab), QtGui.QApplication.translate("Dialog", "Versions", None, QtGui.QApplication.UnicodeUTF8))
        self.latest_publishes_only.setText(QtGui.QApplication.translate("Dialog", "Only show latest versions", None, QtGui.QApplication.UnicodeUTF8))
        self.entity_tab_widget.setTabText(self.entity_tab_widget.indexOf(self.entity_publish_tab), QtGui.QApplication.translate("Dialog", "Publishes", None, QtGui.QApplication.UnicodeUTF8))
        self.entity_tab_widget.setTabText(self.entity_tab_widget.indexOf(self.entity_tasks_tab), QtGui.QApplication.translate("Dialog", "Tasks", None, QtGui.QApplication.UnicodeUTF8))
        self.entity_tab_widget.setTabText(self.entity_tab_widget.indexOf(self.entity_info_tab), QtGui.QApplication.translate("Dialog", "Info", None, QtGui.QApplication.UnicodeUTF8))
        self.publish_tab_widget.setTabText(self.publish_tab_widget.indexOf(self.tab_3), QtGui.QApplication.translate("Dialog", "Version History", None, QtGui.QApplication.UnicodeUTF8))
        self.publish_tab_widget.setTabText(self.publish_tab_widget.indexOf(self.tab), QtGui.QApplication.translate("Dialog", "Contains", None, QtGui.QApplication.UnicodeUTF8))
        self.publish_tab_widget.setTabText(self.publish_tab_widget.indexOf(self.tab_2), QtGui.QApplication.translate("Dialog", "Used In", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("Dialog", "Create Note", None, QtGui.QApplication.UnicodeUTF8))
        self.version_tab_widget.setTabText(self.version_tab_widget.indexOf(self.version_note_tab), QtGui.QApplication.translate("Dialog", "Notes", None, QtGui.QApplication.UnicodeUTF8))
        self.version_tab_widget.setTabText(self.version_tab_widget.indexOf(self.version_publish_tab), QtGui.QApplication.translate("Dialog", "Publishes", None, QtGui.QApplication.UnicodeUTF8))

from ..version_label import VersionLabel
from . import resources_rc
