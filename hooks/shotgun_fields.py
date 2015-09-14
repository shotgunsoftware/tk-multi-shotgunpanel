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
        
    def get_list_item_definition(self, entity_type):
        """
        Controls the rendering of items in the listings.
        """
        
        # define a set of defaults
        values = {
            "top_left": "<big>{code}</big>",
            "top_right": "{updated_at}",
            "body": "<b>By:</b> {created_by}{[<br><b>Description:</b> ]description}"            
            } 
        
        # override 
        if entity_type == "PublishedFile":
            
            values["top_left"] = "<big>{name} v{version_number}</big>"
            values["top_right"] = "{created_at}"
            values["body"] = """
                {published_file_type} by {created_by}<br>
                <b>Comments:</b> {description}
                """            
    
        elif entity_type == "Note":
            
            values["top_left"] = "<big>{created_by}</big>"
            values["body"] = "{content}"     
    
        elif entity_type == "Version":
            
            values["body"] = """
                <b>By:</b> {user|created_by}<br>
                <b>Comments:</b> {description}
                """
        
        elif entity_type == "Task":
            
            values["top_left"] = "<big>{content}</big>"
            values["top_right"] = "{sg_status_list}"
            values["body"] = """
                {[Assigned to ]task_assignees[<br>]} 
                {[<br>Start: ]start_date}
                {[<br>Due: ]due_date}
                """            

        return values
        
    
    def get_all_fields(self, entity_type):
        """
        Define which fields should be displayed in the info tab
        for a given entity
        """
        
        # supported by all normal fields
        base_values = ["id", 
                       "type", 
                       "tag_list",
                       "created_by", 
                       "created_at", 
                       "updated_by",
                       "updated_at"]
        
        # supported by most entities
        std_values = base_values + ["code", 
                                    "project", 
                                    "tags",
                                    "sg_status_list", 
                                    "description"]
        
        if entity_type == "Shot":
            values = std_values
            values += ["assets",
                       "sg_cut_duration",
                       "sg_cut_in", 
                       "sg_cut_out",
                       "sg_head_in",
                       "sg_tail_out",
                       "sg_sequence",
                       "sg_working_duration"]
        
        elif entity_type == "Sequence":
            values = std_values + ["shots", "assets"] 

        elif entity_type == "Project":
            values = base_values + ["sg_description", 
                                    "archived",
                                    "code",
                                    "due",
                                    "name",
                                    "sg_start",
                                    "sg_status",
                                    "tank_name",
                                    "sg_type",
                                    "users"] 

        elif entity_type == "Asset":
            values = std_values + ["sg_asset_type", 
                                   "shots", 
                                   "parents", 
                                   "sequences", 
                                   "assets"] 
 
        elif entity_type == "ClientUser":
            values = base_values + ["email", 
                                   "firstname", 
                                   "lastname", 
                                   "name", 
                                   "sg_status_list"] 

        elif entity_type == "HumanUser":
            values = base_values + ["department",
                                    "groups",
                                    "login",
                                    "email", 
                                    "firstname", 
                                    "lastname", 
                                    "name", 
                                    "sg_status_list"] 

        elif entity_type == "ScriptUser":
            values = base_values + ["description",
                                    "email", 
                                    "firstname", 
                                    "lastname"] 

        elif entity_type == "Group":
            values = base_values + ["users"] 

        elif entity_type == "Version":
            values = std_values + ["user",
                                   "sg_department", 
                                   "sg_first_frame", 
                                   "frame_count",
                                   "frame_range",
                                   "sg_last_frame",
                                   "entity",
                                   "sg_path_to_frames",
                                   "sg_path_to_movie",
                                   "playlists",
                                   "published_files",
                                   "sg_task",
                                   "sg_version_type"]
            
        elif entity_type == "PublishedFile":
            values = std_values + [ "entity", 
                                    "name",
                                    "published_file_type",
                                    "task",
                                    "version",
                                    "version_number"] 

        elif entity_type == "Task":
            values = base_values + [ "task_assignees", 
                                     "est_in_mins", 
                                     "addressings_cc",
                                     "due_date",
                                     "duration",
                                     "entity",
                                     "step",
                                     "start_date",
                                     "sg_status_list",
                                     "project",
                                     "content"] 

        else:
            values = std_values

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

        if entity_type == "ClientUser": 
            values["title"] = "{name}"
            
            values["body"] = """<br>
                <b>Shotgun Client User</b><br><br>
                Email: {email}
                """

        if entity_type == "ApiUser": 
            values["title"] = "{firstname}"
            
            values["body"] = """
                <b>Shotgun Api Script</b><br><br>
                Script Version: {lastname}<br>
                Maintainer: {email}<br>
                Description: {description}
                """

        if entity_type == "Group": 
            values["title"] = "{code}"
            
            values["body"] = """
                <b>Group of users</b><br><br>
                Members: {users}
                """
            
        elif entity_type == "Shot":
            values["body"] = """
                Sequence: {sg_sequence}<br>
                Status: {sg_status_list}<br><br>
                {[Cut In: ]sg_cut_in[  ]}{[Cut Out:]sg_cut_out[  ]}{[Duration: ]sg_cut_duration}<br>
                """
    
        elif entity_type == "Task":
            values["title"] = "Task {content}"
            values["body"] = """
            
                <big>Status: {sg_status_list}</big><br><br>
            
                {[For ]entity::showtype[<br>]}
                {[Assigned to: ]task_assignees[<br>]}
                {[Start: ]start_date}{[ Due: ]due_date}
                """
                
        elif entity_type == "Asset":
            values["body"] = """
                Asset Type: {sg_asset_type}<br>
                Status: {sg_status_list}<br>
                Description: {description}
                """
                    
        elif entity_type == "Project":
            values["title"] = "Project {name}"
            
            values["body"] = """
                <b>Status: {sg_status}<br>
                {[Start Date: ]start_date[<br>]}
                {[End Date: ]end_date[<br>]}
                Description: {sg_description}
                """
                
        elif entity_type == "Note":
            values["title"] = "{subject}"
            
            values["body"] = """
                Note by {created_by} {[(Task ]tasks[)]}<br>
                Written on {created_at}<br>
                {[Addressed to: ]addressings_to}{[, CC: ]addressings_cc}<br>
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
            
        elif entity_type == "Version":
            values["title"] = "{code}"
            
            values["body"] = """
                <b>Version for Review</b><br>
                For {entity::showtype}{[, Task ]sg_task} <br>
                Created by {user|created_by} on {created_at}<br>
                
                {[<br>In Playlists: ]playlists[<br>]}
                
                <br>
                <b>Comments:</b><br>{description}                
                """
            
    
        return values

        
    
