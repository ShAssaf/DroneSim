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

        # clean the image from non-building noise
        image = cv2.imread(path, cv2.IMREAD_COLOR)
        indices = np.where((image[:, :, 1] > 10) & (image[:, :, 2] > 10))
        # Change the pixel values to white (255, 255, 255)
        image[indices] = (255, 255, 255)

        # image[:,:,0] = custom_filter(image[:,:,0], 3, 1)
        # image[:, :, 0] = custom_filter(image[:, :, 0], 5, 3)
        image[:, :, 0] = custom_filter(image[:, :, 0], 10, 5)

        cv2.imwrite("denoised_image_10.jpg", image)
        pass


def custom_filter(img, m, k):
    pad_width = m // 2
    inner_start = (m - k) // 2
    inner_end = inner_start + k

    # Pad the image with appropriate value for easier calculation at the boundaries
    img_pad = np.pad(img, pad_width=pad_width, mode='constant', constant_values=255)

    h, w = img.shape
    out_img = np.copy(img)

    for y in range(pad_width, h + pad_width):
        for x in range(pad_width, w + pad_width):
            # Get the m*m region
            region = img_pad[y - pad_width:y + pad_width, x - pad_width:x + pad_width]

            # Get the k*k inner region
            inner_region = region[inner_start:inner_end, inner_start:inner_end]

            # Get the outer surrounding region
            outer_region = np.concatenate((region[:inner_start, :],
                                           region[inner_end:, :],
                                           region[inner_start:inner_end, :inner_start],
                                           region[inner_start:inner_end, inner_end:]), axis=None)

            # Check the condition
            if np.any(inner_region != 255) and np.all(outer_region == 255):
                out_img[y - pad_width - inner_start + 1:y - pad_width + inner_end,
                x - pad_width - inner_start + 1:x - pad_width + inner_end] = 255

    a = 1
    return out_img


if __name__ == '__main__':
    map = MapObject()
    map.draw_map()
