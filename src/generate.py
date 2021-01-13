import sys
import os

from PIL import Image, ImageDraw, ImageFont

from parse_srt import parse_srt
from parse_log import parse_csv
from merge_log import merge_log

import charts

from config import load_config
from fileutils import add_to_filename


class ImageGenerator:
    def __init__(self, cfg_file: str, srt_file: str, log_file: str, flight_no: int = None, log_offset = 0):
        self.cfg = load_config(cfg_file)

        self.flight_no = flight_no
        self.log_offset = log_offset

        rows = parse_srt(srt_file)

        if log_file:
            log = self.process_log(log_file)
            if log:
                self.merged_rows = merge_log(rows, log)
        else:
            self.merged_rows = rows

        resolution = self.cfg['profile']['resolution'].split('x')
        self.width = int(resolution[0])
        self.height = int(resolution[1])

        self.bkgnd = (128, 128, 128, 0)

        self.build_display_list()


    def str_to_class(self, classname: str) -> type:
        m = sys.modules['charts']
        return getattr(m, classname)


    def build_display_list(self) -> None:
        self.display_list = []

        for item in self.cfg['display']:
            chart_cfg = self.cfg['global_settings'].copy()
            chart_type = item['type']

            try:
                chart_cfg.update(self.cfg['chart_settings'][chart_type])
            except KeyError:
                # chart type data are not specified
                pass

            chart_cfg.update(item)

            cls = self.str_to_class(item['type'])

            chart = cls(chart_cfg)
            self.display_list.append(chart)


    def create_image(self, data: dict, img_no: int, path: str = '') -> None:
        img = Image.new('RGBA', (self.width, self.height), self.bkgnd)
        canvas = ImageDraw.Draw(img)

        canvas.rectangle((0, 0, self.width, self.height), fill=self.bkgnd)

        for item in self.display_list:
            v = item.value_name
            try:
                value = data[v] if v else None
                item.draw(canvas, value, img)
            except KeyError:
                if img_no == 0:
                    print(f'No data for "{v}", skipped')

        fn = os.path.join(path, f'{img_no:04d}.png')
        img.save(fn, 'PNG')


    def process_log(self, log_file: str) -> list:
        log_series = parse_csv(log_file, self.log_offset)
        print(f'Found {len(log_series)} flight(s) in open tx log')

        if len(log_series) > 1 and not self.flight_no:
            raise RuntimeError('More than 1 flight found and flight was not selected')

        if not self.flight_no:
            return log_series[0]

        if self.flight_no >= len(log_series):
            raise RuntimeError(f'Flight no: {self.flight_no} does not exists. there are only {len(log_series)} flights.')

        if self.flight_no:
            return log_series[self.flight_no - 1]



class TestImageGenerator(ImageGenerator):
    def __init__(self, cfg_file: str, srt_file: str, log_file: str, flight_no: int = None, log_offset = 0, bkgnd=(200, 200, 200)):
        super().__init__(cfg_file, srt_file, log_file, flight_no, log_offset)
        self.bkgnd = bkgnd

    def generate(self) -> bool:
        row = next(self.merged_rows)
        self.create_image(row, 0)

        return True


class AllImagesGenerator(ImageGenerator):
    def __init__(self, cfg_file: str, srt_file: str, log_file: str, in_file: str, out_file: str, temp_path: str, flight_no: int = None, log_offset:int = 0, keep_temp: bool = False):
        super().__init__(cfg_file, srt_file, log_file, flight_no, log_offset)

        self.in_file = in_file
        self.out_file = out_file
        self.temp_path = temp_path
        self.keep_temp = keep_temp

    def write_complex_script(self, script, fn):
        s = script[-1]
        script[-1] = s[:-6]

        with open(fn, 'w') as f:
            f.writelines(script)

    def create_windows_script(self, cmd_resize, cmd_overlay, resized_file):
        script_generate = f'''
{cmd_resize}

{cmd_overlay}

        '''
        script_cleanup = '''
echo cleanup
del ????.png
if exist "{resized_file}" del {resized_file}
        '''

        with open(f'{self.temp_path}/ff.cmd', 'w') as f:
            f.write(script_generate)
            if not self.keep_temp:
                f.write(script_cleanup)

    def create_linux_script(self, cmd_resize, cmd_overlay, resized_file):
        script = f'''
{cmd_resize}

{cmd_overlay}
echo "cleanup"
rm ????.png
if test -f "{resized_file}"; then
rm {resized_file}
fi
        '''

        with open(f'{self.temp_path}/ff.sh', 'w') as f:
            f.write(script)

    def create_osx_script(self, cmd_resize, cmd_overlay, resized_file):
        script = f'''
{cmd_resize}

{cmd_overlay}
echo "cleanup"
rm ????.png
if test -f "{resized_file}"; then
rm {resized_file}
fi
        '''

        with open(f'{self.temp_path}/ff.sh', 'w') as f:
            f.write(script)


    def write_cmd(self, no_of_images: int, resized_file: str, cplx_script: str) -> None:
        inputs = ['-i {:04d}.png'.format(i) for i in range(0, no_of_images + 1)]
        input_files = ' '.join(inputs)

        ffmpeg_setting = self.cfg['ffmpeg_setting']
        ffmpeg_path = ffmpeg_setting["ffmpeg"]
        ffmpeg_output_opt = ffmpeg_setting["ffmpeg_output_opt"]
        ffmpeg_resize = ffmpeg_setting["resize_opt"]

        cmd_resize = ''
        if self.cfg['profile']['resize']:
            cmd_resize = f'{ffmpeg_path} -y -i {self.in_file} {ffmpeg_resize} {resized_file}\n'
            self.in_file = resized_file

        in_file = self.in_file.replace('/', os.path.sep)
        cplx_script = cplx_script.replace('/', os.path.sep)
        out_file = self.out_file.replace('/', os.path.sep)

        cmd_overlay = f'{ffmpeg_path} -y -thread_queue_size 1024 -i {in_file} {input_files} -filter_complex_script {cplx_script} {ffmpeg_output_opt} -an {out_file}\n'

        if sys.platform.startswith('linux'):
            self.create_linux_script(cmd_resize, cmd_overlay, resized_file)
        elif sys.platform.startswith('darwin'):
            self.create_osx_script(cmd_resize, cmd_overlay, resized_file)
        elif sys.platform.startswith('win32'):
            self.create_windows_script(cmd_resize, cmd_overlay, resized_file)
        else:
            print('Unknown OS, no script generated')


    def generate(self) -> bool:
        for img_no, row in enumerate(self.merged_rows):
            self.create_image(row, img_no, self.temp_path)

            if img_no == 0:
                complex_filter_script = [f"[0:v][1:v] overlay=enable='between(t, {row['start']}, {row['end']})' [tmp]\n"]
            else:
                complex_filter_script.append(f"; [tmp][{img_no}:v] overlay=enable='between(t, {row['start']}, {row['end']})' [tmp]\n")

            if img_no % 100 == 0:
                print('.', end='', flush=True)


        cplx_script = os.path.join(self.temp_path, 'filter.txt')
        self.write_complex_script(complex_filter_script, cplx_script)

        resized_file = add_to_filename(self.out_file, '-resized')
        self.write_cmd(img_no, resized_file, cplx_script)

        return True

if __name__ == '__main__':
    cfg_fn = 'HD.json'
    srt_fn = 'D:/FPV/Video/DJI/20201227/DJIG0001.srt'
    log_fn = 'D:/FPV/Video/DJI/20201227/Src_one_7-2020-12-27.csv'
    gen = TestImageGenerator(cfg_fn, srt_fn, log_fn, 1)
    gen.generate()

