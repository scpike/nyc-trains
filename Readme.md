This is an inverted version of the MTA's subway time
(http://subwaytime.mta.info/). It uses your browser's location to find
nearby stations.

You need an API key from http://datamine.mta.info/ to use this.

Set three environment variables:

 - `MTA_STOPS_FILE` - path to the stops.txt file from http://web.mta.info/developers/developer-data-terms.html#data
 - `TRAINS_DBFILE` - file path for the sqlite file the app will create to sync arrival information to
 - `MTA_KEY` - Your API key from the MTA

`mta_client.py` syncs trip updates from the MTA's real time GTFS feed to two tables in a sqlite database:

```
    create table stops
        (stop_id text, stop_name text, stop_lat float, stop_lon float)
```


```
    create table arrivals
        (stop_id text, line text, direction text, next_train integer)
```

`trains.py` is a flask API that takes a latitude and longitude gives
upcoming arrival information for nearby stations.
