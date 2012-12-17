import pymongo
from settings import *
db = pymongo.Connection(host=mongodb_host,
                        port=mongodb_port)[database_name]
