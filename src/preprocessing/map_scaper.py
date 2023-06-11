import os
import re
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import sys

from src.utils.Consts import Paths
from src.utils.map_obj import MapObject


def move_browser_view(driver, map_variable, center_lat, new_center_lng):
    # Use JavaScript to pan the map to the new center coordinates.
    pan_to_js = (
        "{map}.panTo(new L.LatLng({lat}, {lng}));"
        .format(map=map_variable, lat=center_lat, lng=new_center_lng)
    )
    driver.execute_script(pan_to_js)
    sleep(3)


def get_bounds_from_browser(driver, map_variable):
    # return format: 'southwest_lng,southwest_lat,northeast_lng,northeast_lat'
    get_bounds_js = "return {map}.getBounds().toBBoxString();".format(map=map_variable)
    bounds = driver.execute_script(get_bounds_js)
    return map(float, bounds.split(','))


def main(mode='bg'):
    if os.path.exists(f"./data/map_scaper/{mode}") is False:
        os.mkdir(f"./data/map_scaper/{mode}")
    else:
        for file in os.listdir(f"./data/map_scaper/{mode}"):
            os.remove(f"./data/map_scaper/{mode}/{file}")
    # Create a new Chrome session
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    if mode == 'bg':
        driver.get(f'file:///{Paths.MAP_BG_HTML_FULL_PATH}')
    else:
        driver.get(f'file:///{Paths.MAP_HTML_FULL_PATH}')

    # Extract the HTML source from the webpage
    html_source = driver.page_source
    # load bounds from csv
    long_min = MapObject.get_map_bounds()['minx'].values[0]
    lat_min = MapObject.get_map_bounds()['miny'].values[0]
    long_max = MapObject.get_map_bounds()['maxx'].values[0]
    lat_max = MapObject.get_map_bounds()['maxy'].values[0]

    map_min_lat = float('inf')
    map_min_lng = float('inf')
    map_max_lat = float('-inf')
    map_max_lng = float('-inf')

    # Use regex to find the map variable.
    # This pattern looks for strings that start with "map_" followed by 32 alphanumeric characters.
    match = re.search(r'map_[a-z0-9]{10,}', html_source)
    # Check if a match was found
    map_variable = match.group(0)

    # Get the initial bounds of the map
    move_browser_view(driver, map_variable, lat_min, long_min)
    southwest_lng, southwest_lat, northeast_lng, northeast_lat = get_bounds_from_browser(driver, map_variable)
    lng_interval = northeast_lng - southwest_lng
    lat_interval = northeast_lat - southwest_lat

    while northeast_lat < lat_max:
        while southwest_lng < long_max:
            # save bounds
            if southwest_lng < map_min_lng:
                map_min_lng = southwest_lng
            if southwest_lat < map_min_lat:
                map_min_lat = southwest_lat
            if northeast_lng > map_max_lng:
                map_max_lng = northeast_lng
            if northeast_lat > map_max_lat:
                map_max_lat = northeast_lat

            driver.save_screenshot(f"./data/map_scaper/{mode}/{southwest_lat}_{southwest_lng}.png")

            # Calculate the longitude of the new center, shifting to the right by the longitude interval
            new_center_lng = northeast_lng + lng_interval / 2
            center_lat = (southwest_lat + northeast_lat) / 2

            # Use JavaScript to pan the map to the new center coordinates.
            move_browser_view(driver, map_variable, center_lat, new_center_lng)
            southwest_lng, southwest_lat, northeast_lng, northeast_lat = get_bounds_from_browser(driver, map_variable)

        new_center_lat = northeast_lat + lat_interval / 2
        move_browser_view(driver, map_variable, new_center_lat, long_min)
        southwest_lng, southwest_lat, northeast_lng, northeast_lat = get_bounds_from_browser(driver, map_variable)

    # save bounds to csv
    MapObject.set_map_bounds(map_min_lng, map_min_lat, map_max_lng, map_max_lat, 'scraper_bounds')
    driver.quit()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    else:
        main(mode=sys.argv[1])
