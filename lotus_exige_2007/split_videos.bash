#!/usr/bin/env bash

# Example usage:

USAGE="Usage: $(basename $0) [OPTIONS]
Options:
  -i: Input video file
  -s <HH:MM:SS HH:MM:SS>: Session start and end time

Splits a video into seaparte sessions based on time.

Example: $(basename $0) -i my_video.avi -s '00:04:32 00:19:14' -s '00:37:01 00:51:32'"

while getopts i:s:h flag
do
   case "${flag}" in
      i) INPUT=${OPTARG};;
      s) SESSION_STAMPS+=("$OPTARG");;
      h) echo "$USAGE"; exit;
   esac
done
shift $((OPTIND -1))

i=1
for STAMPS in "${SESSION_STAMPS[@]}"; do
    echo $STAMPS
    STAMPS_ARRAY=($STAMPS)
    START=${STAMPS_ARRAY[0]}
    END=${STAMPS_ARRAY[1]}

    NAME="${INPUT%%.*}"
    EXT="${INPUT##*.}"

    ffmpeg -ss $START -to $END -i $INPUT -c copy "$NAME"_session_"$i"."$EXT"

    let "i++"
done
