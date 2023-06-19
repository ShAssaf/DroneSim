from datetime import datetime

import PIL
import cv2
import numpy as np
import pandas as pd
import pyproj
from PIL import Image

from src.geojson_pg import GeoJsonParser
from src.utils.Consts import Paths


class MapObject:
    def __init__(self, path=Paths.MAP_PATH):
        self.path = path
        self.image = cv2.imread(self.path)
        self.gj = GeoJsonParser()
        self.bounds = self.get_map_bounds()
        self.MAP_WIDTH = self.image.shape[0]
        self.MAP_HEIGHT = self.image.shape[1]

    def draw_map(self):
        # create a new figure
        # plt.figure(figsize=(8, 8))
        #
        # # create a Basemap instance
        # map = Basemap(
        #     projection='merc', llcrnrlat=self.bounds['miny'], urcrnrlat=self.bounds['maxy']
        #     , llcrnrlon=self.bounds['minx'], urcrnrlon=self.bounds['maxx'])
        # img = plt.imread(self.path)
        # map.imshow(img)
        # for i in range(0, len(self.gj.building)):
        #     for j in range(0, len(self.gj.building[i])):
        #         GeoJsonParser.add_points_for_plotting(self.gj.building[i][j], map)
        # GeoJsonParser.add_roads_for_plotting(self.gj.roads, m)
        # Create a new empty image
        mask = np.zeros_like(self.image)

        # Define the color and thickness of the polygon
        color = (0, 255, 0)  # green
        thickness = 2

        # Draw the polygon onto the empty image
        cv2.fillPoly(mask, [i for i in self.gj.buildings], color)
        result = cv2.addWeighted(self.image, 0.5, mask, 0.5, 0)
        for i in range(0, len(self.gj.building)):
            for j in range(0, len(self.gj.building[i])):
                self.add_points_for_plotting(self.gj.building[i][j])

    @staticmethod
    def get_map_bounds():
        return pd.read_csv(Paths.MAP_BOUNDS_PATH)

    @staticmethod
    def set_map_bounds(southwest_lat, southwest_long, northeast_lat, northeast_long, comment):
        df = pd.read_csv(Paths.MAP_BOUNDS_PATH)
        new_record = pd.DataFrame({'minx': southwest_long, 'miny': southwest_lat, 'maxx': northeast_long,
                                   'maxy': northeast_lat, 'comment': comment})

        # Check if the record already exists in the DataFrame
        is_duplicate = df.isin(new_record).all(axis=None)
        if not is_duplicate:
            # Insert the new record into the DataFrame
            df = pd.concat([df, new_record], ignore_index=True)
            df.to_csv(Paths.MAP_BOUNDS_PATH, index=False)
            print("Record inserted successfully.")

        else:
            print("Record already exists.")

    @staticmethod
    def convert_coordinates_to_utm():
        bounds = MapObject.get_map_bounds()
        bounds = bounds[bounds['comment'] == 'scraper_bounds'].drop(columns=['comment'])
        # calculate the size of the image in meters (x,y) by converting the bounds to utm

        source_crs = pyproj.CRS('EPSG:4326')

        # Define the target CRS (UTM zone 18N)
        target_crs = pyproj.CRS('EPSG:32618')

        # Create the transformer
        transformer = pyproj.Transformer.from_crs(source_crs, target_crs, always_xy=True)

        # Convert the coordinates from WGS84 to UTM
        xmin, ymin = transformer.transform(bounds['minx'].values, bounds['miny'].values)
        xmax, ymax = transformer.transform(bounds['maxx'].values, bounds['maxy'].values)
        MapObject.set_map_bounds(ymin, xmin, ymax, xmax, 'scraper_bounds_utm')

    @staticmethod
    def rescale_map_image(path=Paths.MAP_PATH, scale_factor=1):
        """rescale the map image to the size of the map in meters such that 1 pixel = 1 meter"""
        PIL.Image.MAX_IMAGE_PIXELS = 8140416001

        MapObject.convert_coordinates_to_utm()
        image = Image.open(path)
        # Get the dimensions of the image
        map_bounds = MapObject.get_map_bounds()
        map_bounds = map_bounds[map_bounds['comment'] == 'scraper_bounds_utm'].drop(columns=['comment'])
        x = map_bounds['maxx'].values[0] - map_bounds['minx'].values[0]
        y = map_bounds['maxy'].values[0] - map_bounds['miny'].values[0]

        # Resize the image
        image = image.resize((round(x / scale_factor), round(y / scale_factor)), Image.ANTIALIAS)
        image.save(path.rsplit('/', 1)[0] + f'/rescaled_map_1_pixel_per_{scale_factor}_meter.png')

    @staticmethod
    def clean_map_image(path=Paths.RESCALED_MAP_PATH):
        image = cv2.imread(path, cv2.IMREAD_COLOR)

        indices = np.where((image[:, :, 1] > 0) & (image[:, :, 2] > 0))

        # Change the pixel values to white (255, 255, 255)
        image[indices] = (255, 255, 255)

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Convert the NumPy array back to a PIL image

        # Apply median filter for noise removal
        # denoised_image = cv2.medianBlur(image, ksize=3)  # Adjust the kernel size as needed (e.g., 3x3, 5x5, etc.)

        # Extract the dimensions of the image
        # Define new threshold level
        new_threshold = 200  # adjust this value as needed

        # Define new structuring element size
        new_kernel_size = (15, 15)  # adjust these values as needed

        # Binarize the image with new threshold
        _, binary = cv2.threshold(gray, new_threshold, 1, cv2.THRESH_BINARY_INV)

        # Define the structuring element with new size
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, new_kernel_size)

        # Perform the opening operation
        opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        # Remove small buildings
        cleaned = np.where(opened[..., np.newaxis] == 1, image, 255)
        # Save the denoised image
        # cv2.imwrite("denoised_image3.jpg", denoised_image)
        cv2.imwrite("denoised_image4.jpg", cleaned)
        pass


if __name__ == '__main__':
    map = MapObject()
    map.draw_map()
