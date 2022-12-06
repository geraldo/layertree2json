# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LayerTree2JSONDialogSettings
                                 A QGIS plugin
 Parse QGIS 3 project files and write a JSON config file with layer information.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-07-05
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Gerald Kogler/PSIG
        email                : geraldo@servus.at
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

import os
import webbrowser
from datetime import datetime

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QSettings, QUrl

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'layertree2json_dialog_settings.ui'))


class Settings():

    activeProject = -1
    # [0]: project name
    # [1]: QGS file
    # [2]: QGS path
    # [3]: JSON path base
    # [4]: JSON path extended
    # [5]: Server Host
    # [6]: FTP User
    # [7]: FTP Password
    # [8]: Tile cache
    userProjects = []

    def __init__(self):
        self.readSettings()

    def readSettings(self):
        '''Load the user selected settings. The settings are retained even when
        the user quits QGIS. This just loads the saved information into variables,
        but does not update the widgets. The widgets are updated with showEvent.'''
        qset = QSettings()

        self.activeProject = qset.value('/LayerTree2JSON/ActiveProject', -1)

        self.userProjects = qset.value('/LayerTree2JSON/UserProjects', 0)
        if not isinstance(self.userProjects, list):
            self.userProjects = []


settings = Settings()


class LayerTree2JSONDialogSettings(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, LayerTree2JSON, iface, parent=None):
        super(LayerTree2JSONDialogSettings, self).__init__(parent)
        self.LayerTree2JSON = LayerTree2JSON
        self.iface = iface
        self.setupUi(self)

        self.isNew = False
        self.buttonShowJson.clicked.connect(self.showOnlineFile)
        self.buttonShowProject.clicked.connect(self.showProject)
        self.buttonTest.clicked.connect(self.testConnection)
        self.buttonBoxSettings.helpRequested.connect(self.help)

        self.inputHost.textChanged.connect(self.checkEnabled)
        self.inputQgsPath.textChanged.connect(self.checkEnabled)
        self.inputJsonPath.textChanged.connect(self.checkEnabled)
        self.inputJsonPath2.textChanged.connect(self.checkEnabled)

        #self.dlg.radioMapproxy.toggled.connect(self.changeTilecache)

        self.readSettings()

    def readSettings(self):
        '''Load the user selected settings. The settings are retained even when
        the user quits QGIS. This just loads the saved information into variables,
        but does not update the widgets. The widgets are updated with showEvent.'''
        qset = QSettings()

        settings.readSettings()

    def accept(self):
        '''Accept the settings and save them for next time.'''
        self.editProject()

        if settings.userProjects:
            QSettings().setValue('/LayerTree2JSON/UserProjects', settings.userProjects)
        else:
            QSettings().setValue('/LayerTree2JSON/UserProjects', 0)

        # update active project
        self.LayerTree2JSON.update_project_vars()

        # The values have been read from the widgets and saved to the registry.
        # Now we will read them back to the variables.
        #self.readSettings()
        self.close()

    def editProject(self):
        name = self.inputProjectName.text().strip()
        qgsFile = self.inputQgsFile.text().strip()
        qgsPath = self.inputQgsPath.text().strip()
        jsonPath = self.inputJsonPath.text().strip()
        jsonPath2 = self.inputJsonPath2.text().strip()
        host = self.inputHost.text().strip()
        user = self.inputUser.text().strip()
        password = self.inputPassword.text().strip()
        tilecache = self.radioMapproxy.isChecked()

        if name:
            if not qgsFile:
                qgsFile = name + '.qgs'
            if not qgsPath:
                qgsPath = '/home/me/' + name + '/'
            if not jsonPath:
                jsonPath = '/var/www/html/'
            if not jsonPath2:
                jsonPath2 = name + '/js/data/'

            project = [name, qgsFile, qgsPath, jsonPath, jsonPath2, host, user, password, tilecache]
            currentIndex = self.LayerTree2JSON.dlg.inputProjects.currentIndex()
            if self.isNew:
                currentIndex = len(settings.userProjects)
                settings.userProjects.append(project)
                settings.activeProject = currentIndex
                QSettings().setValue('/LayerTree2JSON/ActiveProject', currentIndex)
            else:
                settings.userProjects[currentIndex] = project

            self.checkEnabled()

            names = []
            for item in settings.userProjects:
                names.append(item[0])
            self.LayerTree2JSON.dlg.inputProjects.clear()
            self.LayerTree2JSON.dlg.inputProjects.addItems(names)
            self.LayerTree2JSON.dlg.inputProjects.setCurrentIndex(currentIndex)

            self.LayerTree2JSON.dlg.buttonEditProject.setEnabled(True);
            self.LayerTree2JSON.dlg.buttonRemoveProject.setEnabled(True);

    def checkEnabled(self):
            fields_filled = self.inputHost.text() != "" and self.inputQgsPath.text() != "" and self.inputJsonPath.text() != "" and self.inputJsonPath2.text() != ""
            self.buttonShowProject.setEnabled(fields_filled)
            self.buttonShowJson.setEnabled(fields_filled)

    def testConnection(self):
        if (self.LayerTree2JSON.inputsFtpOk(self.inputHost.text(), self.inputUser.text(), self.inputPassword.text())):
            self.LayerTree2JSON.connectToFtp(False, False, self.inputHost.text(), self.inputUser.text(), self.inputPassword.text())

    def showOnlineFile(self):
        host = self.inputHost.text()
        path = self.inputJsonPath2.text()
        file = self.inputQgsFile.text() + '.json'
        # add timestamp to path to avoid cache
        webbrowser.open(host + '/' + path + file + '?' + str(datetime.timestamp(datetime.now())))

    def showProject(self):
        host = self.inputHost.text()
        path = self.inputProjectName.text()
        # exception for project ctbb which has different sub projects
        if path == 'ctbb':
            path += '/index'
            if self.LayerTree2JSON.projectFilename != 'poum':
                path += '_' + self.LayerTree2JSON.projectFilename.replace('.qgs', '')
            path += '.php'
        webbrowser.open(host + '/' + path)

    def help(self):
        '''Display a help page'''
        url = QUrl.fromLocalFile(os.path.dirname(__file__) + "/docs/index.html#conf").toString()
        webbrowser.open(url, new=2)
