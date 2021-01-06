import csv
import datetime
import math

def get_date_time(d: dict) -> datetime.datetime:
    dt_str = f'{d["Date"]} {d["Time"]}'
    dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%f')

    return dt

def analyse(csv_file):
    with open(csv_file) as f:
        reader = csv.reader(f)

        header = next(reader)
        start_datetime = None
        prev_offset = None
        flight_no = 0

        print('| fl no | start time |')
        print('|-------|------------|')
        for row in reader:
            d = dict(zip(header, row))
            dt = get_date_time(d)

            if not start_datetime:
                start_datetime = dt
                print(f'|{flight_no:>7}|{d["Time"]}|')

            offset = (dt - start_datetime).total_seconds()
            if prev_offset and (offset - prev_offset) > 10.0:
                flight_no += 1
                start_datetime = dt
                print(f'|{flight_no:>7}|{d["Time"]}|')


            prev_offset = offset


fn = r'D:\FPV\Video\DJI\20201227\Banggod-2020-12-27.csv'
analyse(fn)