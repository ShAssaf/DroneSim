from datetime import datetime

from cv2 import cv2
import numpy as np
import pandas as pd

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
        new_record = {'minx': southwest_long, 'miny': southwest_lat, 'maxx': northeast_long,
                      'maxy': northeast_lat, 'comment': comment}

        # Check if the record already exists in the DataFrame
        is_record_present = (df['minx'] == new_record['minx']) & \
                            (df['miny'] == new_record['miny']) & \
                            (df['maxx'] == new_record['maxx']) & \
                            (df['maxy'] == new_record['maxy'])

        if not is_record_present.any():
            # Insert the new record into the DataFrame
            df = df.append(new_record, ignore_index=True)
            df.to_csv(Paths.MAP_BOUNDS_PATH, index=False)
            print("Record inserted successfully.")
        else:
            print("Record already exists.")


if __name__ == '__main__':
    map = MapObject()
    map.draw_map()
