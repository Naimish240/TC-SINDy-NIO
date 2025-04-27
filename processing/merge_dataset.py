'''
This script merges all three datasets to form the final dataset.
'''

import pandas as pd
import numpy as np

df = pd.read_csv("..\\ibtracs_ni_dataset.csv")
blah = pd.to_datetime(df.ISO_TIME, dayfirst=True)
df['timestamp'] = blah
df['filename'] = df['timestamp'].dt.strftime('%Y%m%d%H%M%S')
df['filename'] = df['filename'].astype(np.int64)

astro = pd.read_csv('astro.csv')
velocity = pd.read_csv('velocity_bands.csv')
bt = pd.read_csv('bt_bands.csv')

output = pd.merge(df, astro, on='filename')
output = pd.merge(output, velocity, on='filename')
output = pd.merge(output, bt, on='filename')
output.drop(['timestamp_x', 'timestamp_y', "NATURE"], axis=1, inplace=True)

output.to_csv('final_dataset.csv', index=False)
