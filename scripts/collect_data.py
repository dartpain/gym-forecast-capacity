import requests
import json
import psycopg2
import datetime
import os

username = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
host = os.getenv('POSTGRES_HOST')
port = int(os.getenv('POSTGRES_PORT'))
database = os.getenv('POSTGRES_DB')
sslmode = 'require'

conn = psycopg2.connect(dbname=database, user=username, password=password, host=host, port=port)
cur = conn.cursor()

def generate_new_token():
    try:
        response = requests.post(
            url="https://api.virginactive.co.uk/auth/login",
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
            data=json.dumps({
                "GrantType": "password",
                "Client": "android",
                "password": os.getenv('PASSWORD'),
                "Scope": "api.virginactive.co.uk",
                "Country": "GB",
                "username": os.getenv('USERNAME')
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        return response.json()
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def send_request(token):
    # Get club stats
    # GET https://api.virginactive.co.uk/club/clubs/details/

    try:
        response = requests.get(
            url="https://api.virginactive.co.uk/club/clubs/details/",
            headers={
                "Authorization": token,
            },
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        return response.json()
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

# get token
cur.execute("SELECT * FROM tokens WHERE id = %s", ('alex',))
token_alex = cur.fetchone()
current_token = token_alex[1]
print(token_alex)
# if token created is more than 1 hour old, get new token
if (datetime.datetime.now() - token_alex[2]).seconds > 3600:
    print('token is old')
    token_alex = generate_new_token()['token']
    print(token_alex)
    current_token = token_alex
    cur.execute("UPDATE tokens SET token = %s, date_created = %s WHERE id = %s", (token_alex, datetime.datetime.now(), 'alex'))
    conn.commit()

club_data = send_request(current_token)
club_data_list = []
for club in club_data['clubs']:
    print(club)
    try:
        percentage = (club['capacity']['currentlyCheckedInCount'] / club['capacity']['maximumAllowedCheckedIn']) * 100
        percentage = int(percentage)
    except ZeroDivisionError:
        percentage = 0
    club_data_list.append({'id': str(club['clubId']) + str(datetime.datetime.now()), 'name': club['name'], 'capacity_current': club['capacity']['currentlyCheckedInCount']
                           , 'capacity_max': club['capacity']['maximumAllowedCheckedIn']
                           , 'date_created': datetime.datetime.now() + datetime.timedelta(hours=1), 'percentage': percentage})



# create table clubs
cur.execute("CREATE TABLE IF NOT EXISTS clubs (id VARCHAR(255) PRIMARY KEY, name VARCHAR(255), capacity_current INTEGER, capacity_max INTEGER, date_created TIMESTAMP, percentage INTEGER)")


# parse club_data_list and write to db
for club in club_data_list:
    cur.execute("INSERT INTO clubs (id, name, capacity_current, capacity_max, date_created, percentage) VALUES (%s, %s, %s, %s, %s, %s)",
                (club['id'], club['name'], club['capacity_current'], club['capacity_max'], club['date_created'], club['percentage']))

    conn.commit()
cur.close()
conn.close()

