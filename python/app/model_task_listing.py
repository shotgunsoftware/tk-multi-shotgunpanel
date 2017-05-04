# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform.qt import QtCore, QtGui
import sgtk
from . import utils

from .model_entity_listing import SgEntityListingModel

# import the shotgun_model module from the shotgun utils framework
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
ShotgunModel = shotgun_model.ShotgunModel


class SgTaskListingModel(SgEntityListingModel):
    """
    Model to list tasks. This subclasses the generic entity listing model 
    in order to be able to fetch user thumbnails for tasks. 
    
    Since tasks can be assigned to multiple people, there isn't a way to get
    the thumbnail for an assignee at the same time as getting the list of tasks.
    Therefore, when the task list has arrived, a signal is set to a second
    model which then fetches the thumbnails for all users assigned to tasks.
    
    :signal request_user_thumbnails(list): Emitted when this class is signalling
        that it needs thumbnails for users. A list of user ids for which 
        thumbnails are needed are passed as arguments with the signal. 
    """
    
    request_user_thumbnails = QtCore.Signal(list)

    def __init__(self, entity_type, parent, bg_task_manager):
        """
        Constructor.
        
        :param entity_type: The entity type that should be loaded into this model.
                            Needs to be a PublishedFile or TankPublishedFile.
        :param parent: QT parent object
        """
        # init base class
        SgEntityListingModel.__init__(self, entity_type, parent, bg_task_manager)
        self.data_refreshed.connect(self._on_data_refreshed)
        
        # have a model to pull down user's thumbnails for task assingments
        self._task_assignee_model = TaskAssigneeModel(self, bg_task_manager)
        self._task_assignee_model.thumbnail_updated.connect(self._on_user_thumb)
        
    def destroy(self):
        """
        Tear down method
        """
        # make sure we gracefully stop the thumbnail model
        self._task_assignee_model.destroy()
        self._task_assignee_model = None
        
        # call base class
        SgEntityListingModel.destroy(self)
        
    ############################################################################################
    # public interface
  
    def _on_data_refreshed(self):
        """
        helper method. dispatches the after-refresh signal
        so that a data_updated signal is consistently sent
        out both after the data has been updated and after a cache has been read in
        """
        if self._sg_location.entity_type not in ["HumanUser", "Project"]:
            # show square thumbs for users and project (my tasks)
            # for other types, fetch user thumbnails
            rows = self.rowCount()
            
            # get the task assignees
            assignees = []
            for x in range(rows):
                data = self.item(x).get_sg_data()
                assignees.extend(data["task_assignees"])
            user_ids = [x["id"] for x in assignees] 
            
            self.request_user_thumbnails.emit(user_ids)
  
    def _on_user_thumb(self, sg_data, image):
        """
        When a user thumb arrives from the 
        user thumbnail retriever
        """
        rows = self.rowCount()
        
        for x in range(rows):
            item = self.item(x)
            data = item.get_sg_data()
            user_ids = [x["id"] for x in data["task_assignees"]]
            if sg_data["id"] in user_ids:
                # this thumbnail should be assigned
                icon = self._sg_formatter.create_thumbnail(image, sg_data)
                item.setIcon(QtGui.QIcon(icon))
  
    def _populate_default_thumbnail(self, item):
        """
        Called whenever an item needs to get a default thumbnail attached to a node.
        When thumbnails are loaded, this will be called first, when an object is
        either created from scratch or when it has been loaded from a cache, then later
        on a call to _populate_thumbnail will follow where the subclassing implementation
        can populate the real image.
        """
        if self._sg_location.entity_type in ["HumanUser", "Project"]:
            # TODO - refactor this into a nicer piece of code
            # show square thumbs for users and project (my tasks)
            item.setIcon(self._sg_formatter._rect_default_icon) 
        else:
            item.setIcon(self._sg_formatter._round_default_icon)
            
 
    def _populate_thumbnail_image(self, item, field, image, path):
        """
        Called whenever a thumbnail for an item has arrived on disk. In the case of
        an already cached thumbnail, this may be called very soon after data has been
        loaded, in cases when the thumbs are downloaded from Shotgun, it may happen later.
 
        This method will be called only if the model has been instantiated with the
        download_thumbs flag set to be true. It will be called for items which are
        associated with shotgun entities (in a tree data layout, this is typically
        leaf nodes).
 
        This method makes it possible to control how the thumbnail is applied and associated
        with the item. The default implementation will simply set the thumbnail to be icon
        of the item, but this can be altered by subclassing this method.
 
        Any thumbnails requested via the _request_thumbnail_download() method will also
        resurface via this callback method.
 
        :param item: QStandardItem which is associated with the given thumbnail
        :param field: The Shotgun field which the thumbnail is associated with.
        :param path: A path on disk to the thumbnail. This is a file in jpeg format.
        """        
        if field not in self._sg_formatter.thumbnail_fields: 
            # there may be other thumbnails being loaded in as part of the data flow
            # (in particular, created_by.HumanUser.image) - these ones we just want to 
            # ignore and not display.
            return
         
        if self._sg_location.entity_type in ["HumanUser", "Project"]:
            # show square thumbs for users and project (my tasks)
            sg_data = item.get_sg_data()
            icon = self._sg_formatter.create_thumbnail(image, sg_data)
            item.setIcon(QtGui.QIcon(icon))


