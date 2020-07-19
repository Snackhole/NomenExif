import os
from PIL import Image, ExifTags


class ExifRenamer:
    def __init__(self):
        self.RenameQueue = []
        self.AvailableTags = set()

    def AddToRenameQueue(self, Additions):
        for Addition in Additions:
            if Addition.endswith(".jpg") or Addition.endswith(".jpeg"):
                try:
                    OpenedAddition = Image.open(Addition)
                    AdditionExifData = {ExifTags.TAGS[NumericTag]: TagContents for NumericTag, TagContents in OpenedAddition._getexif().items() if NumericTag in ExifTags.TAGS}
                except:
                    return False
                AdditionData = {"Path": os.path.abspath(Addition), "ExifData": AdditionExifData}
                self.RenameQueue.append(AdditionData)
        self.DetermineAvailableTags()

    def DetermineAvailableTags(self):
        self.AvailableTags.clear()
        for QueuedFile in self.RenameQueue:
            QueuedFileTags = QueuedFile["ExifData"].keys()
            for QueuedFileTag in QueuedFileTags:
                self.AvailableTags.add(QueuedFileTag)
        for QueuedFile in self.RenameQueue:
            QueuedFileTags = QueuedFile["ExifData"].keys()
            for ExtantTag in self.AvailableTags:
                if ExtantTag not in QueuedFileTags:
                    self.AvailableTags.remove(ExtantTag)
        if "DateTimeOriginal" in self.AvailableTags:
            self.AvailableTags.add("YEAR")
            self.AvailableTags.add("MONTH")
            self.AvailableTags.add("DAY")
            self.AvailableTags.add("HOUR")
            self.AvailableTags.add("MINUTE")
            self.AvailableTags.add("SECOND")

    def Clear(self):
        self.RenameQueue.clear()
        self.AvailableTags.clear()

    def GenerateFileName(self, ExifData, Template):
        FileName = Template
        if "DateTimeOriginal" in self.AvailableTags:
            Year = str(ExifData["DateTimeOriginal"])[0:4]
            Month = str(ExifData["DateTimeOriginal"])[5:7]
            Day = str(ExifData["DateTimeOriginal"])[8:10]
            Hour = str(ExifData["DateTimeOriginal"])[11:13]
            Minute = str(ExifData["DateTimeOriginal"])[14:16]
            Second = str(ExifData["DateTimeOriginal"])[17:19]
            FileName = FileName.replace("[YEAR]", Year)
            FileName = FileName.replace("[MONTH]", Month)
            FileName = FileName.replace("[DAY]", Day)
            FileName = FileName.replace("[HOUR]", Hour)
            FileName = FileName.replace("[MINUTE]", Minute)
            FileName = FileName.replace("[SECOND]", Second)
        for Tag in self.AvailableTags:
            FileName = FileName.replace("[" + Tag + "]", str(ExifData[Tag]))
        return FileName

    def RenameFilesWithTemplate(self, Template):
        for QueuedFile in self.RenameQueue:
            NewName = self.GenerateFileName(QueuedFile["ExifData"], Template)


# if __name__ == "__main__":
#     Renamer = ExifRenamer()
#     Files = [File for File in os.listdir(".") if File.endswith(".jpg") and File != "test.jpg"]
#     Renamer.AddToRenameQueue(Files)
#     Renamer.RenameFilesWithTemplate("[YEAR].[MONTH].[DAY] - [HOUR].[MINUTE].[SECOND]")