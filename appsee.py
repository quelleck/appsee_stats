#!usr/bin/env python3
import requests
import configparser
import urllib.parse
from datetime import date, timedelta


def mon_sun():
    '''
    Returns the previous week's Monday and Sunday
    '''
    day = date.today()
    monday = str(day - timedelta(days=day.weekday()) + timedelta(weeks=-1))
    sunday = str(day - timedelta(days=day.weekday()) + timedelta(days=6,
                                                                 weeks=-1))
    return monday, sunday


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
    url_build['fromdate'] = mon_sun()[0]
    url_build['todate'] = mon_sun()[1]
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
    print("From {} to {}".format(mon_sun()[0], mon_sun()[1]))
    for app in apps:
        crashes_sessions(app)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.conf")
    main()
