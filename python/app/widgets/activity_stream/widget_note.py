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

from .widget_activity_stream_base import ActivityStreamBaseWidget
from .ui.note_widget import Ui_NoteWidget

from .data_manager import ActivityStreamDataHandler
from ... import utils

class NoteWidget(ActivityStreamBaseWidget):
    """
    Widget that replies event stream details for a note
    """
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """
        # first, call the base class and let it do its thing.
        ActivityStreamBaseWidget.__init__(self, parent)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_NoteWidget() 
        self.ui.setupUi(self)
        
        # make sure clicks propagate upwards in the hierarchy
        self.ui.footer.linkActivated.connect(self._entity_request_from_url)
        self.ui.header_left.linkActivated.connect(self._entity_request_from_url)    
        
        self.ui.user_thumb.clicked.connect(lambda entity_type, entity_id: self.entity_requested.emit(entity_type, entity_id))    

    ##############################################################################
    # public interface

    def set_info(self, data):
        """
        Populate text fields for this widget
        
        :param data: data dictionary with activity stream info. 
        """        
        # call base class
        ActivityStreamBaseWidget.set_info(self, data)
        
        self.ui.user_thumb.set_shotgun_data(data["created_by"])
        
        # set standard date field
        self._set_timestamp(data, self.ui.date)

    def set_thumbnail(self, image, thumbnail_type):
        """
        Populate the UI with the given thumbnail
        
        :param image: QImage with thumbnail data
        :param thumbnail_type: thumbnail enum constant:
            ActivityStreamDataHandler.THUMBNAIL_CREATED_BY
            ActivityStreamDataHandler.THUMBNAIL_ENTITY
            ActivityStreamDataHandler.THUMBNAIL_ATTACHMENT
        """        
        if thumbnail_type == ActivityStreamDataHandler.THUMBNAIL_CREATED_BY:
            thumb = utils.create_round_thumbnail(image)          
            self.ui.user_thumb.setPixmap(thumb)

