'''
This script creates a lookup table that maps latitude and longitude to pixel coordinates in the satellite image.
'''

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import pandas as pd

def create_latlon_pixel_mapping(file="output\\20070531060000.png", 
                              grid_spacing=0.1, 
                              output_file="..\\data\\latlon_pixel_map.csv"):
    src_proj = ccrs.Geostationary(central_longitude=57.3)
    src_extent = (-5500000, 5500000, -5500000, 5500000)

    lats = np.arange( -10, 40, grid_spacing)
    lons = np.arange( 35, 110, grid_spacing)

    img = plt.imread(file)
    img_height, img_width = img.shape[:2]
    
    results = []
    
    # Convert latitude/longitude to projection coordinates
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    transformed_points = src_proj.transform_points(ccrs.PlateCarree(), 
                                                  lon_grid.flatten(), 
                                                  lat_grid.flatten())
    
    # Reshape back to grid
    xs = transformed_points[:, 0].reshape(len(lats), len(lons))
    ys = transformed_points[:, 1].reshape(len(lats), len(lons))
    
    # Convert projection coordinates to pixel coordinates
    x_pixel = (xs - src_extent[0]) / (src_extent[1] - src_extent[0]) * img_width
    y_pixel = (ys - src_extent[2]) / (src_extent[3] - src_extent[2]) * img_height
    
    # Create dataframe with all points
    for i in range(len(lons)):
        for j in range(len(lats)):
            lon, lat = lons[i], lats[j]
            x, y = x_pixel[j, i], y_pixel[j, i]
            
            # Check if point is within image bounds
            if (0 <= x < img_width and 0 <= y < img_height):
                results.append({
                    'lat': round(lat, 2),
                    'lon': round(lon, 2),
                    'y_pixel': int(round(x)),
                    'x_pixel': int(round(2500-y))
                })
    
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    print(f"Saved mapping with {len(df)} points to {output_file}")
    
    return df

if __name__ == '__main__':
    create_latlon_pixel_mapping()