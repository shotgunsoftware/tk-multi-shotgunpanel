# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog.ui'
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


from ..qtwidgets import ShotgunPlaybackLabel
from ..qtwidgets import ReplyListWidget
from ..qtwidgets import GlobalSearchWidget
from ..work_area_button import WorkAreaButton

from  . import resources_rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(412, 648)
        self.verticalLayout_23 = QVBoxLayout(Dialog)
        self.verticalLayout_23.setSpacing(0)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.verticalLayout_23.setContentsMargins(0, 0, 0, 0)
        self.main_stack = QStackedWidget(Dialog)
        self.main_stack.setObjectName(u"main_stack")
        self.main_page = QWidget()
        self.main_page.setObjectName(u"main_page")
        self.verticalLayout_17 = QVBoxLayout(self.main_page)
        self.verticalLayout_17.setSpacing(4)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(4, 4, 4, 4)
        self.top_group = QFrame(self.main_page)
        self.top_group.setObjectName(u"top_group")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.top_group.sizePolicy().hasHeightForWidth())
        self.top_group.setSizePolicy(sizePolicy)
        self.top_group.setFrameShape(QFrame.StyledPanel)
        self.top_group.setFrameShadow(QFrame.Raised)
        self.verticalLayout_18 = QVBoxLayout(self.top_group)
        self.verticalLayout_18.setSpacing(4)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(6, 6, 6, 6)
        self.header_stack = QStackedWidget(self.top_group)
        self.header_stack.setObjectName(u"header_stack")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.header_stack.sizePolicy().hasHeightForWidth())
        self.header_stack.setSizePolicy(sizePolicy1)
        self.header_stack.setMinimumSize(QSize(0, 42))
        self.header_stack.setMaximumSize(QSize(16777215, 42))
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.verticalLayout_24 = QVBoxLayout(self.page)
        self.verticalLayout_24.setSpacing(2)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.verticalLayout_24.setContentsMargins(2, 0, 2, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, -1, 4, -1)
        self.navigation_home = QToolButton(self.page)
        self.navigation_home.setObjectName(u"navigation_home")
        self.navigation_home.setMinimumSize(QSize(30, 30))
        self.navigation_home.setMaximumSize(QSize(30, 30))
        icon = QIcon()
        icon.addFile(u":/tk_multi_infopanel/home.png", QSize(), QIcon.Normal, QIcon.Off)
        self.navigation_home.setIcon(icon)
        self.navigation_home.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.navigation_home)

        self.navigation_prev = QToolButton(self.page)
        self.navigation_prev.setObjectName(u"navigation_prev")
        self.navigation_prev.setMinimumSize(QSize(30, 30))
        self.navigation_prev.setMaximumSize(QSize(30, 30))
        icon1 = QIcon()
        icon1.addFile(u":/tk_multi_infopanel/left_arrow.png", QSize(), QIcon.Normal, QIcon.Off)
        self.navigation_prev.setIcon(icon1)
        self.navigation_prev.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.navigation_prev)

        self.navigation_next = QToolButton(self.page)
        self.navigation_next.setObjectName(u"navigation_next")
        self.navigation_next.setMinimumSize(QSize(30, 30))
        self.navigation_next.setMaximumSize(QSize(30, 30))
        icon2 = QIcon()
        icon2.addFile(u":/tk_multi_infopanel/right_arrow.png", QSize(), QIcon.Normal, QIcon.Off)
        self.navigation_next.setIcon(icon2)
        self.navigation_next.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.navigation_next)

        self.details_text_header = QLabel(self.page)
        self.details_text_header.setObjectName(u"details_text_header")
        sizePolicy2 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.details_text_header.sizePolicy().hasHeightForWidth())
        self.details_text_header.setSizePolicy(sizePolicy2)
        self.details_text_header.setMinimumSize(QSize(0, 30))
        self.details_text_header.setMaximumSize(QSize(16777215, 30))
        self.details_text_header.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.details_text_header.setWordWrap(False)

        self.horizontalLayout.addWidget(self.details_text_header)

        self.refresh_button = QToolButton(self.page)
        self.refresh_button.setObjectName(u"refresh_button")
        self.refresh_button.setMinimumSize(QSize(30, 30))
        self.refresh_button.setMaximumSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.refresh_button)

        self.set_context = WorkAreaButton(self.page)
        self.set_context.setObjectName(u"set_context")
        self.set_context.setMinimumSize(QSize(30, 30))
        self.set_context.setMaximumSize(QSize(30, 30))
        icon3 = QIcon()
        icon3.addFile(u":/tk_multi_infopanel/pin.png", QSize(), QIcon.Normal, QIcon.Off)
        icon3.addFile(u":/tk_multi_infopanel/pin_white.png", QSize(), QIcon.Disabled, QIcon.Off)
        self.set_context.setIcon(icon3)
        self.set_context.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.set_context)

        self.search = QToolButton(self.page)
        self.search.setObjectName(u"search")
        self.search.setMinimumSize(QSize(30, 30))
        self.search.setMaximumSize(QSize(30, 30))
        icon4 = QIcon()
        icon4.addFile(u":/tk_multi_infopanel/search.png", QSize(), QIcon.Normal, QIcon.Off)
        self.search.setIcon(icon4)
        self.search.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.search)

        self.label_3 = QLabel(self.page)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(10, 0))
        self.label_3.setMaximumSize(QSize(10, 16777215))

        self.horizontalLayout.addWidget(self.label_3)

        self.current_user = QToolButton(self.page)
        self.current_user.setObjectName(u"current_user")
        self.current_user.setMinimumSize(QSize(30, 30))
        self.current_user.setMaximumSize(QSize(30, 30))
        self.current_user.setFocusPolicy(Qt.NoFocus)
        icon5 = QIcon()
        icon5.addFile(u":/tk_multi_infopanel/default_user_thumb.png", QSize(), QIcon.Normal, QIcon.Off)
        self.current_user.setIcon(icon5)
        self.current_user.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.current_user)

        self.verticalLayout_24.addLayout(self.horizontalLayout)

        self.header_stack.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.horizontalLayout_2 = QHBoxLayout(self.page_2)
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(2, 0, 2, 0)
        self.label = QLabel(self.page_2)
        self.label.setObjectName(u"label")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy3)
        self.label.setMinimumSize(QSize(30, 30))
        self.label.setMaximumSize(QSize(30, 30))
        self.label.setPixmap(QPixmap(u":/tk_multi_infopanel/search.png"))
        self.label.setScaledContents(True)

        self.horizontalLayout_2.addWidget(self.label)

        self.search_input = GlobalSearchWidget(self.page_2)
        self.search_input.setObjectName(u"search_input")

        self.horizontalLayout_2.addWidget(self.search_input)

        self.cancel_search = QPushButton(self.page_2)
        self.cancel_search.setObjectName(u"cancel_search")

        self.horizontalLayout_2.addWidget(self.cancel_search)

        self.header_stack.addWidget(self.page_2)

        self.verticalLayout_18.addWidget(self.header_stack)

        self.line = QFrame(self.top_group)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_18.addWidget(self.line)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(-1, 4, -1, -1)
        self.details_thumb = ShotgunPlaybackLabel(self.top_group)
        self.details_thumb.setObjectName(u"details_thumb")
        self.details_thumb.setMinimumSize(QSize(96, 75))
        self.details_thumb.setMaximumSize(QSize(96, 75))
        self.details_thumb.setPixmap(QPixmap(u":/tk_multi_infopanel/rect_512x400.png"))
        self.details_thumb.setScaledContents(True)
        self.details_thumb.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.verticalLayout_7.addWidget(self.details_thumb)

        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Ignored)

        self.verticalLayout_7.addItem(self.verticalSpacer)

        self.verticalLayout_7.setStretch(1, 1)

        self.horizontalLayout_4.addLayout(self.verticalLayout_7)

        self.details_text_middle = QLabel(self.top_group)
        self.details_text_middle.setObjectName(u"details_text_middle")
        self.details_text_middle.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.details_text_middle.setWordWrap(True)

        self.horizontalLayout_4.addWidget(self.details_text_middle)

        self.verticalLayout_22 = QVBoxLayout()
        self.verticalLayout_22.setSpacing(0)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.verticalLayout_22.setContentsMargins(-1, -1, 6, -1)
        self.action_button = QPushButton(self.top_group)
        self.action_button.setObjectName(u"action_button")
        self.action_button.setMaximumSize(QSize(16, 16))
        self.action_button.setFocusPolicy(Qt.NoFocus)

        self.verticalLayout_22.addWidget(self.action_button)

        self.label_2 = QLabel(self.top_group)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_22.addWidget(self.label_2)

        self.verticalLayout_22.setStretch(1, 1)

        self.horizontalLayout_4.addLayout(self.verticalLayout_22)

        self.horizontalLayout_4.setStretch(1, 1)

        self.verticalLayout_18.addLayout(self.horizontalLayout_4)

        self.verticalLayout_17.addWidget(self.top_group)

        self.page_stack = QStackedWidget(self.main_page)
        self.page_stack.setObjectName(u"page_stack")
        self.entity_page = QWidget()
        self.entity_page.setObjectName(u"entity_page")
        self.verticalLayout = QVBoxLayout(self.entity_page)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.entity_tab_widget = QTabWidget(self.entity_page)
        self.entity_tab_widget.setObjectName(u"entity_tab_widget")
        self.entity_tab_widget.setFocusPolicy(Qt.NoFocus)

        self.verticalLayout.addWidget(self.entity_tab_widget)

        self.page_stack.addWidget(self.entity_page)
        self.note_page = QWidget()
        self.note_page.setObjectName(u"note_page")
        self.verticalLayout_5 = QVBoxLayout(self.note_page)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.note_reply_widget = ReplyListWidget(self.note_page)
        self.note_reply_widget.setObjectName(u"note_reply_widget")

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

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Flow Production Tracking Browser", None))
#if QT_CONFIG(tooltip)
        self.navigation_home.setToolTip(QCoreApplication.translate("Dialog", u"Click to go to your work area", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.navigation_prev.setToolTip(QCoreApplication.translate("Dialog", u"Click to go back", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.navigation_next.setToolTip(QCoreApplication.translate("Dialog", u"Click to go forward", None))
#endif // QT_CONFIG(tooltip)
        self.details_text_header.setText(QCoreApplication.translate("Dialog", u"Header Text", None))
#if QT_CONFIG(tooltip)
        self.refresh_button.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.refresh_button.setText("")
#if QT_CONFIG(tooltip)
        self.set_context.setToolTip(QCoreApplication.translate("Dialog", u"Click to go to your work area", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.search.setToolTip(QCoreApplication.translate("Dialog", u"Search Flow Production Tracking", None))
#endif // QT_CONFIG(tooltip)
        self.label_3.setText("")
        self.label.setText("")
        self.cancel_search.setText(QCoreApplication.translate("Dialog", u"Cancel", None))
        self.details_thumb.setText("")
        self.details_text_middle.setText(QCoreApplication.translate("Dialog", u"Details Text", None))
        self.label_2.setText("")
    # retranslateUi
