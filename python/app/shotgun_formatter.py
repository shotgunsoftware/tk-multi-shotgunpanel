# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk import TankError
from sgtk.platform.qt import QtCore, QtGui
import re
import datetime
import pprint
from . import utils

shotgun_globals = sgtk.platform.import_framework(
    "tk-framework-shotgunutils",
    "shotgun_globals",
)
qtwidgets_utils = sgtk.platform.import_framework(
    "tk-framework-qtwidgets",
    "utils",
)


class ShotgunTypeFormatter(object):
    """
    The Shotgun Formatter object holds information on
    how a particular shotgun entity type should be formatted
    and displayed.

    A lot of the information accessible from this class comes from
    the shotgun_fields hook which defines how information should be
    presented, which fields should be displayed etc.
    """

    def __init__(self, entity_type):
        """
        Constructor
        """
        self._entity_type = entity_type
        self._round_default_icon = QtGui.QPixmap(
            ":/tk_multi_infopanel/round_512x400.png"
        )
        self._rect_default_icon = QtGui.QPixmap(":/tk_multi_infopanel/rect_512x400.png")

        self._app = sgtk.platform.current_bundle()

        # read in the hook data into a dict
        self._hook_data = {}

        self._hook_data["get_list_item_definition"] = self._app.execute_hook_method(
            "shotgun_fields_hook", "get_list_item_definition", entity_type=entity_type
        )

        self._hook_data["get_all_fields"] = self._app.execute_hook_method(
            "shotgun_fields_hook", "get_all_fields", entity_type=entity_type
        )

        self._hook_data["get_main_view_definition"] = self._app.execute_hook_method(
            "shotgun_fields_hook", "get_main_view_definition", entity_type=entity_type
        )

        self._hook_data["get_entity_tabs_definition"] = self._app.execute_hook_method(
            "shotgun_fields_hook",
            "get_entity_tabs_definition",
            entity_type=entity_type,
            shotgun_globals=shotgun_globals,
        )

        self._hook_data["get_entity_default_tab"] = self._app.execute_hook_method(
            "shotgun_fields_hook", "get_entity_default_tab", entity_type=entity_type
        )

        # extract a list of fields given all the different {tokens} defined
        fields = []
        fields += self._resolve_sg_fields(
            self._get_hook_value("get_list_item_definition", "top_left")
        )
        fields += self._resolve_sg_fields(
            self._get_hook_value("get_list_item_definition", "top_right")
        )
        fields += self._resolve_sg_fields(
            self._get_hook_value("get_list_item_definition", "body")
        )
        fields += self._resolve_sg_fields(
            self._get_hook_value("get_main_view_definition", "title")
        )
        fields += self._resolve_sg_fields(
            self._get_hook_value("get_main_view_definition", "body")
        )

        # also include the thumbnail field so that it gets retrieved as part of the general
        # query payload
        fields.extend(self.thumbnail_fields)

        # include system fields that are needed for the app
        if entity_type == "Version":
            fields.append("sg_uploaded_movie")
            fields.append("sg_path_to_frames")
            fields.append("project")
        if entity_type == "Note":
            fields.append("read_by_current_user")
            fields.append("client_note")
            fields.append("project")
        if entity_type == "PublishedFile":
            fields.append("path")
            fields.append("project")
        if entity_type == "Task":
            fields.append("project")

        self._token_fields = set(fields)

    def __repr__(self):
        return "<SG '%s' type formatter>" % self._entity_type

    ###############################################################################################
    # helper methods

    def _resolve_sg_fields(self, token_str):
        """
        Convenience method. Returns the sg fields for all tokens
        given a token_str

        :param token_str: String with tokens, e.g. "{code}_{created_by}"
        :returns: All shotgun fields, e.g. ["code", "created_by"]
        """
        fields = []

        for (_, sg_fields, _, _, _) in self._resolve_tokens(token_str):
            fields.extend(sg_fields)

        return fields

    def _resolve_tokens(self, token_str):
        """
        Resolve a list of tokens from a string.

        Tokens are on the following form:

            {[preroll]shotgun.field.name|sg_field_name_fallback::directive[postroll]}

        Basic Examples:

        - {code}                         # simple format
        - {sg_sequence.Sequence.code}    # deep links
        - {artist|created_by}            # if artist is null, use creted_by

        Directives are also supported - these are used by the formatting logic
        and include the following:

        - {sg_sequence::showtype}        # will generate a link saying
                                         # 'Sequence ABC123' instead of just
                                         # 'ABC123' like it does by default
        - {sg_sequence::nolink}          # no url link will be created

        Optional pre/post roll - if a value is null, pre- and post-strings are
        omitted from the final result. Examples of this syntax:

        - {[Name: ]code}                 # If code is set, 'Name: xxx' will be
                                         # printed out, otherwise nothing.
        - {[Name: ]code[<br>]}           # Same but with a post line break

        :param token_str: String with tokens, e.g. "{code}_{created_by}"
        returns: a list of tuples with (full_token, sg_fields, directive, preroll, postroll)
        """

        try:
            # find all field names ["xx", "yy", "zz.xx"] from "{xx}_{yy}_{zz.xx}"
            raw_tokens = set(re.findall("{([^}^{]*)}", token_str))
        except Exception as error:
            raise TankError("Could not parse '%s' - Error: %s" % (token_str, error))

        fields = []
        for raw_token in raw_tokens:

            pre_roll = None
            post_roll = None
            directive = None

            processed_token = raw_token

            match = re.match("^\[([^\]]+)\]", processed_token)
            if match:
                pre_roll = match.group(1)
                # remove preroll part from main token
                processed_token = processed_token[len(pre_roll) + 2 :]

            match = re.match(".*\[([^\]]+)\]$", processed_token)
            if match:
                post_roll = match.group(1)
                # remove preroll part from main token
                processed_token = processed_token[: -(len(post_roll) + 2)]

            if "::" in processed_token:
                # we have a special formatting directive
                # e.g. created_at::ago
                (sg_field_str, directive) = processed_token.split("::")
            else:
                sg_field_str = processed_token

            if "|" in sg_field_str:
                # there is more than one sg field, we have a
                # series of fallbacks
                sg_fields = sg_field_str.split("|")
            else:
                sg_fields = [sg_field_str]

            fields.append((raw_token, sg_fields, directive, pre_roll, post_roll))

        return fields

    def _get_hook_value(self, method_name, hook_key):
        """
        Validate that value is correct and return it
        """

        if method_name not in self._hook_data:
            raise TankError("Unknown shotgun_fields hook method %s" % method_name)

        data = self._hook_data[method_name]

        if hook_key not in data:
            raise TankError(
                "Hook shotgun_fields.%s does not return "
                "required dictionary key '%s'!" % (method_name, hook_key)
            )

        return data[hook_key]

    def _sg_field_to_str(self, sg_type, sg_field, value, directive=None):
        """
        Converts a Shotgun field value to a string.

        Formatting directives can be passed to alter the conversion behaviour:

        - showtype: Show the type for links, e.g. return "Shot ABC123" instead
          of just "ABC123"

        - nolink: don't return a <a href> style hyperlink for links, instead just
          return a string.

        :param sg_type: Shotgun data type
        :param sg_field: Shotgun field name
        :param value: value to turn into a string
        :param directive: Formatting directive, see above
        """
        str_val = ""

        if value is None:
            return shotgun_globals.get_empty_phrase(sg_type, sg_field)

        elif isinstance(value, dict) and set(["type", "id", "name"]) == set(
            value.keys()
        ):
            # entity link

            if directive == "showtype":
                # links are displayed as "Shot ABC123"

                # get the nice name from our schema
                # this is so that it says "Level" instead of "CustomEntity013"
                entity_type_display_name = shotgun_globals.get_type_display_name(
                    value["type"]
                )
                link_name = "%s %s" % (entity_type_display_name, value["name"])
            else:
                # links are just "ABC123"
                link_name = value["name"]

            if not self._generates_links(value["type"]) or directive == "nolink":
                str_val = link_name
            else:
                str_val = qtwidgets_utils.get_hyperlink_html(
                    url="sgtk:%s:%s" % (value["type"], value["id"]),
                    name=link_name,
                )

        elif isinstance(value, list):
            # list of items
            link_urls = []
            for list_item in value:
                link_urls.append(
                    self._sg_field_to_str(sg_type, sg_field, list_item, directive)
                )
            str_val = ", ".join(link_urls)

        elif sg_field in ["created_at", "updated_at"]:
            created_datetime = datetime.datetime.fromtimestamp(value)
            (str_val, _) = utils.create_human_readable_timestamp(created_datetime)

        elif sg_field == "sg_status_list":
            str_val = shotgun_globals.get_status_display_name(value)

            color_str = shotgun_globals.get_status_color(value)
            if color_str:
                # append colored box to indicate status color
                str_val = "<span style='color: rgb(%s)'>" "&#9608;</span>&nbsp;%s" % (
                    color_str,
                    str_val,
                )

        else:
            str_val = str(value)
            # make sure it gets formatted correctly in html
            str_val = str_val.replace("\n", "<br>")

        return str_val

    def _generates_links(self, entity_type):
        """
        Returns true if the given entity type
        should be hyperlinked to, false if not
        """
        if entity_type in ["Step", "TankType", "PublishedFileType"]:
            return False
        else:
            return True

    def _convert_token_string(self, token_str, sg_data):
        """
        Convert a string with {tokens} given a shotgun data dict

        :param token_str: Token string as defined in the shotgun fields hook
        :param sg_data: Data dictionary to get values from
        :returns: string with tokens replaced with actual values
        """
        # extract all tokens and process them one after the other
        for (
            full_token,
            sg_fields,
            directive,
            pre_roll,
            post_roll,
        ) in self._resolve_tokens(token_str):

            # get the first sg field value we find
            # this is usef when we have a fallback syntax in the token string,
            # for example {artist|created_by}
            for sg_field in sg_fields:
                sg_value = sg_data.get(sg_field)
                if sg_value:
                    # got a value so stop looking
                    break

            if (sg_value is None or sg_value == []) and (pre_roll or post_roll):
                # shotgun value is empty
                # if we have a pre or post roll part of the token
                # then we basicaly just skip the display of both
                # those and the value entirely
                # e.g. Hello {[Shot:]sg_shot} becomes:
                # for shot abc: 'Hello Shot:abc'
                # for shot <empty>: 'Hello '
                token_str = token_str.replace("{%s}" % full_token, "")

            else:
                resolved_value = self._sg_field_to_str(
                    sg_data["type"], sg_field, sg_value, directive
                )

                # potentially add pre/and post
                if pre_roll:
                    resolved_value = "%s%s" % (pre_roll, resolved_value)
                if post_roll:
                    resolved_value = "%s%s" % (resolved_value, post_roll)
                # and replace the token with the value
                token_str = token_str.replace("{%s}" % full_token, resolved_value)

        return token_str

    ####################################################################################################
    # properties

    @property
    def default_pixmap(self):
        """
        Returns the default pixmap associated with this location
        """
        if self.entity_type in ["Note", "HumanUser", "ApiUser", "ClientUser"]:
            return self._round_default_icon
        else:
            return self._rect_default_icon

    @property
    def thumbnail_fields(self):
        """
        Returns the field names to use when looking for thumbnails
        """
        if self.entity_type == "Note":
            return [
                "user.HumanUser.image",
                "user.ClientUser.image",
                "user.ApiUser.image",
            ]
        else:
            return ["image"]

    @property
    def entity_type(self):
        """
        Returns the entity type associated with this formatter
        """
        return self._entity_type

    @property
    def should_open_in_shotgun_web(self):
        """
        Property to indicate if links to this item should
        open in the shotgun web app rather than inside the
        shotgun panel.
        """
        if self._entity_type == "Playlist":
            # jump to sg
            return True
        else:
            # internal link
            return False

    @property
    def all_fields(self):
        """
        All fields listing
        """
        return self._hook_data["get_all_fields"]

    @property
    def fields(self):
        """
        fields needed to render list or main details
        """
        return list(self._token_fields)

    ####################################################################################################
    # public methods

    def create_thumbnail(self, image, sg_data):
        """
        Given a QImage representing a thumbnail and return a formatted
        pixmap that is suitable for that data type.

        :param image: QImage representing a shotgun thumbnail
        :param sg_data: Data associated with the thumbnail
        :returns: Pixmap object
        """
        if self.entity_type in ["HumanUser", "ApiUser"]:
            return utils.create_round_512x400_note_thumbnail(image)

        elif self.entity_type == "ClientUser":
            return utils.create_round_512x400_note_thumbnail(image, client=True)

        elif self.entity_type == "Note":

            client_note = sg_data.get("client_note") or False

            if sg_data["read_by_current_user"] == "unread":
                unread = True
            else:
                unread = False

            return utils.create_round_512x400_note_thumbnail(image, client_note, unread)

        elif self.entity_type == "Task" and sg_data["type"] == "HumanUser":
            # a user icon for a task
            # todo: refcator this logic to make it clearer
            return utils.create_round_512x400_note_thumbnail(image)

        else:
            return utils.create_rectangular_512x400_thumbnail(image)

    @classmethod
    def get_playback_url(cls, sg_data):
        """
        Returns a url to be used for playback

        :param sg_data: Shotgun data dictionary
        :returns: Screening room url
        """
        # TODO - we might want to expose this in the hook at some point
        if sg_data.get("type") != "Version":
            return None

        url = None
        if sg_data.get("sg_uploaded_movie"):
            # there is a web quicktime available!
            sg_url = sgtk.platform.current_bundle().sgtk.shotgun_url
            # redirect to std shotgun player, same as you go to if you click the
            # play icon inside of the shotgun web ui
            url = "%s/page/media_center?type=Version&id=%d" % (sg_url, sg_data["id"])

        return url

    def format_raw_value(self, entity_type, field_name, value, directive=None):
        """
        Format a raw shotgun value

        Formatting directives can be passed to alter the conversion behaviour:

        - showtype: Show the type for links, e.g. return "Shot ABC123" instead
          of just "ABC123"

        - nolink: don't return a <a href> style hyperlink for links, instead just
          return a string.

        :param entity_type: Shotgun entity type
        :param field_name: Shotgun field name
        :param value: Raw shotgun value
        :param directive: Formatting directive
        """
        return self._sg_field_to_str(entity_type, field_name, value, directive)

    def format_entity_details(self, sg_data):
        """
        Render full details for a Shotgun entity.
        Formatting settings are read from the shotgun_fields hook.

        :param sg_data: Shotgun data dictionary. The shotgun fields
               returned by the fields parameter need to be included in
               this data dictionary.
        :returns: tuple with formatted and resolved (header, body) strings.
        """
        title = self._get_hook_value("get_main_view_definition", "title")
        body = self._get_hook_value("get_main_view_definition", "body")

        title_converted = self._convert_token_string(title, sg_data)
        body_converted = self._convert_token_string(body, sg_data)

        return (title_converted, body_converted)

    def format_list_item_details(self, sg_data):
        """
        Render details for list items to be displayed.

        Formatting settings are read from the shotgun_fields hook.

        :param sg_data: Shotgun data dictionary. The shotgun fields
               returned by the fields parameter need to be included in
               this data dictionary.
        :returns: tuple with formatted and resolved (top_left, top_right,
                  body) strings.
        """

        top_left = self._get_hook_value("get_list_item_definition", "top_left")
        top_right = self._get_hook_value("get_list_item_definition", "top_right")
        body = self._get_hook_value("get_list_item_definition", "body")

        top_left_converted = self._convert_token_string(top_left, sg_data)
        top_right_converted = self._convert_token_string(top_right, sg_data)
        body_converted = self._convert_token_string(body, sg_data)

        return (top_left_converted, top_right_converted, body_converted)

    def get_link_filters(self, sg_location):
        """
        Executes hook to return a filter string which links this type up to a
        particular location.

        For example, if the current formatter object is describing how to
        format a Note and the sg_location parameter represents a user,
        a query is returned that describes how to retrieved all notes
        associated with that particular user.

        :param sg_location: Location object describing the object for
                            which associated items should be retrieved.

        :returns: Std shotgun filters that can be used to retrieve
                  associated data
        """

        return self._app.execute_hook_method(
            "shotgun_filters_hook",
            "get_link_filters",
            sg_location=sg_location,
            entity_type=self._entity_type,
            context_project=self._app.context.project,
            context_user=self._app.context.user,
        )


