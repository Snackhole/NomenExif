import copy
import json
import math
import os
import threading

from PyQt6 import QtCore
from PyQt6.QtGui import QIcon, QPalette, QColor, QAction
from PyQt6.QtWidgets import QApplication, QFileDialog, QFrame, QGridLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QProgressBar, QPushButton, QInputDialog

from Core.ExifRenamer import ExifRenamer
from Interface.StatusThread import StatusThread


class MainWindow(QMainWindow):
    def __init__(self, ScriptName, AbsoluteDirectoryPath, AppInst):
        # Store Parameters
        self.ScriptName = ScriptName
        self.AbsoluteDirectoryPath = AbsoluteDirectoryPath
        self.AppInst = AppInst

        # Variables
        self.RestrictedCharacters = ["/", "\\", "#", "%", "&", "{", "}", "<", ">", "*", "?", "$", "!", "'", "\"", ":", "@", "+", "`", "|", "="]
        self.RenameInProgress = False

        # Create Exif Renamer
        self.ExifRenamer = ExifRenamer(self)

        # Initialize
        super().__init__()

        # Create Interface
        self.CreateInterface()
        self.show()

        # Center Window
        self.Center()

        # Load Configs
        self.LoadConfigs()

    def CreateInterface(self):
        # Load Theme
        self.LoadTheme()

        # Create Window Icon
        self.WindowIcon = QIcon(self.GetResourcePath("Assets/NomenExif Icon.png"))

        # Window Icon and Title
        self.setWindowIcon(self.WindowIcon)
        self.setWindowTitle(self.ScriptName)

        # Create Central Frame
        self.Frame = QFrame()

        # Create Widgets
        self.QueueLabel = QLabel("Rename Queue")
        self.QueueLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.QueueListWidget = QListWidget()
        self.AddToQueueButton = QPushButton("Add Files to Rename Queue")
        self.AddToQueueButton.clicked.connect(self.AddToQueue)
        self.ClearQueueButton = QPushButton("Clear Rename Queue")
        self.ClearQueueButton.clicked.connect(self.ClearQueue)
        self.QueueAndTagsSeparator = QFrame()
        self.QueueAndTagsSeparator.setFrameShape(QFrame.Shape.VLine)
        self.QueueAndTagsSeparator.setFrameShadow(QFrame.Shadow.Sunken)
        self.AvailableTagsLabel = QLabel("Available Tags")
        self.AvailableTagsLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.AvailableTagsListWidget = QListWidget()
        self.AvailableTagsListWidget.itemActivated.connect(self.InsertTag)
        self.TemplateSeparator = QFrame()
        self.TemplateSeparator.setFrameShape(QFrame.Shape.HLine)
        self.TemplateSeparator.setFrameShadow(QFrame.Shadow.Sunken)
        self.TemplateLabel = QLabel("Renaming Template:")
        self.TemplateLineEdit = QLineEdit()
        self.RenameButton = QPushButton("Rename Files in Queue with Template")
        self.ProgressSeparator = QFrame()
        self.ProgressSeparator.setFrameShape(QFrame.Shape.HLine)
        self.ProgressSeparator.setFrameShadow(QFrame.Shadow.Sunken)
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

        # Create Actions
        self.CreateActions()

        # Create Menu Bar
        self.CreateMenuBar()

        # Create Status Bar
        self.StatusBar = self.statusBar()

        # Set Central Frame
        self.setCentralWidget(self.Frame)

        # Create Keybindings
        self.CreateKeybindings()

    def CreateActions(self):
        self.SetThemeAction = QAction("Set Theme")
        self.SetThemeAction.triggered.connect(self.SetTheme)

        self.QuitAction = QAction("Quit")
        self.QuitAction.triggered.connect(self.close)

    def CreateMenuBar(self):
        self.MenuBar = self.menuBar()

        self.FileMenu = self.MenuBar.addMenu("File")
        self.FileMenu.addAction(self.SetThemeAction)
        self.FileMenu.addSeparator()
        self.FileMenu.addAction(self.QuitAction)

    def CreateKeybindings(self):
        self.DefaultKeybindings = {}
        self.DefaultKeybindings["QuitAction"] = "Ctrl+Q"

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

        # Keybindings
        KeybindingsFile = self.GetResourcePath("Configs/Keybindings.cfg")
        if os.path.isfile(KeybindingsFile):
            with open(KeybindingsFile, "r") as ConfigFile:
                self.Keybindings = json.loads(ConfigFile.read())
        else:
            self.Keybindings = copy.deepcopy(self.DefaultKeybindings)
        for Action, Keybinding in self.DefaultKeybindings.items():
            if Action not in self.Keybindings:
                self.Keybindings[Action] = Keybinding
        InvalidBindings = []
        for Action in self.Keybindings.keys():
            if Action not in self.DefaultKeybindings:
                InvalidBindings.append(Action)
        for InvalidBinding in InvalidBindings:
            del self.Keybindings[InvalidBinding]
        for Action, Keybinding in self.Keybindings.items():
            getattr(self, Action).setShortcut(Keybinding)

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

        # Keybindings
        with open(self.GetResourcePath("Configs/Keybindings.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.Keybindings, indent=2))

        # Theme
        with open(self.GetResourcePath("Configs/Theme.cfg"), "w") as ConfigFile:
            ConfigFile.write(json.dumps(self.Theme))

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
        if self.DisplayMessageBox("Clear the file queue?", Icon=QMessageBox.Icon.Question, Buttons=(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)) == QMessageBox.StandardButton.Yes:
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

    def DisplayMessageBox(self, Message, Icon=QMessageBox.Icon.Information, Buttons=QMessageBox.StandardButton.Ok, Parent=None):
        MessageBox = QMessageBox(self if Parent is None else Parent)
        MessageBox.setWindowIcon(self.WindowIcon)
        MessageBox.setWindowTitle(self.ScriptName)
        MessageBox.setIcon(Icon)
        MessageBox.setText(Message)
        MessageBox.setStandardButtons(Buttons)
        return MessageBox.exec()

    # Window Management Methods
    def Center(self):
        FrameGeometryRectangle = self.frameGeometry()
        DesktopCenterPoint = QApplication.primaryScreen().availableGeometry().center()
        FrameGeometryRectangle.moveCenter(DesktopCenterPoint)
        self.move(FrameGeometryRectangle.topLeft())

    def CreateThemes(self):
        self.Themes = {}

        # Light
        self.Themes["Light"] = QPalette()
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(120, 120, 120, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, QColor(247, 247, 247, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, QColor(0, 0, 0, 128))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(120, 120, 120, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(120, 120, 120, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Midlight, QColor(247, 247, 247, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(0, 120, 215, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Link, QColor(0, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.LinkVisited, QColor(255, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, QColor(233, 231, 227, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, QColor(0, 0, 0, 128))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Light, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, QColor(227, 227, 227, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, QColor(105, 105, 105, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, QColor(0, 120, 215, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Link, QColor(0, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.LinkVisited, QColor(255, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, QColor(233, 231, 227, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, QColor(0, 0, 0, 128))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, QColor(255, 255, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, QColor(227, 227, 227, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, QColor(160, 160, 160, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, QColor(105, 105, 105, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, QColor(240, 240, 240, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.HighlightedText, QColor(0, 0, 0, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Link, QColor(0, 0, 255, 255))
        self.Themes["Light"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.LinkVisited, QColor(255, 0, 255, 255))

        # Dark
        self.Themes["Dark"] = QPalette()
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, QColor(239, 240, 241, 128))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light, QColor(24, 27, 29, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Midlight, QColor(36, 40, 44, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, QColor(65, 72, 78, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, QColor(0, 0, 0, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(65, 72, 78, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(36, 40, 44, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Link, QColor(41, 128, 185, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.LinkVisited, QColor(127, 140, 141, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, QColor(35, 38, 41, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, QColor(239, 240, 241, 128))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Light, QColor(24, 27, 29, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, QColor(36, 40, 44, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, QColor(65, 72, 78, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, QColor(0, 0, 0, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, QColor(61, 174, 233, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Link, QColor(41, 128, 185, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.LinkVisited, QColor(127, 140, 141, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, QColor(35, 38, 41, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, QColor(239, 240, 241, 128))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, QColor(49, 54, 59, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, QColor(255, 255, 255, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, QColor(24, 27, 29, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, QColor(36, 40, 44, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, QColor(98, 108, 118, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, QColor(65, 72, 78, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, QColor(0, 0, 0, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, QColor(61, 174, 233, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.HighlightedText, QColor(239, 240, 241, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Link, QColor(41, 128, 185, 255))
        self.Themes["Dark"].setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.LinkVisited, QColor(127, 140, 141, 255))

    def LoadTheme(self):
        self.CreateThemes()
        ThemeFile = self.GetResourcePath("Configs/Theme.cfg")
        if os.path.isfile(ThemeFile):
            with open(ThemeFile, "r") as ConfigFile:
                self.Theme = json.loads(ConfigFile.read())
        else:
            self.Theme = "Light"
        self.AppInst.setStyle("Fusion")
        self.AppInst.setPalette(self.Themes[self.Theme])

    def SetTheme(self):
        Themes = list(self.Themes.keys())
        Themes.sort()
        CurrentThemeIndex = Themes.index(self.Theme)
        Theme, OK = QInputDialog.getItem(self, "Set Theme", "Set theme (requires restart to take effect):", Themes, current=CurrentThemeIndex, editable=False)
        if OK:
            self.Theme = Theme
            self.DisplayMessageBox(f"The new theme will be active after {self.ScriptName} is restarted.")

    # Close Event
    def closeEvent(self, Event):
        Close = True
        if self.RenameInProgress:
            Close = self.DisplayMessageBox("Files are currently being renamed.  Exit anyway?", Icon=QMessageBox.Icon.Question, Buttons=(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)) == QMessageBox.StandardButton.Yes
        if Close:
            self.SaveConfigs()
            Event.accept()
        else:
            Event.ignore()
