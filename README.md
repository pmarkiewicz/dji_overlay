# dji overlay

Goal of this project is to replace srt overlay with better looking osd over recorded videos.

Project is crossplatform and should run on linux, os x and any other os where python and ffmpeg are available

Here is sample https://www.youtube.com/watch?v=6el4MmVW32s

# Installation
Install ffmpeg.
Install python. https://www.python.org/
Dowload files from this repository.
From command line switch to folder where application was unpacked and run

    python -m pip install -r requirements.txt

# How to use
Simplest usage with predefined profile is to run on Windows

    python src\dji_overlay.py -video <path to video mp4> -profile profiles\HD.json -run

For other platforms video generation is automatic but after running

    python src\dji_overlay.py -video <path to video mp4> -profile profiles\HD.json

in _img_ folder inside video file folder is a script ff.sh that can used to generate video.

Result video will be created in same folder as source video.

More informations are is in docs folder.

All command line arguments are displayed after -h:

    python src\dji_overlay.py -h

## How it works
Base on srt file and optional log from OpenTX radio dji_overlay creates series of png images and with help of ffmpeg overlays them on video file.
