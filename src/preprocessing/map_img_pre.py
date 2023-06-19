from random import randint
import numpy as np
import PIL
from PIL import Image
import cv2
from src.utils.Consts import Paths
from src.preprocessing.map_creator import map_creator_main
from src.preprocessing.map_scaper import map_scraper_main
from src.preprocessing.map_stitcher import map_stitcher_main

from src.utils.map_obj import MapObject



def main():

    # map_creator_main()
    # map_scraper_main(mode='no_bg')
    # map_stitcher_main(mode='no_bg')
    # MapObject.rescale_map_image()
    MapObject.clean_map_image(Paths.RESCALED_MAP_PATH.format(scale=1))


    pass


if __name__ == "__main__":
    main()
