# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform.qt import QtCore, QtGui
from .ui.reply_list_widget import Ui_ReplyListWidget
from .widget_reply import ReplyWidget 
from .model_reply import SgReplyModel
 
class ReplyListWidget(QtGui.QWidget):
    """
    Note Reply Widget! 
    """
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """

        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_ReplyListWidget() 
        self.ui.setupUi(self)
        
        self._dynamic_widgets = []
        
        self._reply_model = SgReplyModel(self)
        
        
        w = ReplyWidget(self)
        self.ui.reply_layout.addWidget(w)
        
        w = ReplyWidget(self)
        self.ui.reply_layout.addWidget(w)
        


    def load_data(self, sg_entity_dict):
        """
        Clear widget and 
        
        """
        for x in self._dynamic_widgets:
            # remove widget from layout:
            self.ui.reply_layout.removeWidget(x)
            # set it's parent to None so that it is removed from the widget hierarchy
            x.setParent(None)
            # mark it to be deleted when event processing returns to the main loop
            x.deleteLater()
                
        self._dynamic_widgets = []
        
        # load up data from the model
        self.load_data(sg_entity_dict)

