# Copyright (c) 2021 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

import sgtk
from sgtk.platform.qt import QtCore, QtGui
from tank.util import sgre as re

HookClass = sgtk.get_hook_baseclass()


class ViewConfiguration(HookClass):
    """
    Hook to define how the list view data is displayed.
    """

    # The hook class and method that define the item definitions/template strings for rendering items.
    SG_FIELDS_HOOK = "shotgun_fields_hook"
    SG_FIELDS_HOOK_METHOD = "get_list_item_definition"

    # Mapping between the item definition fields to this ViewConfiguration's fields.
    TITLE_FIELD = "top_left"
    SUBTITLE_FIELD = "top_right"
    DETAILS_FIELD = "body"

    def __init__(self, *args, **kwargs):
        """
        Constructor
        """

        super(ViewConfiguration, self).__init__(*args, **kwargs)

        # A look up map for template strings by entity type and field.
        self._template_strings = {}

    def get_item_thumbnail(self, item, sg_data):
        """
        Returns the data to display for this model index item's thumbnail.

        Default implementation gets the item's Qt.DecorationRole data. Override this method
        if the thumbnail data is not stored in the Qt.DecorationRole.

        :param item: The model item.
        :type item: :class:`sgtk.platform.qt.QtGui.QStandardItem`
        :param sg_data: The Shotgun data for this item.
        :type sg_data: dict

        :return: The thumbnail data.
        :rtype: str
                | :class:`sgtk.platform.qt.QtGui.QPixmap`
                | :class:`sgtk.platform.qt.QtGui.QIcon`
        """

        return item.data(QtCore.Qt.DecorationRole)

    def get_item_title(self, item, sg_data):
        """
        Returns the data to display for this model index item's title.

        If a title template string is defined, return a tuple where the first item is the
        template string and the second item is the Shotgun data to format the template
        string with. This tuple return value may be consumed by the :class:`ViewItemDelegate`
        that will search and replace the tempalte string with the specified values from
        the Shotgun data provided.

        :param item: The model item.
        :type item: :class:`sgtk.platform.qt.QtGui.QStandardItem`
        :param sg_data: The Shotgun data for this item.
        :type sg_data: dict

        :return: The title data.
        :rtype: tuple(str,str)
        """

        return self._get_item_data(item, sg_data, self.TITLE_FIELD)

    def get_item_subtitle(self, item, sg_data):
        """
        Returns the data to display for this model index item's subtitle.

        If a subtitle template string is defined, return a tuple where the first item is the
        template string and the second item is the Shotgun data to format the template
        string with. This tuple return value may be consumed by the :class:`ViewItemDelegate`
        that will search and replace the tempalte string with the specified values from
        the Shotgun data provided.

        :param item: The model item.
        :type item: :class:`sgtk.platform.qt.QtGui.QStandardItem`
        :param sg_data: The Shotgun data for this item.
        :type sg_data: dict

        :return: The subtitle data.
        :rtype: tuple(str,str)
        """

        return self._get_item_data(item, sg_data, self.SUBTITLE_FIELD)

    def get_item_details(self, item, sg_data):
        """
        Returns the data to display for this model index item's detailed text.

        If a details template string is defined, return a tuple where the first item is the
        template string and the second item is the Shotgun data to format the template
        string with. This tuple return value may be consumed by the :class:`ViewItemDelegate`
        that will search and replace the tempalte string with the specified values from
        the Shotgun data provided.

        :param item: The model item.
        :type item: :class:`sgtk.platform.qt.QtGui.QStandardItem`
        :param sg_data: The Shotgun data for this item.
        :type sg_data: dict

        :return: The details data.
        :rtype: tuple(str,str)
        """

        return self._get_item_data(item, sg_data, self.DETAILS_FIELD)

    def _get_item_data(self, item, sg_data, field):
        """
        Returns the data to display for the given model item, Shotgun data and field. The display
        data is in the form a tuple, where item (1) is a templated string that has Shotgun tokens
        to resolve using the Shotgun data for the item, and (2) the Shotgun data.

        For more details on the template string format and how Shotgun tokens are resolved, see
        the `shotgun_fields` hook, or the framework `tk-framework-qtwidgets` `utils.py` module where
        the template string may be resolved (e.g. when using the ViewItemDelegaet).

        :return: The display data for the item's field.
        :rtype: tuple(str,str)
        """

        if not sg_data:
            return None

        entity_type = sg_data.get("type")
        if not entity_type:
            return None

        template_str = self._template_strings.get(entity_type, {}).get(field)

        if template_str is None:
            item_def = self.parent.execute_hook_method(
                self.SG_FIELDS_HOOK,
                self.SG_FIELDS_HOOK_METHOD,
                entity_type=entity_type,
            )
            template_str = item_def.get(field, "")
            self._template_strings.setdefault(entity_type, {})[field] = template_str

        return (template_str, sg_data)
