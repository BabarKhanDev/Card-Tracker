import os

import PIL
import cv2 as cv
import numpy as np
import pickle
import torch
import torchvision.transforms

from sklearn import linear_model
from torchvision.models import vgg16, VGG16_Weights
from torchvision import transforms
from PIL import Image

pickle.DEFAULT_PROTOCOL = 5
IMAGE_SCALE = 0.2


# Edge Detection
# Produces a binary image of the edges in an image
def detect_edges(img: cv.Mat | np.ndarray) -> (cv.Mat | np.ndarray, cv.typing.MatLike):
    global IMAGE_SCALE

    img = cv.resize(img, dsize=(9, 0), fx=IMAGE_SCALE, fy=IMAGE_SCALE, interpolation=cv.INTER_CUBIC)
    img_blur = cv.GaussianBlur(img, (3, 3), 0)

    edges = cv.Canny(image=img_blur, threshold1=80, threshold2=80)

    return img, edges


# This is less precise than ransac, but it is more robust
# It will give us lots of area around the card
def bounding_box_from_edges(edges: cv.typing.MatLike, outlier_percent:int = 1) -> (np.ndarray | None):

    global IMAGE_SCALE

    # Handle the case when there are no edges present
    white_pixels = np.where(edges == 255)
    if len(white_pixels[0]) == 0:
        return None

    # Sort the x and y coordinates
    x_coordinates = white_pixels[1]
    y_coordinates = white_pixels[0]
    sorted_x = np.sort(x_coordinates)
    sorted_y = np.sort(y_coordinates)

    # Calculate the number of outliers to be removed and discard them
    num_outliers = round(outlier_percent / 100 * len(x_coordinates))
    x_without_outliers = sorted_x[num_outliers:-num_outliers]
    y_without_outliers = sorted_y[num_outliers:-num_outliers]

    # Calculate the minimum and maximum coordinates after removing outliers
    min_x = np.min(x_without_outliers) / IMAGE_SCALE
    max_x = np.max(x_without_outliers) / IMAGE_SCALE
    min_y = np.min(y_without_outliers) / IMAGE_SCALE
    max_y = np.max(y_without_outliers) / IMAGE_SCALE

    return np.array([
        (max_x, max_y),
        (max_x, min_y),
        (min_x, max_y),
        (min_x, min_y)
    ])


# Using ransac we get the card corners
# TODO: This currently has an issue where if ransac predicts a straight line we get an error and no corners returned
#       This is because we use the gradient of the line in the calculation,
#       if ransac predicts a straight line then grad = 0 or infinite
#       If gradient is infinite then it gets represented as NAN
# TODO: This is very messy and lots of it can be DRY'd out
def corners_from_edges(edges: cv.typing.MatLike) -> np.ndarray:
    global IMAGE_SCALE
    ransac = linear_model.RANSACRegressor()

    # Find the points along the right edge
    right_col = []
    left_col = []
    bottom_row = []
    top_row = []

    for i, row in enumerate(edges):
        # Find all white pixel points
        points = [(i, j) for j, pixel in enumerate(row) if pixel > 200]
        if len(points) == 0:
            continue

        # Organise by largest to smallest
        points.sort(key=lambda x: x[1], reverse=True)
        right_col.append(points[0])
        left_col.append(points[-1])

    for j, row in enumerate(edges.T):
        # Find all white pixel points
        points = [(i, j) for i, pixel in enumerate(row) if pixel > 200]
        if len(points) == 0:
            continue

        # Organise by largest to smallest
        points.sort(key=lambda x: x[1], reverse=True)
        top_row.append(points[0])
        bottom_row.append(points[-1])

    # Arrange points for each side
    right_X, right_y = np.array([x / IMAGE_SCALE for _, x in right_col]).reshape(-1, 1), np.array(
        [y / IMAGE_SCALE for y, _ in right_col]).reshape(-1, 1)
    left_X, left_y = np.array([x / IMAGE_SCALE for _, x in left_col]).reshape(-1, 1), np.array(
        [y / IMAGE_SCALE for y, _ in left_col]).reshape(-1, 1)
    bottom_X, bottom_y = np.array([x / IMAGE_SCALE for _, x in bottom_row]).reshape(-1, 1), np.array(
        [y / IMAGE_SCALE for y, _ in bottom_row]).reshape(-1, 1)
    top_X, top_y = np.array([x / IMAGE_SCALE for _, x in top_row]).reshape(-1, 1), np.array(
        [y / IMAGE_SCALE for y, _ in top_row]).reshape(-1, 1)

    # Compute ransac for Right edge #
    ransac.fit(right_y, right_X)
    right_coef = 1 / ransac.estimator_.coef_
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
        (round(bottom_right_x.item()), round(bottom_right_y.item())),
        (round(top_right_x.item()), round(top_right_y.item())),
        (round(bottom_left_x.item()), round(bottom_left_y.item())),
        (round(top_left_x.item()), round(top_left_y.item()))
    ])


