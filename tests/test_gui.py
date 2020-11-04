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
def context():
    # Tasks in Toolkit Shotgun panel UI Automation project which we're going to use
    # in different test cases.
    # Get credentials from TK_TOOLCHAIN
    sg = get_toolkit_user().create_sg_connection()

    # Create or update the integration_tests local storage with the current test run
    storage_name = "Panel UI Tests"
    local_storage = sg.find_one(
        "LocalStorage", [["code", "is", storage_name]], ["code"]
    )
    if local_storage is None:
        local_storage = sg.create("LocalStorage", {"code": storage_name})
    # Always update local storage path
    local_storage["path"] = os.path.expandvars("${SHOTGUN_CURRENT_REPO_ROOT}")
    sg.update(
        "LocalStorage", local_storage["id"], {"windows_path": local_storage["path"]}
    )

    # Make sure there is not already an automation project created
    filters = [["name", "is", "Toolkit Panel UI Automation"]]
    existed_project = sg.find_one("Project", filters)
    if existed_project is not None:
        sg.delete(existed_project["type"], existed_project["id"])

    # Create a new project with the Film VFX Template
    project_data = {
        "sg_description": "Project Created by Automation",
        "name": "Toolkit Panel UI Automation",
    }
    new_project = sg.create("Project", project_data)

    # Create a Sequence to be used by the Shot creation
    sequence_data = {
        "project": {"type": new_project["type"], "id": new_project["id"]},
        "code": "seq_001",
        "sg_status_list": "ip",
    }
    new_sequence = sg.create("Sequence", sequence_data)

    # Validate if Automation shot task template exists
    shot_template_filters = [["code", "is", "Automation Shot Task Template"]]
    existed_shot_template = sg.find_one("TaskTemplate", shot_template_filters)
    if existed_shot_template is not None:
        sg.delete(existed_shot_template["type"], existed_shot_template["id"])
    # Create a shot task templates
    shot_template_data = {
        "code": "Automation Shot Task Template",
        "description": "This shot task template was created by the Panel UI automation",
        "entity_type": "Shot",
    }
    shot_task_template = sg.create("TaskTemplate", shot_template_data)
    # Get the Comp Pipeline step ID
    comp_pipeline_step_filter = [["code", "is", "Comp"]]
    comp_pipeline_step = sg.find_one("Step", comp_pipeline_step_filter)
    # Create Comp task
    comp_task_data = {
        "content": "Comp",
        "step": comp_pipeline_step,
        "task_template": shot_task_template,
    }
    sg.create("Task", comp_task_data)
    # Get the Light Pipeline step ID
    light_pipeline_step_filter = [["code", "is", "Light"]]
    light_pipeline_step = sg.find_one("Step", light_pipeline_step_filter)
    # Create Light task
    light_task_data = {
        "content": "Light",
        "step": light_pipeline_step,
        "task_template": shot_task_template,
    }
    sg.create("Task", light_task_data)
    # Validate if Automation asset task template exists
    asset_template_filters = [["code", "is", "Automation Asset Task Template"]]
    existed_asset_template = sg.find_one("TaskTemplate", asset_template_filters)
    if existed_asset_template is not None:
        sg.delete(existed_asset_template["type"], existed_asset_template["id"])
    # Create an asset task templates
    asset_template_data = {
        "code": "Automation Asset Task Template",
        "description": "This asset task template was created by the Panel UI automation",
        "entity_type": "Asset",
    }
    asset_task_template = sg.create("TaskTemplate", asset_template_data)
    # Get the Model Pipeline step ID
    model_pipeline_step_filter = [["code", "is", "Model"]]
    model_pipeline_step = sg.find_one("Step", model_pipeline_step_filter)
    # Create Model task
    model_task_data = {
        "content": "Model",
        "step": model_pipeline_step,
        "task_template": asset_task_template,
    }
    sg.create("Task", model_task_data)
    # Get the Rig Pipeline step ID
    rig_pipeline_step_filter = [["code", "is", "Rig"]]
    rig_pipeline_step = sg.find_one("Step", rig_pipeline_step_filter)
    # Create Rig task
    rig_task_data = {
        "content": "Rig",
        "step": rig_pipeline_step,
        "task_template": asset_task_template,
    }
    sg.create("Task", rig_task_data)

    # Create a new shot
    shot_data = {
        "project": new_project,
        "sg_sequence": new_sequence,
        "code": "shot_001",
        "description": "This shot was created by the Panel UI automation",
        "sg_status_list": "ip",
        "task_template": shot_task_template,
    }
    sg.create("Shot", shot_data)

    # Create a new asset
    asset_data = {
        "project": new_project,
        "code": "AssetAutomation",
        "description": "This asset was created by the Panel UI automation",
        "sg_status_list": "ip",
        "sg_asset_type": "Character",
        "task_template": asset_task_template,
    }
    asset = sg.create("Asset", asset_data)

    # Get the publish_file_type id to be passed in the publish creation
    published_file_type_filters = [["code", "is", "Image"]]
    published_file_type = sg.find_one("PublishedFileType", published_file_type_filters)

    # File to publish
    file_to_publish = os.path.join(
        os.path.expandvars("${TK_TEST_FIXTURES}"), "files", "images", "sven.png"
    )

    # Create a version an upload to it
    version_data = {
        "project": new_project,
        "code": "sven.png",
        "description": "This version was created by the Panel UI automation",
        "entity": asset,
    }
    version = sg.create("Version", version_data)
    # Upload a version to the published file
    sg.upload("Version", version["id"], file_to_publish, "sg_uploaded_movie")
    # Create a published file
    # Find the model task to publish to
    filters = [["project", "is", new_project], ["entity.Asset.code", "is", asset["code"]], ["step.Step.code", "is", "model"]]
    fields = ["sg_status_list"]
    model_task = sg.find_one("Task", filters, fields)
    publish_data = {
        "project": new_project,
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
    sg.create("PublishedFile", publish_data)

    # Assign a task to the current user
    # Find current user
    user = get_toolkit_user()
    current_user = sg.find_one("HumanUser", [["login", "is", str(user)]], ["name"])
    # Assign current user to the task model
    sg.update("Task", model_task["id"], {"content": "Model", "task_assignees": [{"type": "HumanUser", "id": current_user["id"]}]})

    return new_project


# This fixture will launch tk-run-app on first usage
# and will remain valid until the test run ends.
@pytest.fixture(scope="session")
def host_application(context):
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


def test_ui_navigation(app_dialog):
    # My Tasks tab validation
    app_dialog.root.captions["Project Toolkit Panel UI Automation"].get().waitExist(timeout=30)
    assert app_dialog.root.tabs["My Tasks"].selected, "My Tasks tab should be selected by default"
    assert app_dialog.root.listitems.exists() == True, "Should be a model task in My Tasks"
    # import pdb;pdb.set_trace()

    # Publishes tab validation
    app_dialog.root.tabs["Publishes"].mouseClick()
    assert app_dialog.root.listitems.exists(), "Missing published file items"
    assert app_dialog.root.checkboxes["Only show latest versions"].exists(), "Missing Only show latest versions checkbox"
    assert app_dialog.root.checkboxes["Only show latest versions"].checked, "Only show latest versions should be checked by default"
