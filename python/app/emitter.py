# Copyright (c) 2016 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform.qt import QtCore, QtGui

class Emitter(QtCore.QObject):
    """
    Houses any signals that the parent Application need to emit.

    :signal context_changed(object, object): When the context is changed, this
        is emitted with old and new context objects passed along, respectively.
    """

    context_changed = QtCore.Signal(object, object)

