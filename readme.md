# sqlalchemy-challenge
Data Analytics Challenge using Flask and SQLAlchemy to analyze climate data provided and create an API endpoint for that same data with both static and dynamic data

## Where to find everything
* Provided data are available in the `/Resources` folder
* Data analysis is available within the `climate_starter.ipynb` notebook
* The Flask app is available in the `app.py` script

## Miscellaneous notes
Can't exactly say I enjoy working with SQLAlchemy. Its implementation leaves much to be desired in terms of usability, especially within VSCode's IDE. Perhaps there's an extension I am missing that would help a lot with context menus.

I ended up using the `dateutil.relativedelta` library for my time delta function, because the main `datetime.timedelta` function did not have an option for months or years. I had concerns for a general case in which leap days could be an issue, rendering a `days=365` inaccurate about 1/4 of the time (give or take, leap days are weird).

I ended up innovating on the code (perhaps risky for grading purposes) to add some features I thought were neat, manage my sqlite sessions better, and trim down my `app.py` code where prudent. 

I'm not sure what we were supposed to do for sqlalchemy model/base variable names, since the convention we have been using in class was a capital letter for the first character. The rubric states that all variables and functions are to be named with lowercase characters with words separated by underscores, so as a shorthand I've decided to change any orm variables to instead be all lowercase with an underscore \_ at the end. Technically still breaks the instructions but hopefully it is preferable to a capital letter in the name.

## Citations
I did general research for syntax issues, and looked at user [@robmatelyan](https://github.com/robmatelyan/sqlalchemy-challenge)'s repo for assistance on getting the `app.py` (most recent commit id `07109ed`) to jsonify data properly in my return statements (namely for station data after I couldn't figure out a generic, dynamic implementation for getting column names and row values).