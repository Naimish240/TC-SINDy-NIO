"""
By @naimish240

This script goes through all the images in the dataset and constructs a dataframe from them for model training
"""

import pandas as pd
import glob
import tqdm
from datetime import datetime
from math import sin, pi
from skyfield.api import load
from skyfield.framelib import ecliptic_frame


images = glob.glob(".\\output\\*.png")

cols = ['filename', 'timestamp', 'year_sine', 'day_sine', 'moon_phase']
data = []

eph = load('de421.bsp')
sun, moon, earth = eph['sun'], eph['moon'], eph['earth']

for image in tqdm.tqdm(images):
    filename = image.split('\\')[-1][:-4]
    date = datetime(year=int(filename[:4]), month=int(filename[4:6]), day=int(filename[6:8]), hour=int(filename[8:10]), minute=int(filename[10:12]))

    ytd = (date - datetime(year=date.year, month=1, day=1)).days
    htd = (date - datetime(year=date.year, month=date.month, day=date.day)).seconds

    if date.year % 4 == 0:
        year_sine = sin(ytd*2*pi/366)
    else:
        year_sine = sin(ytd*2*pi/365)
    
    day_sine = sin(2*pi*htd/86400)

    # https://rhodesmill.org/skyfield/examples.html#what-phase-is-the-moon-tonight
    ts = load.timescale()
    t = ts.utc(date.year, date.month, date.day, date.hour, date.minute)

    e = earth.at(t)
    s = e.observe(sun).apparent()
    m = e.observe(moon).apparent()

    _, slon, _ = s.frame_latlon(ecliptic_frame)
    _, mlon, _ = m.frame_latlon(ecliptic_frame)
    phase = (mlon.degrees - slon.degrees) % 360.0
    moon_phase = sin(phase * pi / 180)

    
    data.append([filename, date, year_sine, day_sine, moon_phase])

df = pd.DataFrame(data, columns=cols)

df.to_csv('astro.csv', index=False)