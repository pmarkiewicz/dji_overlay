import math

from PIL import Image, ImageDraw, ImageFont

class BaseChart:
    '''
    Used to initiate all necessary variables
    '''
    def __init__(self):
        self.border_color = (0, 0, 0)
        self.red_color = (255, 0, 0)
        self.yellow_color = (255, 255, 0)
        self.green_color = (0, 255, 0)
        self.empty_color = (255, 255, 255)
        self.text_color = (0, 0, 0)
        self.text_outline_color = (128, 128, 128)

        self.label_font = "arial.ttf"
        self.label_font_size = 16
        self.value_font = "verdana.ttf"
        self.value_font_size = 16

        self.name = ""
        self.fmt = "2.1f"

        self.background_ext = 3
        self.background_color = (200, 200, 200, 70)
        self.background_alpha = 128


class Watermark(BaseChart):
    def __init__(self, cfg):
        super().__init__()

        self.resize = False

        for k, v in cfg.items():
            self.__setattr__(k, v)

        self.value_name = None
        self.coords = (self.x, self.y)

        self.watermark = None

        try:
            watermark = Image.open(self.file_path)
        except FileNotFoundError:
            print(f'Watermark file "{self.file_path}" not found')
            return 

        if self.resize:
            size = (self.width, self.height)
            self.watermark = watermark.resize(size, Image.LANCZOS)
        else:
            self.watermark = watermark

    def draw(self, canvas: ImageDraw, _, img):
        if self.watermark:
            img.paste(self.watermark, self.coords)

class TChart(BaseChart):
    def __init__(self, cfg):
        super().__init__()

        self.icon = None
        self.icon_margin = 2
        self.unit = ''

        for k, v in cfg.items():
            self.__setattr__(k, v)

        if self.icon:
            self.icon_img = Image.open(self.icon)


    def draw(self, canvas: ImageDraw, value, img):
        if value is None:
            return

        if self.fmt:
            txt = '{} {:{}}{}'.format(self.name, value, self.fmt, self.unit)
        else:
            txt = '{} {}{}'.format(self.name, value, self.unit)

        font = ImageFont.truetype(self.value_font, self.value_font_size)

        x_offs = 0
        y_offs = 0
        txt_w, txt_h = font.getsize(txt)

        if self.icon:
            size = self.icon_img.size
            x_offs = size[0] + self.icon_margin
            y_offs = round((txt_h - size[1]) / 2)

        x1 = self.x - self.background_ext
        y1 = self.y - self.background_ext
        x2 = self.x + x_offs + txt_w + self.background_ext
        y2 = self.y + txt_h + self.background_ext

        if y_offs < 0:
            y1 += y_offs
            y2 -= y_offs

        canvas.rectangle((x1, y1, x2, y2), fill=self.background_color)

        if self.icon:
            img.paste(self.icon_img, (self.x, self.y + y_offs))

        canvas.text((self.x + x_offs, self.y), txt, font=font, fill=self.text_color) #,  stroke_width=1, stroke_fill=self.empty_color)


class DateTimeChart(BaseChart):
    def __init__(self, cfg):
        super().__init__()

        for k, v in cfg.items():
            self.__setattr__(k, v)

        self.value_name = "DateTime"

    def draw(self, canvas: ImageDraw, value, _):
        if value is None:
            return

        font = ImageFont.truetype(self.value_font, self.value_font_size)
        txt = value.strftime(self.fmt)

        canvas.text((self.x, self.y), txt, font=font, fill=self.text_color) #,  stroke_width=1, stroke_fill=self.empty_color)


