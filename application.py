import os
import datetime

from flask import Flask, redirect, request, render_template, jsonify, make_response, Response
from flask_assets import Bundle, Environment
import pandas as pd
import sqlalchemy


username = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
host = os.getenv('POSTGRES_HOST')
port = int(os.getenv('POSTGRES_PORT'))
database = os.getenv('POSTGRES_DB')
sslmode = 'require'

engine = sqlalchemy.create_engine(f'postgresql://{username}:{password}@{host}:{port}/{database}')

application = Flask(__name__)
assets = Environment(application)
css = Bundle("src/main.css", output="dist/main.css", filters="postcss")
js = Bundle("src/*.js", output="dist/main.js")  # new

assets.register("css", css)
assets.register("js", js)
css.build()
js.build()

locations = [{'name': 'Aldersgate', 'address': '200 Aldersgate Street, London, EC1A 4HD', 'id': '76'},
             {'name': 'Bank', 'address': '5 Old Broad Street, London, EC2N 1DW', 'id': '29'},
             {'name': 'Broadgate / Liverpool Street', 'address': 'One Exchange Place, London, EC2M 2QT', 'id': '33'},
             {'name': 'Bromley', 'address': 'The Lido, Baths Road, Bickley, Bromley, BR2 9RB', 'id': '34'},
             {'name': 'Canary Riverside', 'address': 'West Ferry Circus, Canary Wharf, London, E14 8RR', 'id': '35'},
             {'name': 'Cannon Street / Walbrook', 'address': 'The Walbrook Building, 97 Cannon Street, London, EC4N 5AE', 'id': '953'},
             {'name': 'Chelmsford', 'address': 'New Writtle Street, Chelmsford, CM2 0RR', 'id': '27'},
             {'name': 'Chiswick Park', 'address': 'Building 3, 566 Chiswick High Road, London, W4 5YA', 'id': '421'},
             {'name': 'Chiswick Riverside', 'address': 'Riverside Drive, Dukes Meadows, Chiswick, London, W4 2SX', 'id': '405'},
             {'name': 'Clapham', 'address': '4-20 North Street, London, SW4 0HG', 'id': '38'},
             {'name': 'Clearview', 'address': 'Little Warley Hall Lane, Little Warley, Brentwood, CM13 3EN', 'id': '438'},
             {'name': 'Crouch End', 'address': '31 Topsfield Parade, Tottenham Lane, London, N8 8PT', 'id': '39'},
             {'name': 'Fulham Pools', 'address': 'Normand Park, Lillie Road, London, SW6 7ST', 'id': '47'},
             {'name': 'Hammersmith', 'address': 'Shortlands, 181 Hammersmith Road, London, W6 8BT', 'id': '48'},
             {'name': 'Islington Angel', 'address': 'v333 Goswell Road, Islington, London, EC1V 7DG', 'id': '12'},
             {'name': 'Kensington', 'address': '3rd Floor, 17A Old Court Place, London, W8 4PL', 'id': '51'},
             {'name': 'Mayfair', 'address': 'Hereford House, 64 North Row, London, W1K 7DA', 'id': '56'},
             {'name': 'Mill Hill', 'address': '34 Langstone Way, Mill Hill East, London, NW7 1GU', 'id': '57'},
             {'name': 'Moorgate', 'address': '33 Bunhill Row, London, EC1Y 8LP', 'id': '59'},
             {'name': 'Northampton Collingtree Park', 'address': '91 Windingbrook Lane, Collingtree Park, Northampton, NN4 0EB', 'id': '415'},
             {'name': 'Northampton High Street', 'address': 'Northampton High Street, Northampton, NN4 8QE', 'id': '416'},
             {'name': 'Northampton Riverside Park', 'address': 'Ferris Row, Riverside Business Park, Northampton, NN3 9HX', 'id': '2'},
             {'name': 'Northampton West End', 'address': 'Northampton West End, Northampton, NN3 8QE', 'id': '3'},
             {'name': 'Notting Hill', 'address': '119-131 Lancaster Road, London, W11 1QT', 'id': '60'},
             {'name': 'Nottingham', 'address': 'Low Level Station, The Great Northern Close, London Road, Nottingham, NG2 3AE', 'id': '61'},
             {'name': 'Repton Park', 'address': 'Repton Park, Manor Road, Woodford Green, IG8 8GN', 'id': '422'},
             {'name': 'Salford Quays', 'address': 'Unit F31 Lowry Outlet Mall, The Quays, Salford, M50 3AH', 'id': '452'},
             {'name': 'Sheffield Broadfield Park', 'address': '300 Broadfield Park, Broadfield Road, Sheffield, S8 0XQ', 'id': '15'},
             {'name': 'Solihull', 'address': 'Blythe Gate, Blythe Valley Park, Shirley, Solihull, B90 8AT', 'id': '6'},
             {'name': 'Strand', 'address': 'Shell-Mex House, 80 The Strand, London, WC2R 0DT', 'id': '68'},
             {'name': 'Streatham', 'address': '20 Ockley Road, London, SW16 1UB', 'id': '69'},
             {'name': 'Swiss Cottage', 'address': 'Unit 2 Level 1 02 Centre, 255 Finchley Road, London, NW3 6LU', 'id': '410'},
             {'name': 'Thundersley', 'address': '200 Rayleigh Road, Thundersley, Benfleet, SS7 3YN', 'id': '16'},
             {'name': 'Twickenham', 'address': 'South Stand Twickenham Rugby Stadium, 196 Whitton Road, Twickenham, TW2 7BA', 'id': '75'},
             {'name': 'Wandsworth Smugglers Way', 'address': 'Wandsworth Riverside, West Smugglers Way, Wandsworth, London, SW18 1DG', 'id': '425'},
             {'name': 'Wimbledon Worple Road', 'address': '21-33 Worple Road, Wimbledon, London, SW19 4JS', 'id': '408'},
             ]

