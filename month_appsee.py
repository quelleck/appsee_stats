#!usr/bin/env python3
import requests
import configparser
import urllib.parse
import datetime
import calendar
import decimal

def last_month():
    now = datetime.datetime.now()
    year = now.year
    month = now.month - 1
    if now.month == 1:
        year = now.year - 1
        month = 12
    days_in_month = (calendar.monthrange(year, month))[1]
    last_day = datetime.date(year, month, days_in_month)
    first_day = datetime.date(year, month, 1)
    return first_day, last_day


def build_url(app, type, ver):
    '''
    Returns the correct URL structure for each request.
    '''
    url_build = {}
    if ver:
        url_build['appversion'] = config[app]['appversion']
    if type == "crashes":
        url = 'https://api.appsee.com/crashes/daily?'
    elif type == "sessions":
        url = 'https://api.appsee.com/analytics/usage?'
    url_build['apikey'] = config[app]['apikey']
    url_build['apisecret'] = config[app]['apisecret']
    url_build['fromdate'] = last_month()[0]
    url_build['todate'] = last_month()[1]
    url_build['platform'] = config[app]['platform']
    values = urllib.parse.urlencode(url_build)
    return ("{}{}".format(url, values))


def tot_crashed(app, device):
    r = requests.get("{}&devicetype={}".format(
        build_url(app, 'crashes', False), device))
    return r.json()['TotalCrashedSessions']


def tot_sessions(app, device):
    r = requests.get("{}&devicetype={}".format(
        build_url(app, 'sessions', False), device))
    return r.json()['Usage']['Sessions']


def space():
    for x in range(0, 3):
        print('')


def crashes_sessions(app):
    devices = config[app]['devices'].split(' ')
    space()
    print("{}___{}___{}".format('\033[1m', app, '\033[0m'))
    all_sessions = []
    phone_sessions = []
    tablet_sessions = []
    for device in devices:
        print("{}---".format(device))
        total_crashes = tot_crashed(app, device)
        total_sessions = tot_sessions(app, device)
        print("All crashes: {}".format(total_crashes))
        print("All sessions: {}".format(total_sessions))
        crash_math(total_sessions, total_crashes)
        all_sessions += [total_crashes, total_sessions]
        if device == 'iPhone' or device == 'Phone':
            phone_sessions += [total_crashes, total_sessions]
        else:
            tablet_sessions += [total_crashes, total_sessions]
    decimal.getcontext().prec = 2
    try:
        overall = ((D(all_sessions[0]) + D(all_sessions[2])) / D((all_sessions[1]) + D(all_sessions[3]))) * 100
    except IndexError:
        overall = (D(all_sessions[0]) / D(all_sessions[1])) * 100
    print("{}{}{}: {}%".format('\033[1m', 'Overall', '\033[0m', D(overall)))
    return all_sessions, phone_sessions, tablet_sessions


def crash_math(tot_sessions, tot_crashed):
    decimal.getcontext().prec = 2
    crash_percent = (D(tot_crashed) / D(tot_sessions))
    print("Crash Percent: {}%".format(crash_percent * 100))


def main():
    global D
    D = decimal.Decimal
    apps = config.sections()
    print("From {} to {}".format(last_month()[0], last_month()[1]))
    all_stats = []
    phone_stats = []
    tablet_stats = []
    for app in apps:
        all_sessions, phone_sessions, tablet_sessions = crashes_sessions(app)
        all_stats += all_sessions
        phone_stats += phone_sessions
        tablet_stats += tablet_sessions
    print("{}All Phone Apps Overall Crash Percentage: {}{}".format('\033[1m', D(sum(phone_stats[::2])) / D(sum(phone_stats[1::2])) * 100, '\033[0m'))
    print("{}All Tablet Apps Overall Crash Percentage: {}{}".format('\033[1m', D(sum(tablet_stats[::2])) / D(sum(tablet_stats[1::2])) * 100, '\033[0m'))
    print("{}All Apps Overall Crash Percentage: {}{}".format('\033[1m', D(sum(all_stats[::2])) / D(sum(all_stats[1::2])) * 100, '\033[0m'))


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.conf")
    main()
