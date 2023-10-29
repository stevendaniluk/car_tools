#/usr/bin/python3

import argparse
import os
import shutil
import struct

# Format spec for the header data
HEADER_FORMAT = '<' + (
    "I"
    "4s"
    "I"
    "I"
    "20s"
    "I"
    "24s"
    "H"
    "H"
    "H"
    "I"     # Device Serial
    "8s"
    "H"
    "H"     # Magic number
    "I"
    "4s"
    "16s"
    "16s"
    "16s"
    "16s"
    "64s"
    "64s"
    "64s"
    "64s"
    "64s"
    "1024s"
    "I"     # Magic number
)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=\
    "Converts MoTeC .ld files so that they can be opened in i2 Pro")
    parser.add_argument("path", type=str, help="Path to .ld file or directory with .ld files")
    parser.add_argument("--output", type=str, \
        help="Path to output .ld file, will append '.orig' if not provided")
    args = parser.parse_args()

    if args.path:
        args.path = os.path.expanduser(args.path)

    # Determine the paths of all the files to convert
    filenames = []
    if os.path.isfile(args.path):
        filenames.append(args.path)
    elif os.path.isdir(args.path):
        # Get all .ld files in this directory
        for item in os.listdir(args.path):
            if os.path.splitext(item)[1] == ".ld":
                # Candidate file
                if os.path.exists(os.path.splitext(item)[0] + ".ld.orig"):
                    print("Skipping '%s' because '.orig' backup exists" % os.path.split(item)[1])
                    continue
                else:
                    filenames.append(os.path.join(args.path, item))

        if not filenames:
            print("ERROR: No .ld files found in directory '%s'" % args.path)
    else:
        print("ERROR: path '%s' is not valid!" % args.path)
        exit(1)


    for ld_path in filenames:
        print("Converting '%s'..." % os.path.split(ld_path)[1])

        # Rename the original file
        ld_path_orig = ld_path + ".orig"
        os.rename(ld_path, ld_path_orig)

        print("  Opening input file...")
        ld_file = open(ld_path_orig, "rb")

        # Load the header data and modify the fields required to enable Pro Logging
        header_data = ld_file.read(struct.calcsize(HEADER_FORMAT))
        header_data_unpacked = struct.unpack(HEADER_FORMAT, header_data)

        header_data_unpacked = list(header_data_unpacked)
        header_data_unpacked[10] = 0x1F44
        header_data_unpacked[13] = 0xADB0
        header_data_unpacked[26] = 0xc81a4
        header_data_unpacked = tuple(header_data_unpacked)

        # Extract everything from the original file after the header
        file_size = os.path.getsize(ld_path_orig)
        ld_file.seek(struct.calcsize(HEADER_FORMAT))
        og_contents = ld_file.read(file_size - struct.calcsize(HEADER_FORMAT))

        with open(ld_path, "ab") as ld_mod_file:
            print("  Writing modified file...")

            # Write the modified header data, plus the original contents after the header
            ld_mod_file.write(struct.pack(HEADER_FORMAT, *header_data_unpacked))
            ld_mod_file.write(og_contents)


        print("  Pro file generated!")
