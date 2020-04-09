import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from sqlalchemy import and_
from sqlalchemy import or_

from flask import Flask, jsonify

import datetime as dt
from datetime import timedelta

import pandas as pd

#################################################
# Database Setup
#################################################
#engine = create_engine("sqlite:///titanic.sqlite")
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement;
Station     = Base.classes.station;

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
            f"Available Routes:<br>"
            f"/api/v1.0/prcp<br>"
            f"/api/v1.0/stations<br>"
            f"/api/v1.0/tobs<br>"
            f"/api/v1.0/(start)<br>"
            f"/api/v1.0/(start, end)"
            )

#precipitation
#Convert the query results to a dictionary
# using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/prcp")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation data"""
    # Query all passengers
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()
    
    # Convert list of tuples into normal list
    # all_names = list(np.ravel(results))
    # Create a dictionary from the row data and append to a list of all_prcp
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

#stations
#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations data including the name, latitude, longitude of each station"""
    # Query all passengers
    results = session.query(Station.name, Station.latitude, Station.longitude).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for name, age, sex in results:
        station_dict = {}
        station_dict["name"] = name
        station_dict["latitude"] = age
        station_dict["longitude"] = sex
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def temperature_obs():
    session = Session(engine)

    """Return a list of tobs (temperature observation) data for the most active station
        for the last year of data available. """
#    Query the dates and temperature observations of the most active station
#    for the last year of data.
    max_date = session.query(func.max(Measurement.date)).first()
    last_date = dt.datetime.strptime(max_date[0], '%Y-%m-%d')
    one_year_before = last_date - timedelta(days=365)

# Convert the DATE types back to strings
    last_date_str       = last_date.strftime("%Y-%m-%d")
    one_year_before_str = one_year_before.strftime("%Y-%m-%d")
    
    # Create our session (link) from Python to the DB
    
    # Most Active Station
    most_active_stations = session.query(Station.name, Measurement.station, func.count(Measurement.station))\
        .group_by(Measurement.station).order_by(desc(func.count(Measurement.station)))\
        .filter(Measurement.station == Station.station)

    most_active_station = (most_active_stations[0][1])

    results = session.query(Measurement.station, Measurement.tobs, Measurement.date)\
        .filter(Measurement.station == most_active_station) \
        .filter(and_(Measurement.date >= one_year_before_str, \
                     Measurement.date <= last_date_str))

    session.close()

# Create a dictionary from the row data and append to a list of all_passengers
    all_temperatures = []
    for station, tobs, date in results:
        temperature_dict = {}
        temperature_dict["Date"] = date
        #Check during Development
        #temperature_dict["Station"] = station
        temperature_dict["Temperature_Observed"] = tobs
        all_temperatures.append(temperature_dict)
# Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(all_temperatures)


@app.route("/api/v1.0/<start>")
def get_temperatures_s(start):
    # calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return TMIN, TAVG, and TMAX for all dates greater than and equal to the start date"""
    # Query all temperatures
    results = session.query(Measurement.date, Measurement.prcp, Measurement.tobs,)\
            .filter(and_(Measurement.date >= start))
    
    max_date = session.query(func.max(Measurement.date)).first()
    last_date = dt.datetime.strptime(max_date[0], '%Y-%m-%d')
    session.close()

    # Set the start and end date
    start_date = pd.to_datetime(start)
    end_date   = pd.to_datetime(last_date)

    #Use the start and end date to create a range of dates
    range_of_dates = pd.date_range(start=start_date, end=end_date)
    #range_of_dates

    # Strip off the year and create a list of %m-%d strings
    dates_list = []
    for r in range_of_dates:
    #print(r.strftime("%m-%d"))
        dates_list.append([r.strftime("%m-%d"), r.strftime("%Y-%m-%d")])

    # Loop through the list of %m-%d strings and calculate the normals for each date
    normals = []
    for day, date in dates_list:
        dn = daily_normals(day)
        normals.append([date, dn[0][0], dn[0][1], dn[0][2]])

    return jsonify(normals)


@app.route("/api/v1.0/<start>/<end>")
def get_temperatures(start, end=""):
    # calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
    # And less than and equal to the end date
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
       and less than and equal to the end date"""
    # Query all temperatures
    results = session.query(Measurement.date, Measurement.prcp, Measurement.tobs,)\
        .filter(and_(Measurement.date >= start))
    
    max_date = session.query(func.max(Measurement.date)).first()
    last_date = dt.datetime.strptime(max_date[0], '%Y-%m-%d')
    session.close()

    # Set the start and end date
    start_date = pd.to_datetime(start)
    end_date   = pd.to_datetime(end)
    
    #Use the start and end date to create a range of dates
    range_of_dates = pd.date_range(start=start_date, end=end_date)
    #range_of_dates
    
    # Strip off the year and create a list of %m-%d strings
    dates_list = []
    for r in range_of_dates:
        #print(r.strftime("%m-%d"))
        dates_list.append([r.strftime("%m-%d"), r.strftime("%Y-%m-%d")])
    
    # Loop through the list of %m-%d strings and calculate the normals for each date
    normals = []
    for day, date in dates_list:
        dn = daily_normals(day)
        normals.append([date, dn[0][0], dn[0][1], dn[0][2]])
    
    return jsonify(normals)

    
# Create a query that will calculate the daily normals
# (i.e. the averages for tmin, tmax, and tavg for all historic data matching a specific month and day)
def daily_normals(date):
    """Daily Normals.
        
        Args:
        date (str): A date string in the format '%m-%d'
        
        Returns:
        A list of tuples containing the daily normals, tmin, tavg, and tmax
        
        """
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    return session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) == date).all()
    session.close()

#daily_normals("01-01")


if __name__ == '__main__':
    app.run(debug=True)
