import os
import sys

from PIL import Image


def get_lng(file_name):
    return float(file_name.split('_')[1].split('.')[0] + '.' + file_name.split('_')[1].split('.')[1])


def find_closest_floats(float_list):
    closest_floats = {}
    for num in float_list:
        closest_float = min(float_list, key=lambda x: abs(x - num))
        closest_floats[num] = closest_float
    return closest_floats


def main(mode='bg'):
    all_files = os.listdir(f'./data/map_scaper/{mode}')
    all_files = [file for file in all_files if file.endswith('.png')]
    lats = set([float(file.split('_')[0]) for file in all_files])
    lats = sorted(list(lats))
    lat_images = []
    longs = []
    for lat in lats:

        longs = set([get_lng(file) for file in all_files if file.startswith(str(lat))])
        longs = sorted(list(longs))
        image_list = []
        for lng in longs:
            image_list.append(Image.open(f'/Users/shlomo/Desktop/reps/604/data/map_scaper/{mode}/{lat}_{lng}.png'))

        new_lat_image = Image.new("RGB", (sum([i.size[0] for i in image_list]), image_list[0].size[1]))
        x_offset = 0
        for im in image_list:
            new_lat_image.paste(im, (x_offset, 0))
            x_offset += im.size[0]
        lat_images.insert(0, new_lat_image)

    result = Image.new("RGB", (lat_images[0].size[0], sum([i.size[1] for i in lat_images])))
    y_offset = 0
    for im in lat_images:
        result.paste(im, (0, y_offset))
        y_offset += im.size[1]
    result.save(f'/Users/shlomo/Desktop/reps/604/data/map_scaper/{mode}_result.png')
    result.save(f'/Users/shlomo/Desktop/reps/604/data/map_scaper/{mode}_result.tif')


if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    else:
        main(mode=sys.argv[1])
