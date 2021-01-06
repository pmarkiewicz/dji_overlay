# dji overlay

Goal of this project is to replace srt overlay with better looking osd in recorded files.
Project is crossplatform and should run on linux, os x and any other os where python and ffmpeg are available

# Requirements
ffmpeg and python installed.

# Installation
Install ffmpeg.
Install python.
Dowload files from this repository.
From command line switch to folder where application was downloaded and run

    python -m pip install -r requirements.txt

# How to use
Simplest using predefined profile is to run on Windows

    python src\dji_overlay.py -video <path to video mp4> -profile profiles\HD.json -run

For other platforms video generation is automatic but after running

    python src\dji_overlay.py -video <path to video mp4> -profile profiles\HD.json

in _img_ folder inside video file folder is a script ff.cmd that can used with minimal adaptation

this will create output video file in same folder as video file

More information is in docs folder.


## How it works
Base on srt file and optional log from OpenTX radio dji_overlay creates series of png images and with help of ffmpeg overlays them on video file.