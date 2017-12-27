from flask import Flask
import json
import configparser

app = Flask(__name__)

@app.route('/')
def read_json():
    try:
        pass
    finally:
        pass

if __name__ == '__main__':
    app.run()
