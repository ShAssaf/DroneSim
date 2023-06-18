from random import randint
import numpy as np
import PIL
import cv2
from src.utils.Consts import Paths
from PIL import Image

from src.utils.map_obj import MapObject



def main():

    # Open the image
    # image = Image.open(Paths.RESCALED_MAP_PATH.format(scale=1))
    # max_x, max_y = image.size
    #
    # # Generate random starting coordinates
    # start_x = randint(0, max_x)
    # start_y = randint(0, max_y)
    #
    # # Convert the PIL image to a NumPy array
    # image_array = np.array(image)
    #
    # # Find the pixels where R and G channels are greater than 0
    # indices = np.where((image_array[:, :, 0] > 0) & (image_array[:, :, 1] > 0))
    #
    # # Change the pixel values to white (255, 255, 255)
    # image_array[indices] = (255, 255, 255)
    #
    # # Convert the NumPy array back to a PIL image
    # modified_image = Image.fromarray(image_array)
    # # Display the cropped image
    # modified_image.show()
    # modified_image.save('test.png')

    #cropped_image.show()
    MapObject.clean_map_image(Paths.RESCALED_MAP_PATH.format(scale=1))

    pass


if __name__ == "__main__":
    main()
