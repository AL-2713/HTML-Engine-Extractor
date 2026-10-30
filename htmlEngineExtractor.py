from enum import Enum
from engines import engineBase
from src.sRequests import s_requests
from src.sFileHandler import s_FileHandler
from src.sLogs import s_Logs

class exportOptions(Enum):
    save_txt = 0
    save_download = 1
    save_return = 2


class htmlEngineExtractor:
    
    def __init__(self, _exportOption = 2, _logLevel = 2):
        self.log = s_Logs(_logLevel)
        self.requestsBase = s_requests()
        self.fileHandler = s_FileHandler(self.requestsBase)
        
        self.determinedEngine = None
        self.exportOption = None
        
        self.initEngines()
        self.initExportOption(_exportOption)
        
        

    
    # Load the engines into engineContainer
    def initEngines(self):
        engineMod = engineBase(self.requestsBase)
        self.engineContainer = engineMod.engineContainer
        
        self.log.notify(f"Loaded {len(self.engineContainer)} engines")

    
    
    def initExportOption(self, _exportOption):
        self.exportOption = _exportOption
    
    
    
    
    # Main workflow for downloading a game
    def getGame(self, _embedUrl, _requestHeaders = {}):
        
        self.log.notify(f"Starting extraction for: {_embedUrl} !!!")

        self.requestsBase.setHeaders(_requestHeaders)
        self.assetsList = []
        
        parsedEmbed = self.requestsBase.loadEmbed(_embedUrl)
        
        for engineID, engineClass in self.engineContainer.items():
            isValid = engineClass.validate(parsedEmbed, _embedUrl)
            
            if isValid:
                self.determinedEngine = engineID
                self.log.notify("Determined engine type: " + engineClass.ENGINE_NAME)
                
                engineClass.resetAssetArray()
                engineClass.addUrl(_embedUrl)
                engineClass.setUrlBase(_embedUrl)
                engineClass.setLogger(self.log)
                self.assetsList = engineClass.scrape(parsedEmbed, _embedUrl)
                
                return self.saveAssets()
        
        self.log.error("The engine for this game could not be found, or is not supported")
    
    
    # Save the urls returned by the engine class, dependent on the selected exportOption (self.exportOption)
    def saveAssets(self):
        
        if not self.determinedEngine:
            self.log.error("The engine for this game could not be determined")
            return

        urlCount = str(len(self.assetsList))
        
        match(self.exportOption):
            
            # Save to txt list
            case 0:
                urlFileLocation = self.fileHandler.writeFilesToTxt(self.assetsList)
                self.log.notify(f"Exported {urlCount} file URLs to " + urlFileLocation)
            
            # Download
            case 1:
                self.log.notify(f"Downloading {urlCount} files..")
                downloadFolder = self.fileHandler.getDownloadIdentifier(self.assetsList[0]) + "/"
                
                for file in self.assetsList:
                    self.fileHandler.saveFile(file, downloadFolder)
            
            # Return
            case 2:
                return self.assetsList
    
    
    def testEngine(self, _engineID):
        engineTestUrls = self.fileHandler.loadFileList(_engineID)
        
        self.log.notify(f"Loaded {len(engineTestUrls)} urls for {_engineID}")
        
        for testUrl in engineTestUrls:
            self.getGame(testUrl)
        
