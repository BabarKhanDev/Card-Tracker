import cv2 as cv
import numpy as np
from sklearn import linear_model
from PIL import Image

image_scale = 0.2


def find_cards(image):
    # TODO image -> []card_img
    pass


def detect_edges(img):
    # Calculate and return a 2d image with the edges highlighted in white, else black
    global image_scale

    img = cv.resize(img, dsize=(9, 0), fx=image_scale, fy=image_scale, interpolation=cv.INTER_CUBIC)
    img_blur = cv.GaussianBlur(img, (3, 3), 0)
    edges = cv.Canny(image=img_blur, threshold1=80, threshold2=80)
    return edges


def corners_from_edges(edges):
    global image_scale
    ransac = linear_model.RANSACRegressor()

    right_col = []
    left_col = []
    bottom_row = []
    top_row = []

    # Find all edges on the right and left of the card
    for i, row in enumerate(edges):
        # Find all white pixel points
        points = [(i, j) for j, pixel in enumerate(row) if pixel > 200]
        if len(points) == 0:
            continue

        # Organise by largest to smallest
        points.sort(key=lambda x: x[1], reverse=True)
        right_col.append(points[0])
        left_col.append(points[-1])

    # Find all edges on the top and bottom of the card
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
    right_x = np.array([x / image_scale for _, x in right_col]).reshape(-1, 1)
    right_y = np.array([y / image_scale for y, _ in right_col]).reshape(-1, 1)
    left_x = np.array([x / image_scale for _, x in left_col]).reshape(-1, 1)
    left_y = np.array([y / image_scale for y, _ in left_col]).reshape(-1, 1)
    bottom_x = np.array([x / image_scale for _, x in bottom_row]).reshape(-1, 1)
    bottom_y = np.array([y / image_scale for y, _ in bottom_row]).reshape(-1, 1)
    top_x = np.array([x / image_scale for _, x in top_row]).reshape(-1, 1)
    top_y = np.array([y / image_scale for y, _ in top_row]).reshape(-1, 1)

    # Compute ransac for Right edge #
    ransac.fit(right_x, right_y)
    right_coef = ransac.estimator_.coef_
    right_intercept = ransac.estimator_.intercept_

    # Compute ransac for left edge #
    ransac.fit(left_x, left_y)
    left_coef = ransac.estimator_.coef_
    left_intercept = ransac.estimator_.intercept_

    # Compute ransac for bottom edge #
    ransac.fit(bottom_x, bottom_y)
    bottom_coef = ransac.estimator_.coef_
    bottom_intercept = ransac.estimator_.intercept_

    # Compute ransac for top edge #
    ransac.fit(top_x, top_y)
    top_coef = ransac.estimator_.coef_
    top_intercept = ransac.estimator_.intercept_

    # Calculate corner location estimates
    # TODO we need to handle 0 gradient
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


def create_homography(card_img):

    # Get corners of the card
    edges = detect_edges(card_img)
    pts_src = corners_from_edges(edges)

    # Warp corners into 300x400 image
    H, W, _ = card_img.shape
    pts_dst = np.array([(W, H), (W, 0), (0, H), (0, 0)])
    h, _ = cv.findHomography(pts_src, pts_dst)
    card_homography = cv.warpPerspective(card_img, h, (W, H))
    card_homography = cv.resize(card_homography, (300, 400), card_homography, interpolation=cv.INTER_AREA)

    return card_homography


def create_feature_vector(card_img):
    # TODO card_homography -> feature_vector
    pass


def find_closest_card(feature_vector):
    # TODO feature_vector -> []card_id
    pass
