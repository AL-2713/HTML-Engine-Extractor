from bs4 import Comment
from engines import engineObj

class scratch(engineObj):
    
    ENGINE_NAME = "Scratch"
    
    valid_exporter_comments = ["PenguinMod-Packager", "packager.turbowarp.org"]
        
    
    def validate(parsedHtml, embedUrl):
        for comment in parsedHtml.findAll(string=Comment):
            for engineComment in scratch.valid_exporter_comments:
                if engineComment in comment:
                    return True
    
    
    
    # If a project.json file is not found, it's possible the entire game is in the index.html
    def scrape(_parsedHtml, _embedUrl):
        urlBase = scratch.getUrlBase(_embedUrl)
        assetsUrl = urlBase + "assets/"
        projectFile = scratch.req.loadJson(assetsUrl + "project.json")
        
        
        if projectFile:
            
            scratch.addUrl(assetsUrl + "project.json")
            scratch.addUrl(assetsUrl + "script.js")
            
            for x in projectFile['targets']:
                
                for soundObj in x['sounds']:
                    scratch.addUrl(assetsUrl + soundObj['md5ext'])
                
                for costumeObj in x['costumes']:
                    scratch.addUrl(assetsUrl + costumeObj['md5ext'])
            
            if "customFonts" in projectFile:
                for fontObj in projectFile['customFonts']:
                    if "md5ext" in fontObj:
                        scratch.addUrl(assetsUrl + fontObj['md5ext'])
        
        return scratch.assetArray