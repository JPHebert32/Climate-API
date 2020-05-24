import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station 

session = Session(engine)
#################################################
# Flask Setup Weather app
#################################################
app = Flask(__name__)
# Create our session (link) from Python to the DB

# Design a query to retrieve the last 12 months of precipitation data and plot the results
# Calculate the date 1 year ago from the last data point in the database
current_date = (session.query(Measurement.date)
                     .order_by(Measurement.date.desc())
                     .first())

#extract string from query object
current_date = list(np.ravel(current_date))[0]

#convert date string to datetime object
current_date = dt.datetime.strptime(current_date, '%Y-%m-%d')

#extract year, month, and day as integers
current_yr = int(dt.datetime.strftime(current_date, '%Y'))
current_month = int(dt.datetime.strftime(current_date, '%m'))
current_day = int(dt.datetime.strftime(current_date, '%d'))

#calculate one year before latest date
previous_yr = dt.date(current_yr, current_month, current_day) - dt.timedelta(days=365)
previous_yr = dt.datetime.strftime(previous_yr, '%Y-%m-%d')

session.close()
#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (f"Welcome to Surf's Up!: Hawaii Climate API<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/<start><br/>"
            f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Precipitation Data"""
    # Query all Precipitation Data including date, prcp,
    results = (session.query(Measurement.date, Measurement.prcp)
                      .filter(Measurement.date > previous_yr)
                      .order_by(Measurement.date)
                      .all())
    session.close()

    # Convert into dicionarty using 'date' as the KEY an 'prcp' as VALUE
    precipitation_data = []
    for result in results:
        precipitation_dict = {result.date: result.prcp}
        precipitation_data.append(precipitation_dict)

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Stations"""
    # Query all Stations
    results = session.query(Station.name).all()
    
    # Convert list of tuples into normal list
    stations_id = list(np.ravel(results))

    return jsonify(stations_id)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Temperature Data"""
    # Query all Temperature Data including date, tobs, Most active station
    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement ==
                          Measurement.date > previous_yr)
                      .order_by(Measurement.date)
                      .all())
    session.close()

    # Convert into list
    temperature_data = []
    for result in results:
        temperature_dict = {result.date: result.tobs, "Station": result.most_active}
        temperature_data.append(temperature_dict)

    return jsonify(temperature_data)









if __name__ == '__main__':
    app.run(debug=True)