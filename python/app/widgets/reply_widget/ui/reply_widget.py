# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'reply_widget.ui'
#
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_ReplyWidget(object):
    def setupUi(self, ReplyWidget):
        ReplyWidget.setObjectName("ReplyWidget")
        ReplyWidget.resize(559, 393)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(ReplyWidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.thumbnail = QtGui.QLabel(ReplyWidget)
        self.thumbnail.setMinimumSize(QtCore.QSize(60, 60))
        self.thumbnail.setMaximumSize(QtCore.QSize(60, 60))
        self.thumbnail.setText("")
        self.thumbnail.setPixmap(QtGui.QPixmap(":/tk_multi_infopanel_reply_widget/default_user.png"))
        self.thumbnail.setScaledContents(True)
        self.thumbnail.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.thumbnail.setObjectName("thumbnail")
        self.verticalLayout_2.addWidget(self.thumbnail)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.user = QtGui.QLabel(ReplyWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.user.sizePolicy().hasHeightForWidth())
        self.user.setSizePolicy(sizePolicy)
        self.user.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.user.setWordWrap(True)
        self.user.setObjectName("user")
        self.horizontalLayout.addWidget(self.user)
        self.date = QtGui.QLabel(ReplyWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.date.sizePolicy().hasHeightForWidth())
        self.date.setSizePolicy(sizePolicy)
        self.date.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.date.setWordWrap(True)
        self.date.setObjectName("date")
        self.horizontalLayout.addWidget(self.date)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.reply = QtGui.QLabel(ReplyWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reply.sizePolicy().hasHeightForWidth())
        self.reply.setSizePolicy(sizePolicy)
        self.reply.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.reply.setWordWrap(True)
        self.reply.setObjectName("reply")
        self.verticalLayout.addWidget(self.reply)
        self.attachment_header = QtGui.QLabel(ReplyWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.attachment_header.sizePolicy().hasHeightForWidth())
        self.attachment_header.setSizePolicy(sizePolicy)
        self.attachment_header.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.attachment_header.setWordWrap(True)
        self.attachment_header.setObjectName("attachment_header")
        self.verticalLayout.addWidget(self.attachment_header)
        self.attachment_scrollarea = QtGui.QScrollArea(ReplyWidget)
        self.attachment_scrollarea.setMinimumSize(QtCore.QSize(0, 120))
        self.attachment_scrollarea.setMaximumSize(QtCore.QSize(16777215, 120))
        self.attachment_scrollarea.setFrameShape(QtGui.QFrame.NoFrame)
        self.attachment_scrollarea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.attachment_scrollarea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.attachment_scrollarea.setWidgetResizable(True)
        self.attachment_scrollarea.setObjectName("attachment_scrollarea")
        self.attachment_scrollarea_contents = QtGui.QWidget()
        self.attachment_scrollarea_contents.setGeometry(QtCore.QRect(0, 0, 461, 120))
        self.attachment_scrollarea_contents.setObjectName("attachment_scrollarea_contents")
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.attachment_scrollarea_contents)
        self.horizontalLayout_3.setSpacing(1)
        self.horizontalLayout_3.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.thumbnail_7 = QtGui.QLabel(self.attachment_scrollarea_contents)
        self.thumbnail_7.setMinimumSize(QtCore.QSize(128, 100))
        self.thumbnail_7.setMaximumSize(QtCore.QSize(128, 100))
        self.thumbnail_7.setText("")
        self.thumbnail_7.setPixmap(QtGui.QPixmap(":/tk_multi_infopanel_reply_widget/rect_512x400.png"))
        self.thumbnail_7.setScaledContents(True)
        self.thumbnail_7.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnail_7.setObjectName("thumbnail_7")
        self.horizontalLayout_3.addWidget(self.thumbnail_7)
        self.thumbnail_5 = QtGui.QLabel(self.attachment_scrollarea_contents)
        self.thumbnail_5.setMinimumSize(QtCore.QSize(128, 100))
        self.thumbnail_5.setMaximumSize(QtCore.QSize(128, 100))
        self.thumbnail_5.setText("")
        self.thumbnail_5.setPixmap(QtGui.QPixmap(":/tk_multi_infopanel_reply_widget/rect_512x400.png"))
        self.thumbnail_5.setScaledContents(True)
        self.thumbnail_5.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnail_5.setObjectName("thumbnail_5")
        self.horizontalLayout_3.addWidget(self.thumbnail_5)
        self.thumbnail_6 = QtGui.QLabel(self.attachment_scrollarea_contents)
        self.thumbnail_6.setMinimumSize(QtCore.QSize(128, 100))
        self.thumbnail_6.setMaximumSize(QtCore.QSize(128, 100))
        self.thumbnail_6.setText("")
        self.thumbnail_6.setPixmap(QtGui.QPixmap(":/tk_multi_infopanel_reply_widget/rect_512x400.png"))
        self.thumbnail_6.setScaledContents(True)
        self.thumbnail_6.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnail_6.setObjectName("thumbnail_6")
        self.horizontalLayout_3.addWidget(self.thumbnail_6)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.attachment_scrollarea.setWidget(self.attachment_scrollarea_contents)
        self.verticalLayout.addWidget(self.attachment_scrollarea)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(ReplyWidget)
        QtCore.QMetaObject.connectSlotsByName(ReplyWidget)

    def retranslateUi(self, ReplyWidget):
        ReplyWidget.setWindowTitle(QtGui.QApplication.translate("ReplyWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.user.setText(QtGui.QApplication.translate("ReplyWidget", "John Smith", None, QtGui.QApplication.UnicodeUTF8))
        self.date.setText(QtGui.QApplication.translate("ReplyWidget", "3 days ago", None, QtGui.QApplication.UnicodeUTF8))
        self.reply.setText(QtGui.QApplication.translate("ReplyWidget", "McSweeney\'s tote bag ennui, Marfa quinoa lomo chambray squid retro bitters. Schlitz craft beer McSweeney\'s typewriter irony lomo. Four dollar toast selvage vinyl lo-fi, narwhal dreamcatcher tattooed meh drinking vinegar pug craft beer blog jean shorts. Cronut try-hard bespoke, banjo kale chips viral butcher. Occupy McSweeney\'s Godard fanny pack +1 pour-over, skateboard paleo ugh dreamcatcher Banksy. Vinyl pork belly iPhone, four loko DIY cardigan twee Neutra kogi flannel selvage sustainable mumblecore VHS. Hella sustainable vegan, pop-up 3 wolf moon brunch occupy literally direct trade asymmetrical Echo Park trust fund fap crucifix Odd Future.", None, QtGui.QApplication.UnicodeUTF8))
        self.attachment_header.setText(QtGui.QApplication.translate("ReplyWidget", "Attachments", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
