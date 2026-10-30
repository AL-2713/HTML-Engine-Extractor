import re
from engines import engineObj

# Example 1: http://html-classic.itch.zone/html/19772479/index.html
# Example 2: http://html-classic.itch.zone/html/1418191-733102/Vapor%20Trails/index.html
# Example 3: http://html-classic.itch.zone/html/9497817/index.html

# Some games request more assets from a directory defined as streamingAssetsUrl, these cannot be extracted here

class unitywebgl(engineObj):
    
    ENGINE_NAME = "Unity WebGL"
    
    file_vars = ["dataUrl", "wasmCodeUrl", "wasmFrameworkUrl", "codeUrl", "frameworkUrl"]
    
    
    def validate(parsedHtml, embedUrl):
        if parsedHtml.find("canvas", attrs={"id":"unity-canvas"}) or parsedHtml.find("div", attrs={"id":"unity-container"}) or parsedHtml.find("div", attrs={"id":"unityContainer"}):
            return True

        for x in parsedHtml.findAll("script"):
            if x.get("src") and "UnityLoader" in x.get("src"):
                return True
        
        return False
    
    
    def scrape(_parsedHtml, _embedUrl):
        
        # Embed link elements
        for linkElem in _parsedHtml.findAll("link"):
            if linkElem.get("href"):
                unitywebgl.addUrl(linkElem.get("href"))
        
        
        # Stylesheet images
        stylesheetElem = _parsedHtml.find("link", attrs={"rel":"stylesheet"})
        if stylesheetElem:
            stylesheetUrl = unitywebgl.urlBase + stylesheetElem.get("href")
            stylesheetContents = unitywebgl.req.loadFile(stylesheetUrl)
            stylesheetLocation = unitywebgl.getUrlBase(stylesheetUrl)
            for x in unitywebgl.extractCssImages(stylesheetContents):
                unitywebgl.addUrl(stylesheetLocation + x)
        
        
        # Embed scripts
        scripts = _parsedHtml.findAll("script")
        for x in scripts:
            
            if x.get("src") and "http:" not in x.get("src") and "https:" not in x.get("src"):
                unitywebgl.addUrl(x.get("src"))
            
            
            # Some embeds store their instance data in a seperate json file (Example 2)
            # Here we extract the json path from the javascript, then parse the json to get the referenced files
            elif "UnityLoader.instantiate" in x.text:
                instVals = x.text.split('.instantiate(')[1].split(");")[0].split(",")
                jsonFile = unitywebgl.urlBase + instVals[1].replace('"',"").strip()
                unitywebgl.addUrl(jsonFile)
                
                instanceContent = unitywebgl.req.loadJson(jsonFile)
                jsonUrlBase = unitywebgl.getUrlBase(jsonFile)
                for instKey, instVal in instanceContent.items():
                    if instKey in unitywebgl.file_vars:
                        unitywebgl.addUrl(jsonUrlBase + instVal)
            
            
            
            # Other embeds store the instance data in a script element (Example 1)
            elif "dataUrl" in x.text:
                buildUrlVal = unitywebgl.regJavascriptVar(x.text, "buildUrl")
                
                loaderUrlVar = unitywebgl.regJavascriptVar(x.text, "loaderUrl")
                if loaderUrlVar:
                    loaderUrlVar = loaderUrlVar.replace('buildUrl + "', buildUrlVal).strip('"')
                    unitywebgl.addUrl(loaderUrlVar)
                
                # maybe regex can extract it
                for configVar in unitywebgl.file_vars:
                    val = unitywebgl.regJavascriptDict(x.text, configVar)
                    if val:
                        configUrlPath = val.replace('buildUrl + "', buildUrlVal).strip('"')
                        unitywebgl.addUrl(configUrlPath)
                    
        
        return unitywebgl.assetArray
                        
                
                
        
    def regJavascriptDict(_javascript, var):
        regSearch = re.search(var + ': [^,]*', _javascript)
        if regSearch:
            return regSearch.group().split(var + ": ",1)[1]
    
    def regJavascriptVar(_javascript, var):
        regSearch = re.search(var + ' = [^;]*', _javascript)
        if regSearch:
            return regSearch.group().split("= ")[1].strip('"')
        
        return ""
        
        
                    
        
