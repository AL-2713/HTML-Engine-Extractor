from engines import engineObj
import re
import json
import urllib.parse

# Each Stencyl game has its own .js file, inside it is a json string that contains all external assets
# Inside the json is also a libraryArgs key, if the key refrences a .pak file, only audio files are external assets. Everything else is in the .pak file

# Example 1 (Uses a .pak file): http://html-classic.itch.zone/html/7857160-763237/index.html
# Example 2 (Has images and other assets external, and no .pak file): http://html-classic.itch.zone/html/1738568/index.html

class stencyl(engineObj):
    
    ENGINE_NAME = "Stencyl"
    
    def validate(_parsedHtml, _embedUrl):
        return "lime.embed" in str(_parsedHtml)

    
    
    def scrape(_parsedHtml, _embedUrl):
        
        stencyl.iterateElement(_parsedHtml, "script", "src")
        
        mainJs = None
        
        # Needs to be grabbed form lime.embed ( instead
        if "lime.embed" in str(_parsedHtml):
            filesReg = re.findall('lime.embed \("(.*?)"', str(_parsedHtml))
            stencyl.addUrl(filesReg[0] + ".js")
            mainJs = filesReg[0] + ".js"
            stencyl.addUrl(mainJs)

        
        
        if mainJs:
            pakFileExists = False
            mainContents = stencyl.req.loadFile(stencyl.urlBase + mainJs)
            assetJson = re.search(".parse\('(.*?)'", mainContents)
            assetJson = assetJson.group().strip(".parse('").strip("'")
            parsed = json.loads(assetJson)
            
            if "libraryArgs" in parsed:
                for x in parsed['libraryArgs']:
                    if ".pak" in x:
                        pakFileExists = True
                        stencyl.addUrl(x)
            
            
            assetParts = parsed['assets'].split(":")
            for x in stencyl.commonFileTypes:
                for y in assetParts:
                    if x in y:
                        
                        # When a pak file is used, only audio files are external
                        if pakFileExists and x != ".mp3":
                            a=1
                        
                        else:
                            stencyl.addUrl(urllib.parse.unquote(y.split(x)[0] + x))
        
        return stencyl.assetArray