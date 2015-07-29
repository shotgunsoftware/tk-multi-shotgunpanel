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
Hook that controls how Shotgun data should be displayed in the info panel app. 
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
            
        elif entity_type in ["HumanUser", "ApiUser", "ClientUser"]:
            values["style"] = "round"

        return values
    
    def get_list_item_definition(self, entity_type):
        """
        Controls the rendering of items in the listings.
        """
        
        # define a set of defaults
        values = {
            "top_left": "<big>{code}</big>",
            "top_right": "{updated_at::ago}",
            "body": "<b>By:</b> {created_by}{[<br><b>Description:</b> ]description}"            
            } 
        
        # override 
        if entity_type == "PublishedFile":
            
            values["top_left"] = "<big>{name} v{version_number}</big>"
            values["body"] = """
                {published_file_type} by {created_by}{[ (Task ]sg_task[)]}<br>
                <b>Comments:</b> {description}
                """            
    
        elif entity_type == "TankPublishedFile":
                        
            values["top_left"] = "<big>{name} v{version_number}</big>"
            values["body"] = """
                {tank_type} by {created_by}{[ (Task ]sg_task[)]}<br>
                <b>Comments:</b> {description}
                """            
            
        elif entity_type == "Note":
            
            values["top_left"] = "<big>{created_by}</big>"
            values["body"] = "{content}"     
    
        elif entity_type == "Version":
            
            values["body"] = """
                <b>By:</b> {user} (Task {sg_task})<br>
                <b>Comments:</b> {description}
                """
        
        elif entity_type == "Task":
            
            values["top_left"] = "<big>{content}</big>"
            values["body"] = """
                Assigned to {task_assignees}<br>
                Status: {sg_status_list}
                {[<br>Start: ]start_date}
                {[<br>Due: ]due_date}
                """            

        return values
        
    
    def get_all_fields(self, entity_type):
        """
        Define which fields should be displayed in the info tab
        for a given entity
        """
        
        values = ["id", 
                  "type", 
                  "description",
                  "code", 
                  "created_by", 
                  "created_at", 
                  "updated_by",
                  "project", 
                  "updated_at"]
        
        if entity_type == "Note":
            values += ["attachments", 
                       "user", 
                       "content", 
                       "addressings_cc", 
                       "addressings_to", 
                       "client_note", 
                       "note_links",
                       "sg_status_list",
                       "subject",
                       "tag_list",
                       "tasks",
                       "sg_note_type"]
        
        if entity_type == "Shot":
            values += ["sg_cut_in", "sg_cut_out"]
        
        if entity_type == "Asset":
            values += ["sg_asset_type"]

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
        
        if entity_type in ["Step", "Project", "ApiUser", "TankType", "PublishedFileType"]: 
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
            "title": "{type} {code} ({sg_status_list})",
            "body": "Created by: {created_by}",
            }
        
        
        if entity_type == "HumanUser": 

            values["title"] = "User {name}"
            
            values["body"] = """
                Login: {login}<br>
                Email: {email}<br>
                Department: {department}
                """

        if entity_type == "ApiUser": 
            values["title"] = "Script User {firstname}"
            
            values["body"] = """
                Maintainer: {email}<br>
                Version: {lastname}
                """

        if entity_type == "Group": 
            values["title"] = "Group {code}"
            
            values["body"] = """
                Members: {users}<br>
                Open Notes: {open_notes}
                """
            
        elif entity_type == "Shot":
            
            values["body"] = """
                {sg_sequence::showtype}<br>
                Cut in: {sg_cut_in} Cut out: {sg_cut_out} Cut Duration: {sg_cut_duration}<br>
                """
    
        elif entity_type == "Task":
            
            values["title"] = "Task {content} ({sg_status_list})"
            values["body"] = """
                {entity::showtype}<br>
                Start: {start_date} Due: {due_date}<br>
                Assigned to: {task_assignees}
                """
                
        elif entity_type == "Asset":

            values["body"] = """
                Asset Type: {sg_asset_type}<br>
                Status: {sg_status_list}
                """
                    
        elif entity_type == "Project":
            
            values["title"] = "Project {name} ({sg_status_list})"
            
            values["body"] = """
                Name: {name}<br>
                Start Date: {start_date}<br>
                End Date: {end_date}<br>
                Status: {sg_status}<br>
                """                
            
    
        elif entity_type == "Note":
            
            values["title"] = "{subject}"
            
            values["body"] = """Created by {created_by} on {created_at}<br>
                To: {addressings_to}<br>
                CC: {addressings_cc}<br>
                Links: {note_links::showtype}<br>
                Tasks: {tasks}
                <br><br>
                {content}
                """
    
        elif entity_type == "PublishedFile":
            values["title"] = "Publish {code}"
            
            values["body"] = """
                {entity::showtype}<br>
                Task: {task}<br>
                Reviewed in: {version}<br>
                Version number: {version_number}<br>
                File Type: {published_file_type}<br>
                Published by {created_by} on {created_at}<br>
                <br>
                <i><b>Comments:</i> {description}</i>                
                """
            
        elif entity_type == "TankPublishedFile":
            values["title"] = "Publish {code}"
            
            values["body"] = """
                {entity::showtype}<br>
                Task: {task}<br>
                Version number: {version_number}<br>
                File Type: {tank_type}<br>
                Published by {created_by} on {created_at}<br>
                <br>
                <i><b>Comments:</i> {description}</i>                
                """


        
        elif entity_type == "Version":
            
            values["body"] = """
                {entity::showtype}<br>
                Department: {department}<br>
                Task: {sg_task}<br>
                Playlists: {playlists}<br>
                Created by {created_by} on {created_at}<br>
                <br>
                <i><b>Comments:</i> {description}</i>                
                """
            
    
        return values

        
    
