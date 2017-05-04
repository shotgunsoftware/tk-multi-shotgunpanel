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
import datetime

def create_round_thumbnail(image):
    """
    Create a 200 px wide circle thumbnail
    
    :param image: QImage representing a thumbnail
    :returns: Round QPixmap
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

def create_round_512x400_note_thumbnail(image, client=False, unread=False):
    """
    Given a QImage shotgun thumbnail, create a round icon
    with the thumbnail composited onto a centered otherwise empty canvas. 
    This will return a 512x400 pixmap object.
    
    :param image: QImage source image
    :param client: indicates that this is a client note
    :param unread: indicates that this is an unread note 
    :returns: QPixmap circular thumbnail, 380px wide, on a 
              512x400 rect backdrop
    """    
    CANVAS_WIDTH = 512
    CANVAS_HEIGHT = 400
    CIRCLE_SIZE = 380

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
                
        # figure out the offset height wise in order to center the thumb        
        
        # center it
        inlay_offset_h = (CANVAS_HEIGHT - CIRCLE_SIZE)/2
        inlay_offset_w = (CANVAS_WIDTH - CIRCLE_SIZE)/2
        
        # note how we have to compensate for the corner radius
        painter.translate(inlay_offset_w, inlay_offset_h)
        painter.drawEllipse(0, 0, CIRCLE_SIZE, CIRCLE_SIZE)

        if unread:
            UNREAD_NOTE_INDICATOR = QtGui.QPixmap(":/tk_multi_infopanel/unread_indicator.png")
            painter.drawPixmap(-10, -10, UNREAD_NOTE_INDICATOR)
        
        painter.translate(0, 250)
        
        if client:
            CLIENT_NOTE_INDICATOR = QtGui.QPixmap(":/tk_multi_infopanel/client_note_indicator.png")
            painter.drawPixmap(0, 0, CLIENT_NOTE_INDICATOR)
        
        painter.end()
    
    return base_image

def create_rectangular_512x400_thumbnail(image):
    """
    Given a QImage shotgun thumbnail, create a rectangular icon
    with the thumbnail composited onto a centered otherwise empty canvas. 
    This will return a 512x400 pixmap object.
    
    :param image: QImage source image
    :returns: QPixmap rectangular thumbnail on a 512x400 rect backdrop
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
        painter.setPen(QtGui.QPen())
        
        painter.drawRoundedRect(0,  
                                0, 
                                CANVAS_WIDTH, 
                                CANVAS_HEIGHT, 
                                CORNER_RADIUS, 
                                CORNER_RADIUS)
        
        painter.end()
    
    return base_image


def create_human_readable_timestamp(datetime_obj):
    """
    Formats a time stamp the way dates are formatted in the 
    Shotgun activity stream. Examples of output:
    
    Recent posts: 10:32
    This year: 24 June 10:32
    Last year and earlier: 12 December 2007
    
    :param datetime_obj: Datetime obj to format
    :returns: date str
    """
    # standard format 
    full_time_str = datetime_obj.strftime('%a %d %b %Y %H:%M') 

    if datetime_obj > datetime.datetime.now():
        # future times are reported precisely
        return (full_time_str, full_time_str) 
    
    # get the delta and components
    delta = datetime.datetime.now() - datetime_obj

    # the timedelta structure does not have all units; bigger units are converted
    # into given smaller ones (hours -> seconds, minutes -> seconds, weeks > days, ...)
    # but we need all units:
    delta_weeks = delta.days // 7
    delta_days = delta.days

    if delta_weeks > 52:
        # more than one year ago - 26 June 2012
        time_str = datetime_obj.strftime('%d %b %Y %H:%M')
    
    elif delta_days > 1:
        # ~ more than one week ago - 26 June
        time_str = datetime_obj.strftime('%d %b %H:%M')
    
    else:
        # earlier today - display timestamp - 23:22
        time_str = datetime_obj.strftime('%H:%M')
                 
    return (time_str, full_time_str)


