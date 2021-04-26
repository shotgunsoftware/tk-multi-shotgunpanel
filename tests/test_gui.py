# Copyright (c) 2020 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import pytest
import subprocess
import time
import os
import sys
import sgtk

try:
    from MA.UI import topwindows
    from MA.UI import first
except ImportError:
    pytestmark = pytest.mark.skip()


# This fixture will launch tk-run-app on first usage
# and will remain valid until the test run ends.
@pytest.fixture(scope="session")
def host_application(tk_test_project, tk_test_entities):
    """
    Launch the host application for the Toolkit application.

    TODO: This can probably be refactored, as it is not
     likely to change between apps, except for the context.
     One way to pass in a context would be to have the repo being
     tested to define a fixture named context and this fixture
     would consume it.
    """
    process = subprocess.Popen(
        [
            "python",
            "-m",
            "tk_toolchain.cmd_line_tools.tk_run_app",
            # Allows the test for this application to be invoked from
            # another repository, namely the tk-framework-widget repo,
            # by specifying that the repo detection should start
            # at the specified location.
            "--location",
            os.path.dirname(__file__),
            "--context-entity-type",
            tk_test_project["type"],
            "--context-entity-id",
            str(tk_test_project["id"]),
        ]
    )
    try:
        yield
    finally:
        # We're done. Grab all the output from the process
        # and print it so that is there was an error
        # we'll know about it.
        stdout, stderr = process.communicate()
        sys.stdout.write(stdout or "")
        sys.stderr.write(stderr or "")
        process.poll()
        # If returncode is not set, then the process
        # was hung and we need to kill it
        if process.returncode is None:
            process.kill()
        else:
            assert process.returncode == 0


@pytest.fixture(scope="session")
def app_dialog(host_application):
    """
    Retrieve the application dialog and return the AppDialogAppWrapper.
    """
    before = time.time()
    while before + 60 > time.time():
        if sgtk.util.is_windows():
            app_dialog = AppDialogAppWrapper(topwindows)
        else:
            app_dialog = AppDialogAppWrapper(topwindows["python"])

        if app_dialog.exists():
            yield app_dialog
            app_dialog.close()
            return
    else:
        raise RuntimeError("Timeout waiting for the app dialog to launch.")


class AppDialogAppWrapper(object):
    """
    Wrapper around the app dialog.
    """

    def __init__(self, parent):
        """
        :param root:
        """
        self.root = parent["Shotgun: Shotgun"].get()

    def exists(self):
        """
        ``True`` if the widget was found, ``False`` otherwise.
        """
        return self.root.exists()

    def close(self):
        self.root.buttons["Close"].get().mouseClick()


