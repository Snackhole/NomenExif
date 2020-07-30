import os
from Core.ExifRenamer import ExifRenamer

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QFileDialog, QFrame, QGridLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QPushButton)


class MainWindow(QMainWindow):
    def __init__(self, ScriptName, AbsoluteDirectoryPath):
        # Store Parameters
        self.ScriptName = ScriptName
        self.AbsoluteDirectoryPath = AbsoluteDirectoryPath

        # Create Exif Renamer
        self.ExifRenamer = ExifRenamer()

        # Initialize
        super().__init__()

        # Create Interface
        self.CreateInterface()

        # Show Window
        self.show()

        # Center Window
        self.Center()

    def CreateInterface(self):
        # Create Window Icon
        # self.WindowIcon = QIcon(self.GetResourcePath("Assets/NomenExif Icon.png"))

        # Window Icon and Title
        # self.setWindowIcon(self.WindowIcon)
        self.setWindowTitle(self.ScriptName)

        # Create Central Frame
        self.Frame = QFrame()

        # Create Widgets
        self.QueueLabel = QLabel("Rename Queue")
        self.QueueLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.QueueListWidget = QListWidget()
        self.AddToQueueButton = QPushButton("Add Files to Rename Queue")
        self.AddToQueueButton.clicked.connect(self.AddToQueue)
        self.ClearQueueButton = QPushButton("Clear Rename Queue")
        self.ClearQueueButton.clicked.connect(self.ClearQueue)
        self.QueueAndTagsSeparator = QFrame()
        self.QueueAndTagsSeparator.setFrameShape(QFrame.VLine)
        self.QueueAndTagsSeparator.setFrameShadow(QFrame.Sunken)
        self.AvailableTagsLabel = QLabel("Available Tags")
        self.AvailableTagsLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.AvailableTagsListWidget = QListWidget()
        self.TemplateSeparator = QFrame()
        self.TemplateSeparator.setFrameShape(QFrame.HLine)
        self.TemplateSeparator.setFrameShadow(QFrame.Sunken)
        self.TemplateLabel = QLabel("Renaming Template:")
        self.TemplateLineEdit = QLineEdit()
        self.RenameButton = QPushButton("Rename Files in Queue with Template")
        self.RenameButton.clicked.connect(self.Rename)

        # Create Layout
        self.Layout = QGridLayout()

        # Widgets in Layout
        self.Layout.addWidget(self.QueueLabel, 0, 0, 1, 2)
        self.Layout.addWidget(self.AddToQueueButton, 1, 0)
        self.Layout.addWidget(self.ClearQueueButton, 1, 1)
        self.Layout.addWidget(self.QueueListWidget, 2, 0, 1, 2)
        self.Layout.addWidget(self.QueueAndTagsSeparator, 0, 3, 3, 1)
        self.Layout.addWidget(self.AvailableTagsLabel, 0, 4)
        self.Layout.addWidget(self.AvailableTagsListWidget, 1, 4, 2, 1)
        self.Layout.addWidget(self.TemplateSeparator, 3, 0, 1, 5)
        self.TemplateLayout = QGridLayout()
        self.TemplateLayout.addWidget(self.TemplateLabel, 0, 0)
        self.TemplateLayout.addWidget(self.TemplateLineEdit, 0, 1)
        self.TemplateLayout.addWidget(self.RenameButton, 1, 0, 1, 2)
        self.TemplateLayout.setColumnStretch(1, 1)
        self.Layout.addLayout(self.TemplateLayout, 4, 0, 1, 5)

        # # Set and Configure Layout
        self.Layout.setColumnStretch(0, 1)
        self.Layout.setColumnStretch(1, 1)
        self.Frame.setLayout(self.Layout)

        # Create Status Bar
        self.StatusBar = self.statusBar()

        # Set Central Frame
        self.setCentralWidget(self.Frame)

    def GetResourcePath(self, RelativeLocation):
        return self.AbsoluteDirectoryPath + "/" + RelativeLocation

    def AddToQueue(self):
        FilesToAdd = QFileDialog.getOpenFileNames(caption="Files to Add to Queue", filter="JPEG Images (*.jpeg *.jpg)")[0]
        if len(FilesToAdd) < 1:
            return
        AllFilesAddedSuccessfully = self.ExifRenamer.AddToRenameQueue(FilesToAdd)
        self.UpdateDisplay()
        if not AllFilesAddedSuccessfully:
            self.DisplayMessageBox("Some of the selected files could not be added to the queue.  They may not have Exif data.", Icon=QMessageBox.Warning)

    def ClearQueue(self):
        if self.DisplayMessageBox("Clear the file queue?", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No)) == QMessageBox.Yes:
            self.ExifRenamer.Clear()
            self.UpdateDisplay()

    def Rename(self):
        # Check if files in queue and valid template (includes at least one available tag, is not empty string)
        pass

    # Interface Methods
    def UpdateDisplay(self):
        self.QueueListWidget.clear()
        for File in self.ExifRenamer.RenameQueue:
            FileListItem = QListWidgetItem()
            FileListItem.setText(File["FileName"])
            FileListItem.setToolTip(File["Path"])
            self.QueueListWidget.addItem(FileListItem)
        self.AvailableTagsListWidget.clear()
        for AvailableTag in self.ExifRenamer.GetAvailableTags():
            AvailableTagListItem = QListWidgetItem()
            AvailableTagListItem.setText("[" + AvailableTag + "]")
            self.AvailableTagsListWidget.addItem(AvailableTagListItem)


    def DisplayMessageBox(self, Message, Icon=QMessageBox.Information, Buttons=QMessageBox.Ok, Parent=None):
        MessageBox = QMessageBox(self if Parent is None else Parent)
        # MessageBox.setWindowIcon(self.WindowIcon)
        MessageBox.setWindowTitle(self.ScriptName)
        MessageBox.setIcon(Icon)
        MessageBox.setText(Message)
        MessageBox.setStandardButtons(Buttons)
        return MessageBox.exec_()

    # Window Management Methods
    def Center(self):
        FrameGeometryRectangle = self.frameGeometry()
        DesktopCenterPoint = QApplication.primaryScreen().availableGeometry().center()
        FrameGeometryRectangle.moveCenter(DesktopCenterPoint)
        self.move(FrameGeometryRectangle.topLeft())
