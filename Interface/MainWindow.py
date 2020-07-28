from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel, QLineEdit, QListWidget, QMainWindow, QMessageBox, QPushButton, QSizePolicy)


class MainWindow(QMainWindow):
    def __init__(self, ScriptName, AbsoluteDirectoryPath):
        # Store Parameters
        self.ScriptName = ScriptName
        self.AbsoluteDirectoryPath = AbsoluteDirectoryPath

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

        # Button Size Policy
        self.ButtonSizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # Create Central Frame
        self.Frame = QFrame()

        # Create Widgets
        self.QueueLabel = QLabel("Rename Queue")
        self.QueueLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.QueueListView = QListWidget()
        self.AddToQueueButton = QPushButton("Add Files to Rename Queue")
        self.AddToQueueButton.setSizePolicy(self.ButtonSizePolicy)
        self.AddToQueueButton.clicked.connect(self.AddToQueue)
        self.ClearQueueButton = QPushButton("Clear Rename Queue")
        self.ClearQueueButton.setSizePolicy(self.ButtonSizePolicy)
        self.ClearQueueButton.clicked.connect(self.ClearQueue)
        self.QueueAndTagsSeparator = QFrame()
        self.QueueAndTagsSeparator.setFrameShape(QFrame.VLine)
        self.QueueAndTagsSeparator.setFrameShadow(QFrame.Sunken)
        self.AvailableTagsLabel = QLabel("Available Tags")
        self.AvailableTagsLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.AvailableTagsList = QListWidget()
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
        self.Layout.addWidget(self.QueueListView, 1, 0, 2, 1)
        self.Layout.addWidget(self.AddToQueueButton, 1, 1)
        self.Layout.addWidget(self.ClearQueueButton, 2, 1)
        self.Layout.addWidget(self.QueueAndTagsSeparator, 0, 2, 3, 1)
        self.Layout.addWidget(self.AvailableTagsLabel, 0, 3)
        self.Layout.addWidget(self.AvailableTagsList, 1, 3, 2, 1)
        self.Layout.addWidget(self.TemplateSeparator, 3, 0, 1, 4)
        self.TemplateLayout = QGridLayout()
        self.TemplateLayout.addWidget(self.TemplateLabel, 0, 0)
        self.TemplateLayout.addWidget(self.TemplateLineEdit, 0, 1)
        self.TemplateLayout.addWidget(self.RenameButton, 1, 0, 1, 2)
        self.TemplateLayout.setColumnStretch(1, 1)
        self.Layout.addLayout(self.TemplateLayout, 4, 0, 1, 4)

        # Set and Configure Layout
        self.Layout.setColumnStretch(0, 1)
        self.Layout.setColumnStretch(3, 1)
        self.Layout.setRowStretch(1, 1)
        self.Layout.setRowStretch(2, 1)
        self.Frame.setLayout(self.Layout)

        # Create Status Bar
        self.StatusBar = self.statusBar()

        # Set Central Frame
        self.setCentralWidget(self.Frame)

    def GetResourcePath(self, RelativeLocation):
        return self.AbsoluteDirectoryPath + "/" + RelativeLocation

    def AddToQueue(self):
        pass

    def ClearQueue(self):
        pass

    def Rename(self):
        pass

    # Interface Methods
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
