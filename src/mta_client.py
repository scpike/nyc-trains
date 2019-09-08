from google.transit import gtfs_realtime_pb2
import nyct_subway_pb2
import requests
import time
import sys
import math
from datetime import datetime
import sqlite3
import os
import csv

def distance(lat1, lng1, lat2, lng2):
    return math.sqrt(((lat1 - lat2) ** 2) + ((lng1 - lng2) ** 2))

def get_stops():
    stops_file = os.environ['MTA_STOPS_FILE']

    stops = []
    with open(stops_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            stops.append((row['stop_id'], row['stop_name'], float(row['stop_lat']), float(row['stop_lon'])))
    return stops

def format_time(timestamp):
    return timestamp.strftime('%H:%M:%S')

def format_delta(delta):
    minutes, seconds = divmod(delta.total_seconds(), 60)
    return "%2d min %2d sec" % (minutes, seconds)

def get_arrivals(stops, feed_id):
    feed = gtfs_realtime_pb2.FeedMessage()
    key = os.environ['MTA_KEY']
    feed_url = 'http://datamine.mta.info/mta_esi.php?key=%s&feed_id=%d' % (key, feed_id)
    response = requests.get(feed_url)
    feed.ParseFromString(response.content)
    arrivals = []
    for entity in feed.entity:
      if entity.HasField('trip_update'):
        upd = entity.trip_update
        for i in entity.trip_update.stop_time_update:
            line = upd.trip.route_id
            dir = "None"
            if upd.trip.Extensions[nyct_subway_pb2.nyct_trip_descriptor] != None:
                dircode = upd.trip.Extensions[nyct_subway_pb2.nyct_trip_descriptor].direction
                if dircode == 1:
                    dir = "North"
                elif dircode == 3:
                    dir = "South"

            arrival_time = i.arrival.time
            arrivals.append((i.stop_id, line, dir, arrival_time))
    return arrivals

def create_tables(cursor):
    cursor.execute('drop table if exists stops')
    cursor.execute('drop table if exists arrivals')
    cursor.execute('''create table stops
                    (stop_id text, stop_name text, stop_lat float, stop_lon float)''')
    cursor.execute('''create table arrivals
                    (stop_id text, line text, direction text, next_train integer)''')


def write_stops(cursor, stops):
    cursor.executemany('insert into stops values (?,?,?,?)', stops)

def write_arrivals(cursor, arrivals):
    cursor.executemany('insert into arrivals values (?,?,?,?)', arrivals)

def refresh(dbfile):
    conn = sqlite3.connect(dbfile)
    dbcursor = conn.cursor()

    create_tables(dbcursor)

    stops = get_stops()

    write_stops(dbcursor, stops)
    conn.commit()

    feeds = [1, 26, 16, 21, 2, 11, 31, 36, 51]
    for feed_id in feeds:
        arrivals = get_arrivals(stops, feed_id)
        write_arrivals(dbcursor, arrivals)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    refresh(sys.argv[1] or 'trains.sqlite')
