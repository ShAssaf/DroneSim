from src.utils.Consts import Paths
from src.pre_game_map_generator.map_creator import map_creator_main
from src.pre_game_map_generator.map_scaper import map_scraper_main
from src.pre_game_map_generator.map_stitcher import map_stitcher_main
from src.utils.map_obj import MapObject


def main(mode='no_bg', scale=1):
    """this function is the main function of the pre game map generator, it creates the map and the map image
    requirements: the geojson file must be in the path specified in Paths.GEOJSON_PATH
    :param mode: the mode of the map, can be 'no_bg' or 'bg'
    :param scale: the scale of the map image, can be 1 or 2
    """
    map_creator_main(geojson_path=Paths.GEOJSON_PATH)
    map_scraper_main(mode=mode)
    map_stitcher_main(mode=mode)
    MapObject.rescale_map_image(mode=mode, scale_factor=scale)
    MapObject.clean_map_image(Paths.RESCALED_MAP_PATH.format(scale=scale))


if __name__ == "__main__":
    main()
