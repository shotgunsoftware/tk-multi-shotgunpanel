# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\qa\sg_envs\dv\tk\tk-multi-shotgunpanel\resources\dialog.ui'
#
# Created: Tue Aug 15 13:20:40 2023
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from sgtk.platform.qt import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(412, 648)
        self.verticalLayout_23 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_23.setSpacing(0)
        self.verticalLayout_23.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_23.setObjectName("verticalLayout_23")
        self.main_stack = QtGui.QStackedWidget(Dialog)
        self.main_stack.setObjectName("main_stack")
        self.main_page = QtGui.QWidget()
        self.main_page.setObjectName("main_page")
        self.verticalLayout_17 = QtGui.QVBoxLayout(self.main_page)
        self.verticalLayout_17.setSpacing(4)
        self.verticalLayout_17.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.top_group = QtGui.QFrame(self.main_page)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.top_group.sizePolicy().hasHeightForWidth())
        self.top_group.setSizePolicy(sizePolicy)
        self.top_group.setFrameShape(QtGui.QFrame.StyledPanel)
        self.top_group.setFrameShadow(QtGui.QFrame.Raised)
        self.top_group.setObjectName("top_group")
        self.verticalLayout_18 = QtGui.QVBoxLayout(self.top_group)
        self.verticalLayout_18.setSpacing(4)
        self.verticalLayout_18.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout_18.setObjectName("verticalLayout_18")
        self.header_stack = QtGui.QStackedWidget(self.top_group)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header_stack.sizePolicy().hasHeightForWidth())
        self.header_stack.setSizePolicy(sizePolicy)
        self.header_stack.setMinimumSize(QtCore.QSize(0, 42))
        self.header_stack.setMaximumSize(QtCore.QSize(16777215, 42))
        self.header_stack.setObjectName("header_stack")
        self.page = QtGui.QWidget()
        self.page.setObjectName("page")
        self.verticalLayout_24 = QtGui.QVBoxLayout(self.page)
        self.verticalLayout_24.setSpacing(2)
        self.verticalLayout_24.setContentsMargins(2, 0, 2, 0)
        self.verticalLayout_24.setObjectName("verticalLayout_24")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(-1, -1, 4, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.navigation_home = QtGui.QToolButton(self.page)
        self.navigation_home.setMinimumSize(QtCore.QSize(30, 30))
        self.navigation_home.setMaximumSize(QtCore.QSize(30, 30))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/tk_multi_infopanel/home.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.navigation_home.setIcon(icon)
        self.navigation_home.setIconSize(QtCore.QSize(30, 30))
        self.navigation_home.setObjectName("navigation_home")
        self.horizontalLayout.addWidget(self.navigation_home)
        self.navigation_prev = QtGui.QToolButton(self.page)
        self.navigation_prev.setMinimumSize(QtCore.QSize(30, 30))
        self.navigation_prev.setMaximumSize(QtCore.QSize(30, 30))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/tk_multi_infopanel/left_arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.navigation_prev.setIcon(icon1)
        self.navigation_prev.setIconSize(QtCore.QSize(30, 30))
        self.navigation_prev.setObjectName("navigation_prev")
        self.horizontalLayout.addWidget(self.navigation_prev)
        self.navigation_next = QtGui.QToolButton(self.page)
        self.navigation_next.setMinimumSize(QtCore.QSize(30, 30))
        self.navigation_next.setMaximumSize(QtCore.QSize(30, 30))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/tk_multi_infopanel/right_arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.navigation_next.setIcon(icon2)
        self.navigation_next.setIconSize(QtCore.QSize(30, 30))
        self.navigation_next.setObjectName("navigation_next")
        self.horizontalLayout.addWidget(self.navigation_next)
        self.details_text_header = QtGui.QLabel(self.page)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.details_text_header.sizePolicy().hasHeightForWidth())
        self.details_text_header.setSizePolicy(sizePolicy)
        self.details_text_header.setMinimumSize(QtCore.QSize(0, 30))
        self.details_text_header.setMaximumSize(QtCore.QSize(16777215, 30))
        self.details_text_header.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.details_text_header.setWordWrap(False)
        self.details_text_header.setObjectName("details_text_header")
        self.horizontalLayout.addWidget(self.details_text_header)
        self.refresh_button = QtGui.QToolButton(self.page)
        self.refresh_button.setMinimumSize(QtCore.QSize(30, 30))
        self.refresh_button.setMaximumSize(QtCore.QSize(30, 30))
        self.refresh_button.setIconSize(QtCore.QSize(30, 30))
        self.refresh_button.setToolTip("")
        self.refresh_button.setText("")
        self.refresh_button.setObjectName("refresh_button")
        self.horizontalLayout.addWidget(self.refresh_button)
        self.set_context = WorkAreaButton(self.page)
        self.set_context.setMinimumSize(QtCore.QSize(30, 30))
        self.set_context.setMaximumSize(QtCore.QSize(30, 30))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/tk_multi_infopanel/pin.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon3.addPixmap(QtGui.QPixmap(":/tk_multi_infopanel/pin_white.png"), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
        self.set_context.setIcon(icon3)
        self.set_context.setIconSize(QtCore.QSize(30, 30))
        self.set_context.setObjectName("set_context")
        self.horizontalLayout.addWidget(self.set_context)
        self.search = QtGui.QToolButton(self.page)
        self.search.setMinimumSize(QtCore.QSize(30, 30))
        self.search.setMaximumSize(QtCore.QSize(30, 30))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/tk_multi_infopanel/search.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.search.setIcon(icon4)
        self.search.setIconSize(QtCore.QSize(30, 30))
        self.search.setObjectName("search")
        self.horizontalLayout.addWidget(self.search)
        self.label_3 = QtGui.QLabel(self.page)
        self.label_3.setMinimumSize(QtCore.QSize(10, 0))
        self.label_3.setMaximumSize(QtCore.QSize(10, 16777215))
        self.label_3.setText("")
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.current_user = QtGui.QToolButton(self.page)
        self.current_user.setMinimumSize(QtCore.QSize(30, 30))
        self.current_user.setMaximumSize(QtCore.QSize(30, 30))
        self.current_user.setFocusPolicy(QtCore.Qt.NoFocus)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/tk_multi_infopanel/default_user_thumb.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.current_user.setIcon(icon5)
        self.current_user.setIconSize(QtCore.QSize(30, 30))
        self.current_user.setObjectName("current_user")
        self.horizontalLayout.addWidget(self.current_user)
        self.verticalLayout_24.addLayout(self.horizontalLayout)
        self.header_stack.addWidget(self.page)
        self.page_2 = QtGui.QWidget()
        self.page_2.setObjectName("page_2")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.page_2)
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setContentsMargins(2, 0, 2, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtGui.QLabel(self.page_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(30, 30))
        self.label.setMaximumSize(QtCore.QSize(30, 30))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/tk_multi_infopanel/search.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.search_input = GlobalSearchWidget(self.page_2)
        self.search_input.setObjectName("search_input")
        self.horizontalLayout_2.addWidget(self.search_input)
        self.cancel_search = QtGui.QPushButton(self.page_2)
        self.cancel_search.setObjectName("cancel_search")
        self.horizontalLayout_2.addWidget(self.cancel_search)
        self.header_stack.addWidget(self.page_2)
        self.verticalLayout_18.addWidget(self.header_stack)
        self.line = QtGui.QFrame(self.top_group)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_18.addWidget(self.line)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_7 = QtGui.QVBoxLayout()
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setContentsMargins(-1, 4, -1, -1)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.details_thumb = ShotgunPlaybackLabel(self.top_group)
        self.details_thumb.setMinimumSize(QtCore.QSize(96, 75))
        self.details_thumb.setMaximumSize(QtCore.QSize(96, 75))
        self.details_thumb.setText("")
        self.details_thumb.setPixmap(QtGui.QPixmap(":/tk_multi_infopanel/rect_512x400.png"))
        self.details_thumb.setScaledContents(True)
        self.details_thumb.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.details_thumb.setObjectName("details_thumb")
        self.verticalLayout_7.addWidget(self.details_thumb)
        spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Ignored)
        self.verticalLayout_7.addItem(spacerItem)
        self.verticalLayout_7.setStretch(1, 1)
        self.horizontalLayout_4.addLayout(self.verticalLayout_7)
        self.details_text_middle = QtGui.QLabel(self.top_group)
        self.details_text_middle.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.details_text_middle.setWordWrap(True)
        self.details_text_middle.setObjectName("details_text_middle")
        self.horizontalLayout_4.addWidget(self.details_text_middle)
        self.verticalLayout_22 = QtGui.QVBoxLayout()
        self.verticalLayout_22.setSpacing(0)
        self.verticalLayout_22.setContentsMargins(-1, -1, 6, -1)
        self.verticalLayout_22.setObjectName("verticalLayout_22")
        self.action_button = QtGui.QPushButton(self.top_group)
        self.action_button.setMaximumSize(QtCore.QSize(16, 16))
        self.action_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.action_button.setObjectName("action_button")
        self.verticalLayout_22.addWidget(self.action_button)
        self.label_2 = QtGui.QLabel(self.top_group)
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.verticalLayout_22.addWidget(self.label_2)
        self.verticalLayout_22.setStretch(1, 1)
        self.horizontalLayout_4.addLayout(self.verticalLayout_22)
        self.horizontalLayout_4.setStretch(1, 1)
        self.verticalLayout_18.addLayout(self.horizontalLayout_4)
        self.verticalLayout_17.addWidget(self.top_group)
        self.page_stack = QtGui.QStackedWidget(self.main_page)
        self.page_stack.setObjectName("page_stack")
        self.entity_page = QtGui.QWidget()
        self.entity_page.setObjectName("entity_page")
        self.verticalLayout = QtGui.QVBoxLayout(self.entity_page)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.entity_tab_widget = QtGui.QTabWidget(self.entity_page)
        self.entity_tab_widget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.entity_tab_widget.setObjectName("entity_tab_widget")
        self.verticalLayout.addWidget(self.entity_tab_widget)
        self.page_stack.addWidget(self.entity_page)
        self.note_page = QtGui.QWidget()
        self.note_page.setObjectName("note_page")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.note_page)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.note_reply_widget = ReplyListWidget(self.note_page)
        self.note_reply_widget.setObjectName("note_reply_widget")
        self.verticalLayout_5.addWidget(self.note_reply_widget)
        self.page_stack.addWidget(self.note_page)
        self.verticalLayout_17.addWidget(self.page_stack)
        self.main_stack.addWidget(self.main_page)
        self.verticalLayout_23.addWidget(self.main_stack)

        self.retranslateUi(Dialog)
        self.main_stack.setCurrentIndex(0)
        self.header_stack.setCurrentIndex(0)
        self.page_stack.setCurrentIndex(0)
        self.entity_tab_widget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Flow Production Tracking Browser", None, QtGui.QApplication.UnicodeUTF8))
        self.navigation_home.setToolTip(QtGui.QApplication.translate("Dialog", "Click to go to your work area", None, QtGui.QApplication.UnicodeUTF8))
        self.navigation_prev.setToolTip(QtGui.QApplication.translate("Dialog", "Click to go back", None, QtGui.QApplication.UnicodeUTF8))
        self.navigation_next.setToolTip(QtGui.QApplication.translate("Dialog", "Click to go forward", None, QtGui.QApplication.UnicodeUTF8))
        self.details_text_header.setText(QtGui.QApplication.translate("Dialog", "Header Text", None, QtGui.QApplication.UnicodeUTF8))
        self.set_context.setToolTip(QtGui.QApplication.translate("Dialog", "Click to go to your work area", None, QtGui.QApplication.UnicodeUTF8))
        self.search.setToolTip(QtGui.QApplication.translate("Dialog", "Search Flow Production Tracking", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_search.setText(QtGui.QApplication.translate("Dialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.details_text_middle.setText(QtGui.QApplication.translate("Dialog", "Details Text", None, QtGui.QApplication.UnicodeUTF8))

from ..qtwidgets import ShotgunPlaybackLabel, ReplyListWidget, GlobalSearchWidget
from ..work_area_button import WorkAreaButton
from . import resources_rc
