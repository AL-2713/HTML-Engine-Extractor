from htmlEngineExtractor import htmlEngineExtractor as HEE
import sys
import os
import json

class HEE_FE:
    
    
    def __init__(self):
        self.hee = HEE(0)
        self.headers = {}
        
        self.setHeaders()

        if len(sys.argv) >= 2:
            self.cmdUrlInput()
        
        else:
            self.inputUrl()
    
    
    # If the user made headers.txt in the root of the directory, try and load it as a headers json
    def setHeaders(self):
        if os.path.isfile("headers.txt"):
            try:
                self.headers = json.loads(open("headers.txt").read())
            
            except:
                print("Could not load headers")
        
    
    
    # Prompt the user to input their embed url if it wasn't sent in the command
    def inputUrl(self):
        self.validUrl = False
        
        
        while not self.validUrl:
            self.embedUrl = input("Input the embed URL: ")
            self.validUrl = self.embedUrl[:4] == "http"


        self.hee.getGame(self.embedUrl, self.headers)
    
    
    def cmdUrlInput(self):
        
        # Test an engine via: HEE_FE.py test (engineID)
        if sys.argv[1] == "test":
            engineId = input("Input the engineID to test: ")
            self.hee.testEngine(engineId)
        
        # Load a game url via: HEE_FE.py (engineUrl)
        else:
            self.hee.getGame(sys.argv[1], self.headers)


HEE_FE()
