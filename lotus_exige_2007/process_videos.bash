#!/usr/bin/env bash

USAGE="Usage: $(basename $0) directory

Process all videos in the provided directory:
- Changes format to .avi
- Reduces resolution to 1280x720
- Combines all videos together
- Deletes original MP4 files"

DIR=$1

if [ "$DIR" == "." ]; then
  DIR=$(pwd)
elif [ "$DIR" == "-h" ]; then
    echo "$USAGE"
    exit
fi

INPUT_TYPE="MP4"
OUTPUT_TYPE="avi"

# Create the temporary file to dump all video filenames to
TMP_FILE="file_list.txt"
> $TMP_FILE

OUTPUT_NAME=""
for i in $DIR/*.$INPUT_TYPE; do
    [ -f "$i" ] || (echo "ERROR: No videos!"; exit)

    NAME="${i%%.*}"

    # Video files have the naming scheme 'YYYY_MM_DD_HHMMSS_XX', extract only the
    # date section to use as the name of our concatenated output file
    OUTPUT_NAME=${NAME%??????????}

	# Resolution and format change
	ffmpeg -i $NAME.$INPUT_TYPE -vf scale=1280:720 -b 3000k $NAME.$OUTPUT_TYPE

    # Record the name of this file
    echo "file '$NAME.$OUTPUT_TYPE'" >> $TMP_FILE
done

# Concatenate all videos together
ffmpeg -f concat -safe 0 -i $TMP_FILE -c copy $OUTPUT_NAME.$OUTPUT_TYPE

# Clean up all intermediate files
rm $TMP_FILE
for i in $DIR/*.$INPUT_TYPE; do
    [ -f "$i" ] || break

    NAME="${i%%.*}"
    rm $NAME.$INPUT_TYPE
    rm $NAME.$OUTPUT_TYPE
done
