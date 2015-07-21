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
from datetime import datetime , timedelta

def create_round_thumbnail(image):
    """
    Create a circle thumbnail 200px wide
    """
    CANVAS_SIZE = 200

    # get the 512 base image
    base_image = QtGui.QPixmap(CANVAS_SIZE, CANVAS_SIZE)
    base_image.fill(QtCore.Qt.transparent)
    
    # now attempt to load the image
    # pixmap will be a null pixmap if load fails    
    thumb = QtGui.QPixmap.fromImage(image)
    
    if not thumb.isNull():
            
        # scale it down to fit inside a frame of maximum 512x512
        thumb_scaled = thumb.scaled(CANVAS_SIZE, 
                                    CANVAS_SIZE, 
                                    QtCore.Qt.KeepAspectRatioByExpanding, 
                                    QtCore.Qt.SmoothTransformation)  

        # now composite the thumbnail on top of the base image
        # bottom align it to make it look nice
        thumb_img = thumb_scaled.toImage()
        brush = QtGui.QBrush(thumb_img)
        painter = QtGui.QPainter(base_image)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(brush)
        painter.drawEllipse(0, 0, CANVAS_SIZE, CANVAS_SIZE)             
        painter.end()
    
    return base_image

def create_circular_512x400_thumbnail(image, accent=False):
    """
    Given a qimage shotgun thumbnail, create a publish icon
    with the thumbnail composited onto a centered otherwise empty canvas. 
    This will return a 512x400 pixmap object.
    
    :param image: QImage source image
    :param accent: Should the image be accentuated. This can be used to indicate an unread state.
    """

    CANVAS_WIDTH = 512
    CANVAS_HEIGHT = 400
    
    CIRCLE_SIZE = 395

    # get the 512 base image
    base_image = QtGui.QPixmap(CANVAS_WIDTH, CANVAS_HEIGHT)
    base_image.fill(QtCore.Qt.transparent)
    
    # now attempt to load the image
    # pixmap will be a null pixmap if load fails    
    thumb = QtGui.QPixmap.fromImage(image)
    
    if not thumb.isNull():
            
        # scale it to fill a 400x400 square
        thumb_scaled = thumb.scaled(CIRCLE_SIZE, 
                                    CIRCLE_SIZE, 
                                    QtCore.Qt.KeepAspectRatioByExpanding, 
                                    QtCore.Qt.SmoothTransformation)  

        # now composite the thumbnail on top of the base image
        # bottom align it to make it look nice
        thumb_img = thumb_scaled.toImage()
        brush = QtGui.QBrush(thumb_img)
        
        painter = QtGui.QPainter(base_image)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(brush)
        
        if accent:
            pen = QtGui.QPen(QtGui.QColor("#2C93E2"))
            pen.setWidth(18)
            painter.setPen(pen)
        
        # figure out the offset height wise in order to center the thumb        
        
        # center it
        inlay_offset_h = (CANVAS_HEIGHT - CIRCLE_SIZE)/2
        inlay_offset_w = (CANVAS_WIDTH - CIRCLE_SIZE)/2
        
        # note how we have to compensate for the corner radius
        painter.translate(inlay_offset_w, inlay_offset_h)
        painter.drawEllipse(0, 0, CIRCLE_SIZE, CIRCLE_SIZE) 
        
        painter.end()
    
    return base_image
    
    
        

def create_rectangular_512x400_thumbnail(image):
    """
    Given a qimage shotgun thumbnail, create a publish icon
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
    thumb = QtGui.QPixmap.fromImage(image)
    
    if not thumb.isNull():
            
        # scale it down to fit inside a frame of maximum 512x512
        thumb_scaled = thumb.scaled(CANVAS_WIDTH, 
                                    CANVAS_HEIGHT, 
                                    QtCore.Qt.KeepAspectRatioByExpanding, 
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
    



def create_human_readable_timestamp(datetime_obj):
    """
    
    Based on http://code.activestate.com/recipes/578113-human-readable-format-for-a-given-time-delta/
    
    Returns (human_readable_timestamp_str, full_timestamp_str)
    """
    
    from_date = datetime.now()

    # standard format 
    std_format = datetime_obj.strftime('%Y-%m-%d %H:%M')

    std_date = datetime_obj.strftime('%Y-%m-%d')

    if datetime_obj > datetime.now():
        # future times are reported precisely
        return (std_date, std_format)
    
    # get the delta and components
    delta = datetime.now() - datetime_obj

    # the timedelta structure does not have all units; bigger units are converted
    # into given smaller ones (hours -> seconds, minutes -> seconds, weeks > days, ...)
    # but we need all units:
    delta_minutes      = delta.seconds // 60
    delta_hours        = delta.seconds // 3600
    delta_weeks        = delta.days // 7
    delta_days         = delta.days

    # for larger differences, return std format
    if delta_weeks > 2:
        return (std_date, std_format)

    # for dates less than 3 weeks, use human readable time stamps 
    if delta_weeks > 0:
        # 3 weeks ago
        human_time_str = "%d %s ago" % (delta_weeks, "week" if delta_weeks == 1 else "weeks")
     
    elif delta_days == 1:
        human_time_str = "yesterday"
        
    elif delta_days > 1:
        # 2 days ago
        human_time_str = "%d days ago" % delta_days

    elif delta_hours > 0:
        human_time_str = "%d %s ago" % (delta_hours, "hour" if delta_weeks == 1 else "hours")
    
    elif delta_minutes > 0:
        human_time_str = "%d %s ago" % (delta_minutes, "minute" if delta_weeks == 1 else "minutes")
    
    else:
        human_time_str = "%d seconds ago" % delta.seconds
    
    return (human_time_str, std_format)


    
