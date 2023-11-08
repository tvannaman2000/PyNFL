import sys, codecs, io, os.path
import xml.etree.ElementTree as ET
import mysql.connector
from myconn import connect_to_mysql


cfg_file = "dbconfig.xml"


def get_db_config():
    tree = ET.parse(cfg_file)
    root = tree.getroot()
    for x in root[0]:
       if x.tag == "hostname":
              hostname = x.text
       if x.tag == "password":
              password = x.text
       if x.tag == "username":
              username = x.text
       if x.tag == "dbname":
              dbname = x.text
    config = { "host": hostname, "user": username, "password": password, "database": dbname, }
    #print("Con1 =", config)
    return config

