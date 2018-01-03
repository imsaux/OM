import pymysql.cursors
import configparser
import os

class mysqldb():
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        config = configparser.ConfigParser()
        config.read(os.path.join(BASE_DIR, 'config.ini'))
        self.version = config.get('mysql', 'version')
        self.connection = pymysql.connect(host=str(config.get('mysql', 'ip')),
                                     port=int(config.get('mysql', 'port')),
                                     user=str(config.get('mysql', 'user')),
                                     password=str(config.get('mysql', 'password')),
                                     db=str(config.get('mysql', 'db')),
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)


    def v25_carriages(self):
        sql = "SELECT COUNT(td.traindetail_id) FROM traindetail td LEFT JOIN train t on td.train_id = t.train_id WHERE t.train_comedate BETWEEN %s AND %s"

