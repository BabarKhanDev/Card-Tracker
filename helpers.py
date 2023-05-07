import os
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import random
import pickle

from torchvision.models import vgg16, VGG16_Weights
from torchvision import transforms
from PIL import Image
import torch

image_scale = 0.02

# Edge Detection
def detect_edges(img):
    global image_scale

    img = cv.resize(img, dsize = (9,0), fx=image_scale, fy=image_scale, interpolation=cv.INTER_CUBIC)
    img_blur = cv.GaussianBlur(img, (3,3), 0)

    # Sobel Edge Detection
    sobelx = cv.Sobel(src=img_blur, ddepth=cv.CV_64F, dx=1, dy=0, ksize=5) # Sobel Edge Detection on the X axis
    sobely = cv.Sobel(src=img_blur, ddepth=cv.CV_64F, dx=0, dy=1, ksize=5) # Sobel Edge Detection on the Y axis
    sobelxy = cv.Sobel(src=img_blur, ddepth=cv.CV_64F, dx=1, dy=1, ksize=5) # Combined X and Y Sobel Edge Detection
    # Display Sobel Edge Detection Images

    edges = cv.Canny(image=img_blur, threshold1=80, threshold2=80) # Canny Edge Detection
    # Display Canny Edge Detection Image

    return img, edges

def corners_from_edges(edges):
    edge_coords = []

    for i, row in enumerate(edges):
        for j, pixel in enumerate(row):
            if pixel > 100:
                edge_coords.append((j, i))

    # calculate the corners of the image
    max_x = max(x for x, _ in edge_coords)
    max_y = max(x for _, x in edge_coords)
    min_x = min(x for x, _ in edge_coords)
    min_y = min(x for _, x in edge_coords)

    return max_x, max_y, min_x, min_y

# Compute homography and return rescaled image
def compute_homography(max_x, max_y, min_x, min_y, img):
    
    global image_scale

    max_x /= image_scale
    max_y /= image_scale
    min_x /= image_scale
    min_y /= image_scale

    H, W, _ = img.shape

    pts_src = np.array([(max_x , max_y), (max_x, min_y), (min_x, max_y), (min_x, min_y)])
    pts_dst = np.array([(W, H), (W, 0), (0, H), (0,0)])
    h, _ = cv.findHomography(pts_src, pts_dst)
    im_dst = cv.warpPerspective(img, h, (W,H))

    return im_dst

def create_homography_for_all_cards(card_dirs):
    for card_dir in card_dirs:
        if os.path.exists(f"homography_cards/{card_dir}"):
            continue

        img = cv.imread(f"cards/{card_dir}")
        _, edges = detect_edges(img)
        max_x, max_y, min_x, min_y = corners_from_edges(edges)

        card_homography = compute_homography(max_x, max_y, min_x, min_y, img)
        card_homography = cv.resize(card_homography, (300, 400), card_homography, interpolation=cv.INTER_AREA)
        cv.imwrite(f"homography_cards/{card_dir}", card_homography)

def extract_features(model,preprocess, path):

    # Process image
    image = Image.open(f"homography_cards/{path}")
    batch = preprocess(image).unsqueeze(0)

    # Calculate Features
    features = model(batch).squeeze(0)
    return features

def create_model_and_preprocess():

    # Create Model
    weights = VGG16_Weights.IMAGENET1K_V1
    model = vgg16(weights=weights)
    model.eval()
    model.classifier = model.classifier[0]

    # Create inference transforms
    preprocess = transforms.Compose([
        weights.transforms()
    ])

    return model, preprocess

def calculate_features_for_all_cards(card_dirs):

    model, preprocess = create_model_and_preprocess()

    for card_dir in card_dirs:
        if os.path.exists(f"features/{card_dir[:-4]}.pkl"):
            continue

        features = extract_features(model, preprocess, card_dir)
        with open(f"features/{card_dir[:-4]}.pkl", "wb") as file:
            pickle.dump(features, file)

def find_closest_match(features, existing_cards):
    loss_func = torch.nn.MSELoss(reduction = "mean")
    matches = []

    for path in existing_cards:

        with open(f"features/{path[:-4]}.pkl", "rb") as file:
            other_features = pickle.load(file)

        loss = loss_func(other_features, features)
        matches.append((path, loss.item()))
        
    return matches

def load_database():
    with open("card_database.pkl", "rb") as file:
        return pickle.load(file)

def save_database(database):
    with open("card_database.pkl", "wb") as file:
        pickle.dump(database, file)
