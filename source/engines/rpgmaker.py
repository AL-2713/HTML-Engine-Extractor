import json
import re
from engines import engineObj

# Example 1: http://html-classic.itch.zone/html/8062890/www/index.html
# Example 2: https://html-classic.itch.zone/html/14285198/Awakened_Beauty_WEB_1.0.0/index.html
# Example 3 (Uses different file exts): https://html-classic.itch.zone/html/5701518/MistrickWEB/www/index.html
# Example 4: https://html-classic.itch.zone/html/11997169/www/index.html
# Example 5: https://html-classic.itch.zone/html/20218230/index.html

class rpgmaker(engineObj):
    
    ENGINE_NAME = "RPG Maker"
    
    ImageManagerFunctionTypes = ["load", "reserve", "request"]
    

    def validate(parsedHtml, embedUrl):
        scripts = parsedHtml.findAll("script")
        for x in scripts:
            if x.get("src") and "_core.js" in x.get("src"):
                return True
        
        bodyContent = parsedHtml.find("body").get("style")
        if bodyContent == "background-color: black":
            return True
        
        return False
    
    
    def scrape(_parsedHtml, _embedUrl):

        rpgmaker.encryptAudio = False
        rpgmaker.encryptImages = False
        rpgmaker.isMZ = False
        
        rpgmaker.iterateElement(_parsedHtml, "script", "src")
        rpgmaker.iterateElement(_parsedHtml, "link", "href")
        
        
        # plugins.js file will often be loaded in the main embed
        pluginUrl = rpgmaker.findRelativeUrl("plugins")
        
        
        # RPG Maker MZ stores its script URLs in main.js
        if not pluginUrl:
            mainJsUrl = rpgmaker.findRelativeUrl("main.js")
            mainJsContent = rpgmaker.req.loadFile(mainJsUrl)
            mainScripts = mainJsContent.split("scriptUrls = ")[1].split(";")[0]
            mainScriptsList = json.loads(mainScripts)
            for jsScript in mainScriptsList:
                rpgmaker.addUrl(rpgmaker.urlBase + jsScript)
                if "plugins" in jsScript:
                    pluginUrl = rpgmaker.urlBase + jsScript
            
            # If the scripts are referenced in the main.js file, the game will use a .wasm file
            if ".wasm" in mainJsContent:
                wasmReg = re.findall('"(.*?).wasm"', mainJsContent)
                if len(wasmReg) > 0:
                    rpgmaker.addUrl(wasmReg[0] + ".wasm")
            
            rpgmaker.isMZ = True


        if pluginUrl:
            managerUrl = rpgmaker.findRelativeUrl("_managers.js")
            managerContent = rpgmaker.req.loadFile(managerUrl)
            rpgmaker.initImgArray(managerContent)
            
            
            # Find the system json files and init System.json
            dataLocation = "data/"
            foundJsons = re.findall("src: '(.*?).json'", managerContent.replace('"',"'"))
            for x in foundJsons:
                jsonUrl = dataLocation + x + ".json"
                rpgmaker.addUrl(jsonUrl)
            
            rpgmaker.extractSystemJson()
            

            rpgmaker.loopImgFunctions(managerContent)
            rpgmaker.extractPlugins(pluginUrl)
            
            
            # Get loading image
            loadingImg = re.findall("setLoadingImage\('(.*?)'\)", managerContent)
            if len(loadingImg) >= 1:
                rpgmaker.addUrl(loadingImg[0])
                
        
        mapJsons = rpgmaker.initMaps()
            
        rpgmaker.extractRoomData(mapJsons)
            
        
        rpgmaker.loadActors()
        rpgmaker.extractCssFonts()
        
        rpgmaker.extractTilesetJson()
        rpgmaker.extractItemsJson()
        rpgmaker.extractCommonEvents()
    
        return rpgmaker.assetArray

    
    # =========
    # UTILITY FUNCTIONS
    # =========


    # Loop through the assets found for a keyword
    def findRelativeUrl(_keyword):
        for fileUrl in rpgmaker.assetArray:
            if _keyword in fileUrl:
                return fileUrl
    

    # Return the extension, given the file type
    # 0 = image
    # 1 = audio
    # 2 = video
    
    # Will return the encrypted file type if the setting is enabled in the games System.json file
    # Encrypted file types are different between "rpg" and "rmmz" versions, while "rmmz" adds "_" to the end of the extension, "rpg" uses a different type entirely
    def getExt(_extType):
        encryptedTypes = [[".rpgmvp",".png_"],
                          [".rpgmvo",".ogg_"],
                          [".webm", ".webm"],
                          [".rpgmvm",".m4a_"]] # Need confirmation
        
        versionEncryption = 1 if rpgmaker.isMZ else 0
        
        match(_extType):
            case 0:
                return ".png" if not rpgmaker.encryptImages else encryptedTypes[_extType][versionEncryption]
            
            case 1:
                return ".ogg" if not rpgmaker.encryptAudio else encryptedTypes[_extType][versionEncryption]
            
            case 2:
                return ".webm" # {"type":".m4a","encrypt":".rpgmvm"}
            
            # Need examples of games using m4a
            case 3:
                return "m4a" if not False else encryptedTypes[_extType][versionEncryption]
    
    
    
    # Image paths are defined in specific functions in the manager js file
    # Here were extract those paths from the functions and put them into a global dictionary for use later
    def initImgArray(_managerContent):
        imgFunctions = re.findall("ImageManager.([a-zA-Z0-9]+) = function\((.*?)\) { return this.loadBitmap\((.*?),", _managerContent.replace("\r","").replace("\n","").replace("    ", " "))

        rpgmaker.imgFuncArray = {}
        for func in imgFunctions:
            
            for type in rpgmaker.ImageManagerFunctionTypes:
                if type == func[0][:len(type)]:
                    rpgmaker.imgFuncArray[func[0][len(type):]] = func[2].strip("'").strip('"')
    
    
    
    
    # =========
    # EXTRACTION FUNCTIONS
    # =========
    
    
    
    # Find referenced plugin js files, and extract files from plugin settings when applicable
    def extractPlugins(_pluginJsUrl):
        rpgmaker.log.notify("Loading plugins")
        
        pluginsContent = rpgmaker.req.loadFile(_pluginJsUrl)
        pluginJson = pluginsContent.split("=", 1)[1].rsplit(";",1)[0].strip()
        pluginData = json.loads(pluginJson)
        for y in pluginData:
            pluginFileUrl = rpgmaker.getUrlBase(_pluginJsUrl) + "plugins/" + y['name'] + ".js"
            rpgmaker.addUrl(pluginFileUrl)
            
            # Individual plugins have their own files, and need to be implemented as more are found
            match(y['name']):
                
                case "LL_StandingPicture":
                    print(y['name'])
                
                case "CustomLogo":
                    print(y['name'])
                
                case "YEP_GridFreeDoodads":
                    doodadFolder = y['parameters']['Doodads Folder']
                    dodadJsonUrl = rpgmaker.urlBase + "data/Doodads.json"
                    rpgmaker.addUrl(dodadJsonUrl)
                    
                    doodadsData = rpgmaker.req.loadJson(dodadJsonUrl)
                    for doodadList in doodadsData:
                        if type(doodadList) == list:
                            for doodadEntry in doodadList:
                                rpgmaker.addUrl(doodadFolder + doodadEntry['bitmap'] + rpgmaker.getExt(0))
                
                case "KhasAdvancedLighting":
                    lightingFileData = rpgmaker.req.loadFile(pluginFileUrl)
                    lightAssets = re.findall('fileName: "(.*?)"', lightingFileData)
                    lightPath = re.findall('this.loadBitmap\("(.*?)",', lightingFileData)[0]
                    for lightAsset in lightAssets:
                        rpgmaker.addUrl(rpgmaker.urlBase + lightPath + lightAsset + rpgmaker.getExt(0))
                
                case "MOG_Footsteps":
                    rpgmaker.addUrl(rpgmaker.imgFuncArray['System'] + "FootStep.png")
                    rpgmaker.addUrl(rpgmaker.imgFuncArray['System'] + "WaterSplash.png")
                
                case "GALV_CursorImage":
                    rpgmaker.addUrl(rpgmaker.imgFuncArray['System'] + y['parameters']['Cursor Image'] + rpgmaker.getExt(0))
                
                case "GALV_VisualNovelChoices":
                    rpgmaker.addUrl(rpgmaker.imgFuncArray['System'] + "VNButtons.png")
                
                case "SRD_TimedAttackCore":
                    rpgmaker.addUrl("img/SumRndmDde/tas/" + y['parameters']['Background Image'] + rpgmaker.getExt(0))
                
                case "MOG_TitleParticles":
                    pi = 1
                    while pi <= 6:
                        particleFileName = y['parameters']['P1 File Name'] + str(pi) if pi > 1 else y['parameters']['P1 File Name']
                        rpgmaker.addUrl(rpgmaker.imgFuncArray['Title2'] + particleFileName + ".png")
                        pi += 1
                
                case "MOG_TitleLayers":
                    li = 0
                    while li <= 5:
                        rpgmaker.addUrl(rpgmaker.imgFuncArray['Title1'] + "Layer1_" + str(li) + ".png") # Could have more assets?
                        rpgmaker.addUrl(rpgmaker.imgFuncArray['Title1'] + "Layer" + str(li) + ".png")
                        li += 1
                
                case "GradientWipe":
                    for param, paramVal in y['parameters'].items():
                        if "Image" in param and paramVal != "":
                            rpgmaker.addUrl("img/transitions/" + paramVal + ".png")
                
                case "NonCombatMenu":
                    rpgmaker.addUrl(rpgmaker.imgFuncArray['Picture'] + y['parameters']['Background Image'] + ".png")
                
                
                
                case "YEP_X_ExtMesPack1":
                    rpgmaker.addUrl("audio/se/" + y['parameters']['Sound Name'] + ".ogg")
                
                case "YEP_FootstepSounds":
                    rpgmaker.addUrl("audio/se/" + y['parameters']['Default Sound'] + ".ogg")
                
                case "Nasty_Replace_Window_with_Picture":
                    i = 1
                    while i <= 16:
                        windowKey = f"Window {i} Picture Name"
                        if windowKey in y['parameters'] and y['parameters'][windowKey] != "":
                            rpgmaker.addUrl(rpgmaker.imgFuncArray['Picture'] + y['parameters'][windowKey] + ".png")
                
                case "Hendrix_Pictures_UI_Creator": # May be inaccurate
                    rpgmaker.addUrl("js/picturesPosition.json")
                    rpgmaker.addUrl("js/picturesMovePosition.json")
                    rpgmaker.addUrl("js/showTextPositions.json")
                
                case "AltWindowFrame":
                    rpgmaker.addUrl("img/system/Window_Talk" + rpgmaker.getExt(0))
                    rpgmaker.addUrl("img/system/Window_Battle" + rpgmaker.getExt(0))
                    rpgmaker.addUrl("img/system/Window_Status" + rpgmaker.getExt(0))
                    rpgmaker.addUrl("img/system/Window_Other" + rpgmaker.getExt(0))
                
                case "MOG_TitleCommands":
                    i = 0
                    while i <= 3:
                        rpgmaker.addUrl(rpgmaker.imgFuncArray['Title2'] + "Command_" + str(i) + rpgmaker.getExt(0))
                        i += 1
                
                
                case "GALV_MessageBackground":
                    if y['parameters']['Image Variable ID'] == "1":
                        y['parameters']['Image Variable ID'] = "0"
                    
                    rpgmaker.addUrl(rpgmaker.imgFuncArray['System'] + "msgimg_" + y['parameters']['Image Variable ID'] + ".png")
                
                case "GALV_MessageBackgroundMZ":
                    i = 0 # More ids may be possible
                    rpgmaker.addUrl(rpgmaker.imgFuncArray['System'] + "msgimg_" + str(i) + rpgmaker.getExt(0))
                    
    
    
    # Find all map jsons
    def initMaps():
        mapInfoUrl = rpgmaker.findRelativeUrl("MapInfos")
        mapData = rpgmaker.req.loadJson(mapInfoUrl)
        mapJsons = []
        for x in mapData:
            if x == None:
                continue
                
            mapId = str(x['id'])
            i = len(mapId)
                
            while i < 3:
                mapId = "0" + mapId
                i += 1
                
            mapJsonUrl = rpgmaker.urlBase + "data/Map" + mapId + ".json"
            rpgmaker.addUrl(mapJsonUrl)
            mapJsons.append(mapJsonUrl)
        
        return mapJsons

    
    
    # Finds uses of the image functions and extracts the filenames used
    def loopImgFunctions(_managerContent):
        rpgmaker.log.notify("Extracting image functions")

        for x in rpgmaker.assetArray:
            if x[-3:] == ".js" and "/plugins/" not in x:
                jsContent = rpgmaker.req.loadFile(x)

                for funcName,filePath in rpgmaker.imgFuncArray.items():
                    
                    for funcType in rpgmaker.ImageManagerFunctionTypes:
                        funcSearch = re.findall(f"ImageManager.{funcType + funcName}\((.*?)\)", jsContent)

                        for result in funcSearch:
                            rpgmaker.addUrl(rpgmaker.urlBase + filePath + result.strip("'").strip('"') + rpgmaker.getExt(0))
                            rpgmaker.addUrl(rpgmaker.urlBase + filePath + result.strip("'").strip('"') + ".png")
    
    
    # Find and extract face graphics in the actors json
    def loadActors():
        rpgmaker.log.notify("Loading actors")
        
        actorJsonUrl = rpgmaker.findRelativeUrl("Actors.json")
        
        characterDir = rpgmaker.imgFuncArray["Character"] # reserveCharacter
                
        # Get face path
        facePath = rpgmaker.imgFuncArray["Face"]
                
        # Load all possible face urls
        actorData = rpgmaker.req.loadJson(actorJsonUrl)
        for x in actorData:
            if x != None and "faceName" in x and x['faceName'] != "":
                rpgmaker.addUrl(rpgmaker.urlBase + facePath + x['faceName'] + rpgmaker.getExt(0))
            
            if x != None and "characterName" in x and x['characterName'] != "":
                rpgmaker.addUrl(rpgmaker.urlBase + characterDir + x['characterName'] + rpgmaker.getExt(0))
    
    
    # Find and extract audio / images referenced in the system json
    def extractSystemJson():
        systemJsonUrl = rpgmaker.findRelativeUrl("System.json")
        systemData = rpgmaker.req.loadJson(systemJsonUrl)


        # Initialize bools for file encryption
        rpgmaker.encryptAudio = "hasEncryptedAudio" in systemData and systemData['hasEncryptedAudio'] == True
        rpgmaker.encryptImages = "hasEncryptedImages" in systemData and systemData['hasEncryptedImages'] == True
        
            
        for sound in systemData['sounds']:
            if sound['name'] != "":
                rpgmaker.addUrl("audio/se/" + sound['name'] + rpgmaker.getExt(1))

        if "advanced" in systemData:
            if "numberFontFilename" in systemData['advanced']:
                rpgmaker.addUrl("fonts/" + systemData['advanced']['numberFontFilename'])
            
            if "mainFontFilename" in systemData['advanced']:
                rpgmaker.addUrl("fonts/" + systemData['advanced']['mainFontFilename'])
        
        for key, val in systemData.items():
            
            if type(val) == dict:
                if "bgm" in val and val['bgm']['name'] != "":
                    rpgmaker.addUrl("audio/bgm/" + val['bgm']['name'] + rpgmaker.getExt(1))
                
                if "characterName" in val and val['characterName'] != "":
                    rpgmaker.addUrl(rpgmaker.imgFuncArray['Character'] + val['characterName'] + rpgmaker.getExt(0))
                    
            match(key):
                
                case "titleBgm":
                    if systemData['titleBgm']['name'] != "":
                        rpgmaker.addUrl("audio/bgm/" + systemData['titleBgm']['name'] + rpgmaker.getExt(1))
                
                case "title1Name":
                    if systemData['title1Name'] != "":
                        title1Path = rpgmaker.imgFuncArray['Title1']
                        rpgmaker.addUrl(title1Path + systemData['title1Name'] + rpgmaker.getExt(0))
                
                case "title2Name":
                    if systemData['title2Name'] != "":
                        title1Path = rpgmaker.imgFuncArray['Title2']
                        rpgmaker.addUrl(title1Path + systemData['title2Name'] + rpgmaker.getExt(0))
                    
            
    
    # Extract image url from the tileset json
    def extractTilesetJson():
        tilesetJsonUrl = rpgmaker.findRelativeUrl("Tilesets")
        tilesetData = rpgmaker.req.loadJson(tilesetJsonUrl)
        tilesetImgPath = rpgmaker.imgFuncArray['Tileset']
        for entry in tilesetData:
            if type(entry) == dict:
                for tileName in entry['tilesetNames']:
                    if tileName != "":
                        rpgmaker.addUrl(rpgmaker.urlBase + tilesetImgPath + tileName + rpgmaker.getExt(0))
    
    
    
    # Find font files in the css file
    def extractCssFonts():
        for fileUrl in rpgmaker.assetArray:
            if ".css" in fileUrl:
                cssData = rpgmaker.req.loadFile(fileUrl)
                for cssFile in rpgmaker.extractCssImages(cssData):
                    rpgmaker.addUrl(rpgmaker.getUrlBase(fileUrl) + cssFile)
    
    
    # Find item graphics in the Items json
    def extractItemsJson():
        itemsUrl = rpgmaker.findRelativeUrl("Items")
        itemsData = rpgmaker.req.loadJson(itemsUrl)
        for x in itemsData:
            if type(x) is dict:
                graphic = re.findall("<name:(.*?)>", x['note'])
                if len(graphic) >= 1:
                    rpgmaker.addUrl("img/pictures/" + graphic[0] + rpgmaker.getExt(0))
    
    
    # Find and extract room related data from all room jsons
    # Data includes backgrounds, music, and character graphics
    def extractRoomData(_roomUrlArray):
        rpgmaker.log.notify("Extracting room data")
        
        for roomUrl in _roomUrlArray:
            roomData = rpgmaker.req.loadJson(roomUrl)
            
            # Parallax
            if roomData['parallaxName'] != "":
                rpgmaker.addUrl(rpgmaker.imgFuncArray['Parallax'] + roomData['parallaxName'] + rpgmaker.getExt(0))
            
            # BGM
            if "bgm" in roomData and roomData['bgm']['name'] != "":
                rpgmaker.addUrl("audio/bgm/" + roomData['bgm']['name'] + rpgmaker.getExt(1))
            
            # BGS
            if "bgs" in roomData and roomData['bgs']['name'] != "":
                rpgmaker.addUrl("audio/bgs/" + roomData['bgs']['name'] + rpgmaker.getExt(1))
            
            # Regex notes for layer images
            if "note" in roomData and roomData['note'] != "":
                layerReg = re.findall("[LAYER|LAYER_S] [0-9]+ (.*?) ", roomData['note'])
                for layerEntry in layerReg:
                    rpgmaker.addUrl("img/layers/" + layerEntry + rpgmaker.getExt(0))
                
                
            

            for event in roomData['events']:
                if type(event) == dict:
                    for page in event['pages']:
                        rpgmaker.addUrl(rpgmaker.imgFuncArray['Character'] + page['image']['characterName'] + rpgmaker.getExt(0))
                        
                        for list in page['list']:
                            rpgmaker.parseListObj(list)
                            
                            

    
    # Extract the list object in CommonEvents.json
    def extractCommonEvents():
        eventsJsonUrl = rpgmaker.findRelativeUrl("CommonEvents")
        eventData = rpgmaker.req.loadJson(eventsJsonUrl)
        for event in eventData:
            if type(event) is dict:
                for list in event['list']:
                    rpgmaker.parseListObj(list)
                
    
    
    
    # List objects contain in game events, some of which reference files to load
    # This function extract all possible file urls from a list
    def parseListObj(_list):
        
        # Some games like example 5 have nested lists (this appears in Map002.json)
        for x in _list['parameters']:
            if type(x) is dict and "parameters" in x:
                #print(x)
                rpgmaker.parseListObj(x)
        
        
        match(_list['code']):
                                
            # Character Sheets
            case 322:
                if _list['parameters'][1] != "":
                    rpgmaker.addUrl(rpgmaker.imgFuncArray['Character'] + _list['parameters'][1] + rpgmaker.getExt(0))
                                
            # Characters
            case 101:
                if _list['parameters'][0] != "":
                    rpgmaker.addUrl("img/faces/" + _list['parameters'][0] + rpgmaker.getExt(0))
                                        
                    charPicInt = _list['parameters'][1] + 1
                    while charPicInt > 0:
                        rpgmaker.addUrl("img/pictures/" + _list['parameters'][0] + "_" + str(charPicInt) + rpgmaker.getExt(0))
                        charPicInt -= 1
                                
            # Pics
            case 231:
                if _list['parameters'][1] != "":
                    rpgmaker.addUrl("img/pictures/" + _list['parameters'][1] + rpgmaker.getExt(0))
                                
            # SFX
            case 250 | 44:
                if _list['parameters'][0]['name'] != "":
                    rpgmaker.addUrl("audio/se/" + _list['parameters'][0]['name'] + rpgmaker.getExt(1))
                                
            # BGS
            case 245:
                if _list['parameters'][0]['name'] != "":
                    rpgmaker.addUrl("audio/bgs/" + _list['parameters'][0]['name'] + rpgmaker.getExt(1))
                                
            # BGM
            case 241:
                if _list['parameters'][0]['name'] != "":
                    rpgmaker.addUrl("audio/bgm/" + _list['parameters'][0]['name'] + rpgmaker.getExt(1))
                                
            # Video
            case 261:
                if _list['parameters'][0] != "":
                    rpgmaker.addUrl("movies/" + _list['parameters'][0] + rpgmaker.getExt(2))
                    rpgmaker.addUrl("movies/" + _list['parameters'][0] + ".mp4") # mp4 extensions are possible according to the rpg_objects.js function
                                
                                
            case 249:
                rpgmaker.addUrl(rpgmaker.urlBase + "audio/me/" + _list['parameters'][0]['name'] + rpgmaker.getExt(1))
            
            # EVAL
            case 355:
                # Regex logic
                videoReg = re.findall("startVideo\('(.*?)'", _list['parameters'][0])
                if len(videoReg) > 0:
                    rpgmaker.addUrl("movies/" + videoReg[0] + rpgmaker.getExt(2))
            
            
            # Plugin command
            case 357:                
                match(_list['parameters'][0]):
                    
                    case "GALV_LayerGraphicsMZ":
                        if type(_list['parameters'][3]) is dict and "graphic" in _list['parameters'][3]:
                            rpgmaker.addUrl("img/layers/" + _list['parameters'][3]['graphic'] + rpgmaker.getExt(0))
                    
                    case "CGMZ_ToastManager":
                        if type(_list['parameters'][3]) is dict and "SE" in _list['parameters'][3]:
                            seJson = json.loads(_list['parameters'][3]['SE'])
                            rpgmaker.addUrl("audio/se/" + seJson['Name'] + rpgmaker.getExt(1))