class GPSChart(BaseChart):
    def __init__(self, cfg):
        super().__init__()

        for k, v in cfg.items():
            self.__setattr__(k, v)

        self.value_name = "GPS"

    def draw(self, canvas: ImageDraw, value, _):
        if value is None:
            return

        font = ImageFont.truetype(self.value_font, self.value_font_size)
        if self.one_line:
            txt = f'Lon: {value[0]:.6f}  Lat: {value[1]:.6f}'
            canvas.text((self.x, self.y), txt, font=font, fill=self.text_color)
        else:
            txt1 = f'Lon: {value[0]:.6f}'
            txt2 = f'Lat: {value[1]:.6f}'
            canvas.text((self.x, self.y), txt1, font=font, fill=self.text_color)
            
            _, txt_h = font.getsize(txt)
            canvas.text((self.x, self.y + txt_h + self.h_dist), txt2, font=font, fill=self.text_color)



class VChart(BaseChart):
    def __init__(self, cfg):
        super().__init__()

        self.reversed = False

        for k, v in cfg.items():
            self.__setattr__(k, v)

        self.bar_step = (self.max_value - self.min_value) / self.no_of_bars


    def rotated_text(self, text, font, color):
        dx, dy = font.getsize(text)

        img = Image.new('RGBA', (dx, dy), (255, 0, 0, 0))
        canvas = ImageDraw.Draw(img)
        canvas.text((0, 0), text, font=font, fill=color)

        return img.rotate(90, expand=1)

    def draw(self, canvas: ImageDraw, value, img):
        if value is None:
            return

        w = self.bar_w + 2 * self.border_space
        h = self.no_of_bars * (self.bar_h) + (self.no_of_bars - 1) * self.bar_space +  2 * self.border_space
        canvas.rectangle([self.x, self.y, self.x+w, self.y+h], outline = self.border_color)

        x1 = self.x + self.border_space
        x2 = x1 + self.bar_w

        if value > self.color_range_h:
            bar_color = self.green_color if not self.reversed else self.red_color
        elif value >= self.color_range_l:
            bar_color = self.yellow_color
        else:
            bar_color = self.red_color if not self.reversed else self.green_color

        for n in range(0, self.no_of_bars):
            y1 = self.y + self.border_space + n * (self.bar_h + self.bar_space)
            y2 = y1 + self.bar_h

            if self.reversed:
                n_limit = self.min_value + (n + 1) * self.bar_step
                if value <= n_limit:
                    color = bar_color
                else:
                    color = self.empty_color
            else:
                n_limit = self.min_value + (self.no_of_bars - n - 1) * self.bar_step
                if value >= n_limit:
                    color = bar_color
                else:
                    color = self.empty_color

            canvas.rectangle([x1, y1, x2, y2], fill=color)

        font = ImageFont.truetype(self.value_font, self.value_font_size)
        txt = '{:{}}'.format(value, self.fmt)
        txt_w, txt_h = font.getsize(txt)
        dx = math.floor((w - txt_w) / 2)
        dy = math.floor((h - txt_h) / 2)
        canvas.text((self.x + dx, self.y + h + self.border_space), txt, font=font, fill=self.text_color) #,  stroke_width=1, stroke_fill=self.empty_color)

        font = ImageFont.truetype(self.label_font, self.label_font_size)
        txt = self.name
        img2 = self.rotated_text(txt, font, self.text_color)
        txt_w, txt_h = img2.size

        img.paste(img2, box=(self.x - txt_w - self.label_space, self.y + math.floor((h - txt_h) / 2)))


