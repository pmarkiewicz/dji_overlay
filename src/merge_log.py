
def merge_log(origin, log):
    log_iter = iter(log)
    line1 = next(log_iter)
    line2 = next(log_iter)
    started = False
    end_of_data = False

    for row in origin:
        line1_ms = line1['offset']
        line2_ms = line2['offset']
        origin_from = row['start']
        origin_to = row['end']

        if end_of_data:
            data = [(key, None) for key in line1.keys()]
            d = dict(data)
            row.update(d)
        else:
            # log starts later, inser empty data
            if not started and line1_ms > origin_to:
                data = [(key, None) for key in line1.keys()]
                d = dict(data)
                row.update(d)
                continue
            else:
                started = True

            # line2 is ahead in time
            if line2_ms > origin_to:
                row.update(line1)
            else:
                row.update(line2)
                line1 = line2
                try:
                    line2 = next(log_iter)
                except StopIteration:
                     end_of_data = True

        yield row


