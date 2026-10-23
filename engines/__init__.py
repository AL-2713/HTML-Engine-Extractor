import importlib
import tinycss2
from urllib.parse import urlparse
from pathlib import Path

# Loads all the engine classes in the engine/ directory
class engineBase:
    
    engineNames = ["construct", "scratch", "renpy", "gamemaker", "rpgmaker", "unitywebgl", "gdevelop"]
    
    def __init__(self):
        self.engineContainer = {}
        self.initEngines()
    
    
    def initEngines(self):
        for x in self.engineNames:
            
            self.engineContainer[x] = getattr(importlib.import_module("engines." + x, package=None), x)



# The base for all engine classes. Includes global functions and vars
class engineObj:
    
    req = None
    assetArray = []
    
    def setReq(_req):
        engineObj.req = _req
    
    # Return the directory url of a file
    def getUrlBase(_embedUrl):
        urlPath = urlparse(_embedUrl)
        fileName = Path(urlPath.path).name
        
        if "." in fileName:
            return _embedUrl.replace(fileName, "")
        
        return _embedUrl + "/"

    # Add a url to the url array, to be returned after everything is extracted
    def addUrl(_assetUrl):
        if _assetUrl not in engineObj.assetArray:
            engineObj.assetArray.append(_assetUrl)
    
    
    # Find and extract all instances for img(*) in a css string
    def extractCssImages(_cssText):
        parsedStylesheet = tinycss2.parse_stylesheet(_cssText, True, True)
        cssImages = []
        for x in parsedStylesheet:
            for y in x.content:
                if type(y).__name__ == "FunctionBlock":
                    for z in y.arguments:
                        if type(z).__name__ == "StringToken":
                            cssImages.append(z.value)
        
        return cssImages