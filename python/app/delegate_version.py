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

from . import utils

from sgtk.platform.qt import QtCore, QtGui
 
# import the shotgun_model and view modules from the shotgun utils framework
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
shotgun_view = sgtk.platform.import_framework("tk-framework-qtwidgets", "shotgun_view")

from .widget_rect import RectWidget

class VersionDelegate(shotgun_view.WidgetDelegate):
    """
    Delegate which 'glues up' the Details Widget with a QT View.
    """

    def __init__(self, view):
        """
        Constructor
        
        :param view: The view where this delegate is being used
        :param action_manager: Action manager instance
        """                
        shotgun_view.WidgetDelegate.__init__(self, view)
        
    def _create_widget(self, parent):
        """
        Widget factory as required by base class. The base class will call this
        when a widget is needed and then pass this widget in to the various callbacks.
        
        :param parent: Parent object for the widget
        """
        return RectWidget(parent)
    
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
        
        sg_item = shotgun_model.get_sg_data(model_index)

        created_unixtime = sg_item.get("created_at")
        created_datetime = datetime.datetime.fromtimestamp(created_unixtime)
        (human_str, exact_str) = utils.create_human_readable_timestamp(created_datetime)

        user_name = (sg_item.get("artist") or {}).get("name") or "Unknown User"        
        description = sg_item.get("description") or ""
        content = "By %s %s<br><i>%s</i>" % (user_name, human_str, description)

        title = "<b>%s</b>" % sg_item.get("code") or "Untitled Version"

        widget.set_text(title, content)
        
        
    def sizeHint(self, style_options, model_index):
        """
        Specify the size of the item.
        
        :param style_options: QT style options
        :param model_index: Model item to operate on
        """
        return RectWidget.calculate_size()
             
