from flask import Flask, render_template, redirect, jsonify


#dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func

import pandas as pd
import numpy as np
import datetime as dt


app = Flask(__name__)

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurements = Base.classes.measurement
Stations = Base.classes.station

session = Session(engine)

@app.route("/")
def home():
	print("Server received request for 'Home' page.")
	return "Welcome to the Surfs Up Weather API!"

@app.route("/welcome")
#List all available routes
def welcome ():
	return (
		f"Welcome to the Surf Up API<br>"
		f"Available Routes:<br>"
		f"/api/v1.0/precipitation<br>"
		f"Return all dates and precipitations in the database<br>"
		f"/api/v1.0/stations<br>"
		f"Return all stations in the database<br>"
		f"/api/v1.0/tobs<br>"
		f"Return the dates and temperature observations from a year from the last data point<br>"
		f"/api/v1.0/start<br>"
		f"Replace (start) with the start date in the format of YYYY-MM-DD, it will return TMIN, TAVG, and TMAX for all dates greater than and equal to the start date<br>"
		f"/api/v1.0/start/end<br>"
		f"Replace (start) and (end) with the start date and end date in the format of YYYY-MM-DD, it will return TMIN, TAVG, and TMAX for dates between the start and end date inclusive.<br>"
	)
	
@app.route("/api/v1.0/precipitation")
def precipitation():
	
	results = session.query(Measurements.date,Measurements.prcp).filter(Measurements.date >= "08-23-2017").all()

	year_prcp = list(np.ravel(results))
	

	return jsonify(year_prcp)

@app.route("/api/v1.0/stations")
def stations():

	results = session.query(Stations.station).all()

	all_stations = list(np.ravel(results))

	return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temperature():

	last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    
	for date in last_date:
		split_last_date=date.split('-')

	last_year=int(split_last_date[0]); last_month=int(split_last_date[1]); last_day=int(split_last_date[2])

	query_date = dt.date(last_year, last_month, last_day) - dt.timedelta(days=365)
	results = session.query(Measurements.date, Measurements.tobs).\
	filter(Measurements.date > query_date).\
	order_by(Measurements.date).all()
	
	all_date_tobs = list(np.ravel(results))

	return jsonify(all_date_tobs)

@app.route("/api/v1.0/<start>")
def trip1(start):
	last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    
	for date in last_date:
		split_last_date=date.split('-')

	last_year=int(split_last_date[0]); last_month=int(split_last_date[1]); last_day=int(split_last_date[2])

	end_date = dt.date(last_year, last_month, last_day)
	start_date= dt.datetime.strptime(start, '%Y-%m-%d')
	trip_data = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
	filter(Measurements.date >= start_date).filter(Measurements.date <= end_date).all()
	
	trip = list(np.ravel(trip_data))
	return jsonify(trip)


@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):
	
	start_date= dt.datetime.strptime(start, '%Y-%m-%d')
	end_date= dt.datetime.strptime(end,'%Y-%m-%d')
	trip_data = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
	filter(Measurements.date >= start_date).filter(Measurements.date <= end_date).all()
	
	trip = list(np.ravel(trip_data))
	return jsonify(trip)


if __name__ == '__main__':
    app.run(debug=True)