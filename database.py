from helpers import create_model_and_preprocess, extract_features, match_with_all_cards
import os
import torch

class Database:
    def __init__(self):
        # This is a list of all the paths of cards that are in the database
        self.sorted_cards = []
        self.card_groups = {}   # This will store a mapping of card to group, multiple instances of the same card will be in the same group

    def add_new_cards(self):
        model, preprocess = create_model_and_preprocess()
        
        for card_dir in os.listdir("cards"):
            # dont re-add an existing card
            if card_dir in self.sorted_cards:
                continue
            
            # look through all cards in card database and create a list of the matches sorted by loss
            # store the best 3 matches 

            features = extract_features(model, preprocess, f"homography_cards/{card_dir}")
            matches = match_with_all_cards(features)

            print(card_dir)
            print(matches)

            self.card_groups[card_dir] = matches
            self.sorted_cards.append(card_dir)