import datetime


def now():
    return datetime.datetime.now().strftime("%H%M%S")


def folder_date():
    n = datetime.datetime.now()
    return f"{n.year}/{n.month}/{n.day}"
