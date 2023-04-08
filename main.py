import sys
from typing import Optional

import requests
import datetime
import calendar
import argparse


BASE_URL = 'https://api.clickup.com/api/v2/'


def get_success_response(url, headers):
    resp = requests.get(url=url, headers=headers)
    if not 200 <= resp.status_code <= 299:
        raise ValueError(resp.content.decode())
    return resp.json()


def get_teams(headers):
    resp = get_success_response(BASE_URL + 'team/', headers)
    return resp.get('teams')


def get_me(headers):
    resp = get_success_response(BASE_URL + 'user/', headers)
    return resp.get('user')


def milliseconds_to_string(milliseconds):
    s = milliseconds / 1000
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return str(h) + ' hours ' + str(m) + ' minutes'


def get_period(period_type):
    if period_type == 'day':
        now = datetime.datetime.now()
        start_at = int(datetime.datetime(year=now.year, month=now.month, day=now.day).timestamp() * 1000)
        end_at = int(datetime.datetime(year=now.year, month=now.month, day=now.day, hour=23, minute=59).timestamp() * 1000)
    else:
        now = datetime.datetime.now()
        max_days = calendar.monthrange(now.year, now.month)[1]
        start_at = int(datetime.datetime(year=now.year, month=now.month, day=1).timestamp() * 1000)
        end_at = int(datetime.datetime(year=now.year, month=now.month, day=max_days, hour=23, minute=59).timestamp() * 1000)
    return start_at, end_at


def get_tracked_time(headers, team_id, assignee, start_at, end_at):
    url = f'{BASE_URL}team/{team_id}/time_entries?assignee={assignee}'
    if start_at is not None or end_at is not None:
        url = f'{url}&start_date={start_at}&end_date={end_at}'
    resp = get_success_response(url, headers)
    milliseconds = sum([int(x['duration']) for x in resp['data']])
    return milliseconds_to_string(milliseconds)


def main(token: str, period_type: str, workspace: Optional[str] = None):
    headers = {
        'Authorization': token
    }
    teams = get_teams(headers)
    if teams is None:
        raise ValueError('You don\'t have any team')
    me = get_me(headers)
    start_at = end_at = None
    if period_type != 'all':
        start_at, end_at = get_period(period_type)
    for team in teams:
        if workspace is not None and team['name'].lower() != workspace.lower():
            continue
        time = get_tracked_time(headers, team['id'], me['id'], start_at, end_at)
        print(team['name'])
        print('\tTracked: ' + time)


if __name__ == '__main__':
    arguments = argparse.ArgumentParser()
    arguments.add_argument('-t', '--token', type=str, help='ClickUp token')
    arguments.add_argument('-p', '--period', type=str, default='all', help='Period type (day, month, all). Default: all')
    arguments.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    arguments.add_argument('-w', '--workspace', type=str, help='Workspace name')

    args = arguments.parse_args()

    if args.token is None:
        print('ClickUp token is empty.')
        exit(1)

    if args.period not in ['day', 'month', 'all']:
        print('Period %s incorrect' % args.period)
        exit(1)

    main(args.token, args.period, args.workspace)

