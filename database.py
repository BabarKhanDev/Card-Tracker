from helpers import create_model_and_preprocess, extract_features, find_closest_match
import os

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
            
            # look through all cards in sorted cards and find any matches
            # if no matches then we create a new group
            # otherwise we use the group of the match

            features = extract_features(model, preprocess, f"homography_cards/{card_dir}")
            matches = [match for match in find_closest_match(features, self.sorted_cards) if match[1] < 1.3]
            matches.sort(key = lambda x: x[1])

            if len(matches) == 0: # No matches
                self.card_groups[card_dir] = len(set(self.card_groups.values()))
            else: # There is a match
                best_match = matches[0][0]
                match_group = self.card_groups[best_match]
                self.card_groups[card_dir] = match_group

            self.sorted_cards.append(card_dir)