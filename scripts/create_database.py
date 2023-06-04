# Imports
import os

from helpers import create_homography_for_all_cards, calculate_features_for_all_cards
import database as Database

# Main
library_dir = "../user_library"
card_dirs = os.listdir(f"{library_dir}/unsorted_cards")

# THIS WILL RESET THE DATABASe
database = Database.Database(library_dir)
# THE ABOVE WILL RESET THE DATABASE

#database = Database.load()
database.refresh()
Database.save(database, library_dir)