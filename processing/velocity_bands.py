import cv2
import numpy as np
import tqdm
from skimage.registration import optical_flow_ilk
from skimage.draw import polygon2mask
from datetime import datetime, timedelta
import pandas as pd
import argparse
import sys
import os

INPUT_FILE = '..\\ibtracs_ni_dataset.csv'
INPUT_FOLDER = 'output\\'


def LUT(file="..\\latlon_pixel_map.csv"):
    df = pd.read_csv(file)
    foo = df.values.tolist()
    lut = {}

    for lat, lon, x, y in foo:
        lut[lat, lon] = (int(x), int(y))
    
    return lut

COORDINATE_LUT = LUT()

def create_mask(lat, lon, dia_deg):
    # Mask Points
    pts =[[-0.5, 0.0], [-0.4, -0.3], [-0.4, 0.3], [-0.3, -0.4], [-0.3, 0.4], [0.0, -0.5], [0.0, 0.5], [0.3, -0.4], [0.3, 0.4], [0.4, -0.3], [0.4, 0.3], [0.5, 0.0]]
    pts = [[x*dia_deg, y*dia_deg] for x, y in pts]
    pts = [[x+lat, y+lon] for x, y in pts]
    pts = np.array([COORDINATE_LUT[(round(x*10)/10, round(y*10)/10)] for x, y in pts])

    # Create Polygon Mask
    mask = polygon2mask((2500, 2500), pts).astype(int)
    return mask


def calculate_vectors(img1, img2, lat, lon):
    velocity = optical_flow_ilk(img1, img2, num_warp=1)
    
    avg_velocities  = []
    
    # Calculate velocity at 8 bands
    for i in range(8):
        inner_mask = create_mask(lat, lon, i)
        outer_mask = create_mask(lat, lon, i+1)

        # Apply mask
        mask = outer_mask - inner_mask
        
        # Calculate velocity from bands
        vx_band = velocity[0] * mask
        vy_band = velocity[1] * mask

        # Get average velocity in band
        avg_vx = np.sum(vx_band) / np.sum(mask)
        avg_vy = np.sum(vy_band) / np.sum(mask)

        avg_velocities += [avg_vx, avg_vy]
    
    return avg_velocities


def process_image_pair(p1, p2, lat, lon):
    # If image doesn't exist, skip
    try:
        img1 = cv2.imread(f'{INPUT_FOLDER}{p1}.png')
        img2 = cv2.imread(f'{INPUT_FOLDER}{p2}.png')

        # Calculate for IR channel
        ir1 = img1[:, :, 1]
        ir2 = img2[:, :, 1]

    except TypeError:
        return None

    ir = calculate_vectors(ir1, ir2, lat, lon)
    if not ir:
        return None

    # Calculate for WV channel
    wv1 = img1[:, :, 0]
    wv2 = img2[:, :, 0]

    wv = calculate_vectors(wv1, wv2, lat, lon)

    return ir + wv


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Index to process')
    parser.add_argument('--partition', type=int, help='partition number', required=True)
    args = parser.parse_args()

    df = pd.read_csv(INPUT_FILE)
    blah = pd.to_datetime(df.ISO_TIME, dayfirst=True)
    df['timestamp'] = blah
    df['filename'] = df['timestamp'].dt.strftime('%Y%m%d%H%M%S')

    # Use only images where we can calculate vectors with certainty
    rows = df.values.tolist()

    if args.partition == 7:
        to_process = rows[7*160:]

    else:
        to_process = rows[160*args.partition : 160*(args.partition+1)]
    
    lut = []
    for row in tqdm.tqdm(to_process):
        filename = row[6]
        timestamp = row[5]
        f1 = timestamp - timedelta(hours=6)
        f2 = timestamp - timedelta(hours=3)
        f1 = f"{f1.year:04}{f1.month:02}{f1.day:02}{f1.hour:02}{f1.minute:02}{f1.second:02}"
        f2 = f"{f2.year:04}{f2.month:02}{f2.day:02}{f2.hour:02}{f2.minute:02}{f2.second:02}"

        foo = process_image_pair(f1, f2, row[3], row[4])
        if not foo:
            continue

        lut.append([filename] + foo)

    columns = [
        'filename',
        'vel_ir_x_1',
        'vel_ir_y_1',
        'vel_ir_x_2',
        'vel_ir_y_2',
        'vel_ir_x_3',
        'vel_ir_y_3',
        'vel_ir_x_4',
        'vel_ir_y_4',
        'vel_ir_x_5',
        'vel_ir_y_5',
        'vel_ir_x_6',
        'vel_ir_y_6',
        'vel_ir_x_7',
        'vel_ir_y_7',
        'vel_ir_x_8',
        'vel_ir_y_8',
        'vel_wv_x_1',
        'vel_wv_y_1',
        'vel_wv_x_2',
        'vel_wv_y_2',
        'vel_wv_x_3',
        'vel_wv_y_3',
        'vel_wv_x_4',
        'vel_wv_y_4',
        'vel_wv_x_5',
        'vel_wv_y_5',
        'vel_wv_x_6',
        'vel_wv_y_6',
        'vel_wv_x_7',
        'vel_wv_y_7',
        'vel_wv_x_8',
        'vel_wv_y_8'
    ]
    
    output = pd.DataFrame(lut, columns=columns)
    output.to_csv(f'velocity_bands_{args.partition}.csv', index=False)