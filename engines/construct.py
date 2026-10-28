import json
import re
from bs4 import Comment
from engines import engineObj

# Example 1 (c2) (offline.js): http://html-classic.itch.zone/html/7339952/Spamton%20Goes%20To%20Driving%20School/index.html
# Example 2 (c3) (offline.json): http://html-classic.itch.zone/html/17129181/index.html
# Example 3 (c3 game with 3d models) https://app-625289.cdn.games.yandex.net/625289/xm180cp9b6stamxfm4sd0zzmbshkcqks/index.html
# Example 4 (c2 game without audio files referenced in index 7) https://html-classic.itch.zone/html/1563479/index.html


# Most of the time, Construct games will have an 'offline' file (as offline.js for Construct 2, or offline.json for Construct 3)
# This file contains all external file names in the 'fileList' key

# If the offline file doesn't exist, files can still be extracted from the games 'data' file. The file names are referenced but more nested in arrays



# TODO: 3d model textures need to be found within the 3d model file

class construct(engineObj):
    
    ENGINE_NAME = "Construct"
    
    constructScripts = ["c2runtime.js", "scripts/register-sw.js"]
    commonFileNames = ['sw.js', 'offlineClient.js']
    dataFiles = ['offline.json','offline.js','data.json','data.js']
    
    
    def validate(_parsedHtml, _embedUrl):
        
        constructCanvas = _parsedHtml.find("div",attrs={"id":"c2canvasdiv"})
        if constructCanvas:
            return True
        
        # Check if the construct runtime scripts are referenced in the html
        for x in construct.constructScripts:
            if x in str(_parsedHtml):
                return True
        
        comments = _parsedHtml.find_all(string=Comment)
        for x in comments:
            if "Made with Construct" in x:
                return True
        
        return False
    
    
    
    def scrape(_parsedHtml, _embedUrl):
                
        # link assets
        linkElems = _parsedHtml.findAll("link")
        for x in linkElems:
            if x.get("href"):
                construct.addUrl(x.get("href"))
        
        # Script assets
        scriptElems = _parsedHtml.findAll("script")
        for x in scriptElems:
            if x.get("src"):
                construct.addUrl(x.get("src"))
        
        
        # Appmanifest file references
        # Not working yet
        appManifestFile = construct.req.loadJson(construct.urlBase + "appmanifest.json")
        if appManifestFile:
            for appImg in appManifestFile['icons']:
                construct.addUrl(appImg['src'])
        
        
        # Common files
        for x in construct.commonFileNames:
            if construct.req.loadFile(construct.urlBase + x):
                construct.addUrl(x)
        
        
        # Find the file containing the external assets
        scraperFile = None
        for x in construct.dataFiles:
            fileContents = construct.req.loadFile(construct.urlBase + x)
            if fileContents:
                construct.addUrl(x)
            
            if fileContents and scraperFile == None:
                scraperFile = [x, fileContents]
        
        construct.extractScraperFile(scraperFile)

        return construct.assetArray
    
    
    
    
    
    
    # Determine which workflow to use for extracting assets from the data file
    def extractScraperFile(_scraperFile):
        if _scraperFile == None:
            return

        construct.log.notify("Got data file: " + _scraperFile[0])
        
        if _scraperFile[0][:7] == "offline":
            construct.offlineFileExtraction(_scraperFile)
        
        if _scraperFile[0][:4] == "data":
            construct.dataFileExtraction(_scraperFile)
            
            construct.extractConstruct3Scripts(_scraperFile)
    
    
    # If the game has an 'offline' file, extract all the files referenced in it
    def offlineFileExtraction(_scraperFile):
        offlineJson = json.loads(_scraperFile[1].encode())
        for x in offlineJson['fileList']:
            construct.addUrl(x)
    
    
    # If the game has a 'data' file, extract all files referenced in it
    def dataFileExtraction(_scraperFile):
        
        if _scraperFile[1][0] != "{":
            _scraperFile[1] = _scraperFile[1][1:]
        
        dataJson = json.loads(_scraperFile[1])['project']
        
        mediaDir = dataJson[8]
        
        
        
        # Loading logo
        if len(dataJson) >= 39:
            loadingLogo = dataJson[28] + dataJson[39] if "/" not in dataJson[39] else dataJson[39]
            construct.addUrl(loadingLogo)
        
        # Some files
        if len(dataJson) > 45 and type(dataJson[45]) is not str:
            for assetItem in dataJson[45]:
                construct.addUrl(assetItem['name'])
        
        # Audio reference
        if len(dataJson[7]) > 0:
            for audioObj in dataJson[7]:
                audioFile = mediaDir + audioObj[0]
                
                # Construct 2 jsons have the file extension on the file name
                if type(audioObj[1]) is int:
                    construct.addUrl(audioFile)
                
                # While Construct 3 has them listed separately
                else:
                    for audioExt in audioObj[1]:
                        construct.addUrl(audioFile + audioExt[1])
        
        
        # Some construct 2 games don't reference their audio files in the 7th index, instead they're nested in the 6th (Example 4)
        for x in dataJson[6]:
            construct.findOnDemandAudio(x[1], mediaDir)
        
        
        # 3D model reference
        if len(dataJson) >= 52:
            for x in dataJson[52]:
                construct.addUrl(f"3dmodels/{x[0]}.zip")
        
        # Fonts
        if len(dataJson) >= 32:
            fontsDir = dataJson[32]
            for x in dataJson[29]:
                construct.addUrl(fontsDir + x[1].lower())

        construct.imgArray(dataJson[3])

    
    # Loop through the 3rd index of the data.js / data.json file to extract image files
    def imgArray(_imgArray):
        for x in _imgArray:
            if "." in x[0]:
                construct.addUrl(x[0])
            
            if type(x[6]) is list:
                construct.addUrl(x[6][0])
            
            if type(x[7]).__name__ == "list":
                construct.imgArray(x[7])
    
    
    # Audio files are referenced in project index 6, some of which are not referenced in project index 7
    def findOnDemandAudio(_testDict, _mediaDir):
        if type(_testDict) is dict or list:
            for x in _testDict:
                
                # Find and add an audio file
                if type(x) is list and len(x) == 2 and type(x[0]) != list and type(x[1]) != list:
                    if type(x[0]) == str and type(x[1]) == bool:
                        construct.addUrl(_mediaDir + x[0] + ".ogg")
                        construct.addUrl(_mediaDir + x[0] + ".m4a")
                
                
                # This logic for the incremented audio files is very experimental and is only tested with example 4. Need more examples
                # Find and add an audio file with incrementing versions
                    """
                if type(x) == list and len(x) >= 2 and x[0] == 10 and type(x[1]) == list and type(x[1][1]) == str:
                    print(x)
                    iterate = 0
                    while iterate <= x[1][0]:
                        construct.addUrl(_mediaDir + x[1][1] + str(iterate + 1) + ".ogg")
                        construct.addUrl(_mediaDir + x[1][1] + str(iterate + 1) + ".m4a")
                        iterate += 1
                """
                
                # Loop
                elif type(x) is list:
                    construct.findOnDemandAudio(x, _mediaDir)
            
            
            
    
    
    # Find Construct 3 related files
    def extractConstruct3Scripts(_scraperFile):
        if _scraperFile[0].split(".")[1] == "json":
            construct.log.notify("is a construct 3 game")
        
        mainJs = None
        for x in construct.assetArray:
            if x[-7:] == "main.js":
                mainJs = x
        
        if mainJs:
            mainContent = construct.req.loadFile(mainJs)
            mainJsReg = re.findall('"[a-zA-Z0-9/.]*.js"', mainContent)
            mainJsUrlBase = construct.getUrlBase(mainJs)
            for regUrl in mainJsReg:
                if "scripts/" in regUrl:
                    regUrl = regUrl.split("scripts/")[-1]
                    
                construct.addUrl(mainJsUrlBase + regUrl.strip("/").strip('"'))
        
        
        # Check for c3main.js, and it's referenced runtime files
        for x in construct.assetArray:
            if "c3main.js" in x:
                cMainContent = construct.req.loadFile(x)
                mainContentBase = construct.getUrlBase(x)
                runtimeFiles = cMainContent.split('import "')
                for runtimeAsset in runtimeFiles:
                    formatedAsset = runtimeAsset.strip().strip('";')
                    if formatedAsset != "":
                        construct.addUrl(mainContentBase + formatedAsset)
        
        
        # Check if box2d.wasm should be added
        for x in construct.assetArray:
            if "box2d.wasm.js" in x:
                construct.addUrl(x[:-3])
                
