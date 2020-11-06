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
from tk_toolchain.authentication import get_toolkit_user

try:
    from MA.UI import topwindows
    from MA.UI import first
except ImportError:
    pytestmark = pytest.mark.skip()


@pytest.fixture(scope="session")
def credentials():
    # Get credentials from TK_TOOLCHAIN
    sg = get_toolkit_user().create_sg_connection()

    return sg


@pytest.fixture(scope="session")
def context(credentials):
    # Toolkit Shotgun panel UI Automation project which we're going to use
    # in different test cases.

    # Create or update the integration_tests local storage with the current test run
    storage_name = "Panel UI Tests"
    local_storage = credentials.find_one(
        "LocalStorage", [["code", "is", storage_name]], ["code"]
    )
    if local_storage is None:
        local_storage = credentials.create("LocalStorage", {"code": storage_name})
    # Always update local storage path
    local_storage["path"] = os.path.expandvars("${SHOTGUN_CURRENT_REPO_ROOT}")
    credentials.update(
        "LocalStorage", local_storage["id"], {"windows_path": local_storage["path"]}
    )

    # Make sure there is not already an automation project created
    filters = [["name", "is", "Toolkit Panel UI Automation"]]
    existed_project = credentials.find_one("Project", filters)
    if existed_project is not None:
        credentials.delete(existed_project["type"], existed_project["id"])

    # Create a new project with the Film VFX Template
    project_data = {
        "sg_description": "Project Created by Automation",
        "name": "Toolkit Panel UI Automation",
    }
    new_project = credentials.create("Project", project_data)

    return new_project


