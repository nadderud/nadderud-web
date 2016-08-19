from datetime import datetime


def parse_datetime(datetime_string):
    for date_format in ['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S']:
        try:
            return datetime.strptime(datetime_string, date_format)
        except ValueError:
            pass
