from enum import Enum
from engines import engineBase
from src.sRequests import s_requests
from src.sFileWriter import s_FileWriter


class exportOptions(Enum):
    save_txt = 0
    save_download = 1
    save_return = 2


class htmlEngineExtractor:
    
    def __init__(self, _exportOption = 2):
        self.requestsBase = s_requests()
        self.fileWriter = s_FileWriter()
        self.assetsList = []
        self.determinedEngine = None
        self.exportOption = None
        
        self.initEngines()
        self.initExportOption(_exportOption)
        
        

    
    # Load the engines into engineContainer
    def initEngines(self):
        engineMod = engineBase()
        self.engineContainer = engineMod.engineContainer
        
        for x in self.engineContainer:
            print(f"! Loaded {self.engineContainer[x].ENGINE_NAME}")
            self.engineContainer[x].setReq(self.requestsBase)
        
        print(f"Loaded {len(self.engineContainer)} engines")

    
    def initExportOption(self, _exportOption):
        self.exportOption = _exportOption
    
    
    
    
    # Main workflow for downloading a game
    def getGame(self, _embedUrl):
        parsedEmbed = self.requestsBase.loadEmbed(_embedUrl)
        
        for engineID, engineClass in self.engineContainer.items():
            isValid = engineClass.validate(parsedEmbed, _embedUrl)
            
            if isValid:
                self.determinedEngine = engineID
                print("Determined engine type: " + engineClass.ENGINE_NAME)
                
                engineClass.addUrl(_embedUrl)
                engineClass.setUrlBase(_embedUrl)
                self.assetsList = engineClass.scrape(parsedEmbed, _embedUrl)
                
                return self.saveAssets()
        
        print("! The engine for this game could not be found, or is not supported")
    
    
    
    def saveAssets(self):
        
        if not self.determinedEngine:
            print("! The engine for this game could not be determined")
            return

        urlCount = str(len(self.assetsList))
        
        match(self.exportOption):
            case 0:
                urlFileLocation = self.fileWriter.writeFilesToTxt(self.assetsList)
                print(f"! Exported {urlCount} file URLs to " + urlFileLocation)
            
            case 1:
                print("downlaod")
            
            case 2:
                return self.assetsList
