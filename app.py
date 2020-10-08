import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()
# reflect the tables
base.prepare(engine, reflect=True)

# Save reference to the table
measurement = base.classes.measurement
bob = base.classes.station

#create session
session = Session(engine)

#function for range of dates
def calc_temps(start_date, end_date):
    return session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################

@app.route("/")
def main():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    #query
    last_date_query = session.query(func.max(func.strftime("%Y-%m-%d", measurement.date))).all()
    last_date_string = last_date_query[0][0]
    last_date = dt.datetime.strptime(last_date_string, "%Y-%m-%d")
    first_date = last_date - dt.timedelta(365)

    #find dates and precipitation amounts
    prcp_data = session.query(func.strftime("%Y-%m-%d", measurement.date), measurement.prcp).filter(func.strftime("%Y-%m-%d", measurement.date) >= first_date).all()
    
    #dictionary
    results_dict = {}
    for result in prcp_data:
        results_dict[result[0]] = result[1]

    return jsonify(results_dict)


@app.route("/api/v1.0/stations")
def stations():

    #query
    stations_data = session.query(bob).all()

    #create a list of dictionaries
    stations_list = []
    for station in stations_data:
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        stations_list.append(station_dict)

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():

    #query
    last_date_query = session.query(func.max(func.strftime("%Y-%m-%d", measurement.date))).all()
    last_date_string = last_date_query[0][0]
    last_date = dt.datetime.strptime(last_date_string, "%Y-%m-%d")
    first_date = last_date - dt.timedelta(365)

    #get temperature measurements from last year
    results =session.query(measurement).filter(func.strftime("%Y-%m-%d", measurement.date) >= first_date).all()

    #create list of dictionaries
    tobs_list = []
    for result in results:
        tobs_dict = {}
        tobs_dict["date"] = result.date
        tobs_dict["station"] = result.station
        tobs_dict["tobs"] = result.tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start(start):

    #query
    last_date_query = session.query(func.max(func.strftime("%Y-%m-%d", measurement.date))).all()
    last_date = last_date_query[0][0]

    #get the temperatures
    temps = calc_temps(start, last_date)

    #create a list
    return_list = []
    date_dict = {'start_date': start, 'end_date': last_date}
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(return_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    #get the temperatures
    temps = calc_temps(start, end)

    #create a list
    return_list = []
    date_dict = {'start_date': start, 'end_date': end}
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(return_list)

if __name__ == "__main__":
    app.run(debug = True)