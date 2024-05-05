﻿# Card Tracker
I'm building this app because I'm unsatisfied with existing card tracking solutions. 
I want to be able to take photos of my cards and have them tracked automatically. 
I also want to be able to take photos of a binder of cards and have that uploaded automatically.

# How it works
You place photos of the cards in the directory /cards. 
Right now cards need to be on a plain background.
The app then uses a homography to warp the image so that the card fills a 300x400 box.
The warped image is then passed into a VGG16 feature extractor and the feature is pickled and saved. 
We compare these features to see if the cards are the same.

# Setup
Create config file and insert api key, you can get this from [pokemontcg.io](https://pokemontcg.io/)
```bash
cp config.ini.example config.ini
```

# Running without docker
```bash
python3 -m venv venv
. venv/bin/activate (linux) or ./venv/Scripts/activate (win)
pip install -r requirements.txt
python3 setup.py
flask run
```

# Running with Docker

```bash
docker compose up -d --build
```

# TODO
1. Use a proper database instead of a python list
2. Add the ability to resolve false positive matches
3. Add the ability to resolve false negative matches
4. Add the ability to scan an nxm binder page in, it should automatically split the binder image into n*m separate images
