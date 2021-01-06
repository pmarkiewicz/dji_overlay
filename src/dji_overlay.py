import argparse
import pathlib
import os
import sys

from fileutils import *
from generate import TestImageGenerator, AllImagesGenerator

def run_video(temp_dir):
    """
    run video overlay process
    """
    with DirContext(temp_dir):
        os.system('ff.cmd')


def run_test():
    parser = argparse.ArgumentParser(description='Overlays data from DJI goggles (srt) and log from OpenTx on video.')
    parser.add_argument('-test', required=True, action='store_true', help='Generate test image in current folder')
    parser.add_argument('-profile', required=True, help='Profile file with configuration (in json format)')
    parser.add_argument('-srt', required=True, help='Srt file from goggles.')
    parser.add_argument('-log', help='Log file from OpenTx radio')
    parser.add_argument('-flight-no', type=int, help='When there are many flights in log file this is log number (starts from 1)')

    args = parser.parse_args()

    file_exists(args.profile)
    file_exists(args.srt)
        
    if args.log:
        file_exists(args.log)

    gen = TestImageGenerator(args.profile, args.srt, args.log, args.flight_no)
    gen.generate()



def run_generate():
    parser = argparse.ArgumentParser(description='Overlays data from DJI goggles (srt) and log from OpenTx on video.')

    parser.add_argument('-video', required=True, help='Video input file')
    parser.add_argument('-test', action='store_false', help='Generate test image in current folder')
    parser.add_argument('-profile', required=True, help='Profile file with configuration (in json format)')
    parser.add_argument('-srt', help='Srt file from goggles. If missing same file as video will be used.')
    parser.add_argument('-log', help='Log file from OpenTx radio')
    parser.add_argument('-out', help='Video output file. Default is same location as input file with "-out" added to name')
    parser.add_argument('-temp', help='Location for temporary files. Default is "img" folder in out folder')
    parser.add_argument('-flight-no', type=int, help='When there are many flights in log file this is log number (starts from 1)')
    parser.add_argument('-log-offset', type=int, default=0, help='Offset of log file in millisecond compared to srt file')
    parser.add_argument('-run',  action='store_true',help='Offset of log file in millisecond compared to srt file')

    args = parser.parse_args()

    file_exists(args.video)
    file_exists(args.profile)

    if not args.srt:
        args.srt = replace_file_ext(args.video, 'srt')

    file_exists(args.srt)
        
    if args.log:
        file_exists(args.log)

    if not args.out:
        args.out = add_to_filename(args.video, '-out')


    if args.temp:
        folder_exists(args.temp)
        args.temp = add_create_folder(args.temp, 'img')
    else:
        args.temp = add_create_folder(args.out, 'img')    

    gen = AllImagesGenerator(args.profile, args.srt, args.log, args.video, args.out, args.temp, args.flight_no, args.log_offset)
    gen.generate()

    if args.run:
        run_video(args.temp)



if __name__ == '__main__':
    if '-test' in sys.argv:
        run_test()
    else:
        run_generate()



