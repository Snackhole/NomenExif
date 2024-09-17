import math
from Interface.StatusThread import StatusThread
import os
import threading
from Core.ExifRenamer import ExifRenamer

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QFileDialog, QFrame, QGridLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QProgressBar, QPushButton)


class MainWindow(QMainWindow):
    def __init__(self, ScriptName, AbsoluteDirectoryPath):
        # Store Parameters
        self.ScriptName = ScriptName
        self.AbsoluteDirectoryPath = AbsoluteDirectoryPath

        # Variables
        self.RestrictedCharacters = ["/", "\\", "#", "%", "&", "{", "}", "<", ">", "*", "?", "$", "!", "'", "\"", ":", "@", "+", "`", "|", "="]
        self.RenameInProgress = False

        # Create Exif Renamer
        self.ExifRenamer = ExifRenamer(self)

        # Initialize
        super().__init__()

        # Create Interface
        self.CreateInterface()

        # Show Window
        self.show()

        # Center Window
        self.Center()

        # Load Configs
        self.LoadConfigs()

    def CreateInterface(self):
        # Create Window Icon
        self.WindowIcon = QIcon(self.GetResourcePath("Assets/NomenExif Icon.png"))

        # Window Icon and Title
        self.setWindowIcon(self.WindowIcon)
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
        self.AvailableTagsListWidget.itemActivated.connect(self.InsertTag)
        self.TemplateSeparator = QFrame()
        self.TemplateSeparator.setFrameShape(QFrame.HLine)
        self.TemplateSeparator.setFrameShadow(QFrame.Sunken)
        self.TemplateLabel = QLabel("Renaming Template:")
        self.TemplateLineEdit = QLineEdit()
        self.RenameButton = QPushButton("Rename Files in Queue with Template")
        self.ProgressSeparator = QFrame()
        self.ProgressSeparator.setFrameShape(QFrame.HLine)
        self.ProgressSeparator.setFrameShadow(QFrame.Sunken)
        self.RenameButton.clicked.connect(self.Rename)
        self.RenameProgressLabel = QLabel("Rename Progress")
        self.RenameProgressBar = QProgressBar()

        # Widgets to Disable While Renaming
        self.DisableList = []
        self.DisableList.append(self.AddToQueueButton)
        self.DisableList.append(self.ClearQueueButton)
        self.DisableList.append(self.AvailableTagsListWidget)
        self.DisableList.append(self.TemplateLineEdit)
        self.DisableList.append(self.RenameButton)

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
        self.Layout.addWidget(self.ProgressSeparator, 5, 0, 1, 5)
        self.ProgressLayout = QGridLayout()
        self.ProgressLayout.addWidget(self.RenameProgressLabel, 0, 0)
        self.ProgressLayout.addWidget(self.RenameProgressBar, 0, 1)
        self.Layout.addLayout(self.ProgressLayout, 6, 0, 1, 5)

        # Set and Configure Layout
        self.Layout.setColumnStretch(0, 1)
        self.Layout.setColumnStretch(1, 1)
        self.Frame.setLayout(self.Layout)

        # Create Status Bar
        self.StatusBar = self.statusBar()

        # Set Central Frame
        self.setCentralWidget(self.Frame)

    def GetResourcePath(self, RelativeLocation):
        return os.path.join(self.AbsoluteDirectoryPath, RelativeLocation)

    def LoadConfigs(self):
        # Template
        LastEnteredTemplateFile = self.GetResourcePath("Configs/Template.cfg")
        if os.path.isfile(LastEnteredTemplateFile):
            with open(LastEnteredTemplateFile, "r") as ConfigFile:
                self.TemplateLineEdit.setText(ConfigFile.readline())
        else:
            self.TemplateLineEdit.setText("[YEAR].[MONTH].[DAY] - [HOUR].[MINUTE].[SECOND]")

        # Last Opened Directory
        LastOpenedDirectoryFile = self.GetResourcePath("Configs/LastOpenedDirectory.cfg")
        if os.path.isfile(LastOpenedDirectoryFile):
            with open(LastOpenedDirectoryFile, "r") as ConfigFile:
                self.LastOpenedDirectory = ConfigFile.readline()
        else:
            self.LastOpenedDirectory = None

    def SaveConfigs(self):
        if not os.path.isdir(self.GetResourcePath("Configs")):
            os.mkdir(self.GetResourcePath("Configs"))

        # Template
        TemplateString = self.TemplateLineEdit.text()
        if TemplateString != "":
            with open(self.GetResourcePath("Configs/Template.cfg"), "w") as ConfigFile:
                ConfigFile.write(TemplateString)

        # Last Opened Directory
        if type(self.LastOpenedDirectory) == str:
            if os.path.isdir(self.LastOpenedDirectory):
                with open(self.GetResourcePath("Configs/LastOpenedDirectory.cfg"), "w") as ConfigFile:
                    ConfigFile.write(self.LastOpenedDirectory)

    def AddToQueue(self):
        FilesToAdd = QFileDialog.getOpenFileNames(caption="Files to Add to Queue", filter="JPEG Images (*.jpeg *.jpg)", directory=self.LastOpenedDirectory)[0]
        if len(FilesToAdd) < 1:
            return
        AllFilesAddedSuccessfully = self.ExifRenamer.AddToRenameQueue(FilesToAdd)
        self.UpdateDisplay()
        self.LastOpenedDirectory = os.path.dirname(FilesToAdd[0])
        if not AllFilesAddedSuccessfully:
            self.DisplayMessageBox("Some of the selected files could not be added to the queue.  They may not have Exif data.", Icon=QMessageBox.Warning)

    def ClearQueue(self):
        if self.DisplayMessageBox("Clear the file queue?", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No)) == QMessageBox.Yes:
            self.ExifRenamer.Clear()
            self.UpdateDisplay()

    def InsertTag(self):
        self.TemplateLineEdit.insert((self.AvailableTagsListWidget.selectedItems()[0]).text())
        self.TemplateLineEdit.setFocus()

    def ValidTemplate(self, Template):
        ValidTemplate = False
        for Tag in self.ExifRenamer.AvailableTags:
            if f"[{Tag}]" in Template:
                ValidTemplate = True
        for Character in self.RestrictedCharacters:
            if Character in Template:
                return False
        return ValidTemplate

    def Rename(self):
        # Validate Inputs
        if len(self.ExifRenamer.RenameQueue) < 1:
            self.DisplayMessageBox("No files selected to rename.", Icon=QMessageBox.Warning)
            return

        Template = self.TemplateLineEdit.text()

        if not self.ValidTemplate(Template):
            RestrictedCharactersString = ""
            for Character in self.RestrictedCharacters:
                RestrictedCharactersString += f"{Character} "
            RestrictedCharactersString.rstrip()
            self.DisplayMessageBox(f"Rename template must contain at least one available tag, and cannot contain the following characters:\n\n{RestrictedCharactersString}", Icon=QMessageBox.Warning)
            return

        # Start Renaming
        self.SetRenameInProgress(True)
        self.ExifRenamer.RenameFilesWithTemplate(Template)

        # Attempt to Get Rename Thread and Set Up Status Checking
        try:
            RenameThreadInst = [RenameThread for RenameThread in threading.enumerate() if RenameThread.name == "RenameThread"][0]
            StatusThreadInst = StatusThread(RenameThreadInst)
            StatusThreadInst.UpdateProgressSignal.connect(lambda: self.UpdateProgress(RenameThreadInst))
            StatusThreadInst.RenameCompleteSignal.connect(self.RenameComplete)
            StatusThreadInst.start()
        except IndexError:
            self.RenameComplete()

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
            AvailableTagListItem.setText(f"[{AvailableTag}]")
            self.AvailableTagsListWidget.addItem(AvailableTagListItem)

    def SetRenameInProgress(self, RenameInProgress):
        self.RenameInProgress = RenameInProgress
        for Widget in self.DisableList:
            Widget.setDisabled(RenameInProgress)
        if RenameInProgress:
            self.StatusBar.showMessage("Renaming in progress...")
        else:
            self.StatusBar.clearMessage()
            self.RenameProgressBar.reset()

    def UpdateProgress(self, RenameThread):
        RenameProgress = math.floor((RenameThread.FilesRenamed / RenameThread.FileQueueSize) * 100)
        self.RenameProgressBar.setValue(RenameProgress)

    def RenameComplete(self):
        self.SetRenameInProgress(False)
        self.ExifRenamer.Clear()
        self.UpdateDisplay()

    def DisplayMessageBox(self, Message, Icon=QMessageBox.Information, Buttons=QMessageBox.Ok, Parent=None):
        MessageBox = QMessageBox(self if Parent is None else Parent)
        MessageBox.setWindowIcon(self.WindowIcon)
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

    def closeEvent(self, Event):
        Close = True
        if self.RenameInProgress:
            Close = self.DisplayMessageBox("Files are currently being renamed.  Exit anyway?", Icon=QMessageBox.Question, Buttons=(QMessageBox.Yes | QMessageBox.No)) == QMessageBox.Yes
        if Close:
            self.SaveConfigs()
            Event.accept()
        else:
            Event.ignore()
