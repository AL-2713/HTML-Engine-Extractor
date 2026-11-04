import json
from engines import engineObj

# Example: http://html-classic.itch.zone/html/8618172/Bullet%20Bunny/index.html

# The file data.js is where most external assets are referenced, under ['resources']['resources']. All javascript assets are in the html and script elements

class gdevelop(engineObj):
    
    ENGINE_NAME = "GDevelop"

    def validate(_parsedHtml, _embedUrl):
        
        for x in _parsedHtml.findAll("script"):
            if "gdjs.RuntimeGame" in x.text:
                return True
        
        return False
    
    
    def scrape(_parsedHtml, _embedUrl):
        baseUrl = gdevelop.getUrlBase(_embedUrl)
        
        for x in _parsedHtml.findAll("script"):
            if x.get("src"):
                gdevelop.addUrl(baseUrl + x.get("src"))
        
        
        for x in _parsedHtml.findAll("link"):
            if x.get("href"):
                gdevelop.addUrl(baseUrl + x.get("href"))
        
        # Extract files referenced in data.js
        dataJson = gdevelop.req.loadFile(baseUrl + "data.js").split("gdjs.projectData = ", 1)[1].split("gdjs.runtimeGameOptions",2)[0].strip().strip(";")
        parsedData = json.loads(dataJson)
        for asset in parsedData['resources']['resources']:
            gdevelop.addUrl(baseUrl + asset['file'])
        
        # Platform icons are referenced, but don't always exist on the server
        for platKey, platformIcon in parsedData['properties']['platformSpecificAssets'].items():
            gdevelop.addUrl(baseUrl + platformIcon)

        
        return gdevelop.assetArray
    
    