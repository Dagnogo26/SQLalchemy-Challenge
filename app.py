import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///data.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measure= Base.classes.measurement

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
        f"Available Routes:<br/>"
        f"Return a list of precipitation  data including the date<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"Return a list of stations<br/>"
        f"/api/v1.0/stations<br/>"
        f"Return the dates and temperature observations of the most active station for the last year of data<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Return TMIN, TAVG, and TMAX for all dates greater than and equal to the start date<br/>"
        f"/api/v1.0/date<br/>"
        f"Return calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation  data including the date, and prcp """
    # Query 
    # find the recent date

    date= session.query(Measure.date).order_by(desc(Measure.date)).first()
    recent = date[0]

    #find last year date

    months_12 = dt.datetime.strptime(str(recent), '%Y-%m-%d') - dt.timedelta(days=365)
    year_ago= months_12.strftime('%Y-%m-%d')

    #Query the dates and temperature observations of the most active station for the last year of data.

    results = session.query(Measure.date, Measure.prcp).filter(Measure.date >= year_ago).all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipitation
    precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query 
    station_x= session.query(Measure.station).group_by(Measure.station).all()

    session.close()

    # Convert list of tuples into normal list

    all_stations = list(np.ravel(station_x))
   
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature data including the date, and prcp """
    # find the recent date

    date= session.query(Measure.date).order_by(desc(Measure.date)).first()
    recent = date[0]

    #find last year date

    months_12 = dt.datetime.strptime(str(recent), '%Y-%m-%d') - dt.timedelta(days=365)
    year_ago= months_12.strftime('%Y-%m-%d')

    #Query the dates and temperature observations of the most active station for the last year of data.

    data_temp= session.query(Measure.date, Measure.tobs).filter(Measure.date >= year_ago).\
           filter_by(station= "USC00519281").all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipitation
    last_year_temperature = []
    for date, tobs in data_temp:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Temperature"] = tobs
        last_year_temperature.append(temp_dict)

    return jsonify(last_year_temperature)  

@app.route("/api/v1.0/<date>")
def startonlydate(date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return information"""
    # Query TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    start_date= session.query(func.min(Measure.tobs), func.max(Measure.tobs), func.avg(Measure.tobs)).\
            filter(Measure.date >= date).all()

    session.close()

    # Convert list of tuples into normal list

    start_date_info = list(np.ravel(start_date))
   
    return jsonify(start_date_info)  

@app.route("/api/v1.0/<start>/<end>")
def date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return information"""
    # Query calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
    dates= session.query(func.min(Measure.tobs), func.max(Measure.tobs), func.avg(Measure.tobs)).\
            filter(Measure.date >= start).filter(Measure.date <= end).all()

    session.close()

    # Convert list of tuples into normal list

    date_info = list(np.ravel(dates))
   
    return jsonify(date_info)         

if __name__ == '__main__':
    app.run(debug=True)
