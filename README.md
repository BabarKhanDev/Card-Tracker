# Card Tracker
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

# Running

```bash
docker compose up -d --build
```

# TODO
- [x] Allow users to view cards
- [x] Allow users to wishlist cards
- [ ] Allow users to scan their cards in
  
The code for this exists, I need to hook it into the front end
- [ ] Allow users to resolve false negative/positive matches
- [ ] Allow users to scan a binder of cards in
