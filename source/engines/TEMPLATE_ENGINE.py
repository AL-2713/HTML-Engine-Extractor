from engines import engineObj

class TEMPLATE_ENGINE(engineObj):
    
    ENGINE_NAME = "EXAMPLE"
    
    def validate(_parsedHtml, _embedUrl):
        print("This function determines if the embed uses this engine, and returns True if it is the engine")

    
    
    def scrape(_parsedHtml, _embedUrl):
        print("This function goes through specific logic to extract all the files the game uses, and returns an array of urls")
        
        return TEMPLATE_ENGINE.assetArray