@application.route('/', methods=['GET'])
def app_check():
    nrows = 100
    data = pd.read_sql_query(
        """
        SELECT name, date_created, percentage
        FROM clubs
        ORDER BY "date_created" DESC
        LIMIT {}
        """.format(nrows), con=engine)
    data['date_created'] = pd.to_datetime(data['date_created'])
    resp_list = []
    for i in locations:
        # get last value for each location
        try:
            last_value = data[data['name'] == i['name']]['percentage'].iloc[0]
            resp_list.append({'name': i['name'], 'address': i['address'], 'percentage': int(last_value), 'id': i['id']})

        except IndexError:
            print('no data for {}'.format(i['name']))
    print(resp_list)

    #return jsonify(resp_dict)
    return render_template('index.html', data=resp_list)

@application.route('/gym', methods=['GET'])
def gym():
    gym_id = request.args.get('gym_id')
    for each in locations:
        if gym_id == each['id']:
            gym_name = each['name']
            gym_address = each['address']
    data = pd.read_sql_query(
        """
        SELECT name, date_created, percentage
        FROM clubs
        WHERE "name" = '{}'
        ORDER BY "date_created" DESC
        LIMIT 10
        """.format(gym_name), con=engine)
    # get most recent value
    data['date_created'] = pd.to_datetime(data['date_created'])
    last_value = data[data['name'] == gym_name]['percentage'].iloc[0]
    first_value = data[data['name'] == gym_name]['percentage'].iloc[-1]
    # get pct change

    if last_value == 0 or first_value == 0:
        pct_change = 0
    else:
        pct_change = round((last_value - first_value) / first_value * 100, 2)


    return render_template('gym.html', gym_id=gym_id, gym_name=gym_name, gym_address=gym_address, last_value=last_value, pct_change=pct_change)

@application.route('/data/gym', methods=['GET'])
def data_json():
    gym_id = request.args.get('gym_id')
    nrows = 300
    # get gym name from id
    gym_name = [i['name'] for i in locations if i['id'] == gym_id][0]
    data = pd.read_sql_query(
        """
        SELECT name, date_created, percentage
        FROM clubs
        WHERE "name" = '{}'
        ORDER BY "date_created" DESC
        LIMIT {}
        """.format(gym_name, nrows), con=engine)
    data['date_created'] = pd.to_datetime(data['date_created'])
    today = datetime.datetime.now().date()
    now = datetime.datetime.now() + datetime.timedelta(hours=1)
    data = data[data['date_created'].dt.date == today]
    data = data.drop(columns=['name'])
    data['date_created'] = data['date_created'].dt.strftime('%H:%M:%S')
    data = data.rename(columns={'date_created': 'date'})
    data['percentage'] = data['percentage'].apply(lambda x: 100 if x > 100 else x)
    last_value = data.iloc[0]
    lv_temp = {"date": last_value['date'], "predicted": last_value['percentage']}

    data = data.rename(columns={'percentage': 'today'})
    data = data[data['date'] < str(now.time())]


    # second dataframe for predictions
    data2 = pd.read_sql_query(
        """
        SELECT name, date_predicted, percentage
        FROM predictions
        WHERE "name" = '{}' AND "date_predicted" > '{}'
        ORDER BY "date_predicted" DESC
        LIMIT {}
        """.format(gym_name, str(now), nrows), con=engine)
    data2['date_predicted'] = pd.to_datetime(data2['date_predicted'])
    # keep only todays data
    data2 = data2[data2['date_predicted'].dt.date == today]
    data2 = data2.drop(columns=['name'])
    data2['date_predicted'] = data2['date_predicted'].dt.strftime('%H:%M:%S')
    data2 = data2.rename(columns={'date_predicted': 'date'})
    data2['percentage'] = data2['percentage'].apply(lambda x: 100 if x > 100 else x)
    data2['percentage'] = data2['percentage'].apply(lambda x: 0 if x < 0 else x)
    lv_temp = pd.DataFrame(lv_temp, index=[0])


    data2 = data2.rename(columns={'percentage': 'predicted'})
    now = datetime.datetime.now() + datetime.timedelta(hours=1)
    data2 = data2[data2['date'] > str(now.time())]
    data2 = pd.concat([data2, lv_temp], axis=0)
    # concat data and data2
    data = pd.concat([data, data2])

    # rename date to time
    data = data.rename(columns={'date': 'time'})
    # order by time desc
    data = data.sort_values(by=['time'], ascending=True)
    # remove everything before 6am
    data = data[data['time'] > '06:00:00']

    resp_dict = data.to_dict(orient='records')


    return Response(data.to_csv(index=False), mimetype='text/csv')


if __name__ == '__main__':
    application.run()
