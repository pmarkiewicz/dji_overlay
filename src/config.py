
from PIL import ImageColor
import json

def convert_colors(cfg: dict) -> None:
    for k, v in cfg.items():
        if '_color' in k:
            cfg[k] = ImageColor.getrgb(v) 


def load_config(fn):
    with open(fn) as f:
        cfg = json.load(f)

    convert_colors(cfg['global_settings'])

    for _, v in cfg['chart_settings'].items():
        convert_colors(v)

    for item in cfg['display']:
        convert_colors(item)

    return cfg


if __name__ == '__main__':
    load_config('config.json')