
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


engine = create_engine("sqlite:///resources/hawaii.sqlite")
session = Session(engine)

app = Flask(__name__)

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station


@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > one_year_ago).\
        order_by(Measurement.date).all()
    session.close()
    prcp_dict = dict(prcp_data)
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    locations = session.query(Measurement).group_by(Measurement.station).count()
    active_stations = session.query(Measurement.station,func.count(Measurement.station)).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).all()
    stations = dict(active_stations)
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    year_temp = session.query(Measurement.tobs).\
        filter(Measurement.date >= one_year_ago, Measurement.station == 'USC00519281').\
         order_by(Measurement.tobs).all()

    yr_temp = []
    for y_t in year_temp:
        yrtemp = {}
        yrtemp["tobs"] = y_t.tobs
        yr_temp.append(yrtemp)
    return jsonify(yr_temp)


def calc_start_temps(start_date):
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                         filter(Measurement.date >= start_date).all()


@app.route("/api/v1.0/<start>")
def startday(start):
    calc_s_temp = calc_start_temps(start)
    s_temp= list(np.ravel(calc_s_temp))

    t_min = s_temp[0]
    t_max = s_temp[2]
    t_avg = s_temp[1]
    t_dict = {'Minimum temperature': t_min, 'Maximum temperature': t_max, 'Avg temperature': t_avg}

    return jsonify(t_dict)


def calc_temps(start_date, end_date):
    return session.query(func.min(Measurement.tobs), \
                         func.avg(Measurement.tobs), \
                         func.max(Measurement.tobs)).\
                         filter(Measurement.date >= start_date).\
                         filter(Measurement.date <= end_date).all()


@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    calc_se_temp = calc_temps(start, end)
    se_temp= list(np.ravel(calc_se_temp))

    temp_min = se_temp[0]
    temp_max = se_temp[2]
    temp_avg = se_temp[1]
    temp_dict = { 'Minimum temperature': temp_min, 'Maximum temperature': temp_max, 'Avg temperature': temp_avg}

    return jsonify(temp_dict)

if __name__ == '__main__':
    app.run(debug=True)