def test_my_tasks(app_dialog, tk_test_project, tk_test_entities, tk_test_current_user):
    """
    My Tasks tab validation
    """
    # Wait for the UI to show up, click on the home button and make sure My Tasks tab is selected by default
    app_dialog.root.buttons["Click to go to your work area"].waitExist(timeout=30)
    app_dialog.root.buttons["Click to go to your work area"].mouseClick()
    assert app_dialog.root.tabs[
        "My Tasks"
    ].selected, "My Tasks tab should be selected by default"
    # Wait for the task item to show up and then double click on it
    app_dialog.root.listitems.waitExist(timeout=30)
    wait = time.time()
    # This while loop is to make sure the double click on the task switches the current context successfully
    while wait + 30 > time.time():
        if app_dialog.root.captions["Task Model"].exists() is False:
            app_dialog.root.listitems.mouseDoubleClick()
            time.sleep(2)
        else:
            break

    # Activity tab validation
    assert app_dialog.root.captions["Task Model"].exists(), "Not on the right context"
    assert app_dialog.root.tabs[
        "Activity"
    ].selected, "Activity tab should be selected by default"
    assert app_dialog.root.captions[
        "Status:*Waiting to Start*Asset AssetAutomation*Assigned to: "
        + tk_test_current_user["name"]
    ].exists(), "Not on the right task information"
    assert app_dialog.root.captions[
        "Task Model was created on Asset AssetAutomation"
    ].exists(), "Not the right task created on the right entity"

    # Notes tab validation
    app_dialog.root.tabs["Notes"].mouseClick()
    app_dialog.root.captions[
        "Notes associated with this Task, in update order."
    ].waitExist(timeout=30)
    assert (
        app_dialog.root.listitems.exists() is False
    ), "Should not have any notes for the task"

    # Versions tab validation
    app_dialog.root.tabs["Versions"].mouseClick()
    app_dialog.root.captions[
        "Review versions for this Task, in creation order."
    ].waitExist(timeout=30)
    assert (
        app_dialog.root.listitems.exists() is False
    ), "Should not have any versions linked to the Model task"
    assert (
        app_dialog.root.checkboxes["Only show versions pending review"].checked is False
    ), "Only show versions pending review should be unchecked by default"

    # Publishes tab validation
    app_dialog.root.tabs["Publishes"].mouseClick()
    app_dialog.root.listitems.waitExist(timeout=30)
    app_dialog.root.captions["Publishes for this Task, in creation order."].waitExist(
        timeout=30
    )
    app_dialog.root.listitems.waitExist(timeout=30)
    assert app_dialog.root.checkboxes[
        "Only show latest versions"
    ].exists(), "Missing Only show latest versions checkbox"
    assert app_dialog.root.checkboxes[
        "Only show latest versions"
    ].checked, "Only show latest versions should be checked by default"

    # Tasks tab validation
    app_dialog.root.tabs["Tasks"].mouseClick()
    app_dialog.root.captions["All tasks for this Task."].waitExist(timeout=30)
    app_dialog.root.listitems.waitExist(timeout=30)

    # Task Details tab validation
    app_dialog.root.tabs["Details"].mouseClick()
    app_dialog.root.captions["Bid"].waitExist(timeout=30)
    assert app_dialog.root.captions[
        "Assigned To"
    ].exists(), "Assigned To attribute is missing"
    assert app_dialog.root.captions[
        tk_test_current_user["name"]
    ].exists(), "Not assigned to the right user."
    assert app_dialog.root.captions["Cc"].exists(), "Cc attribute is missing"
    assert app_dialog.root.captions[
        "Created by"
    ].exists(), "Created by attribute is missing"
    assert app_dialog.root.captions[
        "Date Created"
    ].exists(), "Date Created attribute is missing"
    assert app_dialog.root.captions[
        "Date Updated"
    ].exists(), "Date Updated attribute is missing"
    assert app_dialog.root.captions[
        "Due Date"
    ].exists(), "Due Date attribute is missing"
    assert app_dialog.root.captions[
        "Duration"
    ].exists(), "Duration attribute is missing"
    assert app_dialog.root.captions["Id"].exists(), "Id attribute is missing"
    assert app_dialog.root.captions[
        str(tk_test_entities[0]["id"])
    ].exists(), "Not getting the right id for Model task"
    assert app_dialog.root.captions["Link"].exists(), "Link attribute is missing"
    assert app_dialog.root.captions[
        "AssetAutomation"
    ].exists(), "Not linked to the right entity. Should be AssetAutomation"
    assert app_dialog.root.captions[
        "Pipeline Step"
    ].exists(), "Pipeline Step attribute is missing"
    assert app_dialog.root.captions[
        "Model"
    ].exists(), "Wrong pipeline step. SHould be Model"
    assert app_dialog.root.captions["Project"].exists(), "Project attribute is missing"
    assert app_dialog.root.captions[
        str(tk_test_project["name"])
    ].exists(), "Wrong project name."
    assert app_dialog.root.captions[
        "Start Date"
    ].exists(), "Start Date attribute is missing"
    assert app_dialog.root.captions["Status"].exists(), "Status attribute is missing"
    assert app_dialog.root.captions[
        "*Waiting to Start"
    ].exists(), "Bad status. Should be Waiting to Start"
    assert app_dialog.root.captions[
        "Task Name"
    ].exists(), "Task Name attribute is missing"
    assert app_dialog.root.captions["Type"].exists(), "Type attribute is missing"
    assert app_dialog.root.captions["Task"].exists(), "Wrong type. Should be Task type"
    assert app_dialog.root.captions[
        "Updated by"
    ].exists(), "Updated by attribute is missing"
    assert app_dialog.root.captions[
        "tag_list"
    ].exists(), "tag_list attribute is missing"

    # Go back to the default work area
    app_dialog.root.buttons["Click to go to your work area"].mouseClick()


