import importlib
import tinycss2
from urllib.parse import urlparse, quote
from pathlib import Path

# Loads all the engine classes in the engine/ directory
class engineBase:
        
    def __init__(self, _req):
        self.engineContainer = {}
        self.engineListFile = "engines/engineIds.txt"
        self.req = _req
        self.initEngines()
    
    
    def initEngines(self):
        engineslist = open(self.engineListFile).read().split("\n")
        
        for engineId in engineslist:
            self.engineContainer[engineId] = getattr(importlib.import_module("engines." + engineId, package=None), engineId)
            self.engineContainer[engineId].setReq(self.req)



# The base for all engine classes. Includes global functions and vars
class engineObj:
    
    req = None
    urlBase = ""
    assetArray = []
    commonFileTypes = [".gif", ".png", ".webp", ".jpg", ".mp3", ".wav", ".ogg", ".m4a", ".webm", "otf", "ttf"]
    urlSafeChars = "/:"
    
    def setReq(_req):
        engineObj.req = _req
    
    def setUrlBase(_embedUrl):
        engineObj.urlBase = engineObj.getUrlBase(_embedUrl)
    
    def setLogger(_logger):
        engineObj.log = _logger
    
    def resetAssetArray():
        engineObj.assetArray = []
    
    
    # Return the directory url of a file
    def getUrlBase(_embedUrl):
        if "?" in _embedUrl:
            _embedUrl = _embedUrl.rsplit("?")[0]
        
        urlPath = urlparse(_embedUrl)
        fileName = Path(urlPath.path).name
        
        if "." in fileName:
            return _embedUrl.replace(fileName, "")
        
        return _embedUrl + "/"


    # Add a url to the url array, to be returned after everything is extracted
    def addUrl(_assetUrl):
        fullUrl = engineObj.urlBase + _assetUrl
        if _assetUrl in engineObj.assetArray or fullUrl in engineObj.assetArray:
            return

        # Append the url to the array if it's a full url
        if "://" in _assetUrl:
            engineObj.assetArray.append(quote(_assetUrl, engineObj.urlSafeChars))
        
        # If not a full url and it's a relative path, append the urlBase to the path
        else:
            engineObj.assetArray.append(quote(fullUrl, engineObj.urlSafeChars))
            
    
    
    # Find and extract all instances for img(*) in a css string
    def extractCssImages(_cssText):
        cssImageTypes = [".png", ".jpg", ".gif"]
        parsedStylesheet = tinycss2.parse_stylesheet(_cssText, True, True)
        cssImages = []
        for x in parsedStylesheet:
            for y in x.content:
                if type(y).__name__ == "FunctionBlock":
                    for z in y.arguments:
                        if type(z).__name__ == "StringToken" and any(x in z.value for x in cssImageTypes):
                            cssImages.append(z.value)
        
        return cssImages
