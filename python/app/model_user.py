# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk.platform.qt import QtCore, QtGui

# import the shotgun_model module from the shotgun utils framework
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model") 
ShotgunModel = shotgun_model.ShotgunModel 

class SgUserModel(ShotgunModel):
    """
    This model represents status codes.
    """
    
    def __init__(self, parent):
        """
        Constructor
        """
        # folder icon
        ShotgunModel.__init__(self, parent, download_thumbs=False)
        fields=["code", "image"]
        self._load_data("HumanUser", [], ["code"], fields)
        self._refresh_data()
    
    ############################################################################################
    # public methods
    
    def get_pixmap(self, code):
        """
        Returns the status as a QPixMap
        """
        for idx in range(self.rowCount()):
            item = self.item(idx)
            
            if item.text() == code:
                icon_name = item.get_sg_data().get("icon.Icon.image_map_key")
                return QtGui.QPixmap(":/tk_multi_infopanel/%s.png" % icon_name)
                        
        return None
        
