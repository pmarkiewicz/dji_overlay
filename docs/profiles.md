# Profiles 
Profile is json file and defines parameters of elements, location and video processing parameters.

Element profile is hierarchical list of properties where any property can be modfied on any level.

## Predefined profiles
There are 3 predefined profiles:
* HD.json - for image from goggles, resolution 1280x720
* FHD.json - for video from airunit, resolution 1920x1080
* 2k.json - for unscaled video from air unit to 2.7k, first step is to upscale video, next to add overlay. This may be usedful for youtube upload. Resolution 2704x1520

## profile section
This defines resolution of generated images and if resize is set to true also resizes video to specified resolution.

## ffmapeg
This defines options used to run ffmpeg
* ffmpeg - location of ffmpeg (full path if not on path)
* ffmpeg_opt - input options for ffmpeg
* ffmpeg_output_opt - output options related to compression
* resize_opt - options use to resize video

## global_settings
Global parameters that can be changed later. Mostly fonts and colors to not repeat them in every item.

## chart_settings
Settings per chart type, if any parameters from global_settings is set here will be changed.

## display
List of items to be overlayed, everyone with location and value.

## colors
All colors and in format as in css, hexadecimal color RGB, i.e. #FF0000 is red color, colors always starts with #and have 6 hex digits

### available chart types
* HChart - horizontal chart made of blocks. Supported parameters:
    * border_color
    * red_color - color used when value is below color_range_l
    * yellow_color - color used when value is between color_range_l and color_range_h
    * green_color - color used when value is above color_range_h
    * empty_color - color used fill part of bar above current value
    * text_color - text color
    * label_font - font used to print label, i.e. verdana.ttf, can be any system font
    * label_font_size - font size 
    * value_font - font used to print value
    * value_font_size - font size
    * name - name of item (label)
    * fmt - number format, as in C, basic examples are 2.1f float number, two difits before decimal and one digit after, for integers 1d is one digit
    * bar_w - chart is made from bars, this is width of the bar in pixels
    * bar_h - height of single bar in pixels
    * bar_space - space between bars in pixels
    * border_space - distance from bar to border in pixels
    * label_space - distance to label from chart
    * reversed - colors are reversed, this is for case when lower number is better i.e. delay
    * min_value - used to scale chart, this is minimum value, in many cases it's zero
    * max_value - used to scale chart, this is maximum value, should be set to max value i.e. for RSSI this will 100, for bitrate this will 50.8
    * color_range_h - color range used to color chart, everything above is green (unless reversed)
    * color_range_l - color range used to color chart, everything below is red (unless reversed)
    * x - location of char, 0 is left side
    * y - location of chart, 0 is top
    * value_name - value to be displayed, list below
* VChart - vertical chart made of blocks. Supported parameters are same like for HChart
* Watermark - overlay of any image, can be used to to add logo or mask gps parameters. Supported parameters:
    * file_path - path to image file
    * x - location of image
    * y - location of image
    * width - width of image to resize
    * height - height of image to resize
    * resize - if true image will be resized to width x height dimensions
* TChart - text information. Supported parameters:
    * name - name of value (label) displayed before value
    * unit - value units, displayed after value
    * x - location of text
    * y - location of text
    * value_name - value to be displayed, list below
* GPSChart - GPS location
    * x - location of text
    * y - location of text
    * one_line - if set to true both coords are in one line else one under another
    * value_name - should be always GPS
* DateChart - date and time
    * x - location of text
    * y - location of text
    * fmt - display format, full list is here https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    * value_name - should be always DateTime

### available values
    'signal': int - signal 0 - 4 from goggles
    'ch': int - channel used by googles
    'flightTime': int - flight time from goggles
    'uavBat': float - battery in V
    'glsBat': float - goggles battery in V
    'uavBatCells': int - no of battery cells
    'glsBatCells': int - no of battery cells in goggles
    'delay': int - delay in ms
    'bitrate': float - bitare
    'DateTime': date and time
    'FM': int - flight mode
    'GPS': gps location
    'GSpd(kmh)': float - ground speed in km/h
    'GSpd(kts)': float - ground speed in m/h
    'Hdg(@)': float - heading
    'Alt(m)': float - altitude in m
    'Alt(ft)': float - altitude in ft
    'Sats': int - no of satelites
    'Ptch(rad)': float - pitch in radians
    'Ptch(deg): float - pitch in degrees
    'Roll(rad)': float - roll in radians
    'Roll(deg)': float - roll in degrees
    'Yaw(rad)': float - yaw in radians
    'Yaw(deg)': float - yaw in degrees
    'RxBt(V)': float - rx battery in V 
    'Curr(A)': float - current in A
    'Capa(mAh)': int - used battery capacity in mAh
    '1RSS(dB)': int - rssi in dB crossfire
    '2RSS(dB)': int - rssi in dB crossfire
    'RQly(%)': int - rx link quality in % crossfire
    'RSNR(dB)': int - signal noise ratio in dB crossfire
    'RFMD': int - rf mode? crossfire
    'TPWR(mW)': int - transmission power in mW crossfire
    'TRSS(dB)': int - tx
    'TQly(%)': int, tx link quality in % crossfire
    'TSNR(dB)': int, tx signal noise ratio in dB crossfire
    'Rud': int: channel value 1000 - 2000
    'Ele': int: channel value 1000 - 2000
    'Thr': int: channel value 1000 - 2000
    'Ail': int: channel value 1000 - 2000
    'S1': int: channel value 1000 - 2000
    'S2': int: channel value 1000 - 2000
    'S3': int: channel value 1000 - 2000
    'LS': int: channel value 1000 - 2000
    'RS': int: channel value 1000 - 2000
    'SA': int: channel value 1000 - 2000
    'SB': int: channel value 1000 - 2000
    'SC': int: channel value 1000 - 2000
    'SD': int: channel value 1000 - 2000
    'SE': int: channel value 1000 - 2000
    'SF': int: channel value 1000 - 2000
    'SG': int: channel value 1000 - 2000
    'SH': int: channel value 1000 - 2000
    'LSW': str,
    'TxBat(V)': float - tranmitter battery V
    'A2(V)': float - A2 in V
    'RSSI(dB)': int - rssi in dB
    'Tmp1(@C)': int
    'Tmp2(@C)': int
    'A4(V)': float - A4 in V
    'VFAS(V)': float - battery voltage from FC in V
    'Fuel(%)': int
    'VSpd(m/s)': float - vertical speed in m/s
    'AccX(g)': float - acceleration in X axis
    'AccY(g)': float - acceleration in Y axis
    'AccZ(g)': float - acceleration in Z axis
    'GAlt(m)': float - GPS altitude in m
    'Rud(%)': int - channel in %
    'Ele(%)': int - channel in %
    'Thr(%)': int - channel in %
    'Ail(%)': int - channel in %
