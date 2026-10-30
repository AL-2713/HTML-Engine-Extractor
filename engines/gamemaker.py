import json
import re
from bs4 import BeautifulSoup
from engines import engineObj

# Example: http://html-classic.itch.zone/html/14797852/index.html
# Example 2: https://html-classic.itch.zone/html/6086484/index.html
# Example 3 (Alternative format): https://html-classic.itch.zone/html/19191432/index.html


# External files are all referenced in the games main javascript file (they all have unique names based on the game title)
# The file names are in a javascript object around the top (most are somewhat obsufcated)
# Sounds are referenced without their file extension (this is always .ogg), and image sheets are in a single array with their file extensions (always .png)
# Particle images are not referenced in the javascript object, instead loaded via a function looping through all the possible file names (IDR_GIF_[1-15].png)
# Some games also have external js files referenced near the start of the js object

# Other games like example 3 Store their data in dat / wasm / unx files, and are referenced in a manifestFiles() function

class gamemaker(engineObj):
    
    ENGINE_NAME = "GameMaker"
    
    
    def validate(parsedHtml, embedUrl):
        scripts = parsedHtml.findAll("script")
        for x in scripts:
            if "GameMaker_Init" in x.text:
                return True

        if "manifestFiles()" in str(parsedHtml) and "GM_pause" in str(parsedHtml):
            return True
        
        return False
    
    
    def scrape(_parsedHtml, _embedUrl):
        
        
        gamemaker.iterateElement(_parsedHtml, "script", "src")
        gamemaker.iterateElement(_parsedHtml, "img", "src")
        
        mainJs = None
        if "<!-- Run the game code -->" in str(_parsedHtml):
            mainJs = str(_parsedHtml).split("<!-- Run the game code -->")[1].split("</script>")[0] + "</script>"
            mainJsElement = BeautifulSoup(mainJs, 'html.parser')
            mainJs = mainJsElement.find("script").get("src")
        
        
        if mainJs:
            mainJsContent = gamemaker.req.loadFile(gamemaker.urlBase + mainJs)
            mainJsJson = "{" + mainJsContent.split("Array.prototype")[1].split("{", 1)[1].split("};")[0] + "}"
            
            # The root of external files
            fileDir = mainJs.split("/")[0] + "/"
            
            
            
            # Images
            images = re.findall('"(.*?).png"', mainJsJson)
            for img in images:
                gamemaker.addUrl(fileDir + img + ".png")
            
            # Sounds / JS files
            for soundString in re.findall('"(.*?)"', mainJsJson.split("audiogroup_default")[0]):
                if soundString != "":
                    
                    if ".js" not in soundString:
                        soundString += ".ogg"
                    
                    gamemaker.addUrl(fileDir + soundString)
            
            # Particles
            if gamemaker.req.fileExists(gamemaker.urlBase + fileDir + "particles/IDR_GIF1.png"):
                idr_i = 1
                while idr_i < 16:
                    gamemaker.addUrl(f"{fileDir}particles/IDR_GIF{idr_i}.png")
                    idr_i += 1
        
        
        if "manifestFiles()" in str(_parsedHtml):
            files = "[" + str(_parsedHtml).split("manifestFiles()")[1].split(".join")[0].split("[")[1]
            for file in json.loads(files):
                gamemaker.addUrl(file)
            
            
                    
        return gamemaker.assetArray
