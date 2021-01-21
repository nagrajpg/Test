"""
Script: seed.py
Description:
This script populates SQLite database with users' information using GitHub Users REST API.

By default it retrieves the first 150 users from GitHub.However, the script accepts a param
called total to customize the number of users to be retrieved.The script is tested using
Python version 3.9.1.
To run the script from command line: python seed.py
usage: seed.py [-h] [total]
 """
import argparse
import json
import sqlite3
import requests
import logging
import sys

from logging.handlers import TimedRotatingFileHandler
from requests import HTTPError, Timeout

# Set logging config
# Set logfile name
# logging.basicConfig(format='%(asctime)s — %(name)s — %(levelname)s — %(message)s')
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = "seed.log"


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    # Logging levels : DEBUG,INFO,WARNING,ERROR,CRITICAL
    # Set log_level to logging.DEBUG
    # log to both console and file
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    # No need to propagate the error up to parent
    logger.propagate = False
    return logger


seed_logger = get_logger("seed")

# Sqlite3 Database name
site_database_name = 'site.db'

# Handle the command line argument to receive optional user input: #total number of users
# If user does not provide any parameter, the script retrieves 150 (default) records
parser = argparse.ArgumentParser()
parser.add_argument("total", default='150', nargs='?', help="Enter the total number of users",
                    type=int)
args = parser.parse_args()
total = args.total
seed_logger.info("Parse command-line arguments: Total = " + str(total))

# setup access_token, and headers
# Note Access token below need to be replaced with valid access token.
# Invalid access code generates 401 Client Error: Unauthorized for url
access_token = '9ca8c57b06b8e2e64c29608712dc38be1a966e6c'
headers = {'Authorization': "Token " + access_token}


# Function gets request url list, multiple fetch urls if total > Maximum allowed records per request
def get_fetch_url_list(number_of_records):
    # API limit max fetch per page
    max_per_page = 100
    # Number of fetches required
    number_of_requests = int(number_of_records / max_per_page)
    # Additional remaining records to be fetched
    additional_records = number_of_records % max_per_page
    record_since = 0
    url_list = list()
    if number_of_records <= max_per_page:
        url_list.append(f"https://api.github.com/users?per_page={number_of_records}&since={record_since}")
    else:
        seed_logger.info("get_fetch_url_list" + str(number_of_requests))
        while number_of_requests > 0:
            url_list.append(f"https://api.github.com/users?per_page={max_per_page}&since={record_since}")
            number_of_requests = number_of_requests - 1
            record_since = record_since + max_per_page
        seed_logger.info("get_fetch_url_list:record_since " + str(record_since))
        if additional_records > 0:
            url_list.append(f"https://api.github.com/users?per_page={additional_records}&since={record_since}")
    return url_list


# Displays length and individual http request url strings.
def print_my_url_list(my_list):
    seed_logger.info("print_my_url_list:Total number of http requests :" + str(len(my_list)))
    seed_logger.info("print_my_url_list:Following is list of Requests to be sent")
    for value in my_list:
        seed_logger.info(value)


# update request parameter "since" value with last user id
# This function is required to avoid duplicate record fetches
def update_url_record_since(update_url, last_id):
    new_url = update_url.split('&')[0] + "&since=" + str(last_id)
    return new_url


# Returns the requested number of user from GitHub
def get_user_list(usr_list):
    seed_logger.info(usr_list)
    last_user_id = 0
    all_github_user_list = list()
    for usr_url in usr_list:
        seed_logger.info("get_user_list:List of URLs" + usr_url)
        if last_user_id > 0:
            new_url = update_url_record_since(usr_url, last_user_id)
            usr_url = new_url
            seed_logger.info("get_user_list:New URL updated record since to last user Id: " + usr_url)
        try:
            response = requests.get(usr_url, headers=headers)
            users = json.loads(response.text)
            response.raise_for_status()
            for user in users:
                seed_logger.info(user)
                # Retrieve user name information using Get User API GET /users/{username} for each user in user list
                user_info_url = f"https://api.github.com/users/{user['login']}"
                seed_logger.info(user_info_url)
                response = requests.get(user_info_url, headers=headers)
                user_info = json.loads(response.text)
                seed_logger.info(user_info)

                # Get User Id information
                user_id = str(user_info['id'])
                seed_logger.info("User Id : {}".format(user_info['id']))
                last_user_id = user_info['id']

                # Get user name information
                name = user_info['name']
                if name is None:
                    name = ' '
                seed_logger.info("User Name : {}".format(user_info['name']))

                # Get user log-in id information
                login = user['login']
                seed_logger.info("User log-in Id: {}".format(user['login']))

                # Get user image information
                avatar = user['avatar_url']
                seed_logger.info("Image URL: {}".format(user['avatar_url']))

                # Get user type information
                user_type = user['type']
                seed_logger.info("User type: {}".format(user['type']))

                # Get link to user GitHub profile
                profile = user['html_url']
                seed_logger.info("Link to GitHub profile: {}".format(user['html_url']))
                all_github_user_list.append((user_id, name, login, avatar, user_type, profile))

        except ConnectionError as err:
            seed_logger.critical("\n\nConnection error encountered \n %s" % err)
        except Timeout as con_time_out_err:
            seed_logger.critical("\n\nThe request timed out. Try again after sometime... \n %s" % con_time_out_err)
        except HTTPError as http_err:
            seed_logger.critical("\n\nHttp request error encountered.\n %s" % http_err)
        except ValueError as e:
            seed_logger.critical("\n\nCould not convert data to a string.\n %s" % e)
    seed_logger.info("\n\nget_user_list:Total number of records retrieved:" + str(len(all_github_user_list)) + "\n")
    return all_github_user_list


# Inserts the GitHub user records into sqlite3 database
# Parameters: User record list, database name in which records are inserted
def insert_into_db(github_user_list, dbname):
    db_conn = None
    count = len(github_user_list)
    if count > 0:
        try:
            db_conn = sqlite3.connect(dbname)
            seed_logger.info("insert_into_db:Database created")

            # DROP Table if it already exists
            drop_table_statement = "DROP TABLE IF EXISTS user;"
            db_conn.execute(drop_table_statement)

            # create table
            db_conn.execute(
                "CREATE TABLE user (user_id INTEGER, name TEXT, login TEXT, avatar TEXT, user_type TEXT, profile TEXT)")
            # Bulk insert
            db_conn.executemany(
                "INSERT INTO user VALUES (?,?,?,?,?,?)",
                github_user_list)
            seed_logger.info("insert_into_db:Inserted %s records in database\n" % count)
            db_conn.commit()
            db_conn.close()
        except sqlite3.OperationalError as e:
            seed_logger.critical("Database operational error encountered \n %s" % e)
        finally:
            if db_conn:
                db_conn.close()
                seed_logger.info("insert_into_db:The SQLite DB connection is closed")
    else:
        seed_logger.info("\ninsert_into_db:No records fetched, no records inserted in database\n")


# Get all the fetch URLs required per the total records requested
new_urls = get_fetch_url_list(total)

# Utility to print URLs used to get user data
print_my_url_list(new_urls)

# Get all the user data
all_users = get_user_list(new_urls)

# insert the records into sqlite database
insert_into_db(all_users, site_database_name)
