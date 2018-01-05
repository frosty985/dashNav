# dashNav
Using python-can to connect to Audi DIS

roadInfo.py 
uses GPSD to get location and speed, downloads info from http://overpass-api.de and writes to a temp file

canSend.py
takes temp file and sends to the DIS

tracker.py
takes location and speed from GPS and creates a googleearth kml file
