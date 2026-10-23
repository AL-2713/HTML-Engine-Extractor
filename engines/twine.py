from engines import engineObj
import re

# Example 1 (Simple example without any external files) https://html-classic.itch.zone/html/2766663/index.html
# Example 2 (Requests several mp3 and png assets) https://html-classic.itch.zone/html/19652379/index.html

class twine(engineObj):
    
    ENGINE_NAME = "Twine"
    
    def validate(_parsedHtml, _embedUrl):
        isTwine = _parsedHtml.find("script", attrs={"id":"twine-user-script"})
        
        if not isTwine:
            isTwine = _parsedHtml.find("style", attrs={"title":"Twine CSS"})
        
        if not isTwine:
            isTwine = _parsedHtml.find("style", attrs={"id":"script-sugarcube"})
        
        if not isTwine:
            isTwine = "Twine.image" in str(_parsedHtml)
        
        
        return isTwine

    
    
    def scrape(_parsedHtml, _embedUrl):
        resourceReg = '"(.*?)[$"]'
        resourceRegAlt = "'(.*?)[$']"
        
        regResult = re.findall(resourceReg, str(_parsedHtml))
        regResultAlt = re.findall(resourceRegAlt, str(_parsedHtml))
        resourceMain = regResult + regResultAlt
        
        for item in resourceMain:
            if any(x in item for x in twine.commonFileTypes) and "base64," not in item:
                twine.addUrl(item)
        
        return twine.assetArray