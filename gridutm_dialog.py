# -*- coding: utf-8 -*-
"""
/***************************************************************************
 gridUtmDialog
                                 A QGIS plugin
 grid with utm
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-09-21
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Bienvenue
        email                : henriprincetoky@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import sys
import os
import os.path
from . import shapefile
from . import shapefile as shp
import math
import processing

# Import de QGIS
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis import *
from qgis.core import *
from qgis.gui import *
from qgis.core import QgsVectorLayer, QgsProject

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QComboBox, QPushButton, QFileDialog, QVBoxLayout


# avoir path plugins
path_absolute = os.path.dirname(os.path.realpath(__file__))

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'gridutm_dialog_base.ui'))


class gridUtmDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(gridUtmDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # pour remplir echelle et orientation, Format
        self.cbxEchelle.addItems("25 50 100 200 500 1000 2000 2500 5000 10000 12500 50000 100000" .split())
        self.cbxOrientation.addItems("Portrait Paysage" .split())
        self.cbxFormat.addItems("A4 A3 A2 A1 PERSO" .split())

        
        # rendre invisible
        self.x_max_2.setVisible(False)
        self.y_max_2.setVisible(False)
        self.x_min_2.setVisible(False)
        self.y_min_2.setVisible(False)
        

        # signal
        self.chbxLayer.clicked.connect(lambda: self.chargerCoucheExist())
        self.btn_RepshpOuvrir.clicked.connect(lambda: self.repShpOuvrir())
        self.btn_RepshpSave.clicked.connect(lambda: self.RepShpSave())
        self.btn_Executer.clicked.connect(lambda: self.Executer())
        

        # change Item
        self.cbxLayer.currentIndexChanged.connect(lambda: self.trouver_coor())
        self.cbxEchelle.currentIndexChanged.connect(lambda: self.trouver_grille())
        self.cbxOrientation.currentIndexChanged.connect(lambda: self.trouver_grille())
        self.cbxFormat.currentIndexChanged.connect(lambda: self.trouver_grille())

    def activeMarge(self):
        if self.chbxMarge.isChecked() == True:
            self.grb_Marge.setEnabled(True)
        else:
            self.grb_Marge.setEnabled(False)

    def backBBox(self, xsource, xtype):
        path_laborde_tmp = path_absolute + '/tmp_shp'
        rep_shpLaborde = os.path.join(path_absolute, 'tmp_shp/shpLaborde.shp')
        rep_shpLaborde = rep_shpLaborde.replace('\\', '/')
        os.chmod(path_laborde_tmp, 0o777)
        if xtype == "EXTERNE":
            # verifier sa projection
            layer = QgsVectorLayer(xsource, 'shpWGS84', 'ogr')
            crs_eto = layer.crs().authid()
            nom_crs = str(crs_eto)
            sf_Init = shapefile.Reader(xsource)
            shapes = sf_Init.shapes()
            box_Init = shapes[0].bbox
            self.putBboxMinMax(box_Init, crs_eto, xsource, rep_shpLaborde)

        if xtype == "LAYERS":
            # verifier sa projection
            crs_eto = xsource.crs().authid()
            nom_crs = str(crs_eto)
            # XMin, YMin : XMax, Ymax
            box_Init = xsource.extent().toString()
            self.putBboxMinMax(box_Init, crs_eto, xsource, rep_shpLaborde)

            

    def putBboxMinMax(self, xbbox, crs_eto, xsource, rep_shpLaborde):
        """
        str_bbox = ''.join(str(xbbox))
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(str_bbox + "  " + crs_eto) 
        msg.setInformativeText('More information')
        msg.setWindowTitle("Error")
        msg.exec_()
        """
        
 
        if crs_eto == 'EPSG:4326':
            bbox2 = xbbox.split(":")
            Minbbox = bbox2[0].split(",")
            Maxbbox = bbox2[1].split(",")
            self.x_min.setText(str(Minbbox[0].strip()))
            self.y_min.setText(str(Minbbox[1].strip()))
            self.x_max.setText(str(Maxbbox[0].strip()))
            self.y_max.setText(str(Maxbbox[1].strip()))
            # transforme en fichier Laborde pour calculer en metric
            parameter = {'INPUT': xsource,
                         'TARGET_CRS': 'EPSG:32738', 'OUTPUT': rep_shpLaborde}
            processing.run("qgis:reprojectlayer", parameter)
            layer2 = QgsVectorLayer(rep_shpLaborde,  'shpLaborde', "ogr")
            box_laborde = layer2.extent().toString()
            # crs_eto2=layer2.crs().authid()
            # XMin, YMin : XMax, Ymax
            bbox2 = box_laborde.split(":")
            Minbbox = bbox2[0].split(",")
            Maxbbox = bbox2[1].split(",")
            # pour calculer en laborde
            self.x_min_2.setText(str(Minbbox[0].strip()))
            self.y_min_2.setText(str(Minbbox[1].strip()))
            self.x_max_2.setText(str(Maxbbox[0].strip()))
            self.y_max_2.setText(str(Maxbbox[1].strip()))
           
        else:
            # XMin YMin XMax Ymax
            Vbbox = xbbox.split(":")
            Minbbox = Vbbox[0].split(",")
            Maxbbox = Vbbox[1].split(",")
            self.x_min.setText(str(Minbbox[0].strip()))
            self.y_min.setText(str(Minbbox[1].strip()))
            self.x_max.setText(str(Maxbbox[0].strip()))
            self.y_max.setText(str(Maxbbox[1].strip()))
            # pour calculer en laborde
            self.x_min_2.setText(str(Minbbox[0].strip()))
            self.y_min_2.setText(str(Minbbox[1].strip()))
            self.x_max_2.setText(str(Maxbbox[0].strip()))
            self.y_max_2.setText(str(Maxbbox[1].strip()))
        
        

    # pour choisir le fichier dans DialogBox standard
    def repShpOuvrir(self):
        global path_absolute
        self.cbxLayer.clear()
        self.chbxLayer.setChecked(False)

        dialog = QFileDialog.getOpenFileName(
            self, "Ouvrir Fichier Vecteur...", None,  "Shape (*.shp)")
        if dialog:
            repshp = dialog[0]
            self.cbxLayer.addItem(repshp)
            shpEtoTmp = self.cbxLayer.currentText()
            # call function
            self.backBBox(repshp, "EXTERNE")

    def trouver_coor(self):
        if self.chbxLayer.isChecked() == True:
            global path_absolute
            s_LayerIndex = self.cbxLayer.currentIndex
            n_layer = str(self.cbxLayer.currentText())
            vl = QgsProject.instance().mapLayersByName(n_layer)[0]
            self.backBBox(vl, "LAYERS")

    def RepShpSave(self):
        filecsv = QFileDialog.getSaveFileName(
            self, "Selectionner fichier de sortie (shapefile) ", "", '*.shp')
        if filecsv:
            #self.TmpMsgbox(filecsv[0])
            self.rep_shpSave.setText(filecsv[0])

        return

    def chargerCoucheExist(self):
        self.cbxLayer.clear()
        if self.chbxLayer.isChecked() == True:
            layer_list = []
            layers = QgsProject.instance().mapLayers().values()
            for layer in layers:
                # pour verifier si vecteur
                # if layer.type() == QgsMapLayer.VectorLayer or QgsMapLayer.rasterLayer:
                if layer.type() == QgsMapLayer.VectorLayer:
                    # layers = self.iface.activeLayer()
                    # if layer > 0:
                    layer_list.append(layer.name())
            self.cbxLayer.addItems(layer_list)
    
    def trouver_grille(self):
        """
        1cm carte donne 50 000 cm  ou 50m ou 0.05 km sur terrain
        donc trouver par orientation et format, echelle
        """
        global dx
        global dy
        minx,maxx,miny,maxy = float(self.x_min_2.toPlainText()), float(self.x_max_2.toPlainText()),float(self.y_min_2.toPlainText()), float(self.y_max_2.toPlainText())
        # trouver dimension grille par format et orientation
        if self.cbxFormat.currentText() =='A4':
            if self.cbxOrientation.currentText() =='Portrait':
                dx = 0.21 * int(self.cbxEchelle.currentText())
                dy = 0.297 * int(self.cbxEchelle.currentText())
            if self.cbxOrientation.currentText() =='Paysage':
                dx = 0.297 * int(self.cbxEchelle.currentText())
                dy = 0.21 * int(self.cbxEchelle.currentText())
        elif self.cbxFormat.currentText() =='A3':
            if self.cbxOrientation.currentText() =='Portrait':
                dx = 0.297 * int(self.cbxEchelle.currentText())
                dy = 0.42 * int(self.cbxEchelle.currentText())
            if self.cbxOrientation.currentText() =='Paysage':
                dx = 0.42 * int(self.cbxEchelle.currentText())
                dy = 0.297 * int(self.cbxEchelle.currentText())
        elif self.cbxFormat.currentText() =='A2':
            if self.cbxOrientation.currentText() =='Portrait':
                dx = 0.42 * int(self.cbxEchelle.currentText())
                dy = 0.594 * int(self.cbxEchelle.currentText())
            if self.cbxOrientation.currentText() =='Paysage':
                dx = 0.594 * int(self.cbxEchelle.currentText())
                dy = 0.42 * int(self.cbxEchelle.currentText())
        elif self.cbxFormat.currentText() =='PERSO':
            if self.cbxOrientation.currentText() =='Portrait':
                dx = 1 * int(self.cbxEchelle.currentText())
                dy = 1 * int(self.cbxEchelle.currentText())
            if self.cbxOrientation.currentText() =='Paysage':
                dx = 1 * int(self.cbxEchelle.currentText())
                dy = 1 * int(self.cbxEchelle.currentText())
        else:
            if self.cbxOrientation.currentText() =='Portrait':
                dx = 0.594 * int(self.cbxEchelle.currentText())
                dy = 1.188 * int(self.cbxEchelle.currentText())
            if self.cbxOrientation.currentText() =='Paysage':
                dx = 10.188 * int(self.cbxEchelle.currentText())
                dy = 0.594 * int(self.cbxEchelle.currentText())
        
        # trouver nombre grille
        nbrx = int(math.ceil(abs(maxx - minx)/dx))
        nbry = int(math.ceil(abs(maxy - miny)/dy))
        # afficher pour informations
        totGrid = nbrx * nbry
        self.lbl_Gridxy.setText(str(dx) + " x " + str(dy))
        self.lbl_Nbregrid.setText("Total: " + str(totGrid) + " dont :" + str(nbrx) + " x " + str(nbry))

    def Executer(self):
        repEto = self.rep_shpSave.toPlainText()
        if repEto != '':
            # recuperer le nom de fichier
            infos_shp = QtCore.QFileInfo(repEto)
            Nomfile = infos_shp.baseName()
            #Creer grid
            minx,maxx,miny,maxy = float(self.x_min.toPlainText()), float(self.x_max.toPlainText()),float(self.y_min.toPlainText()), float(self.y_max.toPlainText())
            nx = int(math.ceil(abs(maxx - minx)/dx))
            ny = int(math.ceil(abs(maxy - miny)/dy))

            # Definir le polygone
            if self.radio_pg.isChecked():
                id=0
                # Ajouter marge pour la dernière case si avec marge
                if self.chbxMarge.isChecked() == True:
                    if self.xMarge.toPlainText() !='' and self.yMarge.toPlainText() !='':
                        if self.xMarge.toPlainText().isnumeric()==True and self.yMarge.toPlainText().isnumeric() ==True:
                            plus_y=int(self.yMarge.toPlainText())*ny
                            plus_x=int(self.xMarge.toPlainText())*nx
                            minx,maxx,miny,maxy = minx,maxx+plus_x,miny-plus_y,maxy

                    else:
                        if self.xMarge.toPlainText() =='' or self.yMarge.toPlainText() =='':
                            self.TmpMsgbox("Valeur incorrecte pour les champs")
                            if self.xMarge.toPlainText() =='':
                                self.xMarge.setFocus()
                            if self.yMarge.toPlainText() =='':
                                self.yMarge.setFocus()
                            # sortie de la function
                            return None
                        if self.xMarge.toPlainText().isnumeric()== False or self.yMarge.toPlainText().isnumeric() == False:
                            self.TmpMsgbox("Valeur incorrecte pour les champs")
                            return None
    
                # Definir le polygone
                w = shp.Writer(shp.POLYGON)
                w.autoBalance = 1
                w.field("id")
                w.field("distance")
                w.field("sens")
                w.field("format")
                w.field("y_x")
                w.field("x") 
                w.field("y")
                #w.field("nom_grid")
                #w.field("nom_col") # x
                #w.field("nom_row") #y
                for i in range(ny):
                    for j in range(nx):
                        id+=1
                        vertices = []
                        parts = []
                        if self.radio_pg.isChecked():
                            if self.xMarge.toPlainText() !='' and self.yMarge.toPlainText() != '':
                                # x =j, y = i
                                if j==0 and i==0:
                                    vertices.append([min(minx+dx*j,maxx),max(maxy-dy*i,miny)])
                                    vertices.append([min(minx+dx*(j+1),maxx),max(maxy-dy*i,miny)])
                                    vertices.append([min(minx+dx*(j+1),maxx),max(maxy-dy*(i+1),miny)])
                                    vertices.append([min(minx+dx*j,maxx),max(maxy-dy*(i+1),miny)])

                                if j ==0 and i>0:
                                    # dymarge=2*i
                                    dymarge=int(self.yMarge.toPlainText())*i
                                    vertices.append([min(minx+dx*j,maxx),max(maxy-dy*i,miny)+dymarge])
                                    vertices.append([min(minx+dx*(j+1),maxx),max(maxy-dy*i,miny)+dymarge])
                                    vertices.append([min(minx+dx*(j+1),maxx),max(maxy-dy*(i+1),miny)+dymarge])
                                    vertices.append([min(minx+dx*j,maxx),max(maxy-dy*(i+1),miny)+dymarge])

                                if j>0 and i==0:
                                    # dxmarge=2*j
                                    dxmarge=int(self.xMarge.toPlainText())*j
                                    vertices.append([min(minx+dx*j,maxx)-dxmarge,max(maxy-dy*i,miny)])
                                    vertices.append([min(minx+dx*(j+1),maxx)-dxmarge,max(maxy-dy*i,miny)])
                                    vertices.append([min(minx+dx*(j+1),maxx)-dxmarge,max(maxy-dy*(i+1),miny)])
                                    vertices.append([min(minx+dx*j,maxx)-dxmarge,max(maxy-dy*(i+1),miny)])


                                if j>0 and i>0:
                                    # dxmarge=2*j
                                    # dymarge=2*i
                                    dymarge=int(self.yMarge.toPlainText())*i
                                    dxmarge=int(self.xMarge.toPlainText())*j
                                    vertices.append([min(minx+dx*j,maxx)-dxmarge,max(maxy-dy*i,miny)+dymarge])
                                    vertices.append([min(minx+dx*(j+1),maxx)-dxmarge,max(maxy-dy*i,miny)+dymarge])
                                    vertices.append([min(minx+dx*(j+1),maxx)-dxmarge,max(maxy-dy*(i+1),miny)+dymarge])
                                    vertices.append([min(minx+dx*j,maxx)-dxmarge,max(maxy-dy*(i+1),miny)+dymarge])
                            else:
                                vertices.append([min(minx+dx*j,maxx),max(maxy-dy*i,miny)])
                                vertices.append([min(minx+dx*(j+1),maxx),max(maxy-dy*i,miny)])
                                vertices.append([min(minx+dx*(j+1),maxx),max(maxy-dy*(i+1),miny)])
                                vertices.append([min(minx+dx*j,maxx),max(maxy-dy*(i+1),miny)])
                        
                            parts.append(vertices)
                            w.poly(parts)

                        # charger shapefile
                        w.record(id, 
                        str(self.cbxEchelle.currentText()),
                        str(self.cbxOrientation.currentText()),
                        str(self.cbxFormat.currentText()),
                        str(i) +"_" + str(j), j, i)
                
                # sauvegarder shapefile
                w.save(repEto)


            # Definir le point
            if self.radio_pt.isChecked():
                id=0
                w = shp.Writer(shp.POINT)
                w.autoBalance = 1
                w.field("id")
                w.field("distance")
                w.field("sens")
                w.field("format")
                w.field("y_x")
                w.field("x") 
                w.field("y")
                for i in range(ny):
                    for j in range(nx):
                        id+=1
                        pos_x = minx + (dx*j)
                        pos_y = maxy - (dy*i)
                        val_yx = str(i) +"_" + str(j)

                        #charger shapefile
                        w.point(float(pos_x), float(pos_y))
                        w.record(id, 
                        str(self.cbxEchelle.currentText()),
                        str(self.cbxOrientation.currentText()),
                        str(self.cbxFormat.currentText()),
                        val_yx, j, i)
                        
                # sauvegarder shapefile
                w.save(repEto)

            
            # charger dans qgis avec SCR UTM 38S: 32738
            if self.chbxCanvas.isChecked() == True:
                layer = QgsVectorLayer(repEto, Nomfile, "ogr")
                if not layer.isValid():
                    self.TmpMsgbox("Impossible de charger le fichier")
                    
                else:
                    layer.setCrs( QgsCoordinateReferenceSystem(32738, QgsCoordinateReferenceSystem.EpsgCrsId) )
                    QgsProject.instance().addMapLayer(layer)
            
            
            
                
        else:
            self.TmpMsgbox("Veuillez selectionner le Repertoire pour le shapefile")
            
    def TmpMsgbox(self, hafatra):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(hafatra) 
        msg.setInformativeText('More information')
        msg.setWindowTitle("Error")
        msg.exec_()