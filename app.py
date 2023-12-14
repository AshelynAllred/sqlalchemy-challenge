# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from dateutil.relativedelta import relativedelta as rd
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
base_ = automap_base()
# reflect the tables
base_.prepare(autoload_with=engine)

# Save references to each table
station_ = base_.classes.station
measure_ = base_.classes.measurement

# putting these up here so they are in a more usable scope
# ----------
# may cause issues if you did this on production, since the data could update
# and these variables might not.
sess = Session(engine)
date_latest = dt.datetime.strptime(sess.query(measure_.date).order_by(measure_.date.desc()).first().date, '%Y-%m-%d')
dstr_latest = dt.date.strftime(date_latest, '%Y-%m-%d')
dstr_1yr_back = dt.date.strftime(date_latest - rd(months=12), '%Y-%m-%d')
most_active = sess.query(measure_.station, func.count(measure_.station)).group_by(measure_.station).order_by(func.count(measure_.station).desc()).first()
sess.close()

# There was a comment to create the session here,
# but I do not think there is a reliable way to close it when we are done
# that is built into Flask itself.
# Seems redundant and inefficient, but oh well

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################


@app.route('/')
@app.route('/api/v1.0/')
def home():
    import urllib
    # Create our session (link) from Python to the DB
    print('Accessed: Landing Page')

    # I'd like to find a way to do this programatically but I don't have time

    # Yes, I did this all by hand. I live and breathe HTML (aside from having to look up tags every 5 minutes)
    return (
        f'''<!DOCTYPE html>
        <html lang='en'>
            <body>
                <h1>Welcome!</h1>
                <h2>Available Endpoints:</h2>
                <ul>
                    <li>"<a href='/'>/</a>" or "<a href='/api/v1.0/'>/api/v1.0/</a>" - this page</li>
                    <li>"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a>" - All precipitation data from the last 12 months, broken down by date in <code>'YYYY-MM-DD'</code> format, then by station</li>
                    <li>"<a href='/api/v1.0/stations'>/api/v1.0/stations</a>" - List of all stations, broken down by station id</li>
                    <li>"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a>" - All temperature observation data in the last 12 months from the most-active station in that time period</li>
                    <li>"<a href='/api/v1.0/2017-01-01'>/api/v1.0/&lt;start&gt;</a>" - Summary of temperature observation data (min, max, avg) from the <strong>&lt;start&gt;</strong> date to present date (format <code>'YYYY-MM-DD'</code>)
                        <br/>(link above points to date <code>2017-01-01</code>)
                    </li>
                    <li>"<a href='/api/v1.0/2016-01-01/2017-01-01'>/api/v1.0/&lt;start&gt;/&lt;end&gt;</a>" - Same summary as above, but with an <strong>&lt;end&gt;</strong> date (same date format as above)
                        <br/>(link above points to date range from <code>2016-01-01</code> to <code>2017-01-01</code>)
                    </li>
                </ul>
            </body>
        </html>
        '''
    )

@app.route('/api/v1.0/precipitation')
def prcp():
    # Create our session (link) from Python to the DB
    sess = Session(engine)
    print('Accessed: /api/v1.0/precipitation')
    
    prcp_data = sess.query(measure_.date, measure_.prcp, measure_.station).filter(measure_.date >= dstr_1yr_back).order_by(measure_.date.desc())

    
    # There are multiple precipitation measurements per date,
    # so we need a clever way to get them all in with the date as the key.
    # 
    # Any json representation that returns a single prcp value, other than a summary (avg, max, etc) value 
    # across all non-null measurements for a given date, or for a specific (unspecified) station, would be wrong
    # So I've also decided to include station codes so we know where each prcp point comes from.
    # 
    # Though techincally, 'prcp' is still the value under the 'date' key, it is just a further key for actual values by station
    dates_found = []
    prcp_dict = {}
    for date, prcp, station in prcp_data:
        prcp_row_dict = {}
        # Check for an existing date in our dates_found list
        if date in dates_found:
            # if it exists, add our precipitation value with the station code as the key
            # (should be non-destructive since the addition is the station code and prcp)
            prcp_dict[date]['Precipitation'][station] = prcp
        else:
            # if it doesn't, add new dictionary into our row's dictionary
            # so we don't get a KeyError
            prcp_row_dict['Precipitation'] = {station: prcp}
            # add our row dictionary to our main precipitation dictionary with date as the key
            # (this is where the station code gets actually added as a key to the main dict)
            prcp_dict[date] = prcp_row_dict
            # and add the date to our dates_found list
            dates_found.append(date)

    #  Close the session since we are done
    sess.close()

    # return json representation
    return jsonify(prcp_dict)

