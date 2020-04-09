import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from sqlalchemy import and_
from sqlalchemy import or_

from flask import Flask, jsonify


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
            f"/api/v1.0/(start)<br>"
            f"/api/v1.0/(start, end)"
            )


#precipitation
#Convert the query results to a dictionary
#using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/prcp")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    
    # Convert list of tuples into normal list
    # all_names = list(np.ravel(results))

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

    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all passengers
    results = session.query(Station.name, Station.latitude, Station.longitude).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_stations = []
    for name, age, sex in results:
        station_dict = {}
        station_dict["name"] = name
        station_dict["latitude"] = age
        station_dict["longitude"] = sex
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/<start>")
def get_temperatures_s(start):
    end=""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all temperatures
    if end=="":
        results = session.query(Measurement.date, Measurement.prcp, Measurement.tobs,)\
            .filter(and_(Measurement.date >= start))
    else:
        results = session.query(Measurement.date, Measurement.prcp, Measurement.tobs,)\
            .filter(and_(Measurement.date >= start, Measurement.date <= end))

    session.close()
# Create a dictionary from the row data and append to a list of all_passengers
    all_temperatures = []
    for d, p, t in results:
        temperature_dict = {}
        temperature_dict["Date"] = d
        temperature_dict["Precipitation"] = p
        temperature_dict["Temperature_Observed"] = t
        all_temperatures.append(temperature_dict)

    return jsonify(all_temperatures)


@app.route("/api/v1.0/<start>/<end>")
def get_temperatures(start, end=""):
  # Create our session (link) from Python to the DB
    session = Session(engine)
           
    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all temperatures
    if end=="":
            results = session.query(Measurement.date, Measurement.prcp, Measurement.tobs,)\
           .filter(and_(Measurement.date >= start))
    else:
            results = session.query(Measurement.date, Measurement.prcp, Measurement.tobs,)\
           .filter(and_(Measurement.date >= start, Measurement.date <= end))
           
    session.close()
           # Create a dictionary from the row data and append to a list of all_passengers
    all_temperatures = []
    for d, p, t in results:
           temperature_dict = {}
           temperature_dict["Date"] = d
           temperature_dict["Precipitation"] = p
           temperature_dict["Temperature_Observed"] = t
           all_temperatures.append(temperature_dict)
           
    return jsonify(all_temperatures)
    
# Create a query that will calculate the daily normals
# (i.e. the averages for tmin, tmax, and tavg for all historic data matching a specific month and day)
def daily_normals(date):
    """Daily Normals.
        
        Args:
        date (str): A date string in the format '%m-%d'
        
        Returns:
        A list of tuples containing the daily normals, tmin, tavg, and tmax
        
        """
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    return session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) == date).all()

#daily_normals("01-01")



if __name__ == '__main__':
    app.run(debug=True)
