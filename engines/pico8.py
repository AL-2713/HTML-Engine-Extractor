from engines import engineObj
import re

# Example https://html-classic.itch.zone/html/3799305/ufo_html/index.html

# PICO-8 games are only made up of 1 js file (a cartridge)

class pico8(engineObj):
    
    ENGINE_NAME = "PICO-8"
    
    def validate(_parsedHtml, _embedUrl):
        isPico = _parsedHtml.find("title").text == "PICO-8 Cartridge"
        
        if not isPico:
            isPico = "p8_run_cart" in str(_parsedHtml)
        
        return isPico

    
    
    def scrape(_parsedHtml, _embedUrl):
        cartReg = re.findall('src = "(.*?)";', str(_parsedHtml))
        if cartReg:
            pico8.addUrl(cartReg[0])
        
        return pico8.assetArray