def test_activity_notes_tabs(
    app_dialog, tk_test_project, tk_test_entities, tk_test_current_user
):
    """
    Activity and Notes tabs validation
    """
    # Wait for the UI to show up and click on the Activity tab
    app_dialog.root.buttons["Click to go to your work area"].waitExist(timeout=30)
    app_dialog.root.buttons["Click to go to your work area"].mouseClick()

    # Click on the Activity tab
    app_dialog.root.tabs["Activity"].mouseClick()
    assert app_dialog.root.tabs["Activity"].selected, "Activity tab should be selected"

    # Wait until note creation field is showing up.
    wait = time.time()
    while wait + 30 > time.time():
        if app_dialog.root.captions["Loading SG Data..."].exists():
            time.sleep(1)
        else:
            break

    # Click to create a new note
    app_dialog.root.captions["Click to create a new note..."].mouseClick()

    # Validate that all buttons are available
    assert app_dialog.root.buttons[
        "Cancel"
    ].exists(), "Cancel buttons is not showing up"
    assert app_dialog.root.buttons[
        "Attach Files"
    ].exists(), "Attach Screenshot buttons is not showing up"
    assert app_dialog.root.buttons[
        "Take Screenshot"
    ].exists(), "Take Screenshot buttons is not showing up"
    assert app_dialog.root.buttons[
        "Create Note"
    ].exists(), "Create Note buttons is not showing up"

    # Add a note
    app_dialog.root.textfields.typeIn("New note created by automation")
    app_dialog.root.buttons["Create Note"].mouseClick()
    app_dialog.root.captions["Reply to this Note"].waitExist(timeout=30)

    # Validate the Note gets created
    assert app_dialog.root.captions[
        "New note created by automation"
    ].exists(), "New note wasn't created"
    assert app_dialog.root.captions[
        "Reply to this Note"
    ].exists(), "New note wasn't created"

    # Validate that all activities are showing up in the activity stream
    assert app_dialog.root.captions[
        "Published File sven.png was created on Asset AssetAutomation"
    ].exists(), "Published File sven.png creation is missing in the activity stream"
    assert app_dialog.root.captions[
        "Version sven.png was created on Asset AssetAutomation"
    ].exists(), "Version sven.png creation is missing in the activity stream"
    assert app_dialog.root.captions[
        "Task Rig was created on Asset AssetAutomation"
    ].exists(), "Task Rig creation is missing in the activity stream"
    assert app_dialog.root.captions[
        "Task Model was created on Asset AssetAutomation"
    ].exists(), "Task Model creation is missing in the activity stream"
    assert app_dialog.root.captions[
        "Asset AssetAutomation was created"
    ].exists(), "Asset AssetAutomation creation is missing in the activity stream"
    assert app_dialog.root.captions[
        "Project " + str(tk_test_project["name"]) + " was created"
    ].exists(), (
        "Project Toolkit UI Automation creation is missing in the activity stream"
    )
    assert app_dialog.root.buttons[
        "Click here to see the Activity stream in Shotgun."
    ].exists(), "Hyperlink to see the Activity Stream in SG is missing"

    # Click on the Notes tab
    app_dialog.root.tabs["Notes"].mouseClick()
    assert app_dialog.root.tabs["Notes"].selected, "Notes tab should be selected"

    # Notes tab validation
    app_dialog.root.captions["All notes for this project, in update order."].waitExist(
        timeout=30
    )

    # Open the note item
    app_dialog.root.listitems.waitExist(timeout=30)
    app_dialog.root.listitems.mouseDoubleClick()
    app_dialog.root.captions["*Note on " + str(tk_test_project["name"])].waitExist(
        timeout=30
    )
    assert app_dialog.root.captions[
        "New note created by automation"
    ].exists(), "New Note is missing"
    assert app_dialog.root.captions[
        "Note by "
        + tk_test_current_user["name"]
        + "*Written on*Addressed to: "
        + tk_test_current_user["name"]
        + "*Associated With:*"
        + tk_test_project["name"]
        + "*"
    ].exists(), "Not the Notes details"

    # Create a reply
    app_dialog.root.captions["Reply to this Note"].mouseClick()
    app_dialog.root.dialogs["Reply"].waitExist(timeout=30)

    # Validate that all buttons are available
    assert (
        app_dialog.root.dialogs["Reply"].buttons["Cancel"].exists()
    ), "Cancel buttons is not showing up"
    assert (
        app_dialog.root.dialogs["Reply"].buttons["Attach Files"].exists()
    ), "Attach Screenshot buttons is not showing up"
    assert (
        app_dialog.root.dialogs["Reply"].buttons["Take Screenshot"].exists()
    ), "Take Screenshot buttons is not showing up"
    assert (
        app_dialog.root.dialogs["Reply"].buttons["Create Note"].exists()
    ), "Create Note buttons is not showing up"

    # Validate that the File browser is showing up after clicking on the Files to attach button then close it
    app_dialog.root.dialogs["Reply"].buttons["Attach Files"].mouseClick()
    app_dialog.root.dialogs["Select files to attach."].waitExist(timeout=30)

    # Get image path to be published
    image_path = os.path.normpath(
        os.path.expandvars("${TK_TEST_FIXTURES}/files/images/sven.png")
    )

    # Type in image path
    app_dialog.root.dialogs["Select files to attach."].textfields[
        "File name:"
    ].mouseClick()
    app_dialog.root.dialogs["Select files to attach."].textfields["File name:"].pasteIn(
        image_path
    )
    app_dialog.root.dialogs["Select files to attach."].textfields[
        "File name:"
    ].waitIdle(timeout=30)
    app_dialog.root.dialogs["Select files to attach."].textfields["File name:"].typeIn(
        "{ENTER}"
    )

    # Validate that all buttons are available
    assert (
        app_dialog.root.dialogs["Reply"].buttons["Cancel"].exists()
    ), "Cancel button is not showing up"
    assert (
        app_dialog.root.dialogs["Reply"].buttons["add_button"].exists()
    ), "Add attachments button is not showing up"
    assert (
        app_dialog.root.dialogs["Reply"].buttons["remove_button"].exists()
    ), "Remove attachments button is not showing up"
    assert (
        app_dialog.root.dialogs["Reply"].buttons["Create Note"].exists()
    ), "Create Note button is not showing up"
    app_dialog.root.dialogs["Reply"].buttons["Create Note"].mouseClick()

    # Take a screenshot
    app_dialog.root.dialogs["Reply"].buttons["Take Screenshot"].mouseClick()
    app_window = first(app_dialog.root)
    width, height = app_window.size
    app_window.mouseSlide(width * 0, height * 0)
    app_window.mouseDrag(width * 1, height * 1)

    # Add a note
    app_dialog.root.dialogs["Reply"].textfields.typeIn("New Reply")
    app_dialog.root.dialogs["Reply"].buttons["Create Note"].mouseClick()
    app_dialog.root.captions["New Reply"].waitExist(timeout=30)

    # Validate the note gets created
    app_dialog.root.buttons["Click to go back"].mouseClick()
    app_dialog.root.captions["All notes for this project, in update order."].waitExist(
        timeout=30
    )
    app_dialog.root.tabs["Activity"].mouseClick()
    app_dialog.root.captions["New Reply"].waitExist(timeout=30)

    # Go back to the default work area
    app_dialog.root.buttons["Click to go to your work area"].mouseClick()