@pytest.fixture(scope="session")
def assetTask(context, credentials):
    # Create a Sequence to be used by the Shot creation
    sequence_data = {
        "project": {"type": context["type"], "id": context["id"]},
        "code": "seq_001",
        "sg_status_list": "ip",
    }
    new_sequence = credentials.create("Sequence", sequence_data)

    # Validate if Automation shot task template exists
    shot_template_filters = [["code", "is", "Automation Shot Task Template"]]
    existed_shot_template = credentials.find_one("TaskTemplate", shot_template_filters)
    if existed_shot_template is not None:
        credentials.delete(existed_shot_template["type"], existed_shot_template["id"])
    # Create a shot task templates
    shot_template_data = {
        "code": "Automation Shot Task Template",
        "description": "This shot task template was created by the Panel UI automation",
        "entity_type": "Shot",
    }
    shot_task_template = credentials.create("TaskTemplate", shot_template_data)
    # Get the Comp Pipeline step ID
    comp_pipeline_step_filter = [["code", "is", "Comp"]]
    comp_pipeline_step = credentials.find_one("Step", comp_pipeline_step_filter)
    # Create Comp task
    comp_task_data = {
        "content": "Comp",
        "step": comp_pipeline_step,
        "task_template": shot_task_template,
    }
    credentials.create("Task", comp_task_data)
    # Get the Light Pipeline step ID
    light_pipeline_step_filter = [["code", "is", "Light"]]
    light_pipeline_step = credentials.find_one("Step", light_pipeline_step_filter)
    # Create Light task
    light_task_data = {
        "content": "Light",
        "step": light_pipeline_step,
        "task_template": shot_task_template,
    }
    credentials.create("Task", light_task_data)
    # Validate if Automation asset task template exists
    asset_template_filters = [["code", "is", "Automation Asset Task Template"]]
    existed_asset_template = credentials.find_one(
        "TaskTemplate", asset_template_filters
    )
    if existed_asset_template is not None:
        credentials.delete(existed_asset_template["type"], existed_asset_template["id"])
    # Create an asset task templates
    asset_template_data = {
        "code": "Automation Asset Task Template",
        "description": "This asset task template was created by the Panel UI automation",
        "entity_type": "Asset",
    }
    asset_task_template = credentials.create("TaskTemplate", asset_template_data)
    # Get the Model Pipeline step ID
    model_pipeline_step_filter = [["code", "is", "Model"]]
    model_pipeline_step = credentials.find_one("Step", model_pipeline_step_filter)
    # Create Model task
    model_task_data = {
        "content": "Model",
        "step": model_pipeline_step,
        "task_template": asset_task_template,
    }
    credentials.create("Task", model_task_data)
    # Get the Rig Pipeline step ID
    rig_pipeline_step_filter = [["code", "is", "Rig"]]
    rig_pipeline_step = credentials.find_one("Step", rig_pipeline_step_filter)
    # Create Rig task
    rig_task_data = {
        "content": "Rig",
        "step": rig_pipeline_step,
        "task_template": asset_task_template,
    }
    credentials.create("Task", rig_task_data)

    # Create a new shot
    shot_data = {
        "project": context,
        "sg_sequence": new_sequence,
        "code": "shot_001",
        "description": "This shot was created by the Panel UI automation",
        "sg_status_list": "ip",
        "task_template": shot_task_template,
    }
    credentials.create("Shot", shot_data)

    # Create a new asset
    asset_data = {
        "project": context,
        "code": "AssetAutomation",
        "description": "This asset was created by the Panel UI automation",
        "sg_status_list": "ip",
        "sg_asset_type": "Character",
        "task_template": asset_task_template,
    }
    asset = credentials.create("Asset", asset_data)

    # Get the publish_file_type id to be passed in the publish creation
    published_file_type_filters = [["code", "is", "Image"]]
    published_file_type = credentials.find_one(
        "PublishedFileType", published_file_type_filters
    )

    # File to publish
    file_to_publish = os.path.join(
        os.path.expandvars("${TK_TEST_FIXTURES}"), "files", "images", "sven.png"
    )

    # Create a version an upload to it
    version_data = {
        "project": context,
        "code": "sven.png",
        "description": "This version was created by the Panel UI automation",
        "entity": asset,
    }
    version = credentials.create("Version", version_data)
    # Upload a version to the published file
    credentials.upload("Version", version["id"], file_to_publish, "sg_uploaded_movie")
    # Create a published file
    # Find the model task to publish to
    filters = [
        ["project", "is", context],
        ["entity.Asset.code", "is", asset["code"]],
        ["step.Step.code", "is", "model"],
    ]
    fields = ["sg_status_list"]
    model_task = credentials.find_one("Task", filters, fields)
    publish_data = {
        "project": context,
        "code": "sven.png",
        "name": "sven.png",
        "description": "This file was published by the Panel UI automation",
        "published_file_type": published_file_type,
        "path": {"local_path": file_to_publish},
        "entity": asset,
        "task": model_task,
        "version_number": 1,
        "version": version,
        "image": file_to_publish,
    }
    publish_file = credentials.create("PublishedFile", publish_data)

    # Assign a task to the current user
    # Find current user
    user = get_toolkit_user()
    current_user = credentials.find_one(
        "HumanUser", [["login", "is", str(user)]], ["name"]
    )
    # Assign current user to the task model
    credentials.update(
        "Task",
        model_task["id"],
        {
            "content": "Model",
            "task_assignees": [{"type": "HumanUser", "id": current_user["id"]}],
        },
    )

    return (model_task, publish_file, version)


# This fixture will launch tk-run-app on first usage
# and will remain valid until the test run ends.
@pytest.fixture(scope="session")
def host_application(context, assetTask):
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
            context["type"],
            "--context-entity-id",
            str(context["id"]),
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


