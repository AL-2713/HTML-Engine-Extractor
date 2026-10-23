import zipfile
import io
from engines import engineObj

# Example: http://html-classic.itch.zone/html/19307243/index.html


# Games will reference their external files in the gameZip file (often game.zip)
# Inside the zip is 'game/renpyweb_remote_files.txt' where every other line references a file path
# If the referenced file is an image, it would be (image path) \n (image - x,y). whereas audio files are formated as (audio path) \n (music -)

class renpy(engineObj):
    
    ENGINE_NAME = "Ren'Py"
    
    
    def validate(parsedHtml, embedUrl):
        scripts = parsedHtml.findAll("script")
        for x in scripts:
            if x.get("src") and "renpy" in x.get("src"):
                return True
        
        
        return False
    
    
    def scrape(_parsedHtml, _embedUrl):
        urlBase = renpy.getUrlBase(_embedUrl)
        
        # Get manifest and images referenced in it
        manifestUrl = urlBase + "manifest.json"
        manifestJson = renpy.req.loadJson(manifestUrl)
        if manifestJson:
            renpy.addUrl(manifestUrl)
            for ico in manifestJson['icons']:
                renpy.addUrl(urlBase + ico['src'])
        
        # Get splashscreen
        imgs = _parsedHtml.findAll("img")
        for imgElem in imgs:
            if imgElem.get("src"):
                renpy.addUrl(urlBase + imgElem['src'])
        
        # Get scripts
        scripts = _parsedHtml.findAll("script")
        for x in scripts:
            if x.get("src") and "http" not in x.get("src"):
                renpy.addUrl(urlBase + x.get('src'))
        
        
        # Get game.zip and its files it requests
        zipFileUrl = urlBase + "game.zip"
        renpy.addUrl(zipFileUrl)
        gameZipContent = renpy.req.loadFile(zipFileUrl, {"stream":True}, False)
        zipFile = zipfile.ZipFile(io.BytesIO(gameZipContent.content))
        with zipFile.open("game/renpyweb_remote_files.txt") as assetList:
            lines = assetList.read().decode().split("\n")
            for x in lines:
                if "/" in x:
                    renpy.addUrl(urlBase + "game/" + x)
                

        
        return renpy.assetArray