def test_versions_tab(
    app_dialog, tk_test_project, tk_test_entities, tk_test_current_user
):
    """
    Versions tab validation
    """
    # Wait for the UI to show up and click on the Versions tab
    app_dialog.root.buttons["Click to go to your work area"].waitExist(timeout=30)
    app_dialog.root.buttons["Click to go to your work area"].mouseClick()

    # Click on the Versions tab
    app_dialog.root.tabs["Versions"].mouseClick()
    assert app_dialog.root.tabs["Versions"].selected, "Versions tab should be selected"
    app_dialog.root.listitems.waitExist(timeout=30)
    assert (
        app_dialog.root.checkboxes["Only show versions pending review"].checked is False
    ), "Only show versions pending review should be unchecked by default"

    # Open the version
    app_dialog.root.listitems.mouseDoubleClick()
    app_dialog.root.captions[
        "This version was created by the Toolkit UI automation"
    ].waitExist(timeout=30)
    assert app_dialog.root.tabs[
        "Activity"
    ].selected, "Activity tab should be selected by default"
    app_dialog.root.captions["sven.png"].waitExist(timeout=30)
    assert app_dialog.root.captions[
        "Version sven.png was created on Asset AssetAutomation"
    ].exists(), "Version info is missing"
    assert app_dialog.root.captions[
        "Asset AssetAutomation*Status:*Pending Review*Created by "
        + tk_test_current_user["name"]
        + " on*Comments: This version was created by the Toolkit UI automation*"
    ].exists(), "Version info is missing or wrong"

    # Create a note on the version
    app_dialog.root.captions["Click to create a new note..."].mouseClick()
    app_dialog.root.textfields.typeIn("New note on a version created by automation")
    app_dialog.root.buttons["Create Note"].mouseClick()
    app_dialog.root.captions["Reply to this Note"].waitExist(timeout=30)

    # Click on the Notes tab and wait to make sure the note is showing up in the list item
    app_dialog.root.tabs["Notes"].mouseClick()
    app_dialog.root.listitems.waitExist(timeout=30)

    # Open the Note and make sure breadcrumb is good
    app_dialog.root.listitems.mouseDoubleClick()
    app_dialog.root.captions["*Note on sven.png, AssetAutomation"].waitExist(timeout=30)
    # Go back to the Note page and make sure breadcrumb is good
    app_dialog.root.buttons["Click to go back"].mouseClick()
    app_dialog.root.captions["sven.png"].waitExist(timeout=30)
    # Click back again and make sure the Versions tab is selected
    app_dialog.root.buttons["Click to go back"].mouseClick()
    app_dialog.root.captions["Project " + str(tk_test_project["name"])].waitExist(
        timeout=30
    )
    assert app_dialog.root.tabs[
        "Versions"
    ].selected, "Activity tab should be selected by default"

    # Re-select the version item
    app_dialog.root.listitems.mouseDoubleClick()
    app_dialog.root.tabs["Publishes"].waitExist(timeout=30)

    # Click on the Publishes tab and wait to make sure the published file is showing up in the list item
    app_dialog.root.tabs["Publishes"].mouseClick()
    app_dialog.root.listitems.waitExist(timeout=30)

    # Version's Details tab validation
    app_dialog.root.tabs["Details"].mouseClick()
    app_dialog.root.captions["Cuts"].waitExist(timeout=30)
    assert app_dialog.root.captions["Artist"].exists(), "Artist attribute is missing"
    assert app_dialog.root.captions[
        tk_test_current_user["name"]
    ].exists(), "Not asssigned to the right artist."
    assert app_dialog.root.captions[
        "Client Approved"
    ].exists(), "Client Approved attribute is missing"
    assert app_dialog.root.captions[
        "False"
    ].exists(), "Wrong client approved value. Should be False"
    assert app_dialog.root.captions[
        "Client Approved at"
    ].exists(), "Client Approved at attribute is missing"
    assert app_dialog.root.captions[
        "Client Approved by"
    ].exists(), "Client Approved by attribute is missing"
    assert app_dialog.root.captions[
        "Created by"
    ].exists(), "Created by attribute is missing"
    assert app_dialog.root.captions[
        "Date Created"
    ].exists(), "Date Created attribute is missing"
    assert app_dialog.root.captions[
        "Date Updated"
    ].exists(), "Date Updated attribute is missing"
    assert app_dialog.root.captions[
        "Department"
    ].exists(), "Department attribute is missing"
    assert app_dialog.root.captions[
        "Description"
    ].exists(), "Description attribute is missing"
    assert app_dialog.root.captions[
        "This version was created by the Toolkit UI automation"
    ].exists(), "Wrong description."
    assert app_dialog.root.captions[
        "First Frame"
    ].exists(), "First Frame attribute is missing"
    assert app_dialog.root.captions[
        "Frame Count"
    ].exists(), "Frame Count attribute is missing"
    assert app_dialog.root.captions[
        "Frame Range"
    ].exists(), "Frame Range attribute is missing"
    assert app_dialog.root.captions[
        "Frame Rate"
    ].exists(), "Frame Rate attribute is missing"
    assert app_dialog.root.captions["Id"].exists(), "Id attribute is missing"
    assert app_dialog.root.captions[
        str(tk_test_entities[2]["id"])
    ].exists(), "Not getting the right id for Model task"
    assert app_dialog.root.captions[
        "Last Frame"
    ].exists(), "Last Frame attribute is missing"
    assert app_dialog.root.captions["Link"].exists(), "Link attribute is missing"
    assert app_dialog.root.captions[
        "AssetAutomation"
    ].exists(), "Not linked to the right entity. Should be AssetAutomation"
    assert app_dialog.root.captions[
        "Path to Frames"
    ].exists(), "Path to Frames attribute is missing"
    assert app_dialog.root.captions[
        "Path to Geometry"
    ].exists(), "Path to Geometry attribute is missing"
    assert app_dialog.root.captions[
        "Path to Movie"
    ].exists(), "Path to Movie attribute is missing"
    assert app_dialog.root.captions[
        "Playlists"
    ].exists(), "Playlists attribute is missing"
    assert app_dialog.root.captions["Project"].exists(), "Project attribute is missing"
    assert app_dialog.root.captions[
        str(tk_test_project["name"])
    ].exists(), "Wrong project. Should be Toolkit UI Automation"
    assert app_dialog.root.captions[
        "Published Files"
    ].exists(), "Published Files attribute is missing"
    assert app_dialog.root.captions["Status"].exists(), "Status attribute is missing"
    assert app_dialog.root.captions[
        "*Pending Review"
    ].exists(), "Bad status. Should be Pending Review"
    assert app_dialog.root.captions["Task"].exists(), "Task attribute is missing"
    assert app_dialog.root.captions["Type"].exists(), "Type attribute is missing"
    assert app_dialog.root.captions[
        "Version"
    ].exists(), "Wrong type. Should be Version type"
    assert app_dialog.root.captions[
        "Updated by"
    ].exists(), "Updated by attribute is missing"
    assert app_dialog.root.captions[
        "Version Name"
    ].exists(), "Version Name attribute is missing"
    assert app_dialog.root.captions[
        "sven.png"
    ].exists(), "Wrong version name. Should be sven.png"
    assert app_dialog.root.captions[
        "tag_list"
    ].exists(), "tag_list attribute is missing"

    # Go back to the default work area
    app_dialog.root.buttons["Click to go to your work area"].mouseClick()


