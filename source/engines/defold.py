from engines import engineObj
import re

# Example 1 (refrences wasm files link elements and load() function) https://html-classic.itch.zone/html/19898628/Incremental%20Wars/index.html
# Example 2 (references exeName string in the path variable) https://html-classic.itch.zone/html/1476734/Unit%204/index.html
# Example 3 (example of a game without an exeName) https://html-classic.itch.zone/html/852219/default/__htmlLaunchDir/Type%20to%20Win/index.html

class defold(engineObj):
    
    ENGINE_NAME = "Defold"
    
    def validate(_parsedHtml, _embedUrl):
        engineLoader = _parsedHtml.find("script", attrs={"src":"dmloader.js"})
        return engineLoader

    
    
    def scrape(_parsedHtml, _embedUrl):
        foundExeName = None
        
        scriptFiles = _parsedHtml.findAll("script")
        for x in scriptFiles:
            if x.get("src"):
                defold.addUrl(x.get("src"))
        
        
        # Extract files from the archive_files.json file
        # This is where most external assets are referenced
        archiveFilesJson = "archive/archive_files.json"
        defold.addUrl(archiveFilesJson)
        
        jsonContent = defold.req.loadJson(defold.urlBase + archiveFilesJson)
        for fileEntry in jsonContent['content']:
            for fileName in fileEntry['pieces']:
                defold.addUrl("archive/" + fileName['name'])
        
        
        # Some exports of defold games reference their preloader assets in link elements
        # These files are also referenced in the dmloader.js file
        linkAssets = _parsedHtml.findAll("link")
        for x in linkAssets:
            if x.get("href"):
                defold.addUrl(x.get("href"))
                
                if not foundExeName and "wasm" in x.get("href"):
                    foundExeName = x.get("href").replace(".wasm", "").replace("_wasm.js", "")
        
        
        
        
        # Each game has a *.wasm and *_wasm.js file, with the asterisk being the exeName string
        # There are a few different places the exeName can be found in the game
        
        
        # Get the exeName variable from the load function, to get the wasm and wasm.js files
        if not foundExeName:
            exeNameReg = re.search("EngineLoader.load(.*?);", str(_parsedHtml))
            
            if exeNameReg:
                foundExeName = exeNameReg.group().split(", ")[1].split(")")[0].strip('"')
                defold.addUrl(foundExeName + "_wasm.js")
                defold.addUrl(foundExeName + ".wasm")
        
        
        # The exeName variable can also be referenced in a path variable
        if not foundExeName:
            pathReg = re.search('path = "(.*?)";', str(_parsedHtml))
            if pathReg:
                foundExeName = pathReg.group().split(" = ")[1].replace('.wasm";', "").strip('"')
                defold.addUrl(foundExeName + "_wasm.js")
                defold.addUrl(foundExeName + ".wasm")
        
        
        if not foundExeName:
            print("STILL LOOKING FOR exeName")
        
        
        # Some games have splash.png
        splashImgReg = re.search('splash_image: "(.*?)"', str(_parsedHtml))
        if splashImgReg:
            splashImgFileName = splashImgReg.group().split(":")[1].strip().strip('"')
            defold.addUrl(splashImgFileName)
        
        
        # Sometimes embeds have images in the css
        # try_game.png is referenced a lot, but doesn't always exist
        cssString = _parsedHtml.find("style").text
        for x in defold.extractCssImages(cssString):
            defold.addUrl(x)
        
        return defold.assetArray