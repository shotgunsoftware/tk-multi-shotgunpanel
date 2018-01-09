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
from .ui.list_item_widget import Ui_ListItemWidget
from .work_area_button import FloatingWorkAreaButton

shotgun_menus = sgtk.platform.import_framework("tk-framework-qtwidgets", "shotgun_menus")

class ListItemWidget(QtGui.QWidget):
    """
    Widget that is used to display entries in all the item listings.
    This widget goes together with the list item delegate and is always
    manufactured by the list item delegate.
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

        # set up action menu. parent it to the button to prevent cases where it
        # shows up elsewhere on screen (as in Houdini)
        self._menu = shotgun_menus.ShotgunMenu(self.ui.button)
        self.ui.button.setMenu(self._menu)
        self.ui.button.setVisible(False)
                                  
        # this forces the menu to be right aligned with the button. This is
        # preferable since many DCCs show the embed panel on the far right.  In
        # houdini at least, before forcing this layout direction, the menu was
        # showing up partially offscreen.
        self.ui.button.setLayoutDirection(QtCore.Qt.RightToLeft)

        # add work area button
        self._work_area_button = FloatingWorkAreaButton(self.ui.box)

    @property
    def actions_menu(self):
        """
        ShotgunMenu derived actions menu
        """
        return self._menu

    @property
    def actions_button(self):
        """
        Actions button widget
        """
        return self.ui.button

    @property
    def work_area_button(self):
        """
        The special button which controls the work area
        """
        return self._work_area_button

    def set_selected(self, selected):
        """
        Adjust the style sheet to indicate selection or not
        
        :param selected: True if selected, false if not
        """
        if selected:
            self.ui.box.setStyleSheet(self._css_selected)
        
    def set_highlighted(self, highlighted):
        """
        Adjust the style sheet to indicate that an object is highlighted
        
        :param selected: True if selected, false if not
        """
        if highlighted:
            self.ui.box.setStyleSheet(self._css_decorated)
        else:
            self.ui.box.setStyleSheet(self._no_style)

    def set_up_work_area(self, entity_type, entity_id):
        """
        Sets up the set work area button

        :param entity_type: shotgun type to set up work area for
        :param entity_id:  Shotgun id to set up work area for
        """
        self._work_area_button.set_up(entity_type, entity_id)

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
        
        :param header_left: Header text as string
        :param header_right: Header text as string
        :param body: Body text as string
        """
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


