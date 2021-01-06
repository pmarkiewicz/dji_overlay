from collections import namedtuple
import re

import srt

RE_CONV = {
            int: re.compile('(\d+)'), 
            float: re.compile('(\d+\.\d+)')
}

CONVERSIONS = {'signal': int, 'ch': int, 'flightTime': int,  'uavBat': float,  'glsBat': float,  'uavBatCells': int,   'glsBatCells': int,   'delay': int, 'bitrate': float, 'rcSignal': int}

def extract(v, f):
    m = RE_CONV[f].search(v)

    return m.group(1)

def convert_values(d: dict) -> None:
    for name, f in CONVERSIONS.items():
        v = extract(d[name], f)
        d[name] = f(v)

def parse_content(content: str) -> tuple:
    items = content.split(' ')

    d = {}
    for item in items:
        name, val = item.split(':')
        d[name] = val

    convert_values(d)

    # result = []
    # for n in EXPORT_NAMES:
    #     result.append(d[n])

    return d

def parse_srt(srt_file: str):
    '''
    srt: file name to be parsed
    output is list of DJI_Data with all details
    '''

    with open(srt_file) as f:
        
        for line in srt.parse(f):
            content = parse_content(line.content)
            content['start'] = line.start.total_seconds()
            content['end'] = line.end.total_seconds()

            yield content



if __name__ == '__main__':
    fn = r'D:\FPV\Video\DJI\20201221\DJIG0009.srt'
    g = parse_srt(fn)

    l = next(g)
    max_sig = l['signal']
    min_bit = max_bit = l['bitrate']
    min_del = max_del = l['delay']

    for l in g:
        if max_sig < l.signal:
            max_sig = l.signal

        if max_bit < l.bitrate:
            max_bit = l.bitrate

        if min_bit > l.bitrate:
            min_bit = l.bitrate

        if max_del < l.delay:
            max_del = l.delay

        if min_del > l.delay:
            min_del = l.delay

    print('max signal: ', max_sig)
    print('min bitrate: ', min_bit)
    print('max bitrate: ', max_bit)
    print('min delay: ', min_del)
    print('max deltay', max_del)
