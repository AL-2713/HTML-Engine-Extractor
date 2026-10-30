# HTML-Engine-Extractor
Many webgames online are made with game engines to make developing them easier. Engines like Construct, Unity, Scratch, Gamemaker among dozens of others. The files exported by these engines are often loaded dynamically on runtime.

Inspired by [fpcurator](https://github.com/FlashpointProject/fpcurator), this library is made to make archival of these games easier, by finding and extracting all the file URLs the game uses!

# Usage
Download and extract all the source files to its own folder, you can then run **HEE_FE.py** to run the extractor<br>
The wrapper file HEE_FE.py can be ran from the command line (assuming you have python installed) via **python HEE_FE.py [EMBED_URL]**<br>
You can also write your own wrapper and run the extractor class from there

If the engine was verified and it extracts the urls, it will export the list of urls to a .txt file in the **exports/** directory

# Currently Supported Engines
These are the engines that can be extracted. Some support for these are still being tested
- Construct
- Scratch
- Ren'Py
- Unity WebGL
- GDevelop
- Defold
- Twine
- PICO-8
- Godot
- GameMaker