def test_my_tasks(app_dialog, assetTask):
    # My Tasks tab validation
    # Wait for the UI to show up and double click on the task
    app_dialog.root.buttons["Click to go to your work area"].waitExist(timeout=30)
    app_dialog.root.buttons["Click to go to your work area"].mouseClick()
    assert app_dialog.root.tabs[
        "My Tasks"
    ].selected, "My Tasks tab should be selected by default"
    wait = time.time()
    # Click on the home button util the task is showing up. Timeout after 60 seconds.
    while wait + 60 > time.time():
        if app_dialog.root.listitems.exists() is False:
            app_dialog.root.buttons["Click to go to your work area"].mouseClick()
        else:
            break
    app_dialog.root.listitems.mouseDoubleClick()

    # Activity tab validatation
    app_dialog.root.captions["Task Model"].waitExist(timeout=60)
    assert app_dialog.root.tabs[
        "Activity"
    ].selected, "Activity tab should be selected by default"
    assert app_dialog.root.captions[
        "Status: Waiting to Start*Asset AssetAutomation*Assigned to: Azure Pipelines"
    ].exists(), "Not on the right task informations"
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
    app_dialog.root.captions["Publishes for this Task, in creation order."].waitExist(
        timeout=30
    )
    assert app_dialog.root.listitems.exists(), "Missing published file items"
    assert app_dialog.root.checkboxes[
        "Only show latest versions"
    ].exists(), "Missing Only show latest versions checkbox"
    assert app_dialog.root.checkboxes[
        "Only show latest versions"
    ].checked, "Only show latest versions should be checked by default"

    # Tasks tab validation
    app_dialog.root.tabs["Tasks"].mouseClick()
    app_dialog.root.captions["All tasks for this Task."].waitExist(timeout=30)
    assert app_dialog.root.listitems.exists(), "Missing tasks list items"

    # Task Details tab validation
    app_dialog.root.tabs["Details"].mouseClick()
    app_dialog.root.captions["Bid"].waitExist(timeout=30)
    assert app_dialog.root.captions[
        "Assigned To"
    ].exists(), "Asssigned To attribute is missing"
    assert app_dialog.root.captions[
        "Azure Pipelines"
    ].exists(), "Not asssigned to the right user. Should be Azure Pipelines"
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
        str(assetTask[0]["id"])
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
        "Toolkit Panel UI Automation"
    ].exists(), "Wrong project. Should be Toolkit Panel UI Automation"
    assert app_dialog.root.captions[
        "Start Date"
    ].exists(), "Start Date attribute is missing"
    assert app_dialog.root.captions["Status"].exists(), "Status attribute is missing"
    assert app_dialog.root.captions[
        "Waiting to Start"
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


def test_activity_notes_tabs(app_dialog):
    # Activity tab validation
    # Wait for the UI to show up and click on the Activity tab
    app_dialog.root.buttons["Click to go to your work area"].waitExist(timeout=30)
    app_dialog.root.buttons["Click to go to your work area"].mouseClick()

    # Click on the Activity tab
    app_dialog.root.tabs["Activity"].mouseClick()
    assert app_dialog.root.tabs["Activity"].selected, "Activity tab should be selected"

    # Wait until note creation field is showing up.
    wait = time.time()
    while wait + 30 > time.time():
        if app_dialog.root.captions["Loading Shotgun Data..."].exists():
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
        "Task Light was created on Shot shot_001"
    ].exists(), "Task Light creation is missing in the activity stream"
    assert app_dialog.root.captions[
        "Task Comp was created on Shot shot_001"
    ].exists(), "Task Comp creation is missing in the activity stream"
    assert app_dialog.root.captions[
        "Shot shot_001 was created"
    ].exists(), "Shot shot_001 creation is missing in the activity stream"
    assert app_dialog.root.captions[
        "Sequence seq_001 was created"
    ].exists(), "Sequence seq_001 creation is missing in the activity stream"
    assert app_dialog.root.captions[
        "Project Toolkit Panel UI Automation was created"
    ].exists(), (
        "Project Toolkit Panel UI Automation creation is missing in the activity stream"
    )
    assert app_dialog.root.buttons[
        "Click here to see the Activity stream in Shotgun."
    ].exists(), "Hyperlink to see the Activity Stream in Shotgun is missing"

    # Click on the Notes tab
    app_dialog.root.tabs["Notes"].mouseClick()
    assert app_dialog.root.tabs["Notes"].selected, "Notes tab should be selected"

    # Notes tab validation
    app_dialog.root.captions["All notes for this project, in update order."].waitExist(
        timeout=30
    )
    assert app_dialog.root.listitems.exists(), "Should have a note created"

    # Open the note item
    app_dialog.root.listitems.mouseDoubleClick()
    app_dialog.root.captions["Azure's Note on Toolkit Panel UI Automation"].waitExist(
        timeout=30
    )
    assert app_dialog.root.captions[
        "New note created by automation"
    ].exists(), "New Note is missing"
    assert app_dialog.root.captions[
        "Note by Azure Pipelines*Written on*Addressed to: Azure Pipelines*Associated With:*Project Toolkit Panel UI Automation*"
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
    MyOGL = first(app_dialog.root)
    width, height = MyOGL.size
    MyOGL.mouseSlide(width * 0, height * 0)
    MyOGL.mouseDrag(width * 1, height * 1)

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
    assert app_dialog.root.captions[
        "New Reply"
    ].exists(), "Reply Note is missing in the activity stream"

    # Go back to the default work area
    app_dialog.root.buttons["Click to go to your work area"].mouseClick()


def test_versions_tab(app_dialog, assetTask):
    # Versions tab validation
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
        "This version was created by the Panel UI automation"
    ].waitExist(timeout=30)
    assert app_dialog.root.tabs[
        "Activity"
    ].selected, "Activity tab should be selected by default"
    assert app_dialog.root.captions[
        "sven.png"
    ].exists(), "Breadcrumb isn't at the right location. Should be sven.png"
    assert app_dialog.root.captions[
        "Version sven.png was created on Asset AssetAutomation"
    ].exists(), "Version info is missing"
    assert app_dialog.root.captions[
        "Asset AssetAutomation*Status:*Pending Review*Created by Azure Pipelines on*Comments: This version was created by the Panel UI automation*"
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
    app_dialog.root.captions["Azure's Note on sven.png, AssetAutomation"].waitExist(
        timeout=30
    )
    # Go back to the Note page and make sure breadcrumb is good
    app_dialog.root.buttons["Click to go back"].mouseClick()
    app_dialog.root.captions["sven.png"].waitExist(timeout=30)
    # Click back again and make sure the Versions tab is selected
    app_dialog.root.buttons["Click to go back"].mouseClick()
    app_dialog.root.captions["Project Toolkit Panel UI Automation"].waitExist(
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
        "Azure Pipelines"
    ].exists(), "Not asssigned to the right artist. Should be Azure Pipelines"
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
        "This version was created by the Panel UI automation"
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
        str(assetTask[2]["id"])
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
        "Toolkit Panel UI Automation"
    ].exists(), "Wrong project. Should be Toolkit Panel UI Automation"
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


