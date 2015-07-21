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

import datetime
from ... import utils
 
class ActivityStreamWidget(QtGui.QWidget):
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
        
