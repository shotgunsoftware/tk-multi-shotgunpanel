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
        Dialog.resize(522, 778)
        self.verticalLayout_7 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
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
        self.current_entity = QtGui.QLabel(Dialog)
        self.current_entity.setObjectName("current_entity")
        self.horizontalLayout_2.addWidget(self.current_entity)
        self.verticalLayout_7.addLayout(self.horizontalLayout_2)
        self.stackedWidget = QtGui.QStackedWidget(Dialog)
        self.stackedWidget.setObjectName("stackedWidget")
        self.entity_page = QtGui.QWidget()
        self.entity_page.setObjectName("entity_page")
        self.verticalLayout = QtGui.QVBoxLayout(self.entity_page)
        self.verticalLayout.setObjectName("verticalLayout")
        self.entity_details = QtGui.QWidget(self.entity_page)
        self.entity_details.setObjectName("entity_details")
        self.horizontalLayout = QtGui.QHBoxLayout(self.entity_details)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.entity_thumb = QtGui.QLabel(self.entity_details)
        self.entity_thumb.setMinimumSize(QtCore.QSize(150, 100))
        self.entity_thumb.setMaximumSize(QtCore.QSize(150, 100))
        self.entity_thumb.setObjectName("entity_thumb")
        self.horizontalLayout.addWidget(self.entity_thumb)
        self.entity_text = QtGui.QLabel(self.entity_details)
        self.entity_text.setObjectName("entity_text")
        self.horizontalLayout.addWidget(self.entity_text)
        self.verticalLayout.addWidget(self.entity_details)
        self.tabWidget = QtGui.QTabWidget(self.entity_page)
        self.tabWidget.setObjectName("tabWidget")
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
        self.tabWidget.addTab(self.entity_note_tab, "")
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
        self.tabWidget.addTab(self.entity_version_tab, "")
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
        self.tabWidget.addTab(self.entity_publish_tab, "")
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
        self.tabWidget.addTab(self.entity_tasks_tab, "")
        self.entity_info_tab = QtGui.QWidget()
        self.entity_info_tab.setObjectName("entity_info_tab")
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.entity_info_tab)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.entity_info_view = QtGui.QListView(self.entity_info_tab)
        self.entity_info_view.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.entity_info_view.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.entity_info_view.setUniformItemSizes(True)
        self.entity_info_view.setObjectName("entity_info_view")
        self.verticalLayout_9.addWidget(self.entity_info_view)
        self.tabWidget.addTab(self.entity_info_tab, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.stackedWidget.addWidget(self.entity_page)
        self.note_page = QtGui.QWidget()
        self.note_page.setObjectName("note_page")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.note_page)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.note_details = QtGui.QWidget(self.note_page)
        self.note_details.setObjectName("note_details")
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.note_details)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.note_thumb = QtGui.QLabel(self.note_details)
        self.note_thumb.setMinimumSize(QtCore.QSize(100, 100))
        self.note_thumb.setMaximumSize(QtCore.QSize(100, 100))
        self.note_thumb.setObjectName("note_thumb")
        self.horizontalLayout_3.addWidget(self.note_thumb)
        self.note_text = QtGui.QLabel(self.note_details)
        self.note_text.setObjectName("note_text")
        self.horizontalLayout_3.addWidget(self.note_text)
        self.verticalLayout_5.addWidget(self.note_details)
        self.note_reply_view = QtGui.QListView(self.note_page)
        self.note_reply_view.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.note_reply_view.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.note_reply_view.setUniformItemSizes(True)
        self.note_reply_view.setObjectName("note_reply_view")
        self.verticalLayout_5.addWidget(self.note_reply_view)
        self.stackedWidget.addWidget(self.note_page)
        self.publish_page = QtGui.QWidget()
        self.publish_page.setObjectName("publish_page")
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.publish_page)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.publish_details = QtGui.QWidget(self.publish_page)
        self.publish_details.setObjectName("publish_details")
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.publish_details)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.publish_thumb = QtGui.QLabel(self.publish_details)
        self.publish_thumb.setMinimumSize(QtCore.QSize(150, 100))
        self.publish_thumb.setMaximumSize(QtCore.QSize(150, 100))
        self.publish_thumb.setObjectName("publish_thumb")
        self.horizontalLayout_4.addWidget(self.publish_thumb)
        self.publish_text = QtGui.QLabel(self.publish_details)
        self.publish_text.setObjectName("publish_text")
        self.horizontalLayout_4.addWidget(self.publish_text)
        self.verticalLayout_6.addWidget(self.publish_details)
        self.publish_publish_view = QtGui.QListView(self.publish_page)
        self.publish_publish_view.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.publish_publish_view.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.publish_publish_view.setUniformItemSizes(True)
        self.publish_publish_view.setObjectName("publish_publish_view")
        self.verticalLayout_6.addWidget(self.publish_publish_view)
        self.stackedWidget.addWidget(self.publish_page)
        self.version_page = QtGui.QWidget()
        self.version_page.setObjectName("version_page")
        self.verticalLayout_10 = QtGui.QVBoxLayout(self.version_page)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.version_details = QtGui.QWidget(self.version_page)
        self.version_details.setObjectName("version_details")
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.version_details)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.version_thumb = QtGui.QLabel(self.version_details)
        self.version_thumb.setMinimumSize(QtCore.QSize(150, 100))
        self.version_thumb.setMaximumSize(QtCore.QSize(150, 100))
        self.version_thumb.setObjectName("version_thumb")
        self.horizontalLayout_5.addWidget(self.version_thumb)
        self.version_text = QtGui.QLabel(self.version_details)
        self.version_text.setObjectName("version_text")
        self.horizontalLayout_5.addWidget(self.version_text)
        self.verticalLayout_10.addWidget(self.version_details)
        self.tabWidget_2 = QtGui.QTabWidget(self.version_page)
        self.tabWidget_2.setObjectName("tabWidget_2")
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
        self.tabWidget_2.addTab(self.version_note_tab, "")
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
        self.tabWidget_2.addTab(self.version_publish_tab, "")
        self.verticalLayout_10.addWidget(self.tabWidget_2)
        self.stackedWidget.addWidget(self.version_page)
        self.verticalLayout_7.addWidget(self.stackedWidget)

        self.retranslateUi(Dialog)
        self.stackedWidget.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Shotgun Browser", None, QtGui.QApplication.UnicodeUTF8))
        self.navigation_home.setToolTip(QtGui.QApplication.translate("Dialog", "Clicking the <i>home button</i> will take you to the location that best matches your current work area.", None, QtGui.QApplication.UnicodeUTF8))
        self.navigation_prev.setToolTip(QtGui.QApplication.translate("Dialog", "<i>Go back</i> in the folder history.", None, QtGui.QApplication.UnicodeUTF8))
        self.navigation_next.setToolTip(QtGui.QApplication.translate("Dialog", "<i>Go forward</i> in the folder history.", None, QtGui.QApplication.UnicodeUTF8))
        self.current_entity.setText(QtGui.QApplication.translate("Dialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.entity_thumb.setText(QtGui.QApplication.translate("Dialog", "Entity", None, QtGui.QApplication.UnicodeUTF8))
        self.entity_text.setText(QtGui.QApplication.translate("Dialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.entity_note_view.setToolTip(QtGui.QApplication.translate("Dialog", "If you select a publish in the main view, this list shows <i>the complete history for that publish</i>, who created each publish, the description and the publish date. If you select an item, an action menu will appear, allowing you to load historical versions into your scene.", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.entity_note_tab), QtGui.QApplication.translate("Dialog", "Notes", None, QtGui.QApplication.UnicodeUTF8))
        self.entity_version_view.setToolTip(QtGui.QApplication.translate("Dialog", "If you select a publish in the main view, this list shows <i>the complete history for that publish</i>, who created each publish, the description and the publish date. If you select an item, an action menu will appear, allowing you to load historical versions into your scene.", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.entity_version_tab), QtGui.QApplication.translate("Dialog", "Versions", None, QtGui.QApplication.UnicodeUTF8))
        self.entity_publish_view.setToolTip(QtGui.QApplication.translate("Dialog", "If you select a publish in the main view, this list shows <i>the complete history for that publish</i>, who created each publish, the description and the publish date. If you select an item, an action menu will appear, allowing you to load historical versions into your scene.", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.entity_publish_tab), QtGui.QApplication.translate("Dialog", "Publishes", None, QtGui.QApplication.UnicodeUTF8))
        self.entity_task_view.setToolTip(QtGui.QApplication.translate("Dialog", "If you select a publish in the main view, this list shows <i>the complete history for that publish</i>, who created each publish, the description and the publish date. If you select an item, an action menu will appear, allowing you to load historical versions into your scene.", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.entity_tasks_tab), QtGui.QApplication.translate("Dialog", "Tasks", None, QtGui.QApplication.UnicodeUTF8))
        self.entity_info_view.setToolTip(QtGui.QApplication.translate("Dialog", "If you select a publish in the main view, this list shows <i>the complete history for that publish</i>, who created each publish, the description and the publish date. If you select an item, an action menu will appear, allowing you to load historical versions into your scene.", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.entity_info_tab), QtGui.QApplication.translate("Dialog", "Info", None, QtGui.QApplication.UnicodeUTF8))
        self.note_thumb.setText(QtGui.QApplication.translate("Dialog", "Note", None, QtGui.QApplication.UnicodeUTF8))
        self.note_text.setText(QtGui.QApplication.translate("Dialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.note_reply_view.setToolTip(QtGui.QApplication.translate("Dialog", "If you select a publish in the main view, this list shows <i>the complete history for that publish</i>, who created each publish, the description and the publish date. If you select an item, an action menu will appear, allowing you to load historical versions into your scene.", None, QtGui.QApplication.UnicodeUTF8))
        self.publish_thumb.setText(QtGui.QApplication.translate("Dialog", "Publish", None, QtGui.QApplication.UnicodeUTF8))
        self.publish_text.setText(QtGui.QApplication.translate("Dialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.publish_publish_view.setToolTip(QtGui.QApplication.translate("Dialog", "If you select a publish in the main view, this list shows <i>the complete history for that publish</i>, who created each publish, the description and the publish date. If you select an item, an action menu will appear, allowing you to load historical versions into your scene.", None, QtGui.QApplication.UnicodeUTF8))
        self.version_thumb.setText(QtGui.QApplication.translate("Dialog", "Version", None, QtGui.QApplication.UnicodeUTF8))
        self.version_text.setText(QtGui.QApplication.translate("Dialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.version_note_view.setToolTip(QtGui.QApplication.translate("Dialog", "If you select a publish in the main view, this list shows <i>the complete history for that publish</i>, who created each publish, the description and the publish date. If you select an item, an action menu will appear, allowing you to load historical versions into your scene.", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.version_note_tab), QtGui.QApplication.translate("Dialog", "Notes", None, QtGui.QApplication.UnicodeUTF8))
        self.version_publish_view.setToolTip(QtGui.QApplication.translate("Dialog", "If you select a publish in the main view, this list shows <i>the complete history for that publish</i>, who created each publish, the description and the publish date. If you select an item, an action menu will appear, allowing you to load historical versions into your scene.", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.version_publish_tab), QtGui.QApplication.translate("Dialog", "Publishes", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