class TaskAssigneeModel(ShotgunModel):
    """
    Helper class used by SgTaskListingModel. Because tasks in Shotgun 
    can be assigned to more than one person, it is not straight forward 
    to determine a assignee based thumbnail for tasks. This model is used
    as a helper to retrieve user thumbnails for task assignees so that the
    SgTaskListingModel can present them as belonging to the tasks.
    
    This model works as a very simple thumbnail creation facility:
    it's connected to a task listing model's request_user_thumbnails signal
    and whenever this fires, it retrieves those thumbnails from shotgun
    and emits a thumbnail_updated signal for each one of them.
    
    :signal thumbnail_updated(dict, QImage): Emitted whenever a thumbnail
        is available. the dictionary contains shotgun data about the user
        and the thumbnail and the QImage holds the actual thumbnail object.
    """
    
    thumbnail_updated = QtCore.Signal(dict, QtGui.QImage)

    def __init__(self, parent, bg_task_manager):
        """
        Constructor
        
        :param parent: QT parent object
        """
        # init base class
        ShotgunModel.__init__(self, 
                              parent, 
                              bg_load_thumbs=True, 
                              bg_task_manager=bg_task_manager)
        self._app = sgtk.platform.current_bundle()
        self._task_model = parent
        
        # connect it with the request_user_thumbnails signal on the 
        # task model, so that whenever that model requests thumbnails, this
        # model starts loading that data.
        self._task_model.request_user_thumbnails.connect(self._load_user_thumbnails)

    def _load_user_thumbnails(self, user_ids):
        """
        Load thumbnails for all the given user ids
        
        :param user_ids: List of user ids
        """        
        if len(user_ids) > 0:
            fields = ["image"]
            self._load_data("HumanUser", [["id", "in", user_ids]], ["id"], fields)    
            self._refresh_data()

    def _populate_thumbnail_image(self, item, field, image, path):
        """
        Called whenever a thumbnail for an item has arrived on disk. In the case of
        an already cached thumbnail, this may be called very soon after data has been
        loaded, in cases when the thumbs are downloaded from Shotgun, it may happen later.

        This method will be called only if the model has been instantiated with the
        download_thumbs flag set to be true. It will be called for items which are
        associated with shotgun entities (in a tree data layout, this is typically
        leaf nodes).

        This method makes it possible to control how the thumbnail is applied and associated
        with the item. The default implementation will simply set the thumbnail to be icon
        of the item, but this can be altered by subclassing this method.

        Any thumbnails requested via the _request_thumbnail_download() method will also
        resurface via this callback method.

        :param item: QStandardItem which is associated with the given thumbnail
        :param field: The Shotgun field which the thumbnail is associated with.
        :param image: Image object representing the thumbnail
        :param path: A path on disk to the thumbnail. This is a file in jpeg format.
        """        
        self._current_pixmap = utils.create_round_thumbnail(image)
        sg_data = item.get_sg_data()
        self.thumbnail_updated.emit(sg_data, image)
