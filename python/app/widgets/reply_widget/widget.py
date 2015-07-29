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

import datetime
from ... import utils
 
class ReplyListWidget(QtGui.QWidget):
    """
    Widget that displays a series of replies to a note
    """
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """

        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self, parent)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_ReplyListWidget() 
        self.ui.setupUi(self)
        
        # set up our reply area
        self.ui.reply_input.set_placeholder_text("Reply to this Note...")
        self.ui.reply_input.data_updated.connect(self.refresh)
        
        # holds the note that we are associating with
        self._current_entity_link = None
        
        # dynamically built widgets are stored here, 
        # keyed by reply id
        self._dynamic_widgets = {}
        
        # create a data model to use to load the replies
        self._reply_model = SgReplyModel(self)
        self._reply_model.thumbnail_updated.connect(self._update_thumbnail)
        self._reply_model.data_updated.connect(self._update_sg_data)
        
    def set_data_retriever(self, data_retriever):
        
        self.ui.reply_input.set_data_retriever(data_retriever)
        
        
    def set_current_user_thumbnail(self, pixmap):
        """
        Update the current user thumb for this widget.
        This thumbnail is displayed next to the 
        reply input widget and normally represents
        the current user.
        
        :param pixmap: Pixmap object to repreesent the current user
        """
        self.ui.current_user_thumbnail.setPixmap(pixmap)
        
    def _update_thumbnail(self, reply_id):
        """
        Update the thumbnail for the given reply id.
        
        :param reply_id: reply id to update thumbnail for
        """        
        # find the corresponding widget
        widget = self._dynamic_widgets.get(reply_id)
        
        # find the item in the model
        item = self._reply_model.item_from_entity("Reply", reply_id)
        thumb_pixmap = item.icon().pixmap(100)
        
        # do the update
        widget.set_thumbnail(thumb_pixmap)

    def _update_sg_data(self):
        """
        Rebuild the widget with new sg data from the model.
        """
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
            
            # TODO - should probably hook this up to the shotgun formatter
            # need to work out how the relationship between this widget and the
            # formatter works...
            created_datetime = datetime.datetime.fromtimestamp(sg_data["created_at"])
            (human_str, _) = utils.create_human_readable_timestamp(created_datetime) 
            
            w.set_content(sg_data["user"]["name"], human_str, sg_data["content"])
            w.set_thumbnail(pixmap)
            
            self.ui.reply_layout.addWidget(w)
            self._dynamic_widgets[sg_id] = w
        
    def _clear_widget(self):
        """
        Clear the widget from all existing replies
        """
        for x in self._dynamic_widgets.values():
            # remove widget from layout:
            self.ui.reply_layout.removeWidget(x)
            # set it's parent to None so that it is removed from the widget hierarchy
            x.setParent(None)
            # mark it to be deleted when event processing returns to the main loop
            x.deleteLater()
                
        self._dynamic_widgets = {}
        
    ##########################################################################################
    # public interface
        
    def refresh(self):
        """
        Refresh this widget. This will
        """
        self._reply_model.load(self._current_entity_link)
        
        
    def load_data(self, sg_entity_dict):
        """
        Load replies for a given entity.
        
        :param sg_entity_dict: Shotgun link dictionary with keys type and id.
        """
        self._current_entity_link = sg_entity_dict
        
        # tell reply widget where to push new entries...
        self.ui.reply_input.set_current_entity(sg_entity_dict["type"], sg_entity_dict["id"])
        
        # load up data from the model
        self.refresh()