def test_publishes_tab(
    app_dialog, tk_test_project, tk_test_entities, tk_test_current_user
):
    """
    Publishes tab validation
    """
    # Wait for the UI to show up and click on the Publishes tab
    app_dialog.root.buttons["Click to go to your work area"].waitExist(timeout=30)
    app_dialog.root.buttons["Click to go to your work area"].mouseClick()

    # Click on the Publishes tab
    app_dialog.root.tabs["Publishes"].mouseClick()
    assert app_dialog.root.tabs[
        "Publishes"
    ].selected, "Publishes tab should be selected"
    app_dialog.root.listitems.waitExist(timeout=30)
    assert app_dialog.root.checkboxes[
        "Only show latest versions"
    ].checked, "Only show latest versions should be checked by default"

    # Open the published file
    app_dialog.root.listitems.mouseDoubleClick()
    app_dialog.root.captions["The version history for this publish."].waitExist(
        timeout=30
    )
    assert app_dialog.root.tabs[
        "Version History"
    ].selected, "Version History tab should be selected by default"
    app_dialog.root.captions["sven.png"].waitExist()
    assert app_dialog.root.captions[
        "Not set, Version 1*For Asset AssetAutomation, Task Model*Created by "
        + tk_test_current_user["name"]
        + " on*Reviewed here: sven.png*Comments:*This file was published by the Toolkit UI automation*"
    ].exists(), "Version info is missing or wrong"

    # Click on the Uses tab and list item should be empty
    app_dialog.root.tabs["Uses"].mouseClick()
    assert (
        app_dialog.root.listitems.exists() is False
    ), "Should not have any publishes listed"

    # Click on the Used By tab and list item should be empty
    app_dialog.root.tabs["Used By"].mouseClick()
    assert (
        app_dialog.root.listitems.exists() is False
    ), "Should not have any publishes listed"

    # Publish's Details tab validation
    app_dialog.root.tabs["Details"].mouseClick()
    app_dialog.root.captions["tag_list"].waitExist(timeout=30)
    assert app_dialog.root.captions[
        "Created by"
    ].exists(), "Created by attribute is missing"
    assert app_dialog.root.captions[
        tk_test_current_user["name"]
    ].exists(), "Not asssigned to the right artist."
    assert app_dialog.root.captions[
        "Date Created"
    ].exists(), "Date Created attribute is missing"
    assert app_dialog.root.captions[
        "Date Updated"
    ].exists(), "Date Updated attribute is missing"
    assert app_dialog.root.captions[
        "Description"
    ].exists(), "Description attribute is missing"
    assert app_dialog.root.captions[
        "This file was published by the Toolkit UI automation"
    ].exists(), "Missing or wrong description."
    assert app_dialog.root.captions["Id"].exists(), "Id attribute is missing"
    assert app_dialog.root.captions[
        str(tk_test_entities[1]["id"])
    ].exists(), "Not getting the right id for Model task"
    assert app_dialog.root.captions["Link"].exists(), "Link attribute is missing"
    assert app_dialog.root.captions[
        "AssetAutomation"
    ].exists(), "Not linked to the right entity. Should be AssetAutomation"
    assert app_dialog.root.captions["Name"].exists(), "Name attribute is missing"
    assert app_dialog.root.captions[
        "sven.png"
    ].exists(), "Wrong published file name. Should be sven.png"
    assert app_dialog.root.captions["Project"].exists(), "Project attribute is missing"
    assert app_dialog.root.captions[
        str(tk_test_project["name"])
    ].exists(), "Wrong project name."
    assert app_dialog.root.captions[
        "Published File Name"
    ].exists(), "Published File Name attribute is missing"
    assert app_dialog.root.captions[
        "Published File Type"
    ].exists(), "Published File Type attribute is missing"
    assert app_dialog.root.captions[
        "Not set"
    ].exists(), "Wrong published file type, Should be Not set."
    assert app_dialog.root.captions["Status"].exists(), "Status attribute is missing"
    assert app_dialog.root.captions[
        "*Waiting to Start"
    ].exists(), "Bad status. Should be Waiting to Start"
    assert app_dialog.root.captions["Task"].exists(), "Task attribute is missing"
    assert app_dialog.root.captions["Model"].exists(), "Wrong task, Should be Model."
    assert app_dialog.root.captions["Type"].exists(), "Type attribute is missing"
    assert app_dialog.root.captions[
        "PublishedFile"
    ].exists(), "Wrong type, Should be PublishedFile."
    assert app_dialog.root.captions[
        "Updated by"
    ].exists(), "Updated by attribute is missing"
    assert app_dialog.root.captions["Version"].exists(), "Version attribute is missing"
    assert app_dialog.root.captions[
        "Version Number"
    ].exists(), "Wrong type. Should be Version type"
    assert app_dialog.root.captions["1"].exists(), "Wrong version number. Should be 1"

    # Go back to the default work area
    app_dialog.root.buttons["Click to go to your work area"].mouseClick()


