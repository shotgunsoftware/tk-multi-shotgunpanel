# Copyright (c) 2020 Autdesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.
import sgtk
import pprint

HookBaseClass = sgtk.get_hook_baseclass()


class ShotgunFilters(HookBaseClass):
    """
    Controls the filter configuration for the Shotgun Panel.

    Via this hook, the data that is retrieved for the Shotgun Panel can be controlled.
    """

    def get_link_filters(self, sg_location, entity_type, context_project, context_user):
        """
        Returns a filter string which links the entity type up to a particular
        location.

        :param sg_location: Location object describing the object for
                            which associated items should be retrieved.
        :param entity_type: The entity type to link to the location.
        :param context_project: The current context project.
        :param context_user: The current context user.

        :returns: Std shotgun filters that can be used to retrieve
                  associated data
        """

        link_filters = []

        if sg_location.entity_type in ["HumanUser"]:
            # the logic for users is different
            # here we want give an overview of their work
            # for the current project

            # When the current project is None, the user is in site context and we want to get
            # the requested fields for all user's tasks, notes, versions and publishes.
            if context_project:
                link_filters.append(["project", "is", context_project])

            if entity_type == "Task":
                # show tasks i am assigned to
                link_filters.append(["task_assignees", "in", [sg_location.entity_dict]])
                link_filters.append(["sg_status_list", "is_not", "fin"])

            elif (
                entity_type == "Note"
                and sg_location.entity_type == context_user.get("type")
                and sg_location.entity_id == context_user.get("id")
            ):
                # not just any user, but this is ME!
                # show notes that are TO me, CC me or on tasks which I have been
                # assigned. Use advanced filters for this one so we can use OR
                #
                # we basically want to show notes that are FOR me.

                link_filters.append(
                    {
                        "filter_operator": "or",
                        "filters": [
                            ["created_by", "is", sg_location.entity_dict],
                            [
                                "addressings_cc.Group.users",
                                "in",
                                sg_location.entity_dict,
                            ],
                            [
                                "addressings_to.Group.users",
                                "in",
                                sg_location.entity_dict,
                            ],
                            ["replies.Reply.user", "is", sg_location.entity_dict],
                            ["addressings_cc", "in", sg_location.entity_dict],
                            ["addressings_to", "in", sg_location.entity_dict],
                            [
                                "tasks.Task.task_assignees",
                                "in",
                                sg_location.entity_dict,
                            ],
                        ],
                    }
                )

            elif entity_type == "Note":
                # another user that isn't me.
                # show notes that are by this user or where this user has replied
                #
                # we basically want to show items that were generated BY this user.
                link_filters.append(
                    {
                        "filter_operator": "or",
                        "filters": [
                            ["created_by", "is", sg_location.entity_dict],
                            ["replies.Reply.user", "is", sg_location.entity_dict],
                        ],
                    }
                )

            else:
                # for other things, show items created by me
                link_filters.append(["created_by", "is", sg_location.entity_dict])

        elif sg_location.entity_type in ["ClientUser", "ApiUser"]:
            # the logic for users is different
            # here we want give an overview of their work
            # for the current project

            if entity_type == "Note":
                # show notes that are by this user or where this user has replied
                #
                # we basically want to show items that were generated BY this user.
                link_filters.append(
                    {
                        "filter_operator": "or",
                        "filters": [
                            ["replies.Reply.user", "is", sg_location.entity_dict],
                            ["created_by", "is", sg_location.entity_dict],
                        ],
                    }
                )
                if context_project:
                    # we are in a non-site context. only tasks from this project
                    link_filters.append(["project", "is", context_project])

            else:
                link_filters.append(["created_by", "is", sg_location.entity_dict])
                if context_project:
                    # we are in a non-site context. only tasks from this project
                    link_filters.append(["project", "is", context_project])

        elif sg_location.entity_type == "Task":

            # tasks are usually associated via a task field rather than via a link field
            if entity_type == "Note":
                link_filters.append(["tasks", "in", [sg_location.entity_dict]])

            elif entity_type == "Version":
                link_filters.append(["sg_task", "is", sg_location.entity_dict])

            elif entity_type in ["PublishedFile", "TankPublishedFile"]:
                link_filters.append(["task", "is", sg_location.entity_dict])

            elif entity_type == "Task":
                link_filters.append(["sibling_tasks", "is", sg_location.entity_dict])

            else:
                link_filters.append(["entity", "is", sg_location.entity_dict])

        elif sg_location.entity_type == "Project":

            # tasks are usually associated via a task field rather than via a link field
            if entity_type == "Note":
                link_filters.append(["project", "is", sg_location.entity_dict])

            elif entity_type == "Version":
                link_filters.append(["project", "is", sg_location.entity_dict])

            elif entity_type in ["PublishedFile", "TankPublishedFile"]:
                link_filters.append(["project", "is", sg_location.entity_dict])

            elif entity_type == "Task":
                # my tasks tab on project
                if context_user is None:
                    raise sgtk.TankError(
                        "Use of the My Tasks tab is not supported when a current Shotgun user "
                        "cannot be determined. This is most often the case when a script key "
                        "is used for authentication rather than a user name and password."
                    )

                link_filters.append(["task_assignees", "in", [context_user]])
                link_filters.append(["sg_status_list", "is_not", "fin"])
                link_filters.append(["project", "is", sg_location.entity_dict])

            else:
                link_filters.append(["entity", "is", sg_location.entity_dict])

        elif sg_location.entity_type == "Version":

            if entity_type == "Note":
                link_filters.append(["note_links", "in", [sg_location.entity_dict]])

            elif entity_type in ["PublishedFile", "TankPublishedFile"]:
                link_filters.append(["version", "is", sg_location.entity_dict])

            else:
                link_filters.append(["entity", "is", sg_location.entity_dict])

        else:
            if entity_type == "Note":
                link_filters.append(["note_links", "in", [sg_location.entity_dict]])
            else:
                link_filters.append(["entity", "is", sg_location.entity_dict])

        self.logger.debug(
            "%s Resolved %s into the following sg query:\n%s"
            % (self, sg_location, pprint.pformat(link_filters))
        )

        return link_filters
