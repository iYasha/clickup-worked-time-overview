import sys
import requests
import datetime
import calendar


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
    url = BASE_URL + 'team/%s/time_entries?start_date=%s&end_date=%s&assignee=%s' % (team_id, start_at, end_at, assignee)
    resp = get_success_response(url, headers)
    milliseconds = sum([int(x['duration']) for x in resp['data']])
    return milliseconds_to_string(milliseconds)


def main(token):
    headers = {
        'Authorization': token
    }
    teams = get_teams(headers)
    if teams is None:
        raise ValueError('You don\'t have any team')
    me = get_me(headers)
    for team in teams:
        start_at_day, end_at_day = get_period('day')
        start_at_month, end_at_month = get_period('month')
        
        time_day = get_tracked_time(headers, team['id'], me['id'], start_at_day, end_at_day)
        time_month = get_tracked_time(headers, team['id'], me['id'], start_at_month, end_at_month)
        print(team['name'])
        print('\tDay: ' + time_day)
        print('\tMonth: ' + time_month)


if __name__ == '__main__':

    with open('TOKEN.txt', 'r') as file:
        token = file.read().rstrip()
        file.close()
        if len(token) > 0:
            main(token)
        else:
            print('Error: Paste token into TOKEN.txt at script root folder.')

