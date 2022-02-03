# -*- coding: utf-8 -*-
from __future__ import absolute_import
from builtins import str
from qgis.PyQt import QtGui
from qgis.gui import QgsMapTool
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsPoint
from .brasil_IDF_dialog import BrasilIDFDialog
from qgis.PyQt.QtCore import pyqtSignal
from . import brasil_IDF_dialog
from . import resources

class PointTool(QgsMapTool):   
    afterClick = pyqtSignal()
    def __init__(self, iface, dlg):
        QgsMapTool.__init__(self, iface.mapCanvas())
        self.canvas = iface.mapCanvas()
        self.dlg = dlg
        
    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        
        x = event.pos().x()
        y = event.pos().y()
        
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        
    def canvasReleaseEvent(self, event):
        
    #if event.button() == 1:        
        
        crsSrc = self.canvas.mapSettings().destinationCrs()
        crsWGS = QgsCoordinateReferenceSystem(4326)

        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        #If Shift is pressed, convert coords to EPSG:4326
        if crsSrc != crsWGS:
            xform = QgsCoordinateTransform(crsSrc, crsWGS)
            point = xform.transform(QgsPoint(point.x(),point.y()))

        xx = str(round(point.x(),2)) 
        yy = str(round(point.y(),2))         
                
        self.dlg.long_line.setText(xx)
        self.dlg.lat_line.setText(yy)   
   
        self.afterClick.emit()
        
        

    def activate(self):
        pass

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True