@app.route('/api/v1.0/stations')
def stations():
    # Create our session (link) from Python to the DB
    sess = Session(engine)
    print('Accessed: /api/v1.0/stations')
    
    # query pretty much all relevant station data
    # it seems to work better if we call for all columns individually, I seemed to have issues doing otherwise
    # and had to refer to another repo (of the same name by robmatelyan, see readme.md file)
    stations_query = sess.query(station_.id, 
                                station_.name,
                                station_.station, 
                                station_.latitude, 
                                station_.longitude,
                                station_.elevation).all()


    # root of dictionary, with empty dictionary for us to add key/values to in our for loop
    stations_dict = {'id': {}}

    # for loop to populate stations_dict
    for id, name, station, latitude, longitude, elevation in stations_query:
        # assign empty dict to station_row_dict so we can populate it with relevant values
        station_row_dict = {}
        station_row_dict['station'] = station
        station_row_dict['name'] = name
        station_row_dict['latitude'] = latitude
        station_row_dict['longitude'] = longitude
        station_row_dict['elevation'] = elevation
        # add values into our main dictionary under id as the key
        stations_dict['id'][id] = station_row_dict

    # Close the session since we are done
    sess.close()

    # return json list of stations from dataset
    return jsonify(stations_dict)

@app.route('/api/v1.0/tobs')
# temperature observation
def tobs():
    # Create our session (link) from Python to the DB
    sess = Session(engine)
    print('Accessed: /api/v1.0/tobs')

    # query dates and temp ovsercations of most active station for previous year of data
    # ('most active station' was determined at the beginning of the script as a global variable,
    #  may not be the best way to do things but it made the variable usable in more places without
    #  having to make further unecessary queries on static data)
    tobs_1yr = sess.query(measure_.date, 
                          measure_.tobs).filter(measure_.date >= dstr_1yr_back, 
                                               measure_.station == most_active[0]).order_by(measure_.date).all()

    # create our basic tobs dictionary object, using the station code as the root key
    tobs_dict = {most_active[0]: {}}
    
    # for loop to fill out temperature data underneath the station code, 
    # with date as the key and temp as the value
    for date, tobs in tobs_1yr:
        tobs_dict[most_active[0]][date] = tobs
    
    # Close the session since we are done
    sess.close()

    # return json list of tobs data for most active station
    return tobs_dict


# I found out you can assign several routes to one function
# So I decided to reconsolidate my code to flexibly handle both start, and start-end use cases
@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/')
@app.route('/api/v1.0/<start>/<end>')
def date_range_summary(start, end=None):
    
    # Set end to latest date value (calculated at top of script) if it is empty
    # (in effect, nothing entered for <end> means it defaults to present)
    if end is None:
        end = dstr_latest
    
    # return an error if the dates are invalid
    # (important because we are technically just doing date comparisons with strings due to sqlite limitations)
    try:
        dt.datetime.strptime(start, '%Y-%m-%d')
        dt.datetime.strptime(end, '%Y-%m-%d')
    except:
        return {'error': 'Invalid date. Please enter your date(s) in the following format: YYYY-MM-DD'}

    # Create our session (link) from Python to the DB
    sess = Session(engine)
    # log access of url
    print('Accessed: date range temp summary (/api/v1.0/YYYY-MM-DD)(/YYYY-MM-DD)')

    # calc TMIN, TAVG, TMAX for dates from <start> to <end>, inclusive
    tobs_summ = sess.query(func.min(measure_.tobs).label('min'), 
                           func.max(measure_.tobs).label('max'), 
                           func.avg(measure_.tobs).label('avg')).filter(measure_.date >= start, 
                                                                       measure_.date <= end).first()

    # Close the session since we are done
    sess.close()

    # return JSON list of min temp, avg temp, max temp for specified range
    return {'min': tobs_summ.min,
            'max': tobs_summ.max,
            'avg': tobs_summ.avg}


# Actually, y'know, run the app
if __name__ == '__main__':
    app.run(debug=True)