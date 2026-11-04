from engines import engineObj
import re

# Example: https://embed.gsrca.de/p/rFVx/GZTGGNB/play.html
# Example 2 (Includes fonts and tables): https://embed.gsrca.de/p/9eLB/HE4DAMZ/play.html

# I've only seen examples from https://arcade.gamesalad.com, more sources would be nice

# All files are referenced in either object.json or assets.json
# object.json includes scene jsons (each being named a number, determined by the length of the "scenes" key) and tables (referenced in the "attributes" key, being named after an id)
# assets.json includes images, sounds and fonts file names. All being named after ascending numbers, accept fonts

class gamesalad(engineObj):
    
    ENGINE_NAME = "GameSalad"
    
    def validate(_parsedHtml, _embedUrl):
        for x in _parsedHtml.findAll("script"):
            if "gsStart(" in str(x):
                return True

    
    
    def scrape(_parsedHtml, _embedUrl):
        
        gamesalad.iterateElement(_parsedHtml, "link", "href")
        gamesalad.iterateElement(_parsedHtml, "script", "src")

        for x in gamesalad.extractCssImages(_parsedHtml.find("style").text):
            gamesalad.addUrl(x)
        
        
        gsStartFunction = re.search("gsStart((.*?));", str(_parsedHtml))
        if gsStartFunction:
            embedDomain = "http://" + gamesalad.getUrlDomain(gamesalad.urlBase)
            
            functionParams = gsStartFunction.group().split("(")[1].split(")")[0].split(",")
            gameRoot = functionParams[1].strip(" ").strip("'")
            gameRoot = embedDomain + gameRoot + "/"
            
            gamesalad.addUrl(gameRoot + "object.json")
            gamesalad.addUrl(gameRoot + "assets.json")
            
            # Get scene jsons
            objectJson = gamesalad.req.loadJson(gameRoot + "object.json")
            scene_i = 1
            while scene_i <= len(objectJson['scenes']):
                gamesalad.addUrl(gameRoot + "scenes/" + str(scene_i) + ".json")
                scene_i += 1
            
            # Get table jsons
            for key, val in objectJson['attributes'].items():
                if key[:2] == "id" and "@" in val and val['@'] == "table":
                    gamesalad.addUrl(gameRoot + "tables/" + key + ".json")
                
            
            
            # Get images / sounds
            assetsJson = gamesalad.req.loadJson(gameRoot + "assets.json")
            for key, val in assetsJson.items():
                
                match(type(val).__name__):
                    
                    case "list":
                        for assetObj in val:
                            gamesalad.extractAssetObj(assetObj, gameRoot, key)
                            
                    case "dict":
                        gamesalad.extractAssetObj(val, gameRoot, key)
                    

        return gamesalad.assetArray

    
    def extractAssetObj(_assetObj, _gameRoot, _key):
        
        match(type(_assetObj['files']).__name__):
            case "dict":
                gamesalad.addUrl(_gameRoot + _key + "/" + _assetObj['files']['name'])
            
            case "list":
                for subAsset in _assetObj['files']:
                    gamesalad.addUrl(_gameRoot + _key + "/" + subAsset['name'])
        
        
        