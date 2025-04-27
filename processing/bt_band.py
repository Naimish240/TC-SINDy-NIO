import cv2
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import tqdm
from scipy.constants import Planck, speed_of_light, Boltzmann
from skimage.draw import polygon2mask


INPUT_FILE = '..\\data\\ibtracs_ni_dataset.csv'
INPUT_FOLDER = 'output\\'


def LUT(file="..\\data\\latlon_pixel_map.csv"):
    df = pd.read_csv(file)
    foo = df.values.tolist()
    lut = {}

    for lat, lon, x, y in foo:
        lut[lat, lon] = (int(x), int(y))
    
    return lut

COORDINATE_LUT = LUT()


def calc_bt(arr, lmbda):
    try:
        T = ((Planck*speed_of_light)/(lmbda*Boltzmann)) * 1 / (np.log(1+((2*Planck*speed_of_light*speed_of_light)/(arr * lmbda**5))))
        return T
    except:
        return 0


def process_image(img):
    ir = img[:, :, 1]
    wv = img[:, :, 0]

    ir_t = calc_bt(ir, 11500*10e-9)
    wv_t = calc_bt(wv,  6400*10e-9)

    return np.stack((ir_t, wv_t), axis=0)


def create_mask(lat, lon, dia_deg):
    # Mask Points
    pts =[[-0.5, 0.0], [-0.4, -0.3], [-0.4, 0.3], [-0.3, -0.4], [-0.3, 0.4], [0.0, -0.5], [0.0, 0.5], [0.3, -0.4], [0.3, 0.4], [0.4, -0.3], [0.4, 0.3], [0.5, 0.0]]
    pts = [[x*dia_deg, y*dia_deg] for x, y in pts]
    pts = [[x+lat, y+lon] for x, y in pts]
    pts = np.array([COORDINATE_LUT[(round(x*10)/10, round(y*10)/10)] for x, y in pts])

    # Create Polygon Mask
    mask = polygon2mask((2500, 2500), pts).astype(int)
    return mask


def calculate_vectors(img, lat, lon):
    avg_bts  = []
    
    # Calculate brightness_temp at 8 bands
    for i in range(8):
        inner_mask = create_mask(lat, lon, i)
        outer_mask = create_mask(lat, lon, i+1)

        # Apply mask
        mask = outer_mask - inner_mask
        
        # Calculate brightness_temp from bands
        bt_band_ir = img[0] * mask
        bt_band_wv = img[1] * mask

        # Get average brightness_temp in band
        avg_bt_ir = np.sum(bt_band_ir) / np.sum(mask)
        avg_bt_wv = np.sum(bt_band_wv) / np.sum(mask)

        avg_bts += [avg_bt_ir, avg_bt_wv]
    
    return avg_bts


def main():
    df = pd.read_csv(INPUT_FILE)
    blah = pd.to_datetime(df.ISO_TIME, dayfirst=True)
    df['timestamp'] = blah
    df['filename'] = df['timestamp'].dt.strftime('%Y%m%d%H%M%S')

    # Use only images where we can calculate vectors with certainty
    rows = df.values.tolist()
    
    lut = []
    for row in tqdm.tqdm(rows):
        filename = row[6]
        timestamp = row[5]
        f2 = timestamp - timedelta(hours=3)
        f = f"{f2.year:04}{f2.month:02}{f2.day:02}{f2.hour:02}{f2.minute:02}{f2.second:02}"

        try:
            img = process_image(cv2.imread(f'{INPUT_FOLDER}{f}.png'))
        except:
            continue
        
        
        foo = calculate_vectors(img, row[3], row[4])
        lut.append([filename] + foo)

    columns = [
        'filename',
        'bt_ir_1',
        'bt_wv_1',
        'bt_ir_2',
        'bt_wv_2',
        'bt_ir_3',
        'bt_wv_3',
        'bt_ir_4',
        'bt_wv_4',
        'bt_ir_5',
        'bt_wv_5',
        'bt_ir_6',
        'bt_wv_6',
        'bt_ir_7',
        'bt_wv_7',
        'bt_ir_8',
        'bt_wv_8',
    ]

    output = pd.DataFrame(lut, columns=columns)
    output.to_csv('bt_bands.csv', index=False)

if __name__ == '__main__':
    main()
