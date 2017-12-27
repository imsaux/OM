from flask import Flask, jsonify
import os
# import json
import pymysql.cursors
import configparser

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('mysql.ini')
connection = pymysql.connect(host=str(config.get('mysql', 'ip')),
                             port=int(config.get('mysql', 'port')),
                             user=str(config.get('mysql', 'user')),
                             password=str(config.get('mysql', 'password')),
                             db=str(config.get('mysql', 'db')),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


@app.route('/', methods=['GET'])
def send_json():
    try:
        with connection.cursor() as cursor:
            sql_lie = "SELECT COUNT(0) FROM train t WHERE t.train_comedate BETWEEN %s AND %s"
            sql_liang = "SELECT COUNT(td.traindetail_id) FROM traindetail td LEFT JOIN train t on td.train_id = t.train_id WHERE t.train_comedate BETWEEN %s AND %s"
            sql_alarm = "SELECT problemtype, COUNT(problemtype) FROM alarmdetail WHERE inserttime > %s group by problemtype"
            cursor.execute(sql_alarm, ('2017-01-01'))
            f = cursor.fetchall()
            result = dict()
            for l in f:
                result[l['problemtype']] = l['COUNT(problemtype)']
            cursor.execute(sql_lie, ('2017-01-01', '2017-12-31'))
            f_lie = cursor.fetchall()
            result['列数'] = f_lie[0]['COUNT(0)']
            cursor.execute(sql_liang, ('2017-01-01', '2017-12-31'))
            f_liang = cursor.fetchall()
            result['辆数'] = f_liang[0]['COUNT(td.traindetail_id)']

            return jsonify(result)
    finally:
        connection.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)