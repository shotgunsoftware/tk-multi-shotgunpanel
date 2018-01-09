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
 
# import the shotgun_model and view modules from the shotgun utils framework
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
shotgun_view = sgtk.platform.import_framework("tk-framework-qtwidgets", "views")

from .widget_list_item import ListItemWidget

class ListItemDelegate(shotgun_view.EditSelectedWidgetDelegate):
    """
    Delegate which 'glues up' the Details Widget with a QT View.
    
    It is used in most of the item listings in the Panel:
    
    - list of notes
    - list of publishes
    - list of versions
    - list of tasks

    It is paired up with the ListItemWidget.

    :signal change_work_area(str, int): Fires when someone clicks the change
        work area button. Arguments passed are the entity type and entity id

    """

    change_work_area = QtCore.Signal(str, int)

    def __init__(self, view, action_manager):
        """
        Constructor
        
        :param view: The view where this delegate is being used
        :param action_manager: Action manager instance
        """                
        shotgun_view.EditSelectedWidgetDelegate.__init__(self, view)
        self._action_manager = action_manager
        
    def _create_widget(self, parent):
        """
        Widget factory as required by base class. The base class will call this
        when a widget is needed and then pass this widget in to the various callbacks.
        
        :param parent: Parent object for the widget
        """
        return ListItemWidget(parent)
    
    def _on_before_selection(self, widget, model_index, style_options):
        """
        Called when the associated widget is selected. This method 
        implements all the setting up and initialization of the widget
        that needs to take place prior to a user starting to interact with it.
        
        :param widget: The widget to operate on (created via _create_widget)
        :param model_index: The model index to operate on
        :param style_options: QT style options
        """
        # do std drawing first
        self._on_before_paint(widget, model_index, style_options)        
        widget.set_selected(True)
        
        # now set up actions menu
        sg_item = shotgun_model.get_sg_data(model_index)

        num_actions = self._action_manager.populate_menu(
            widget.actions_menu,
            sg_item,
            self._action_manager.UI_AREA_MAIN
        )
        if num_actions > 0:
            widget.actions_button.show()

        # set up the switch work area
        widget.set_up_work_area(sg_item["type"], sg_item["id"])

        widget.work_area_button.change_work_area.connect(self.change_work_area.emit)

    def _on_before_paint(self, widget, model_index, style_options):
        """
        Called by the base class when the associated widget should be
        painted in the view. This method should implement setting of all
        static elements (labels, pixmaps etc) but not dynamic ones (e.g. buttons)
        
        :param widget: The widget to operate on (created via _create_widget)
        :param model_index: The model index to operate on
        :param style_options: QT style options
        """
        icon = shotgun_model.get_sanitized_data(model_index, QtCore.Qt.DecorationRole)
        if icon:
            thumb = icon.pixmap(512)
            widget.set_thumbnail(thumb)

        # note: This is a violation of the model/delegate independence.
        if model_index.model().sourceModel().is_highlighted(model_index):
            widget.set_highlighted(True)
        else:
            widget.set_highlighted(False)

        # get the shotgun data
        sg_item = shotgun_model.get_sg_data(model_index)
        
        # get the formatter object which defines how this object is to be presented
        sg_formatter = model_index.model().sourceModel().get_formatter()
        
        # ask to format the data
        (header_left, header_right, body) = sg_formatter.format_list_item_details(sg_item)

        widget.set_text(header_left, header_right, body)

        
    def sizeHint(self, style_options, model_index):
        """
        Specify the size of the item.
        
        :param style_options: QT style options
        :param model_index: Model item to operate on
        """
        return ListItemWidget.calculate_size()
             
