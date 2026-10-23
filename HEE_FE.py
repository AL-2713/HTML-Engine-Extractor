from htmlEngineExtractor import htmlEngineExtractor as HEE
import sys

class HEE_FE:
    
    
    def __init__(self):
        self.hee = HEE(0)

        if len(sys.argv) >= 2:
            self.cmdUrlInput()
        
        else:
            self.inputUrl()
        
        
    
    
    # Prompt the user to input their embed url if it wasn't sent in the command
    def inputUrl(self):
        self.validUrl = False
        
        while not self.validUrl:
            self.embedUrl = input("Input the embed URL: ")
            self.validUrl = self.embedUrl[:4] == "http"

        
        self.hee.getGame(self.embedUrl)
    
    
    def cmdUrlInput(self):
        self.hee.getGame(sys.argv[1])


HEE_FE()