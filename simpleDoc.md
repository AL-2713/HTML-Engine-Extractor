# Html-Engine-Extractor Docs

## htmlEngineExtractor
class <strong>htmlEngineExtractor</strong>(int _exportOption = 2, int _logLevel = 2)

Loading the class loads all the basic functions and engine classes needed for the extractor to work</br>
- _exportOption: Determines how the class will save urls it extracts from the URL you request:
    - 0: Saves the extracted URLs to a list, inside "exports/"
    - 1: Download the extracted URLs to the "exports/" folder
    - 2: Returns the array of URLs after running the getGame function

- _logLevel: Specifies what messages to print in the console while running. Different levels will output different messages
    - 0: No messages will be logged
    - 1: Only error messages are logged
    - 2: Errors and notifications are logged
</br>

def <strong>getGame</strong>(string _embedUrl, dict _requestHeaders = {})

Initiates the extraction of the game URLs. It first goes through each engine class and runs the **verify** function to confirm what game engine the game uses. If the engine is determined, it will run the **scrape** function for that engine and save the URLs, else no other actions are done.

- _embedUrl: The HTTP URL for the game embed you want to extract. To clarify, it's not the webpage the game is played on, for example "https://barribob.itch.io/golem-quest", it is the embeded html file that runs the game "https://html-classic.itch.zone/html/20026559/index.html". The scripts do not handle extraction of game embeds from webpages.

- _requestHeaders: A parsed dictionary of headers to be sent for any URL request.
</br>

def <strong>testEngine</strong>(string _engineID)

Runs through several embed URLs to extract all at once. This is intended for testing of specific engines to confirm if any engines run into errors while extracting.</br>
URL lists are stored in a text file under **engines/testLists/** as a .txt file named after the engineID

- _engineID: The engineID of which to run the URL test. If and engineID is given that does not exist or doesn't have a .txt file setup, nothing will happen
</br>