class HChart(BaseChart):
    def __init__(self, cfg):
        super().__init__()

        self.reversed = False
        
        for k, v in cfg.items():
            self.__setattr__(k, v)

        self.bar_step = (self.max_value - self.min_value) / self.no_of_bars

    def draw(self, canvas: ImageDraw, value, img):
        if value is None:
            return

        w = self.no_of_bars * self.bar_w + (self.no_of_bars - 1) * self.bar_space + 2*self.border_space
        h = self.bar_h + 2 * self.border_space
        canvas.rectangle([self.x, self.y, self.x+w, self.y+h], outline = self.border_color)
        
        y1 = self.y + self.border_space
        y2 = y1 + self.bar_h

        if value > self.color_range_h:
            bar_color = self.green_color if not self.reversed else self.red_color
        elif value >= self.color_range_l:
            bar_color = self.yellow_color
        else:
            bar_color = self.red_color if not self.reversed else self.green_color

        for n in range(0, self.no_of_bars):
            x1 = self.x + self.border_space + n * (self.bar_w + self.bar_space)
            x2 = x1 + self.bar_w

            if self.reversed:
                n_limit = self.min_value + (self.no_of_bars - n) * self.bar_step
                if value <= n_limit:
                    color = bar_color
                else:
                    color = self.empty_color
            else:
                n_limit = self.min_value + (n) * self.bar_step
                if value >= n_limit:
                    color = bar_color
                else:
                    color = self.empty_color

            canvas.rectangle([x1, y1, x2, y2], fill=color)

        font = ImageFont.truetype(self.label_font, self.label_font_size)
        txt = self.name
        _, txt_h = font.getsize(txt)
        canvas.text((self.x, self.y - txt_h - 2*self.border_space), txt, font=font, fill=self.text_color) #,  stroke_width=1, stroke_fill=self.empty_color)

        font = ImageFont.truetype(self.value_font, self.value_font_size)
        txt = '{:{}}'.format(value, self.fmt)
        txt_w, txt_h = font.getsize(txt)
        dx = math.floor((w - txt_w) / 2)
        canvas.text((self.x + dx, y2 + 2*self.border_space), txt, font=font, fill=self.text_color) #,  stroke_width=1, stroke_fill=self.empty_color)


class SChart(BaseChart):
    def __init__(self, cfg):
        super().__init__()

        for k, v in cfg.items():
            self.__setattr__(k, v)
        
        self.ind_line_len = 5
        self.start_angle = -180
        self.end_angle = -25
        self.angle = self.start_angle - self.end_angle

    def draw(self, canvas: ImageDraw, value):
        if value is None:
            return

        box = [self.x, self.y, self.x + 2*self.size, y + 2*self.size]
        val = round(value / (self.color_range_h - self.color_range_l) * self.angle)
        canvas.arc(box, -180, val, self.red_color, self.width)

        canvas.rectangle((self.x, self.y, self.x+2*self.size, self.y+self.size), outline = self.border_color)

        # labels
        canvas.line((self.x-self.ind_line_len, self.y+self.size, self.x, self.y+self.size), fill=self.border_color, width=1)
        font = ImageFont.truetype(self.label_font, self.label_font_size)
        txt = f'{self.color_range_l}'
        txt_w, txt_h = font.getsize(txt)
        canvas.text((self.x - txt_w - self.ind_line_len,  self.y +self.size - txt_h), txt, font=font, fill=self.text_color) #,  stroke_width=1, stroke_fill=self.empty_color)

        p_angle = self.angle / 3
        px0 = self.size * math.sin(p_angle)
        py0 = self.size * math.cos(p_angle)
        px1 = (self.size + self.ind_line_len) * math.sin(p_angle)
        py1 = (self.size + self.ind_line_len) * math.cos(p_angle)
        canvas.line((self.x-px0, self.y-py0, self.x-px1, self.y-py1), fill=self.border_color, width=1)


class AHChart(BaseChart):
    def __init__(self, cfg):
        super().__init__()

        for k, v in cfg.items():
            self.__setattr__(k, v)

        self.pitch_px_per_rad = (self.height / 2) / (math.pi / 2)
        self.center_x = self.x + self.width / 2
        self.center_y = self.y + self.height / 2

    def fix_xy(self, x, y, a, b):
        if y > 0.0 and y > self.height / 2:
            y = self.height / 2 
            x = (y - b) / a
        elif y < 0.0 and y < -self.height / 2:
            y = -self.height / 2 
            x = (y - b) / a

        return x, y

    def draw(self, canvas: ImageDraw, value, img):
        if value is None:
            return

        pitch, roll = value
        b = self.pitch_px_per_rad * pitch
        #canvas.line((self.x, y_mid, self.x + self.width, y_mid), self.color)
        a = math.tan(roll)
        x1 = self.width / 2
        y1 = a*x1 + b

        x1, y1 = self.fix_xy(x1, y1, a, b)

        x2 = -self.width / 2
        y2 = a*x2 + b
        x2, y2 = self.fix_xy(x2, y2, a, b)

        canvas.line((self.center_x + x1, self.center_y - y1, self.center_x + x2, self.center_y - y2))



