import datetime as dt

def date_to_excel(date):
    temp = dt.datetime(1899, 12, 30)    # Note, not 31st Dec but 30th!
    delta = date - temp
    return float(delta.days) + (float(delta.seconds) / 86400)

def struct_time_to_datetime(date):
    return dt.datetime(date.tm_year,date.tm_mon,date.tm_mday,date.tm_hour,date.tm_min,date.tm_sec)