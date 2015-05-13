# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk.platform.qt import QtCore, QtGui


def create_round_thumbnail(path):
    """
    Create a circle thumbnail 200px wide
    """
    CANVAS_SIZE = 200

    # get the 512 base image
    base_image = QtGui.QPixmap(CANVAS_SIZE, CANVAS_SIZE)
    base_image.fill(QtCore.Qt.transparent)
    
    # now attempt to load the image
    # pixmap will be a null pixmap if load fails    
    thumb = QtGui.QPixmap(path)
    
    if not thumb.isNull():
            
        # scale it down to fit inside a frame of maximum 512x512
        thumb_scaled = thumb.scaled(CANVAS_SIZE, 
                                    CANVAS_SIZE, 
                                    QtCore.Qt.KeepAspectRatio, 
                                    QtCore.Qt.SmoothTransformation)  

        # now composite the thumbnail on top of the base image
        # bottom align it to make it look nice
        thumb_img = thumb_scaled.toImage()
        brush = QtGui.QBrush(thumb_img)
        painter = QtGui.QPainter(base_image)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(brush)
        painter.drawEllipse(0, 0, thumb_scaled.width(), thumb_scaled.height())             
        painter.end()
    
    return base_image

    
        

def create_overlayed_publish_thumbnail(path):
    """
    Given a path to a shotgun thumbnail, create a publish icon
    with the thumbnail composited onto a centered otherwise empty canvas. 
    This will return a 512x400 pixmap object.
    """

    CANVAS_WIDTH = 512
    CANVAS_HEIGHT = 400
    CORNER_RADIUS = 10

    # get the 512 base image
    base_image = QtGui.QPixmap(CANVAS_WIDTH, CANVAS_HEIGHT)
    base_image.fill(QtCore.Qt.transparent)
    
    # now attempt to load the image
    # pixmap will be a null pixmap if load fails    
    thumb = QtGui.QPixmap(path)
    
    if not thumb.isNull():
            
        # scale it down to fit inside a frame of maximum 512x512
        thumb_scaled = thumb.scaled(CANVAS_WIDTH, 
                                    CANVAS_HEIGHT, 
                                    QtCore.Qt.KeepAspectRatio, 
                                    QtCore.Qt.SmoothTransformation)  

        # now composite the thumbnail on top of the base image
        # bottom align it to make it look nice
        thumb_img = thumb_scaled.toImage()
        brush = QtGui.QBrush(thumb_img)
        
        painter = QtGui.QPainter(base_image)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(brush)
        
        # figure out the offset height wise in order to center the thumb
        height_difference = CANVAS_HEIGHT - thumb_scaled.height()
        width_difference = CANVAS_WIDTH - thumb_scaled.width()
        
        # center it with wise
        inlay_offset_w = (width_difference/2)+(CORNER_RADIUS/2)
        # bottom height wise
        #inlay_offset_h = height_difference+CORNER_RADIUS
        inlay_offset_h = (height_difference/2)+(CORNER_RADIUS/2)
        
        # note how we have to compensate for the corner radius
        painter.translate(inlay_offset_w, inlay_offset_h)
        painter.drawRoundedRect(0,  
                                0, 
                                thumb_scaled.width()-CORNER_RADIUS, 
                                thumb_scaled.height()-CORNER_RADIUS, 
                                CORNER_RADIUS, 
                                CORNER_RADIUS)
        
        painter.end()
    
    return base_image
    
