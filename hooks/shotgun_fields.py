# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Hook that configures which data should be displayed from Shotgun 
"""
import sgtk
import os

HookBaseClass = sgtk.get_hook_baseclass()

class ShotgunConfiguration(HookBaseClass):
    
    
    def get_thumbnail_settings(self, entity_type):
        """
        
        """
        values = {
            "style": "rect",
            "sg_field": "image",
            }
                
        if entity_type == "Note":
            values["style"] = "round"
            values["sg_field"] = "user.HumanUser.image"
            
        elif entity_type == "Task":
            values["style"] = "round"
        
        elif entity_type in ["HumanUser", "ApiUser", "ClientUser"]:
            values["style"] = "round"

    
        return values
    
    def get_list_item_definition(self, entity_type):
        """
        Controls the rendering of items in the listings.
        """
        
        # define a set of defaults
        values = {
            "top_left": "{code}",
            "top_right": "{created_at}",
            "body": "By {created_by} %s<br><i>{description}</i>"            
            } 
        
        # override 
        if entity_type == "PublishedFile":
            
            values["top_left"] = "{name} v{version_number}"
            values["body"] = "By {created_by} %s<br>{published_file_type}<br><i>{description}</i>"            
    
        elif entity_type == "TankPublishedFile":
                        
            values["top_left"] = "{name} v{version_number}"
            values["body"] = "By {created_by} %s<br>{tank_type}<br><i>{description}</i>"            
            
        elif entity_type == "Note":
            
            values["top_left"] = "{created_by}"
            values["body"] = "{content}"            
    
        elif entity_type == "Task":
            
            values["top_left"] = "{content}"
            values["body"] = "Assigned to: {task_assignees}<br>Status: {sg_status_list}<br>Start: {start_date}<br>Due: {due_date}"            

        elif entity_type == "Version":

            values["top_left"] = "{code}"
            values["body"] = "By {created_by} %s<br><i>{description}</i>"
        
        return values
        
    
    def get_all_fields(self, entity_type):
        """
        Define which fields should be displayed in the info tab
        for a given entity
        """
        
        values = ["code", "created_by", "created_at"]
        
        if entity_type == "Shot":
            values += ["sg_cut_in", "sg_cut_out"]
        
        return values
    
    
    def get_tab_visibility(self, entity_type):
        """
        Define which tabs should be visible
        """
        values = {
            "tasks_tab": True,
            "publishes_tab": True,
            "versions_tab": True,
            "notes_tab": True
            }
        
        if entity_type in "HumanUser": 
            values["tasks_tab"] = False
            values["publishes_tab"] = False
            values["versions_tab"] = False
            values["notes_tab"] = False
            
        elif entity_type == "Task":
            values["tasks_tab"] = False 
    
        return values

    def get_main_view_definition(self, entity_type):
        """
        Define which info is shown in the detail section 
        """
        
        values = {
            "play_url": None,
            "title": "{type} {code}",
            "body": "Project: {project}<br>Created by: {created_by}",
            "footer": "{description}"
            }
        
        
        if entity_type in "HumanUser": 

            values["title"] = "User {name}"
            
            values["body"] = """
                Name: {name}<br>
                Email: {email}<br>
                Department: {department}
                """

            values["footer"] = ""         
            

        elif entity_type == "Shot":
            
            values["body"] = """
                Project: {project}<br>
                Sequence: {sg_sequence}<br>
                Status: {sg_status_list}<br>
                Cut in: {sg_cut_in}<br>
                Cut out: {sg_cut_out}<br>
                Duration: {sg_cut_duration}<br>
                """
    
        elif entity_type == "Task":
            
            values["title"] = "Task {content}"
            
            values["body"] = """
                Project: {project}<br>
                Status: {sg_status_list}<br>
                Start Date: {start_date}<br>
                Due Date: {due_date}<br>
                Associated with: {entity}<br>
                Pipeline Step: {step}<br>
                Assigned to: {task_assignees}
                """
                
            
            
        elif entity_type == "Asset":

            values["body"] = """
                Project: {project}<br>
                Asset Type: {sg_asset_type}<br>
                Status: {sg_status_list}
                """
            
        
        elif entity_type == "Project":
            
            values["title"] = "Project {name}"
            
            values["body"] = """
                Name: {name}<br>
                Start Date: {start_date}<br>
                End Date: {end_date}<br>
                Status: {sg_status}<br>
                """                
            
    
        elif entity_type == "Note":
            
            values["title"] = "{subject}"
            
            values["footer"] = """
                Created by {created_by} {created_at}<br>
                <br>
                {content}
                """

            values["body"] = """
                Project: {project}<br>
                Status: {sg_status_list}<br>
                To: {addressings_to}<br>
                CC: {addressings_cc}<br>
                Linked to: {note_links}<br>
                Tasks: {tasks}
                """                
            
    
        elif entity_type == "PublishedFile":
            values["title"] = "Publish {code}"
            
            values["footer"] = """
                Published by {created_by} {created_at}<br>
                <br>
                <i><b>Comments:</i>{description}</i>
                """
                
            values["body"] = """
                Project: {project}<br>
                Associated with: {entity}<br>
                Task: {task}<br>
                Reviewed in: {version}<br>
                Version number: {version_number}<br>
                File Type: {published_file_type}<br>
                """
            
        elif entity_type == "TankPublishedFile":
            values["title"] = "Publish {code}"
            
            values["footer"] = """
                Published by {created_by} {created_at}<br>
                <br>
                <i><b>Comments:</i>{description}</i>
                """

            values["body"] = """
                Project: {project}<br>
                Associated with: {entity}<br>
                Task: {task}<br>
                Version number: {version_number}<br>
                File Type: {tank_type}<br>
                """

        
        elif entity_type == "Version":
            
            values["play_url"] = "{sg_url}/page/screening_room?entity_type={type}&entity_id={id}"
            
            values["footer"] = """
                Created by {created_by} {created_at}<br>
                <br>
                <i><b>Comments:</i>{description}</i>
                """

            values["body"] = """
                Project: {project}<br>
                Status: {sg_status_list}<br>
                Frame Range: {frame_range}<br>
                Department: {department}<br>
                Associated with: {entity}<br>
                Task: {task}<br>
                Playlists: {playlists}<br>
                """
            
    
        return values

        
    
