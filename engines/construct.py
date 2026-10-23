import json
from engines import engineObj

# Example 1 (c2) (offline.js): http://html-classic.itch.zone/html/7339952/Spamton%20Goes%20To%20Driving%20School/index.html
# Example 1 (c3) (offline.json): http://html-classic.itch.zone/html/17129181/index.html

# Most of the time, Construct games will have an 'offline' file (as offline.js for Construct 2, or offline.json for Construct 3)
# This file contains all external file names in the 'fileList' key

# If the offline file doesn't exist, files can still be extracted from the games 'data' file. The file names are referenced but more nested in arrays

class construct(engineObj):
    
    ENGINE_NAME = "Construct"
    
    constructScripts = ["c2runtime.js", "scripts/register-sw.js"]
    commonFileNames = ['sw.js', 'offlineClient.js']
    dataFiles = ['offline.json','offline.js','data.json','data.js']
    
    
    def validate(_parsedHtml, _embedUrl):
        
        # Check if the construct runtime scripts are referenced in the html
        jsScriptCheck = _parsedHtml.find_all("script")
        for x in jsScriptCheck:
            if x.get("src") and x.get("src") in construct.constructScripts:
                return True
        
        return False
    
    
    def scrape(_parsedHtml, _embedUrl):
        baseUrl = construct.getUrlBase(_embedUrl)
        
        # link assets
        linkElems = _parsedHtml.findAll("link")
        for x in linkElems:
            if x.get("href"):
                construct.addUrl(baseUrl + x.get("href"))
        
        # Script assets
        scriptElems = _parsedHtml.findAll("script")
        for x in scriptElems:
            if x.get("src"):
                construct.addUrl(baseUrl + x.get("src"))
        
        
        # Appmanifest file references
        # Not working yet
        appManifestFile = construct.req.loadJson(baseUrl + "appmanifest.json")
        if appManifestFile:
            for appImg in appManifestFile['icons']:
                construct.addUrl(baseUrl + appImg['src'])
        
        
        # Common files
        for x in construct.commonFileNames:
            if construct.req.loadFile(baseUrl + x):
                construct.addUrl(baseUrl + x)
        
        
        # Find the file containing the external assets
        scraperFile = None
        for x in construct.dataFiles:
            fileContents = construct.req.loadFile(baseUrl + x)
            if fileContents:
                construct.addUrl(baseUrl + x)
            
            if fileContents and scraperFile == None:
                scraperFile = [x, fileContents]
        
        construct.extractScraperFile(scraperFile, baseUrl)
        
        return construct.assetArray
    
    
    # Determine which workflow to use for extracting assets from the data file
    def extractScraperFile(_scraperFile, _baseUrl):
        if _scraperFile == None:
            return

        print("- Got data file: " + _scraperFile[0])
        
        if _scraperFile[0][:7] == "offline":
            construct.offlineFileExtraction(_scraperFile, _baseUrl)
        
        if _scraperFile[0][:4] == "data":
            construct.dataFileExtraction(_scraperFile, _baseUrl)
    
    
    # If the game has an 'offline' file, extract all the files referenced in it
    def offlineFileExtraction(_scraperFile, _baseUrl):
        offlineJson = json.loads(_scraperFile[1].encode())
        for x in offlineJson['fileList']:
            construct.addUrl(_baseUrl + x)
    
    
    # If the game has a 'data' file, extract all files referenced in it
    def dataFileExtraction(_scraperFile, _baseUrl):
        fileTypes = ['.png','.jpg','.otf','.webp']
        mediaTypes = ['.ogg','.m4a','.web','.webm']
        
        dataJson = json.loads(_scraperFile[1])['project']
        
        mediaDir = dataJson[8]
        
        # Loading logo
        if dataJson[28] and dataJson[39]:
            loadingLogo = dataJson[28] + dataJson[39] if "/" not in dataJson[39] else dataJson[39]
            construct.addUrl(_baseUrl + loadingLogo)
        
        # Some files
        if len(dataJson) > 45:
            for assetItem in dataJson[45]:
                construct.addUrl(_baseUrl + assetItem['name'])
        
        # Audio reference
        if dataJson[7]:
            for audioObj in dataJson[7]:
                construct.addUrl(_baseUrl + mediaDir + audioObj[0] + audioObj[1][0][1])
        
        construct.imgArray(dataJson[3], _baseUrl)
    
    
    # Loop through the 3rd index of the data.js / data.json file to extract image files
    def imgArray(_imgArray, _baseUrl):
        for x in _imgArray:
            if "." in x[0]:
                construct.addUrl(_baseUrl + x[0])
            
            if type(x[7]).__name__ == "list":
                construct.imgArray(x[7], _baseUrl)
        