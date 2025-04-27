'''
This script plots the tracks for the cyclones in the final dataset on a map.
'''

import pandas as pd
import cartopy.crs as ccrs
import matplotlib.cm as cm
import matplotlib.pyplot as plt


df = pd.read_csv('final_dataset.csv')

fig = plt.figure(figsize=(10,10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([35, 110, -10, 40], crs=ccrs.PlateCarree())
ax.coastlines()

colors = cm.get_cmap('tab20', len(df.NAME.unique()))

# Start plotting
for idx, cyclone in enumerate(df.NAME.unique()):
    foo = df[df.NAME == cyclone].values.tolist()
    
    lons = [row[3] for row in foo]  # Longitude
    lats = [row[2] for row in foo]  # Latitude
    
    plt.plot(
        lons,
        lats,
        color=colors(idx),
        marker='o',
        markersize=2,
        transform=ccrs.Geodetic(),
        label=cyclone
    )

plt.legend(loc='upper right', fontsize='small', title='Cyclones')
plt.show()