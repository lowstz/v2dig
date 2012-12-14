import pymongo
from tornado.options import define, options
define("mongo_host", default="127.0.0.1", help="database host")
define("mongo_host_port", default=27017, help="database host port", type=int)
define("mongo_database", default="v2dig", help="databbase name")

db = pymongo.Connection(host=options.mongo_host,
                        port=options.mongo_host_port)[options.mongo_database]
