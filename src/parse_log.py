import csv
import datetime
import math

from haversine import haversine, Unit

def parse_gps(coords: str) -> tuple:
    if coords:
        n = coords.split(' ')
        return (float(n[0]), float(n[1]))

    return None


CONVERSIONS = {
    'Date': lambda dt: datetime.datetime.strptime(dt, '%Y-%m-%d'),
    'Time': lambda dt: datetime.datetime.strptime(dt, '%H:%M:%S.%f'),
    'FM': int,
    'GPS': parse_gps,
    'GSpd(kmh)': float,
    'GSpd(kts)': float,
    'Hdg(@)': float, 
    'Alt(m)': float, 
    'Alt(ft)': float, 
    'Sats': int, 
    'Ptch(rad)': float, 
    'Roll(rad)': float, 
    'Yaw(rad)': float, 
    'RxBt(V)': float, 
    'Curr(A)': float, 
    'Capa(mAh)': int, 
    '1RSS(dB)': int, 
    '2RSS(dB)': int,
    'RQly(%)': int,
    'RSNR(dB)': int,
    'RFMD': int,
    'TPWR(mW)': int,
    'TRSS(dB)': int,
    'TQly(%)': int, 
    'TSNR(dB)': int, 
    'Rud': int, 
    'Ele': int, 
    'Thr': int, 
    'Ail': int, 
    'S1': int,
    'S2': int,
    'S3': int,
    'LS': int,
    'RS': int,
    'SA': int,
    'SB': int,
    'SC': int,
    'SD': int,
    'SE': int,
    'SF': int,
    'SG': int,
    'SH': int,
    'LSW': str,
    'TxBat(V)': float,
    # FrSky
    'A2(V)': float,
    'RSSI(dB)': int,
    'Tmp1(@C)': int,
    'Tmp2(@C)': int,
    'A4(V)': float,
    'VFAS(V)': float,
    'Fuel(%)': int,
    'VSpd(m/s)': float,
    'AccX(g)': float,
    'AccY(g)': float,
    'AccZ(g)': float,
    'GAlt(m)': float,
}

def fix_types(d: dict) -> None:
    missing_sensor = []

    for name, val in d.items():
        try:
            f = CONVERSIONS[name]
            d[name] = f(val)
        except KeyError:
            if name not in missing_sensor:
                missing_sensor.append(name)
            
    # if (missing_sensor):
    #     print(missing_sensor)


def get_date_time(d: dict) -> datetime.datetime:
    dt_str = f'{d["Date"]} {d["Time"]}'
    dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%f')

    return dt

def rc_to_percent(rc):
    '''
    converts input value -1024 - +1024 to percent value
    '''
    return round(((rc + 1024) / 2048) * 100)

def convert_units(d):
    '''
    adds and converts units i.e. km/h <-> mph
    '''
    
    if 'GSpd(kmh)' in d:
        d['GSpd(kts)'] = d['GSpd(kmh)'] / 1.852
    elif 'GSpd(kts)' in d:
        d['GSpd(kmh)'] = d['GSpd(kts)'] * 1.852

    if 'Alt(m)' in d:
        d['Alt(ft)'] = d['Alt(m)'] * 3.28084
    elif 'Alt(ft)' in d:
        d['Alt(m)'] = d['Alt(ft)'] / 3.28084

    d['Rud(%)'] = rc_to_percent(d['Rud'])
    d['Ele(%)'] = rc_to_percent(d['Ele'])
    d['Thr(%)'] = rc_to_percent(d['Thr'])
    d['Ail(%)'] = rc_to_percent(d['Ail'])

    if 'Ptch(rad)' in d: 
        d['Ptch(deg)'] = math.degrees(d['Ptch(rad)'])

    if 'Roll(rad)' in d: 
        d['Roll(deg)'] = math.degrees(d['Roll(rad)'])

    if 'Yaw(rad)' in d:
        d['Yaw(deg)'] = math.degrees(d['Yaw(rad)'])


def parse_csv(csv_file: str, time_offset_ms: int = 0) -> list:
    '''
    parse log data from csv file and shifts by time offset (in ms)
    as open tx will save long from many flights in one file there is flight_no parameter
    gap between fligts is counted when difference between 2 fields is bigger than 10 seconds
    '''

    time_shift = datetime.timedelta(milliseconds=time_offset_ms)

    series = []
    with open(csv_file) as f:
        reader = csv.reader(f)

        header = next(reader)
        start_datetime = None
        home_pos = None
        prev_offset = None

        flight = []
        for row in reader:
            d = dict(zip(header, row))
            dt = get_date_time(d)

            if not start_datetime:
                start_datetime = dt

            offset = ((dt - start_datetime) + time_shift).total_seconds()
            d['offset'] = offset
            if prev_offset and (offset - prev_offset) > 10.0:
                start_datetime = dt
                series.append(flight)
                offset = 0
                flight = []
            
            prev_offset = offset


            fix_types(d)

            d['AH'] = (d['Ptch(rad)'], d['Roll(rad)'])
            d['DateTime'] = datetime.datetime.combine(d['Date'].date(), d['Time'].time())

            if d['GPS']:
                if not home_pos:
                    home_pos = d['GPS']

                d['distance(m)'] = haversine(home_pos, d['GPS'], unit=Unit.METERS)
                d['distance(ft)'] = haversine(home_pos, d['GPS'], unit=Unit.FEET)
            else:
                d['distance(m)'] = None
                d['distance(ft)'] = None

            convert_units(d)

            flight.append(d)

    series.append(flight)

    return series


if __name__ == '__main__':

    fn = r'D:\FPV\Video\DJI\20201227\Banggod-2020-12-27.csv'

    g = parse_csv(fn, 0)
    for i in g:
        pass


