import os
import pickle
import torch
from PIL import Image
from tqdm import tqdm
from helpers import create_model_and_preprocess, match_with_all_cards, create_homography_for_all_cards

'''
The Database Class will store the details of the cards that a user owns
initialise a database with a library_dir, this will be where cards are stored.
unsorted cards are stored in library_dir/unsorted_cards, the Database class will search here for new cards,
once a classification is predicted the card will be moved into library_dir/homography_cards

There are two functions, load(library_dir) and save(database, library_dir)
Load: given a library directory, load the saved database
Save: given a database and a library_dir, pickle the database and store it in the library directory
'''


class Database:
    def __init__(self, library_dir: str) -> None:

        # This is a list of all the paths of cards that are in the database
        self.library_dir = library_dir
        self.sorted_cards = []

        # This will store a mapping of card to group, multiple instances of the same card will be in the same group
        self.card_groups = {}

    #  This method will add new cards to the database
    #  Currently it uses a feature vector comparison, this is slow and will be changed to a different model
    def refresh(self) -> None:

        # Set up environment
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, preprocess = create_model_and_preprocess()
        model = model.to(device)

        # Create a homography of all cards and save to disk
        create_homography_for_all_cards(self.library_dir)

        # Loop through all cards and find their best matches
        for card_dir in tqdm(os.listdir(f"{self.library_dir}/unsorted_cards")):

            # don't re-add an existing card
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


def load(library_dir: str) -> Database:
    with open(f"{library_dir}/card_database.pkl", "rb") as file:
        return pickle.load(file)


def save(database: Database, library_dir: str) -> None:
    with open(f"{library_dir}/card_database.pkl", "wb") as file:
        pickle.dump(database, file)