# Compute homography and return rescaled image
def compute_homography(pts_src: cv.Mat | np.ndarray, img: cv.Mat | np.ndarray) -> cv.typing.MatLike:
    H, W, _ = img.shape
    pts_dst = np.array([(W, H), (W, 0), (0, H), (0, 0)])
    h, _ = cv.findHomography(pts_src, pts_dst)
    im_dst = cv.warpPerspective(img, h, (W, H))
    return im_dst


def create_homography_for_all_cards(library_dir: str) -> None:
    for card_dir in os.listdir(f"{library_dir}/unsorted_cards"):
        if os.path.exists(f"{library_dir}/homography_cards/{card_dir}"):
            continue

        img = cv.imread(f"{library_dir}/unsorted_cards/{card_dir}")
        _, edges = detect_edges(img)
        pts_src = bounding_box_from_edges(edges)

        card_homography = compute_homography(pts_src, img)
        card_homography = cv.resize(card_homography, (300, 400), card_homography, interpolation=cv.INTER_AREA)
        cv.imwrite(f"{library_dir}/homography_cards/{card_dir}", card_homography)


def extract_features(
        model: torch.nn.Module,
        preprocess: torchvision.transforms.Compose,
        path: str,
        image: np.ndarray | PIL.Image = None) -> None:

    if image is None:
        image = Image.open(f"{path[:-4]}.jpg").convert('RGB')
    batch = preprocess(image).unsqueeze(0)

    # Move to device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    batch, model = batch.to(device), model.to(device)

    # Calculate Features
    features = model(batch).squeeze(0)
    del batch

    with open(path, "wb") as file:
        pickle.dump(features, file)


def create_model_and_preprocess() -> (torch.nn.Module, torchvision.transforms.Compose):
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


def calculate_features_for_all_cards(card_dirs, library_dir):
    model, preprocess = create_model_and_preprocess()

    for card_dir in card_dirs:
        if os.path.exists(f"{library_dir}/features/{card_dir[:-4]}.pkl"):
            continue

        features = extract_features(model, preprocess, f"{library_dir}/homography_cards/{card_dir}")
        with open(f"{library_dir}/features/{card_dir[:-4]}.pkl", "wb") as file:
            pickle.dump(features, file)


def find_closest_match(features, existing_cards):
    loss_func = torch.nn.MSELoss(reduction="mean")
    matches = []
    device = "cuda" if torch.cuda.is_available() else "cpu"

    for path in existing_cards:
        with open(f"features/{path[:-4]}.pkl", "rb") as file:
            other_features = pickle.load(file)

        loss = loss_func(other_features.to(device), features.to(device))
        matches.append((path, loss.item()))

    return matches


# Given the features of one of our cards, 
# this function will return the closest matches
def match_with_all_cards(features):
    loss_func = torch.nn.MSELoss(reduction="mean")
    matches = np.empty((0, 3), dtype=str)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    features = features.to(device)

    sets = os.listdir("../tcg_cache/features")

    for set in sets:

        feature_dirs = os.listdir(f"../tcg_cache/features/{set}")
        for other_features_dir in feature_dirs:

            # Load the other cards features
            with open(f"../tcg_cache/features/{set}/{other_features_dir}", "rb") as file:
                other_features = pickle.load(file)

            # Compare the other card with this one
            loss = loss_func(features, other_features.to(device))
            loss = loss.item()

            # If they are a good match then add to matches
            if len(matches) <= 3 or loss < matches[:, 2].max():
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

            del other_features

    del features

    return matches
