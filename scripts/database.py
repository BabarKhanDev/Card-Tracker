import os
import pickle

from PIL import Image
import torch
from tqdm import tqdm

from helpers import create_model_and_preprocess, match_with_all_cards, create_homography_for_all_cards


class Database:
    def __init__(self, library_dir):
        # This is a list of all the paths of cards that are in the database
        self.library_dir = library_dir
        self.sorted_cards = []
        self.card_groups = {}   # This will store a mapping of card to group, multiple instances of the same card will be in the same group

    def refresh(self):
        # Set up environment
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, preprocess = create_model_and_preprocess()
        model = model.to(device)

        # Create a homography of all cards and save to disk
        create_homography_for_all_cards(self.library_dir)
        
        # Loop through all cards and find their best matches
        for card_dir in tqdm(os.listdir(f"{self.library_dir}/unsorted_cards")):
            
            # dont re-add an existing card
            if card_dir in self.sorted_cards:
                continue
            
            # Create a feature vector for this card and save to disk
            image = Image.open(f"{self.library_dir}/homography_cards/{card_dir}").convert('RGB')
            batch = preprocess(image).unsqueeze(0).to(device)
            features = model(batch).squeeze(0)
            del batch
            with open(f"{self.library_dir}/features/{card_dir[:-4]}.pkl", "wb") as file:
                pickle.dump(features, file)

            # Calculate the best matches
            matches = match_with_all_cards(features)

            self.card_groups[card_dir] = matches
            self.sorted_cards.append(card_dir)
        
def load(library_dir):
    with open(f"{library_dir}/card_database.pkl", "rb") as file:
        return pickle.load(file)
    
def save(database, library_dir):
    with open(f"{library_dir}/card_database.pkl", "wb") as file:
        pickle.dump(database, file)