# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Wrapper for the various widgets used from frameworks so that they can be used
easily from with Qt Designer
"""

import sgtk

activity_stream = sgtk.platform.import_framework("tk-framework-qtwidgets", "activity_stream")
ActivityStreamWidget = activity_stream.ActivityStreamWidget
ReplyListWidget = activity_stream.ActivityStreamWidget

note_input_widget = sgtk.platform.import_framework("tk-framework-qtwidgets", "note_input_widget")
NoteInputWidget = note_input_widget.NoteInputWidget

version_label = sgtk.platform.import_framework("tk-framework-qtwidgets", "version_label")
VersionLabel = version_label.VersionLabel

global_search_widget = sgtk.platform.import_framework("tk-framework-qtwidgets", "global_search_widget")
GlobalSearchWidget = global_search_widget.GlobalSearchWidget


