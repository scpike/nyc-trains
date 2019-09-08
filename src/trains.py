from flask import Flask, request, url_for
from collections import OrderedDict
from datetime import datetime

import mta_client
import sqlite3
import json
import os

static_path = os.path.abspath(os.path.dirname(__file__)) + '/../web/'
app = Flask(__name__, static_folder=static_path, static_url_path="/assets")
last_refresh = None

dbfile = os.environ['TRAINS_DBFILE']

def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%I:%M:%S%p')

def format_delta(delta):
    minutes, seconds = divmod(delta, 60)
    if (minutes <= 2):
        return "%2dm %2ds" % (minutes, seconds)
    else:
        return "%2dm" % minutes

@app.route('/')
def home():
    return app.send_static_file('html/index.html')

@app.route('/trains.json')
def trains():
    global last_refresh
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    if (last_refresh == None or
        (datetime.now() - last_refresh).total_seconds() > 5):
        mta_client.refresh(dbfile)
        last_refresh = datetime.now()

    conn = sqlite3.connect(dbfile)
    dbcursor = conn.cursor()

    fmt = """select stop_name, stop_lat, stop_lon, line, direction,
case when next_train = 0 then 0 else (next_train - strftime('%s','now')) END wait_time_seconds,
next_train
from stops
inner join arrivals on arrivals.stop_id = stops.stop_id
where (({lat} - stop_lat) * ({lat} - stop_lat) +
		 ({lon} - stop_lon) * ({lon} - stop_lon)) < 0.00005
	and (next_train - strftime('%s','now')) < 1800
        and (next_train == 0 or (next_train - strftime('%s','now')) >= 0)
order by direction,
		(({lat} - stop_lat) * ({lat} - stop_lat) +
		({lon} - stop_lon) *  ({lon} - stop_lon)),
		(next_train - strftime('%s','now'))"""
    query = fmt.format(lat=latitude, lon=longitude)

    result = {}
    for row in dbcursor.execute(query):
        stop_name = row[0]
        line = row[3]
        direction = "Uptown" if row[4] == "North" else "Downtown"
        wait_time = row[5]
        arrival_time = row[6]

        if not direction in result:
            result[direction] = OrderedDict()
        dir = result[direction]

        if not stop_name in dir:
            dir[stop_name] = OrderedDict()

        if not line in dir[stop_name]:
            dir[stop_name][line] = []

        dir[stop_name][line].append({
            "wait_time": format_delta(wait_time),
            "arrival_time": format_time(arrival_time)
            })

    return json.dumps(result)

if __name__ == '__main__':
    app.run()
