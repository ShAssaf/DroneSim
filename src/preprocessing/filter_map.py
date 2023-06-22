import cv2
import numpy as np

from src.utils.Consts import Paths





def main(path=Paths.RESCALED_MAP_PATH.format(scale=1)):
    image = cv2.imread(path, cv2.IMREAD_COLOR)

    map = cv2.imread("./map.png", cv2.IMREAD_GRAYSCALE)