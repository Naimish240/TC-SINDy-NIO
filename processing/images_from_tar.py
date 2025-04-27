"""
By @naimish240

This script goes through the nested tarfiles from the eumetsat download, 
merges the image channels and saves them to an output directory.
ONLY PROCESSES IMAGES FROM ibtracs
"""

import tarfile
import glob
import io
import os
from PIL import Image
import tqdm
import sys
import argparse
import pandas as pd

def process_tar(tar_path, output_folder, required_images):
    # Create output folder if not exists
    os.makedirs(output_folder, exist_ok=True)

    with tarfile.open(tar_path, 'r') as tar:
        members = tar.getmembers()
        print(f"... Found {len(members)} images")
        skip = 0
        duplicate = 0

        for member in tqdm.tqdm(members):
            inner_tar = tar.extractfile(member).read()
            stream = io.BytesIO(inner_tar)
            stream.seek(0)

            with tarfile.open(fileobj=stream, mode='r') as images:
                channels = images.getmembers()
                IR = None
                VIS = None
                WV = None
                timestamp = ''
                for channel in channels:
                    # Skip if image smaller than 100 kb, because image should be atleast 60 kb
                    if channel.size/1024 < 60:
                        skip += 1
                        break

                    timestamp = channel.name.split('-')[-1][:-4]

                    # Skip if timestamp is irrelevant to our use case
                    if timestamp not in required_images:
                        break

                    # Check if image exists
                    if os.path.isfile(f"{output_folder}\\{timestamp}.png"):
                        duplicate += 1
                        break

                    if 'IR108' in channel.name:
                        f = images.extractfile(channel).read()
                        img_stream = io.BytesIO(f)
                        IR = Image.open(img_stream).convert('L')

                    if 'VIS6' in channel.name:
                        f = images.extractfile(channel).read()
                        img_stream = io.BytesIO(f)
                        VIS = Image.open(img_stream).convert('L').resize((2500,2500))

                    if 'WV73' in channel.name:
                        f = images.extractfile(channel).read()
                        img_stream = io.BytesIO(f)
                        WV = Image.open(img_stream).convert('L')
                else:
                    try:
                        if None in [VIS, IR, WV]:
                            skip += 1
                            continue

                        image = Image.merge('RGB', [VIS, IR, WV]) # VIS, IR, WV | IR, VIS, WV | WV, IR, VIS
                        image.save(f"{output_folder}\\{timestamp}.png")

                    except KeyboardInterrupt:
                        print()
                        print(f"... {skip} image(s) were skipped")
                        print("Saving image and exitting...")
                        image.save(f"{output_folder}\\{timestamp}.png")
                        sys.exit()

    print(f"... {skip} image(s) were skipped.")
    print(f"... {duplicate} image(s) were duplicates")


if __name__ == '__main__':
    # Set up for 8 threads, OS level
    parser = argparse.ArgumentParser(description='Index to process')
    parser.add_argument('--partition', type=int, help='partition number', required=True)
    args = parser.parse_args()

    ORDERS_PATH = '..\\..\\eumetsat_dataset\\archive.eumetsat.int\\umarf-gwt\\onlinedownload\\Naimish\\'
    OUTPUT_PATH = 'output'

    orders = glob.glob(ORDERS_PATH+'**\\*.tar', recursive=True)
    print(f"... Found {len(orders)} tar files")
    print(f"... Partition number: {args.partition}")

    orders.sort()

    if args.partition == 7:
        to_process = orders[7*9:]

    else:
        to_process = orders[9*args.partition : 9*(args.partition+1)]

    # Run sanity check to make sure everything processed
    to_process = orders

    df = pd.read_csv('../ibtracs_ni_dataset.csv')
    foo = pd.to_datetime(df.ISO_TIME, dayfirst=True)
    df['timestamp'] = foo
    df['filename'] = df['timestamp'].dt.strftime('%Y%m%d%H%M%S')
    required_images = df.filename.tolist()


    print("")

    for bar in to_process:
        print('*'*50)
        print(f'... Processing {bar}')
        process_tar(bar, OUTPUT_PATH, required_images)
        print('*'*50)



