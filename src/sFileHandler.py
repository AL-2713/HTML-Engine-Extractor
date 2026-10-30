import time
import os


class s_FileHandler:
    
    exportsDir = "exports/"
    engineTestListPath = "engines/testLists/"
    
    def __init__(self, _req):
        self.req = _req
    
    
    
    def getDownloadIdentifier(self, _fileUrl):
        domain = _fileUrl.split("://")[1].split("/")[0]
        timeStamp = str(int(time.time()))
        return domain + "_" + timeStamp
    
    
    # Create a directory if it doesn't exist
    def initDirectory(self, fileLocation):
        dirPath = fileLocation.rsplit("/", 1)[0] + "/"
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
    
    
    # Write all urls to a text file
    def writeFilesToTxt(self, _urlArray):
        fileName = self.exportsDir + self.getDownloadIdentifier(_urlArray[0]) + ".txt"
        self.initDirectory(fileName)
        
        with open(fileName, "a") as urlFile:
            for x in _urlArray:
                urlFile.write(x + "\n")
        
        return fileName

    
    # Load a file in the engine test lists directory
    def loadFileList(self, _engineID):
        engineTestFile = self.engineTestListPath + _engineID + ".txt"
        urlList = []
        if os.path.isfile(engineTestFile):
            with open(engineTestFile) as testList:
                for line in testList:
                    urlList.append(line.strip())
        
        return urlList
    
    
    # Download a file from a url and save it with its url structure
    def saveFile(self, _fileUrl, _downloadFolder):
        fileContent = self.req.loadFile(_fileUrl, self.req.headers, False)
        
        if fileContent == None:
            return
        
        filePath = self.exportsDir + _downloadFolder + _fileUrl.split("://")[1]
        self.initDirectory(filePath)
        
        with open(filePath, "wb") as savedFile:
            savedFile.write(fileContent.content)
