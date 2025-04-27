'''
Renders position for cyclone from ibtracs dataset as videos on satellite image frames.
'''

import pandas as pd
import cv2
import glob
import tqdm
import os


def load_dataset():
    df = pd.read_csv('..\\data\\ibtracs_ni_dataset.csv')
    foo = pd.to_datetime(df.ISO_TIME, dayfirst=True)
    df['timestamp'] = foo
    df['filename'] = df['timestamp'].dt.strftime('%Y%m%d%H%M%S')
    
    return df, glob.glob("output/*.png")


def validate_images(df, images):
    count = 0
    for f in df['filename'].tolist():
        if f'output\\{f}.png' not in images:
            print("MISSING", f)
            count += 1
    print(f"Missing {count} / {df.shape[0]}")


def LUT(file="latlon_pixel_map.csv"):
    df = pd.read_csv(file)
    foo = df.values.tolist()
    lut = {}

    for lat, lon, x, y in foo:
        lut[(lat, lon)] = (int(x), int(y))
    
    return lut


def plot_cyclone(file, points):
    img = cv2.imread(f'output\\{file}.png')
    for point in points:
        cv2.circle(img, point, 3, (0, 255, 255), 2)

    #cv2.imshow("image", img)
    #cv2.waitKey()
    
    return img


def render_video(df, lut):
    foo = list(zip(df.LAT, df.LON))
    points = [lut[(x, y)] for x, y in foo]

    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    video = cv2.VideoWriter(filename=f'..\\renders/{df.NAME.unique()[0]}.avi', fourcc=fourcc, isColor=1, frameSize=(2500, 2500), fps=6)

    images = df.filename.tolist()
    images.sort()

    for image in images:
        path = f'output\\{image}.png'
        if not os.path.exists(path):
            continue

        img = plot_cyclone(image, points)
        video.write(img)

    # Hold final frame for one second
    for _ in range(6):
        video.write(img)

    cv2.destroyAllWindows()
    video.release()


def main():
    df, _ = load_dataset()
    lut = LUT()
    for cyclone in tqdm.tqdm(df.NAME.unique()):
        sub_df = df[df.NAME == cyclone].copy()
        render_video(sub_df, lut)

if __name__ == '__main__':
    main()
