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
                {published_file_type} by {created_by}<br>
                <b>Comments:</b> {description}
                """            
    
        elif entity_type == "TankPublishedFile":
                        
            values["top_left"] = "<big>{name} v{version_number}</big>"
            values["body"] = """
                {tank_type} by {created_by}<br>
                <b>Comments:</b> {description}
                """            
            
        elif entity_type == "Note":
            
            values["top_left"] = "<big>{created_by}</big>"
            values["body"] = "{content}"     
    
        elif entity_type == "Version":
            
            values["body"] = """
                <b>By:</b> {user}<br>
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
        
        if entity_type in ["Step", "ApiUser", "TankType", "PublishedFileType"]: 
            values["tasks_tab"] = False
            values["publishes_tab"] = False
            values["versions_tab"] = False
            values["notes_tab"] = False

        elif entity_type == "Group":
            values["tasks_tab"] = False
            values["publishes_tab"] = False
            values["versions_tab"] = False
            
        elif entity_type == "Project":
            values["tasks_tab"] = False
            
        elif entity_type == "Task":
            values["tasks_tab"] = False 
    
        return values

    def get_main_view_definition(self, entity_type):
        """
        Define which info is shown in the detail section 
        """
        
        values = {
            "title": "{type} {code}",
            "body": "Created by: {created_by}",
            }
        
        
        if entity_type == "HumanUser": 
            values["title"] = "{name}"
            
            values["body"] = """
                Login: {login}<br>
                Email: {email}<br>
                Department: {department}
                """

        if entity_type == "ApiUser": 
            values["title"] = "Script {firstname}"
            
            values["body"] = """
                Maintainer: {email}<br>
                Version: {lastname}
                """

        if entity_type == "Group": 
            values["title"] = "Group {code}"
            
            values["body"] = """
                Members: {users}
                """
            
        elif entity_type == "Shot":
            values["body"] = """
                Sequence: {sg_sequence}<br>
                Status: {sg_status_list}<br>
                {[Cut In: ]sg_cut_in[  ]}{[Cut Out:]sg_cut_out[  ]}{[Cut Duration: ]sg_cut_duration}<br>
                """
    
        elif entity_type == "Task":
            values["title"] = "Task {content}"
            values["body"] = """
            
                <big>Status: {sg_status_list}</big><br><br>
            
                {[For ]entity::showtype}<br>
                {[Start: ]start_date}{[ Due: ]due_date}<br><br>
                
                Assigned to: {task_assignees}
                """
                
        elif entity_type == "Asset":
            values["body"] = """
                Asset Type: {sg_asset_type}<br>
                Status: {sg_status_list}
                """
                    
        elif entity_type == "Project":
            values["title"] = "Project {name}"
            
            values["body"] = """
                Status: {sg_status}<br>
                {[Start Date: ]start_date[<br>]}
                {[End Date: ]end_date[<br>]}
                """
            
    
        elif entity_type == "Note":
            values["title"] = "{subject}"
            
            values["body"] = """
                Note by {created_by} {[(Task ]tasks[)]}<br>
                Written on {created_at}<br>
                {[Addressed to:]addressings_to}{[, CC: ]addressings_cc}<br>
                <br>
                Associated With:<br>{note_links::showtype}
                """
    
        elif entity_type == "PublishedFile":
            values["title"] = "{code}"
            
            values["body"] = """
                <big>{published_file_type}, Version {version_number}</big><br>
                For {entity::showtype}{[, Task ]task} <br>
                Created by {created_by} on {created_at}<br>
            
                {[<br>Reviewed here: ]version[<br>]}

                <br>
                <b>Comments:</b><br>
                {description}                
                """
            
        elif entity_type == "TankPublishedFile":
            values["title"] = "{code}"
            
            values["body"] = """
                <big>{tank_type}, Version {version_number}</big><br>
                For {entity::showtype}{[, Task ]task} <br>
                Created by {created_by} on {created_at}<br>
            
                <br>
                <b>Comments:</b><br>
                {description}
                """

        elif entity_type == "Version":
            values["title"] = "{code}"
            
            values["body"] = """
                <b>Version for Review</b><br>
                For {entity::showtype}{[, Task ]sg_task} <br>
                Created by {created_by} on {created_at}<br>
                
                {[<br>In Playlists: ]playlists[<br>]}
                
                <br>
                <b>Comments:</b><br>{description}                
                """
            
    
        return values

        
    
