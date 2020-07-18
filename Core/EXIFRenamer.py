from PIL import Image, ExifTags


class EXIFRenamer:
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
                AdditionData = {"Path": Addition, "ExifData": AdditionExifData}
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

    def Clear(self):
        self.RenameQueue.clear()
        self.AvailableTags.clear()
