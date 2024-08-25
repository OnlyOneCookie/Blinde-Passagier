# Blindä Passagier
## Demo Website
- You can find the demo which is the visualization of the backend logic here: https://bernhackt24.web.app
- **IMPORTANT NOTE:** You need to wait while you enter the station's name, since that searchbox is not optimized on speed. Have some patience.
- Use the example "Lausanne" as the station and track 4 to 6.

## Before we start
### What you need to do
- SwissPass
- [Python >v3.10](https://www.python.org/downloads/release/python-3100/)
- [SBB Developer Account](https://developer.sbb.ch/home)
- [SBB Journey Maps API Key](https://developer.sbb.ch/apis/journey-maps/information)
- [Node.js v20.17.0](https://github.com/nodejs/node/tree/v20.17.0)

## Structure
### Code
Anything that has to do with code is within this very folder.  
Keep as well in mind that we do have multiple versions of the project since we started with a small PoC in Python, moved on with Flask and ended with Angular.

### Documentation
Any artifact in form of a documentation is within this folder.

### Presentation
Any artifact in form of a presentation (PowerPoint, PDF, Video) is within this folder.

### Misc
Anything else which is needed in this repository will be here.

## How to use
### Python
1. `python -m venv .venv`
2. `source .venv/bin/activate` (UNIX)  
`.venv/Scripts/Activate.ps1` (Windows)  
3. `cd code/backend`
4. `pip install -r requirements.txt`  
5. `python poc.py API_KEY` (Proof of Concept)  
6. `python app.py API_KEY` (Flask)  

### Angular
1. `cd code/web`
2. `npm install`
3. `ng serve` 
