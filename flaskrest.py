"""
Script: flaskrest.py
Description:
This script creates REST service which provides Github profiles (users') information in the database.
Following are the  REST API details.

GET  /Profiles

Pararmeters:
-------------
Name                    Type               Description
usertype                string             Valid User Type values (User or Organization),
                                           returns all users of the type 

id                      integer            returns user information with matching id

loginid                 string             returns user information with matching username/loginid

pagination              integer            number of record per page for pagination (Max limited to 100)

pagenumber              integer            page number for which data needs to be retrived

orderby                 string             orders records as per orderby (valid values: 'id' 
                                            or 'names'or 'loginids' or 'profiles') defaults to orderby id

The script is tested using Python version 3.9.1.
To run the script from command line: python flaskrest.py
 """

from flask import Flask, request
from flask_restful import Api, Resource, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy, Pagination
from logger import get_logger
from flask_caching import Cache
from requests import HTTPError
import sqlite3
import logging

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple", # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 100
}

app = Flask(__name__)
# tell Flask to use the above defined config
app.config.from_mapping(config)
cache = Cache(app)

api = Api(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

rest_svc_logger =  get_logger('restsvc',logging.DEBUG, True, 'rest_svc_log')
per_page_default = 20
per_page_max = 100

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    login = db.Column(db.String(50))
    avatar = db.Column(db.String(150))
    user_type = db.Column(db.String(50))
    profile = db.Column(db.String(150))
  
resource_fields = {
    'user_id': fields.Integer,
    'name': fields.String,
    'login': fields.String,
    'avatar': fields.String,
    'user_type': fields.String,
    'profile': fields.String
}

class UserInfo(Resource):
    def get_validated_param_Ordrby(self,ord_by):
        orderby = ord_by
        if orderby == 'id':
            orderby = 'user_id'
        elif orderby == 'names':
            orderby = 'name'
        elif orderby == 'loginids':
            orderby = 'login'
        elif orderby == 'profiles':
            orderby = 'profile'
        elif orderby is None:
            # default value
            orderby = 'user_id'
        return orderby
    @marshal_with(resource_fields)
    # Cache the results for efficiency
    @cache.memoize(timeout=500)
    # Get requested user data from database
    def get_user_data(self,user_id,login,usertype,perpage,pagenum,orderby_param):
        result = 'No record retreived from Database'
        try :
            if  user_id is not None:
                result = User.query.filter_by(user_id = user_id).first()
                rest_svc_logger.info("Arguments received user id ="+str(user_id))
                rest_svc_logger.info(result)
            elif login is not None:
                result = User.query.filter_by(login = login).first()
                rest_svc_logger.info("Arguments received login id ="+str(login))
                rest_svc_logger.info(result)
            elif usertype is not None:
                if perpage is None:
                    # default per page
                    perpage = per_page_default 
                if int(perpage) > 100 :
                    perpage = per_page_max
                if pagenum is None:
                    pagenum = 1
                orderby = self.get_validated_param_Ordrby(orderby_param)
                query = User.query.filter_by(user_type = usertype).order_by(orderby)
                pagination = query.paginate(pagenum, int(perpage), True, int(perpage))
                result = pagination.items
                rest_svc_logger.info(result)
        except ValueError as val_err:
            rest_svc_logger.error("\n\nInvalid request check parameter values.\n %s" % val_err)
        except sqlite3.OperationalError as db_err:
            rest_svc_logger.error("\n\nInvalid request check parameter values.\n %s" % db_err)
        return result

    def get(self):
        user_id = request.args.get('id')
        login = request.args.get('loginid')
        usertype = request.args.get('usertype')
        perpage = request.args.get('pagination')
        pagenum = request.args.get('pagenumber')
        orderby = request.args.get('orderby')
        # Get user data from database
        result = self.get_user_data(user_id,login,usertype,perpage,pagenum,orderby)
        if not result:
            rest_svc_logger.error("Abort:Could not find user data in database")
            abort(404, message="Could not find user data in database")
        return result

api.add_resource(UserInfo, "/Profiles")


if __name__ == "__main__":
    app.run(host = "localhost", port= 5001, debug=True)
