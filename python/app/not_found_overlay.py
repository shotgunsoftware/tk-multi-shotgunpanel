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
import sgtk

overlay_module = sgtk.platform.import_framework("tk-framework-qtwidgets", "overlay_widget")
ShotgunModelOverlayWidget = overlay_module.ShotgunModelOverlayWidget

class NotFoundModelOverlay(ShotgunModelOverlayWidget):
    """
    Shotgun model overlay extended to display a bitmap in case
    no records are found.
    """
    
    def __init__(self, model, view):
        """
        :param model: Shotgun Model to monitor
        :param view: View to place overlay on top of.
        """
        self._no_items_overlay = QtGui.QPixmap(":/tk_multi_infopanel/no_items_found.png")
                
        # init base class
        ShotgunModelOverlayWidget.__init__(self, model, view)
        
        # hook up callbacks
        self._model = model
        self._model.data_refreshed.connect(self._on_data_arrived)
        self._model.cache_loaded.connect(self._on_data_arrived)
    
    def _on_data_arrived(self):
        """
        Called when data has arrived
        """
        if len(self._model.entity_ids) == 0:
            self.show_message_pixmap(self._no_items_overlay)
