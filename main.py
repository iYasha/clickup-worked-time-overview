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


def main(token, period_type):
    headers = {
        'Authorization': token
    }
    teams = get_teams(headers)
    if teams is None:
        raise ValueError('You don\'t have any team')
    me = get_me(headers)
    for team in teams:
        start_at, end_at = get_period(period_type)
        time = get_tracked_time(headers, team['id'], me['id'], start_at, end_at)
        print(team['name'])
        print('\tTracked: ' + time)


if __name__ == '__main__':
    available_period = ['day', 'month']
    period = 'month'

    if len(sys.argv) == 0:
        print('ClickUp token is empty.')
        exit(1)
    if len(sys.argv) == 3:
        if sys.argv[2] in available_period:
            period = sys.argv[2]
        else:
            print('Period %s incorrect' % sys.argv[2])
            exit(1)
    main(sys.argv[1], period)

