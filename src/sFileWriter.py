import time
import os


class s_FileWriter:
    
    exportsDir = "exports/"
    
    
    # Create a directory if it doesn't exist
    def initDirectory(self, fileLocation):
        dirPath = fileLocation.rsplit("/")[0] + "/"
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
    
    
    # Write all urls to a text file
    def writeFilesToTxt(self, _urlArray):
        fileName = self.exportsDir + str(int(time.time())) + ".txt"
        self.initDirectory(fileName)
        
        with open(fileName, "a") as urlFile:
            for x in _urlArray:
                urlFile.write(x + "\n")
        
        return fileName