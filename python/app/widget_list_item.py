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
import datetime

from sgtk.platform.qt import QtCore, QtGui
 
# import the shotgun_model and view modules from the shotgun utils framework
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
shotgun_view = sgtk.platform.import_framework("tk-framework-qtwidgets", "shotgun_view")

from .ui.list_item_widget import Ui_ListItemWidget

class ListItemWidget(QtGui.QWidget):
    """
    """
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """
        QtGui.QWidget.__init__(self, parent)

        # make sure this widget isn't shown
        self.setVisible(False)
        
        # set up the UI
        self.ui = Ui_ListItemWidget() 
        self.ui.setupUi(self)
                
        # compute highlight colors
        p = QtGui.QPalette()
        highlight_col = p.color(QtGui.QPalette.Active, QtGui.QPalette.Highlight)
        self._highlight_str = "rgb(%s, %s, %s)" % (highlight_col.red(), 
                                                   highlight_col.green(), 
                                                   highlight_col.blue())
        self._transp_highlight_str = "rgba(%s, %s, %s, 25%%)" % (highlight_col.red(), 
                                                                 highlight_col.green(), 
                                                                 highlight_col.blue())        
                                    
    def set_selected(self, selected):
        """
        Adjust the style sheet to indicate selection or not
        
        :param selected: True if selected, false if not
        """
        if selected:
            self.ui.box.setStyleSheet("""#box {border-width: 2px; 
                                                 border-color: %s; 
                                                 border-style: solid; 
                                                 background-color: %s}
                                      """ % (self._highlight_str, self._transp_highlight_str))

        else:
            self.ui.box.setStyleSheet("")
    
    def set_highlighted(self, highlighted):
        """
        Adjust the style sheet to indicate that an object is highlighted
        
        :param selected: True if selected, false if not
        """
        if highlighted:
            self.ui.box.setStyleSheet("""#box {border-width: 1px; 
                                                 border-color: %s; 
                                                 border-style: solid}
                                      """ % self._highlight_str)

        else:
            self.ui.box.setStyleSheet("")

    def set_thumbnail(self, pixmap):
        """
        Set a thumbnail given the current pixmap.
        The pixmap must be 100x100 or it will appear squeezed
        
        :param pixmap: pixmap object to use
        """
        self.ui.thumbnail.setPixmap(pixmap)
            
    def set_text(self, header_left, header_right, body):
        """
        Populate the lines of text in the widget
        
        :param header: Header text as string
        :param body: Body text as string
        """
        #self.setToolTip("%s<br>%s" % (header_left, body))        
        self.ui.top_left.setText(header_left)
        self.ui.top_right.setText(header_right)
        self.ui.body.setText(body)

    @staticmethod
    def calculate_size():
        """
        Calculates and returns a suitable size for this widget.
        
        :returns: Size of the widget
        """        
        return QtCore.QSize(300, 90)


