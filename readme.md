About seed.py script and Flask Web App
----------------------------------------
Script: seed.py
Description:
This script populates a SQLite3 database. By default it retrieves the first 150 users from GitHub.
However, the script accepts a param called total to customize the number of users to be retrieved.
The script is tested using Python version 3.9.1
To run the script from command line: python seed.py
usage: seed.py [-h] [total]
Code has documented logic. The script logs information to console and log file for debug /info.

About Generated sqlite3 database:
Database name is site.db

About Flask application:
Creates a view to show the info of all the users of the database in a table. Profile avatar is visible and clicking the username sends you to the GitHub profile.Pagination implemented using Flask-SQLAlchemy, default size is set to 25. The page is responsive even with a large amount of data 

To run the Flask application:
python app.py

Improvements since previous version:
- Bugs resolved: 
    - Fixed the issue of fetching duplicate records
    - Fixed edge cases when requested total > 100
    - Fixed issue when name conatined special characters

- Added improved error handling 
- Added logging to console and file
- Replaced individual SQL inserts with Bulk insert (sqlite3 executemany)

-Added REST Service (uses flask_restful) to retrieve data from database using REST API

-Added caching

API:

GET 	 /Profiles

Parameters:

------                          --------                           ----------------
1  Parameter name : id	            Type:integer	             Description: returns user information with matching id

2  Parameter name: loginid	        Type:string	                 Description: returns user information with matching username/loginid

3  Parameter name: usertype	    Type:string	                 Description: Valid User Type values (User or Organization), returns all users of the type 

4  Parameter name: pagination	    Type:integer	             Description: number of records per page for pagination

5  Parameter name: pagenumber      Type:integer            	 Description: page number for which data needs to be retrived

6  Parameter name: orderby         Type:string             	 Description: orders records as per orderby (valid values: 'id' 
                                                                                                  or 'names'or 'loginids' or 'profiles'
                                                                                                  default is orderby ‘id’)




