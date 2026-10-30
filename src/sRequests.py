import time
import requests
import json
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings()

# Code: Handles all http requests, including parsing responses and validating if responses are successful

class s_requests:
    
    def __init__(self):
        self.headers = None
        
    
    
    def loadFile(self, _url, _params = {}, _decode = True):
        if _url[:4] != "http":
            print("NOT A VALID URL")
            return None


        if _params == {} and self.headers:
            _params = self.headers
        
        urlContent = None
        urlContent = requests.get(_url, verify=False, headers=_params)
        while urlContent == None:
            try:
                urlContent = requests.get(_url, verify=False, headers=_params)
            except:
                print(f"Error getting url: {_url}, waiting to retry...")
                time.sleep(20)
        
        if urlContent.status_code == 404:
            print("! 404 request: " + _url)
            return None
        
        if _decode:
            urlContent = urlContent.content.decode()
        
        return urlContent


    # Load and parse an html file
    def loadEmbed(self, _embedUrl):
        fileContent = self.loadFile(_embedUrl)
        parsedEmbed = BeautifulSoup(fileContent, 'html.parser')
        return parsedEmbed
    
    
    # Load and parse a json file
    def loadJson(self, _jsonUrl):
        fileContent = self.loadFile(_jsonUrl)
        
        try:
            return json.loads(fileContent)
        
        except:
            return None
    
    # Check if a file exists on the server
    def fileExists(self, _fileUrl):
        return requests.head(_fileUrl, verify=False).status_code == 200
    
    
    def setHeaders(self, _headers):
        self.headers = _headers
