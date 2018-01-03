from flask import Flask, jsonify, request
import os, datetime
import configparser
import ommysql
import ominit

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config.ini'))


@app.route('/', methods=['GET'])
def send_json():
    result = dict()
    _now = datetime.datetime.now()
    _v = config.get('mysql', 'version')
    result.update(ommysql.mysqldb._trains())
    result.update(ommysql.mysqldb._carriages())
    result.update(ommysql.mysqldb._warning())

    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', int(config.get('API', 'port'))))
    app.run(host='0.0.0.0', port=port)