def test_search(app_dialog):
    """
    Search widget validation
    """
    # Wait for the UI to show up and click on the Versions tab
    app_dialog.root.buttons["Click to go to your work area"].waitExist(timeout=30)
    app_dialog.root.buttons["Click to go to your work area"].mouseClick()

    # Click on the search button
    app_dialog.root.buttons["Search Shotgun"].mouseClick()
    app_dialog.root.textfields.waitExist(timeout=30)

    # Search for sven.png
    app_dialog.root.textfields.typeIn("sven.png")
    topwindows.listitems["sven.png"].waitExist(timeout=30)

    # Clear the search text field
    app_dialog.root.textfields.buttons.mouseClick()

    # Do another search for asset
    app_dialog.root.textfields.mouseClick()
    app_dialog.root.textfields.typeIn("asset")
    topwindows.listitems["AssetAutomation"].waitExist(timeout=30)
    assert topwindows.listitems[
        "Rig"
    ].exists(), "Rig isn't showing up in the search list."
    assert topwindows.listitems[
        "Model"
    ].exists(), "Model isn't showing up in the search list."
    assert topwindows.listitems[
        "sven.png"
    ].exists(), "sven.png isn't showing up in the search list."

    # Clear the search text field
    app_dialog.root.textfields.buttons.mouseClick()

    # Do another search with a value that has not match
    app_dialog.root.textfields.mouseClick()
    app_dialog.root.textfields.typeIn("popo")
    topwindows.listitems["No matches found!"].waitExist(timeout=30)

    # Click on the search Cancel button
    app_dialog.root.buttons["Cancel"].mouseClick()

    # Go back to the default work area
    app_dialog.root.buttons["Click to go to your work area"].mouseClick()
