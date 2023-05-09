import os
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import random
from sklearn import linear_model
import pickle
pickle.DEFAULT_PROTOCOL = 5

from tqdm import tqdm
from time import perf_counter

from torchvision.models import vgg16, VGG16_Weights
from torchvision import transforms
from PIL import Image
import torch

image_scale = 0.2

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

# Using ransac we get the card corners
def corners_from_edges(edges):
    global image_scale
    ransac = linear_model.RANSACRegressor()

    # Find the points along the right edge
    right_col  = []
    left_col   = []
    bottom_row = []
    top_row    = []

    for i, row in enumerate(edges):
        # Find all white pixel points
        points = [(i,j) for j, pixel in enumerate(row) if pixel > 200]
        if len(points) == 0:
            continue

        # Organise by largest to smallest
        points.sort(key=lambda x: x[1], reverse=True)   
        right_col.append(points[0])
        left_col.append(points[-1])
    
    for j, row in enumerate(edges.T):
        # Find all white pixel points
        points = [(i,j) for i, pixel in enumerate(row) if pixel > 200]
        if len(points) == 0:
            continue

        # Organise by largest to smallest
        points.sort(key=lambda x: x[1], reverse=True)   
        top_row.append(points[0])
        bottom_row.append(points[-1])

    # Arrange points for each side
    right_X,  right_y   = np.array([x/image_scale for _, x in right_col ]).reshape(-1, 1), np.array([y/image_scale for y,_ in right_col ]).reshape(-1, 1)
    left_X,   left_y    = np.array([x/image_scale for _, x in left_col  ]).reshape(-1, 1), np.array([y/image_scale for y,_ in left_col  ]).reshape(-1, 1)
    bottom_X, bottom_y  = np.array([x/image_scale for _, x in bottom_row]).reshape(-1, 1), np.array([y/image_scale for y,_ in bottom_row]).reshape(-1, 1)
    top_X,    top_y     = np.array([x/image_scale for _, x in top_row   ]).reshape(-1, 1), np.array([y/image_scale for y,_ in top_row   ]).reshape(-1, 1)

    # Compute ransac for Right edge #
    ransac.fit(right_y, right_X)
    right_coef      = 1 / ransac.estimator_.coef_
    right_intercept = -1 * ransac.estimator_.intercept_ / ransac.estimator_.coef_

    # Compute ransac for left edge #
    ransac.fit(left_y, left_X)
    left_coef = 1 / ransac.estimator_.coef_
    left_intercept = -1 * ransac.estimator_.intercept_ / ransac.estimator_.coef_

    # Compute ransac for bottom edge #
    ransac.fit(bottom_X, bottom_y)
    bottom_coef = ransac.estimator_.coef_
    bottom_intercept = ransac.estimator_.intercept_

    # Compute ransac for top edge #
    ransac.fit(top_X, top_y)
    top_coef = ransac.estimator_.coef_
    top_intercept = ransac.estimator_.intercept_

    # Calculate corner location estimates
    top_right_x = (right_intercept - top_intercept) / (top_coef - right_coef)
    top_right_y = top_coef * top_right_x + top_intercept

    top_left_x = (left_intercept - top_intercept) / (top_coef - left_coef)
    top_left_y = top_coef * top_left_x + top_intercept

    bottom_right_x = (right_intercept - bottom_intercept) / (bottom_coef - right_coef)
    bottom_right_y = bottom_coef * bottom_right_x + bottom_intercept

    bottom_left_x = (left_intercept - bottom_intercept) / (bottom_coef - left_coef)
    bottom_left_y = bottom_coef * bottom_left_x + bottom_intercept
    return np.array([
            (round(bottom_right_x.item()),round(bottom_right_y.item())),
            (round(top_right_x.item()), round(top_right_y.item())),
            (round(bottom_left_x.item()),round(bottom_left_y.item())),
            (round(top_left_x.item()), round(top_left_y.item()))
        ])

# Compute homography and return rescaled image
def compute_homography(pts_src, img):

    H, W, _ = img.shape

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
        pts_src = corners_from_edges(edges)

        card_homography = compute_homography(pts_src, img)
        card_homography = cv.resize(card_homography, (300, 400), card_homography, interpolation=cv.INTER_AREA)
        cv.imwrite(f"homography_cards/{card_dir}", card_homography)

def extract_features(model,preprocess, path):

    card_dir = path.split("/")[1:]
    if os.path.exists(f"features/{card_dir[:-4]}.pkl"):
        with open(f"features/{card_dir[:-4]}.pkl", "rb") as file:
            return pickle.load(file)

    # Process image
    image = Image.open(path).convert('RGB')
    batch = preprocess(image).unsqueeze(0)

    # Move to device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    batch, model = batch.to(device), model.to(device)
    
    # Calculate Features
    features = model(batch).squeeze(0)
    del batch
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

        features = extract_features(model, preprocess, f"homography_cards/{card_dir}")
        with open(f"features/{card_dir[:-4]}.pkl", "wb") as file:
            pickle.dump(features, file)

def find_closest_match(features, existing_cards):
    loss_func = torch.nn.MSELoss(reduction = "mean")
    matches = []
    device = "cuda" if torch.cuda.is_available() else "cpu"

    for path in existing_cards:

        with open(f"features/{path[:-4]}.pkl", "rb") as file:
            other_features = pickle.load(file)

        loss = loss_func(other_features.to(device), features.to(device))
        matches.append((path, loss.item()))
        
    return matches

def match_with_all_cards(features):

    loss_func = torch.nn.MSELoss(reduction = "mean")
    matches = np.empty((0,3), dtype=str)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    features = features.to(device)

    sets = os.listdir("card_db/features")
    
    loading_feature_time = 0
    calc_loss_time = 0
    match_adding_time = 0

    for set in tqdm(sets):

        feature_dirs = os.listdir(f"card_db/features/{set}")
        for other_features_dir in feature_dirs:
            
            # Load the other cards features
            load_features_start = perf_counter()
            with open(f"card_db/features/{set}/{other_features_dir}", "rb") as file:
                other_features = pickle.load(file)
            load_features_end = perf_counter()
            loading_feature_time += load_features_end - load_features_start

            # Compare the other card with this one
            loss_calc_start = perf_counter()
            loss = loss_func(features, other_features.to(device))
            loss = loss.item()
            loss_calc_end = perf_counter()
            calc_loss_time += loss_calc_end - loss_calc_start

            # If they are a good match then add to matches
            add_match_start = perf_counter()
            if len(matches) <= 3 or loss < matches[:,2].max():
                matches = np.append(
                    matches,
                    np.array([
                        [set, 
                         other_features_dir[:-4], 
                         str(loss)]
                        ]),
                    axis=0
                )
                # Sort the array and take the first 3
                matches = matches[matches[:, 2].argsort()][:3]

            add_match_end = perf_counter()
            match_adding_time += add_match_end - add_match_start

            del other_features

    print(f"Time to load features: {loading_feature_time}")                
    print(f"Time to calc loss: {calc_loss_time}")   
    print(f"Time to add match: {match_adding_time}")   

    del features

    return matches

def load_database():
    with open("card_database.pkl", "rb") as file:
        return pickle.load(file)

def save_database(database):
    with open("card_database.pkl", "wb") as file:
        pickle.dump(database, file)
