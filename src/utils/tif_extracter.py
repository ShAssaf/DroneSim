import os
import geopandas as gpd
import pandas as pd
from PIL import Image


def find_geometry(tif_name, shp_dfs, crs=False):
    for df in shp_dfs:
        if tif_name in df['SHRT_FNAME'].values:
            if crs:
                return df.crs
            else:
                return df[df['SHRT_FNAME'] == tif_name]['geometry']
    return None


def find_files(root_dir):
    tif_files = []
    shp_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.tif'):
                tif_files.append(os.path.join(dirpath, filename))
            elif filename.endswith('.shp'):
                shp_files.append(os.path.join(dirpath, filename))
    shp_name = list(set([i.split('/')[-1] for i in shp_files]))
    shp_dfs = []
    for i in shp_name:
        for j in shp_files:
            if j.endswith(i):
                shp_dfs.append(gpd.read_file(j))
                break

    filter_dfs = []
    for df in shp_dfs:
        if 'location' in df.columns and 'SHRT_FNAME' not in df.columns:
            df['SHRT_FNAME'] = df['location'].apply(lambda x: x.split('/')[-1])
        filter_dfs.append(df.filter(items=['SHRT_FNAME', 'geometry']))
    # df =  gpd.GeoDataFrame(pd.concat(filter_dfs,axis=0, join="inner"))
    return tif_files, filter_dfs


tif_pdir = '/Users/shlomo/Documents/new york'

# copy all the tif files to a new folder
tif_files, shp_dfs = find_files(tif_pdir)

bounds_df = pd.DataFrame(columns=['minx', 'miny', 'maxx', 'maxy'], index=[i.split('/')[-1] for i in tif_files])
for tif in tif_files:
    bounds_df.loc[tif.split('/')[-1]] = find_geometry(tif.split('/')[-1], shp_dfs).bounds.values[0]

bounds_df.sort_values(by=['miny', 'minx'], inplace=True)
y_image_list = []
for y_ in bounds_df['miny'].unique():
    # for x_ in bounds_df['minx'].unique():
    x_ = bounds_df[bounds_df['miny'] == y_].index
    # new_image = Image.new("RGB", (width1 + width2, height1))
    image_list = []
    for x in x_:
        path = [i for i in tif_files if i.endswith(x)][0]
        image_list.append(Image.open(path))
    new_image = Image.new("RGB", (sum([i.size[0] for i in image_list]), image_list[0].size[1]))
    x_offset = 0
    for im in image_list:
        new_image.paste(im, (x_offset, 0))
        x_offset += im.size[0]
    new_image.save(tif_pdir + '/' + str(y_) + '.jpg')
    y_image_list.insert(0, new_image)
new_image = Image.new("RGB", (y_image_list[0].size[0], sum([i.size[1] for i in y_image_list])))
y_offset = 0
for im in y_image_list:
    new_image.paste(im, (0, y_offset))
    y_offset += im.size[1]
new_image.save(tif_pdir + '/' + 'complete.jpg')

# next line only for new york
shp_dfs[0].to_crs("EPSG:6347", inplace=True)

new_bounds_df = pd.DataFrame(columns=['minx', 'miny', 'maxx', 'maxy'], index=[i.split('/')[-1] for i in tif_files])
for tif in tif_files:
    new_bounds_df.loc[tif.split('/')[-1]] = find_geometry(tif.split('/')[-1], shp_dfs).bounds.values[0]

x_len = new_bounds_df['maxx'].max() - new_bounds_df['minx'].min()
y_len = new_bounds_df['maxy'].max() - new_bounds_df['miny'].min()

actual_map_size = new_image.size

pass
