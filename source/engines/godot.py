from engines import engineObj
import json

# Example 1: https://html-classic.itch.zone/html/10877122/web/index.html
# Example 2 (Uses a gdextensionLib): https://html.itch.zone/html/17704595/index.html
# Example 3 (Uses a unique loadFile name): https://html-classic.itch.zone/html/7550065/itch/index.html

class godot(engineObj):
    
    ENGINE_NAME = "Godot"
    
    def validate(_parsedHtml, _embedUrl):
        if "GODOT_CONFIG" in str(_parsedHtml):
            return True

    
    
    def scrape(_parsedHtml, _embedUrl):
        
        # The global file name used for files, most often it's "index"
        loadFileName = None
        
        godot.iterateElement(_parsedHtml, "script", "src")
        godot.iterateElement(_parsedHtml, "link", "href")
        godot.iterateElement(_parsedHtml, "img", "src")
        
        
        if "GODOT_CONFIG = " in str(_parsedHtml):
            godotConfig = str(_parsedHtml).split("GODOT_CONFIG = ")[1].split(";")[0]
            configJson = json.loads(godotConfig)
            for fileName, fileSize in configJson['fileSizes'].items():
                
                if loadFileName == None:
                    loadFileName = fileName.split(".")[0]
                
                godot.addUrl(fileName)
            
            if "gdextensionLibs" in configJson:
                for x in configJson['gdextensionLibs']:
                    godot.addUrl(x)
        
        
        commonFiles = [".audio.position.worklet.js", ".audio.worklet.js", ".side.wasm"]
        
        for x in commonFiles:
            commonFileName = loadFileName + x
            if godot.req.fileExists(godot.urlBase + commonFileName):
                godot.addUrl(commonFileName)
            
        
        
        return godot.assetArray