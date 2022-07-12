#!/usr/bin/env python3

import argparse
import os
from PIL import Image

DESCRIPTION = """Generates a set of coloured images linearly interpolating between
Blue->Green->Red to indicate tire temperature."""

""" Generates a set fo RGB values that linear interpolates between
Blue->Green->Red.

frac: 0=Blue, 0.5=Green, 1.0=Red
"""
def get_rgb_values(frac):
    if frac <= 0.25:
        r = 0
        g = 4 * frac
        b = 1
    elif frac > 0.25 and frac <= 0.5:
        r = 0
        g = 1
        b = 1 - 2 * frac
    elif frac > 0.5 and frac <= 0.75:
        r = 4 * (frac - 0.5)
        g = 1
        b = 0
    else:
        r = 1
        g = 1 -  4 * (frac - 0.75)
        b  = 0

    return (int(255 * r), int(255 * g), int(255 * b))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("source", type=str, help="Path to source image")
    parser.add_argument("count", type=int, help="Number of images to create")

    args = parser.parse_args()

    if args.count <= 1:
        print("ERROR: count must be >1")
        exit(1)

    args.source = os.path.expanduser(args.source)
    if not os.path.isfile(args.source):
        print("ERROR: source file %s does not exist" % args.source)
        exit(1)

    source_dir, source_filename = os.path.split(args.source)
    source_filename, source_ext = os.path.splitext(source_filename)

    img = Image.open(args.source)
    [u_size, v_size] = img.size

    for i in range(args.count):
        frac = i / (args.count - 1)
        for u in range(u_size):
            for v in range(v_size):
                [r, g, b, a] = img.getpixel((u, v))
                if a > 0:
                    img.putpixel((u, v), get_rgb_values(frac))

        output_name = os.path.join(source_dir, source_filename + "_" + str(i + 1) + source_ext)
        img.save(output_name)
