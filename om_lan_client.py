from flask import Flask, jsonify, request
import os, datetime
import configparser
import om_mysql
# import om_init

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config.ini'))


@app.route('/', methods=['GET'])
def send_json():
    my = om_mysql.mysqldb()
    _now = datetime.datetime.now()
    _start_time = str(config.get('lan', 'stat_time')).zfill(2)
    _from = _now.strftime('%Y%m%d') + _start_time + '0000'
    _to = _now.strftime('%Y%m') + str(_now.day + 1).zfill(2) + _start_time + '0000'

    result = dict()
    result.update(my.sitename())
    result.update(my.trains(_from, _to))
    result.update(my.carriages(_from, _to))
    result.update(my.warning(_from, _to))
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', int(config.get('lan', 'restapi_port'))))
    app.run(host='localhost', port=port)