if __name__ == '__main__':
    from datetime import datetime

    cfg = {
        "border_color": (0, 0, 0),
        "red_color": (255, 0, 0),
        "yellow_color": (255, 255, 0),
        "green_color": (0, 255, 0),
        "empty_color": (255, 255, 255),
        "text_color": (0, 0, 0),
        "text_outline_color": (128, 128, 128),

        "label_font": "arial.ttf",
        "label_font_size": 14,
        "value_font": "verdana.ttf",
        "value_font_size": 14,

        "name": "",
        "fmt": "2.1f"
    }

    cfg_txt = cfg.copy()
    cfg_txt.update({
            "text_color": "#010101",
            "units": ""
    })

    cfg_hchart = cfg.copy()
    cfg_hchart.update({
            "bar_w": 22, 
            "bar_h": 8, 
            "bar_space": 3, 
            "border_space": 2, 
            "label_space": 3,
            "reversed": False,
            "min_value": 0    
    })

    cfg_vchart = cfg.copy()
    cfg_vchart.update({
            "bar_w": 22, 
            "bar_h": 5, 
            "bar_space": 1, 
            "border_space": 2, 
            "label_space": 3,
            "reversed": False,
            "min_value": 0 
    })

    cfg_ah = cfg.copy()
    cfg_ah.update({
        "color": (200, 200, 200),
    })

    cfg_br = cfg_vchart.copy()
    cfg_br.update({
            "name": "bitrate",
            "no_of_bars": 10,
            "color_range_h": 25, 
            "color_range_l": 15, 
            "max_value": 50.8, 
            "bar_h": 2, 
            "bar_space": 2,
            "x": 20, 
            "y": 10, 
    })

    cfg_sig = cfg_vchart.copy()
    cfg_sig.update({
            "name": "signal", 
            "no_of_bars": 4, 
            "color_range_h": 3, 
            "color_range_l": 2, 
            "max_value": 4, 
            "bar_space": 2, 
            "fmt": "1d",
            "x": 80, 
            "y": 10, 
    })

    cfg_batv = cfg_vchart.copy()
    cfg_batv.update({
            "name": "bat", 
            "no_of_bars": 10, 
            "color_range_h": 22.8, 
            "color_range_l": 21.0, 
            "min_value": 18.0, 
            "max_value": 25.8, 
            "bar_h": 2, 
            "bar_space": 1,
            "x": 200, 
            "y": 100, 
    })

    cfg_bath = cfg_hchart.copy()
    cfg_bath.update({
            "name": "bat", 
            "no_of_bars": 10, 
            "color_range_h": 22.8, 
            "color_range_l": 21.0, 
            "min_value": 18.0, 
            "max_value": 25.8, 
            "bar_h": 3, 
            "bar_space": 5,
            "x": 950, 
            "y": 100, 

    })

    cfg_delayv = cfg_vchart.copy()
    cfg_delayv.update({
            "name": "delay", 
            "no_of_bars": 4, 
            "color_range_h": 38, 
            "color_range_l": 32, 
            "min_value": 18, 
            "max_value": 50, 
            "bar_space": 2, 
            "fmt": "2d", 
            "reversed": True,
            "x": 140, 
            "y": 10, 
    })

    cfg_delayh = cfg_vchart.copy()
    cfg_delayh.update({
            "name": "delay", 
            "no_of_bars": 4, 
            "color_range_h": 38, 
            "color_range_l": 32, 
            "min_value": 18, 
            "max_value": 50, 
            "bar_space": 2, 
            "fmt": "2d", 
            "reversed": True,
            "x": 950, 
            "y": 10, 
    })

    cfg_dt = {
        "x": 50,
        "y": 690,
    }

    img = Image.new('RGBA', (1280, 720), (10, 128, 128, 128))
    draw = ImageDraw.Draw(img)

    br_val = [50.6, 45.5, 40.5, 23.5, 11.1, 5.4]
    for y, v in zip(range(10, 550, 90), br_val):
        cfg_br['y'] = y
        br = VChart(cfg_br)
        br.draw(draw, v, img)

    sig_val = [5, 4, 3, 2, 1, 0]
    for y, v in zip(range(10, 550, 60), sig_val):
        cfg_sig['y'] = y
        sig = VChart(cfg_sig)
        sig.draw(draw, v, img)

    bat_val = [25.1, 23.0, 22.1, 21.3, 20.1, 19.2]

    for y, v in zip(range(10, 550, 60), bat_val):
        cfg_batv['y'] = y
        batv = VChart(cfg_batv)
        batv.draw(draw, v, img)

    for y, v in zip(range(460, 800, 25), bat_val):
        cfg_bath['y'] = y
        bath = HChart(cfg_bath)
        bath.draw(draw, v, img)

    delay_val = [18, 22, 29, 32, 38, 48]
    for y, v in zip(range(10, 550, 70), delay_val):
        cfg_delayv['y'] = y
        delayv = VChart(cfg_delayv)
        delayv.draw(draw, v, img)

    for y, v in zip(range(300, 800, 25), delay_val):
        cfg_delayh['y'] = y
        delayh = HChart(cfg_delayh)
        delayh.draw(draw, v, img)


    cfg_thr = cfg_txt.copy()
    cfg_thr.update({
            "type": "TChart",
            "name": "Curr", 
            "unit": "A",
            "x": 450, 
            "y": 110, 
            "value_name": "Curr(A)",
            "icon": "icons/alt-20.png"
    })

    thr = TChart(cfg_thr)
    thr.draw(draw, 10, img)

    cfg_speed = {
        'name': 'speed', 
        'color_range_h': 100, 
        'color_range_l': 0,
        'fmt': '2.1f', 
        'width': 12, 
        'border_width': 4,
        'x': 450, 
        'y': 10,
        'size': 40,
    }
    cfg_speed.update(cfg)

    speed = SChart(cfg_speed)
    speed.draw(draw, 100)

    icon = 'icons/alt-20.png'
    image = Image.open(icon)
    img.paste(image, (500, 500))

    img.save('test.png', 'PNG')

    img = Image.new('RGB', (1280, 720), (128, 128, 128))
    draw = ImageDraw.Draw(img)

    w = int(1280 / 3)
    h = int(720 / 3)

    to_rad = math.pi / 180

    ah_data = [
        (14, -33, 0, 0), (30.4, -27.5, 0, 0), (0, 25, 10, 25),
        (0, 5, 14, -2.9), (0, 10, 30.4, -16), (0, 25, 45, 25),
        (45, 45, -45, -45), (89, 89, -89, -89), (1, 1, -1, -1),
    ]
    ah_gen = (d for d in ah_data)

    for x in range(0, 3):
        for y in range(0, 3):
            cfg_ah['x'] = x * w
            cfg_ah['y'] = y * h
            cfg_ah['width'] = w
            cfg_ah['height'] = h

            ah = AHChart(cfg_ah)

            d = next(ah_gen)
            d_rad1 = (d[0] * to_rad, d[1] * to_rad)
            d_rad2 = (d[2] * to_rad, d[3] * to_rad)

            ah.draw(draw, d_rad1, img)
            ah.draw(draw, d_rad2, img)



    img.save('test_ah.png', 'PNG')



