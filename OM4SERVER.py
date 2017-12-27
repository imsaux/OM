from flask import Flask, redirect, request
import requests
import os
import json
import configparser

app = Flask(__name__)

@app.route('/')
def read_json():

    r = requests.get('http://0.0.0.0:5000')
    return r.content

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)