class ShotgunEntityFormatter(ShotgunTypeFormatter):
    """
    A more detailed formatter subclassing the ShotgunTypeFormatter.

    This formatter takes a Shotgun entity id, meaning that it can
    be more intelligent when resolving things like descriptions, tooltips etc.
    """

    def __init__(self, entity_type, entity_id):
        """
        Constructor
        """
        super(ShotgunEntityFormatter, self).__init__(entity_type)
        self._entity_id = entity_id

    def __repr__(self):
        return "<SG %s %s entity formatter>" % (self._entity_type, self._entity_id)

    @property
    def entity_id(self):
        """
        The entity id for this formatter
        """
        return self._entity_id

    @property
    def entity_dict(self):
        """
        Returns the shotgun entity dict for this formatter
        """
        return {"type": self.entity_type, "id": self.entity_id}

    @property
    def is_current_user(self):
        """
        Returns true if the formatter represents the current user.
        """
        # Note: the context's user might be None if we're authenticated with a
        # script key and the user's current OS login doesn't match their Shotgun
        # user name. In that situation, we don't know what the Shotgun user is,
        # and we get a None back from the context. In that case, we need to
        # assume that is_current_user is False.
        if (
            self._app.context.user is not None
            and self.entity_type == self._app.context.user.get("type")
            and self.entity_id == self._app.context.user.get("id")
        ):
            return True
        else:
            return False

    @property
    def default_tab(self):
        """
        Tab to start a new view with
        """

        return self._hook_data["get_entity_default_tab"]

    def get_tab_data(self, name, field, default_value=None):
        """
        Return the data field's value for the tab under the given name.
        """

        defintion = self._get_hook_value("get_entity_tabs_definition", name)
        return defintion.get(field, default_value)

    def show_entity_tab(self, name):
        """
        Return whether or not to show the tab for the entity type.
        """
        from .dialog import AppDialog

        if (
            name == AppDialog.ENTITY_TAB_INFO
            and self.is_current_user
            and self.entity_type == "HumanUser"
        ):
            return (False, "")

        defintion = self._get_hook_value("get_entity_tabs_definition", name)
        caption = defintion["name"]

        if (
            self.is_current_user
            and self.entity_type == "HumanUser"
            and name in [AppDialog.ENTITY_TAB_VERSIONS, AppDialog.ENTITY_TAB_PUBLISHES]
        ):
            caption = "My %s" % caption

        elif name == AppDialog.ENTITY_TAB_TASKS and (
            (self.is_current_user and self.entity_type == "HumanUser")
            or self.entity_type == "Project"
        ):
            caption = "My %s" % caption

        return (defintion["enabled"], caption)

    def get_entity_tab_description(self, name):
        """
        Return the tab description for this entity type.
        """
        from .dialog import AppDialog

        if self.entity_type != "Project":
            if self.is_current_user:
                if name == AppDialog.ENTITY_TAB_NOTES:
                    return "Your conversations, in update order."

                if name == AppDialog.ENTITY_TAB_VERSIONS:
                    return "Your review versions, in creation order."

                if name == AppDialog.ENTITY_TAB_PUBLISHES:
                    if self._app.context.project:
                        return "Your publishes for this project, in creation order."
                    return "All your publishes, in creation order."

                if name == AppDialog.ENTITY_TAB_TASKS:
                    if self._app.context.project:
                        return "Your active tasks for this project."
                    return "All your active tasks."

        definition = self._get_hook_value("get_entity_tabs_definition", name)
        return definition.get("description", "")
