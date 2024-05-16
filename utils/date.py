import datetime


def now():
    return datetime.datetime.now().strftime("H%M%S")


def folder_date():
    n = datetime.datetime.now()
    return f"{now.year}/{n.month}/{n.day}"
