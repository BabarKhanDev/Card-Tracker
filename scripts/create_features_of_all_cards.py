# This script downloads every card and creates the feature vector for it

# Import required libraries
import os
import pickle
from tqdm import tqdm

import requests
import io
import torch
from torchvision import transforms
from PIL import Image

from helpers import extract_features, create_model_and_preprocess

# Set up environment
cache_dir = "../tcg_cache"
model, preprocess = create_model_and_preprocess()

# First loop through our cached sets
sets = os.listdir(f"{cache_dir}/card_data")

for set in tqdm(sets):

    # make a directory for the set if it doesn't exist
    if not os.path.exists(os.path.join(os.getcwd(), f"{cache_dir}\\features", set[:-4])):
        os.makedirs(f"{cache_dir}/features/{set[:-4]}")

    # open the cached set details
    with open(f"{cache_dir}/card_data/{set}", "rb") as file:
        set_details = pickle.load(file)
    
    # Get the relevant details for each card in the set
    cards = [{"image_url":card.images.large, "name":card.number} for card in set_details]

    # Loop through each card and create a feature vector for it
    for card in cards:

        # Check if the card already has extracted features
        if card["name"] == "?":
            name = "unknown"
        else:
            name = card["name"]

        path = f"../tcg_cache/features/{set[:-4]}/{name}.pkl"
        
        if os.path.exists(path): continue

        # If we dont already have the features:
        # Get the url and download the image as a PIL object
        image_url = card["image_url"]
        response = requests.get(image_url)
        image_data = response.content
        image = Image.open(io.BytesIO(image_data)).convert('RGB')

        # Create feature vector and save it
        extract_features(model, preprocess, path, image)