def test_publishes_tab(app_dialog, assetTask):
    # Publishes tab validation
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
    assert app_dialog.root.captions[
        "sven.png"
    ].exists(), "Published file name is missing or wrong"
    assert app_dialog.root.captions[
        "Image, Version 1*For Asset AssetAutomation, Task Model*Created by Azure Pipelines on*Reviewed here: sven.png*Comments:*This file was published by the Panel UI automation*"
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
        "Azure Pipelines"
    ].exists(), "Not asssigned to the right artist. Should be Azure Pipelines"
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
        "This file was published by the Panel UI automation"
    ].exists(), "Missing or wrong description."
    assert app_dialog.root.captions["Id"].exists(), "Id attribute is missing"
    assert app_dialog.root.captions[
        str(assetTask[1]["id"])
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
        "Toolkit Panel UI Automation"
    ].exists(), "Wrong project. Should be Toolkit Panel UI Automation"
    assert app_dialog.root.captions[
        "Published File Name"
    ].exists(), "Published File Name attribute is missing"
    assert app_dialog.root.captions[
        "Published File Type"
    ].exists(), "Published File Type attribute is missing"
    assert app_dialog.root.captions[
        "Image"
    ].exists(), "Wrong published file type, Should be Image."
    assert app_dialog.root.captions["Status"].exists(), "Status attribute is missing"
    assert app_dialog.root.captions[
        "Waiting to Start"
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
    # Search validation
    # Wait for the UI to show up and click on the Versions tab
    app_dialog.root.buttons["Click to go to your work area"].waitExist(timeout=30)
    app_dialog.root.buttons["Click to go to your work area"].mouseClick()

    # Click on the search button
    app_dialog.root.buttons["Search Shotgun"].mouseClick()
    app_dialog.root.textfields.waitExist(timeout=30)

    # Search for sven.png
    app_dialog.root.textfields.typeIn("sven.png")
    assert topwindows.listitems[
        "sven.png"
    ].exists(), "sven.png isn't showing up in the search list."

    # Clear the search text field
    app_dialog.root.textfields.buttons.mouseClick()

    # Do another search for asset
    app_dialog.root.textfields.mouseClick()
    app_dialog.root.textfields.typeIn("asset")
    assert topwindows.listitems[
        "AssetAutomation"
    ].exists(), "AssetAutomation isn't showing up in the search list."
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
    assert topwindows.listitems[
        "No matches found!"
    ].exists(), "No matches found! isn't showing up in the search list."

    # Click on the search Cancel button
    app_dialog.root.buttons["Cancel"].mouseClick()

    # Go back to the default work area
    app_dialog.root.buttons["Click to go to your work area"].mouseClick()
