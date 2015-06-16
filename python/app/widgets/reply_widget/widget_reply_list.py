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
        
        # widgets, keyed by reply id
        self._dynamic_widgets = {}
        
        self._reply_model = SgReplyModel(self)
        
        self._reply_model.thumbnail_updated.connect(self._update_thumbnail)
        self._reply_model.data_updated.connect(self._update_sg_data)
        
        
    def _update_thumbnail(self, sg_id):
        print 'update thumb! %s' % sg_id
        
        widget = self._dynamic_widgets.get(sg_id)
        if widget is None:
            print "old request!"
            return
        
        item = self._reply_model.item_from_entity("Reply", sg_id)
        thumb_pixmap = item.icon().pixmap(100)
        widget.set_thumbnail(thumb_pixmap)
         
        

    def _update_sg_data(self):
        print 'update data! %s records' % self._reply_model.rowCount()
        
        self._clear_widget()
        
        # now redraw the entire reply thread
        sg_records = {}
        for idx in xrange(self._reply_model.rowCount()):
            
            sg_model_item = self._reply_model.item(idx)
            sg_data = sg_model_item.get_sg_data()
            pixmap = sg_model_item.icon().pixmap(100)
            sg_records[sg_data["id"]] = {"sg_data": sg_data, "thumb": pixmap}
        
        for sg_id in sorted(sg_records.keys()):
            
            sg_data = sg_records[sg_id]["sg_data"]
            pixmap = sg_records[sg_id]["thumb"]
            
            w = ReplyWidget(self)
            w.set_content(str(sg_data["user"]["name"]), 
                          str(sg_data["created_at"]), 
                          sg_data["content"])
            w.set_thumbnail(pixmap)
            
            w.resize(10,10)
            
            self.ui.reply_layout.addWidget(w)
            self._dynamic_widgets[sg_id] = w
        


    def _clear_widget(self):
        """
        Reset widget
        """
        for x in self._dynamic_widgets.values():
            # remove widget from layout:
            self.ui.reply_layout.removeWidget(x)
            # set it's parent to None so that it is removed from the widget hierarchy
            x.setParent(None)
            # mark it to be deleted when event processing returns to the main loop
            x.deleteLater()
                
        self._dynamic_widgets = {}
        


    def load_data(self, sg_entity_dict):
        """
        Load conversation
        """
        # load up data from the model
        self._reply_model.load(sg_entity_dict)





