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
    Widget that is used to display entries in all the item listings.
    This widget goes together with the list item delegate and is always
    manuafactured by the list item delegate.
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
        
        # the property stylesheet syntax seems brittle and hacky so 
        # keeping the style sheet modifications local here rather
        # than in global css
        
        # todo: figure out a better way to do this!

        self._css_decorated = """
            #box { border-width: 2px; 
                   border-radius: 4px;
                   border-color: rgb(48, 167, 227); 
                   border-style: solid;
            }
            """
        
        self._css_selected = """
            #box { border-width: 2px; 
                   border-radius: 4px;
                   border-color: rgb(48, 167, 227); 
                   border-style: solid; 
                   background-color: rgba(48, 167, 227, 25%);
            }        
            """                                    

        self._no_style = """
            #box { border-width: 2px; 
                   border-radius: 4px;
                   border-color: rgba(0, 0, 0, 0%); 
                   border-style: solid; 
            }        
            """

        # set up action menu
        self._menu = QtGui.QMenu()
        self._actions = []
        self.ui.button.setMenu(self._menu)
        self.ui.button.setVisible(False)
                                  

    def set_selected(self, selected):
        """
        Adjust the style sheet to indicate selection or not
        
        :param selected: True if selected, false if not
        """
        if selected:
            self.ui.box.setStyleSheet(self._css_selected)
            self.ui.button.setVisible(True)
        
    def set_highlighted(self, highlighted):
        """
        Adjust the style sheet to indicate that an object is highlighted
        
        :param selected: True if selected, false if not
        """
        if highlighted:
            self.ui.box.setStyleSheet(self._css_decorated)
        else:
            self.ui.box.setStyleSheet(self._no_style)

    def set_actions(self, actions):
        """
        Adds a list of QActions to add to the actions menu for this widget.
        
        :param actions: List of QActions to add
        """
        if len(actions) == 0:
            self.ui.button.setVisible(False)
        else:
            self.ui.button.setVisible(True)
            self._actions = actions
            for a in self._actions:
                self._menu.addAction(a)

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
        self.ui.list_item_top_left.setText(header_left)
        self.ui.list_item_top_right.setText(header_right)
        self.ui.list_item_body.setText(body)

    @staticmethod
    def calculate_size():
        """
        Calculates and returns a suitable size for this widget.
        
        :returns: Size of the widget
        """        
        return QtCore.QSize(300, 102)


