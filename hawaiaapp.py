# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station



#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!:<br>
    Available Routes for Hawaii Weather Data:<br/><br>
    Daily Precipitation Totals for last 12 months (2016-08-24 to 2017-08-23):<br>
    /api/v1.0/precipitation<br><br>
    _______________________<br>
    Active Weather Stations in the Data set:<br>
    /api/v1.0/stations<br>
       _______________________<br>
    Temperature Observations for Station USC00519281 for Last Year:<br>
    /api/v1.0/tobs<br>
       _______________________<br>
    Minimum, Maximum and average temperature from a given start date to end of dataset:<br>
    Please enter Start Date in the format: YYYY-MM-DD <br>
    /api/v1.0/<start><br>
       _______________________<br>
    Minimum, Maximum and average temperature from a given start date to a given end date:<br>
    Please enter Start Date followed by End date in the format YYYY-MM-DD/YYYY-MM-DD :<br>
    /api/v1.0/<start>/<end><br>
    ''')

   
@app.route("/api/v1.0/precipitation")
def precipitation():
   # Create our session (link) from Python to the DB
   session = Session(engine)
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= prev_year).all()
   
   # Close session                   
   session.close()

   precip = {date: prcp for date, prcp in precipitation}
   return jsonify(precip) 

    
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(Station.station).all()
    # Close session                   
    session.close()

    stations = list(np.ravel(results))
    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")
def tobs():
     # Create session
    session = Session(engine)

    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    prev_year = dt.datetime.strptime(latest_date, '%Y-%m-%d')- dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= prev_year).all()
    # Close session                   
    session.close()

    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
# Create session
    session = Session(engine)

    sel = [Measurement.date,
           func.min(Measurement.tobs), 
           func.max(Measurement.tobs), 
           func.avg(Measurement.tobs)]
    if not end:
        start = dt.datetime.strptime(start, '%Y-%m-%d')   
        
        results = session.query(*sel).filter(Measurement.date >= start).all()
        session.close()
        print(results)
        temps = list(np.ravel(results)) 
        print(temps)     
        return jsonify(temps)

    else:
        start = dt.datetime.strptime(start, "%Y-%m-%d")
        end = dt.datetime.strptime(end, "%Y-%m-%d")

        results = session.query(*sel).filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()

        session.close()

    # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps=temps)

     

 

if __name__ == '__main__':
    app.run(debug=True)