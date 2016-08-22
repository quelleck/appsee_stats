#!usr/bin/env python3
import requests
import configparser
import urllib.parse
import datetime
import calendar


def last_month():
    '''
    Returns the previous month
    2016-07-01
    '''
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


def ver_tot_crashed(app, device):
    r = requests.get("{}&devicetype={}".format(
        build_url(app, 'crashes', True), device))
    return r.json()['TotalCrashedSessions']


def ver_tot_sessions(app, device):
    r = requests.get("{}&devicetype={}".format(
        build_url(app, 'sessions', True), device))
    return r.json()['Usage']['Sessions']


def space():
    for x in range(0, 3):
        print('')


def crashes_sessions(app):
    devices = config[app]['devices'].split(' ')
    numbers = {}
    space()
    print("{}___{}___{}".format('\033[1m', app, '\033[0m'))
    for device in devices:
        print("{}---".format(device))
        total_crashes = tot_crashed(app, device)
        total_sessions = tot_sessions(app, device)
        ver_crashes = ver_tot_crashed(app, device)
        ver_sessions = ver_tot_sessions(app, device)
        print("All crashes: {}".format(total_crashes))
        print("All sessions: {}".format(total_sessions))
        print("{} crashes: {}".format(config[app]['appversion'], ver_crashes))
        print("{} sessions: {}".format(config[app]['appversion'],
                                       ver_sessions))


def main():
    apps = config.sections()
    print("From {} to {}".format(last_month()[0], last_month()[1]))
    for app in apps:
        crashes_sessions(app)

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.conf")
    main()
