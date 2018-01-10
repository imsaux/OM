from flask import Flask, redirect, request
import requests
import os
import json
import configparser

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, 'site.ini'))

@app.route('/')
def read_json():
    result = dict()
    for site in config.sections():
        url = 'http://%s:%s' % (str(config.get(site, 'ip')), str(config.get(site, 'port')))
        r = requests.get(url)
        result[site] = json.loads(r.content.decode(encoding='utf8'), encoding='gbk')

    return repr(result) + '\n'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', int(config.get('lan', 'server_port'))))
    app.run(host='localhost', port=port)