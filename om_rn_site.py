from flask import Flask, jsonify, request
# import requests
import os
# import json
import pymysql.cursors
import configparser

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config.ini'))


@app.route('/', methods=['GET'])
def send_json():
    try:
        connection = pymysql.connect(host=str(config.get('mysql', 'ip')),
                                     port=int(config.get('mysql', 'port')),
                                     user=str(config.get('mysql', 'user')),
                                     password=str(config.get('mysql', 'password')),
                                     db=str(config.get('mysql', 'db')),
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        _v = config.get('mysql', 'version')
        sql_lie = sql_liang = sql_alarm = ''
        if _v == '2.6':
            sql_lie = "SELECT COUNT(0) FROM train t WHERE t.train_comedate BETWEEN %s AND %s"
            sql_liang = "SELECT COUNT(td.traindetail_id) FROM traindetail td LEFT JOIN train t on td.train_id = t.train_id WHERE t.train_comedate BETWEEN %s AND %s"
            sql_alarm = "SELECT problemtype, COUNT(problemtype) FROM alarmdetail WHERE inserttime > %s group by problemtype"
        elif _v == '2.5':
            sql_lie = "SELECT COUNT(0) FROM train t WHERE t.train_comedate BETWEEN %s AND %s"
            sql_liang = "SELECT COUNT(td.traindetail_id) FROM traindetail td LEFT JOIN train t on td.train_id = t.train_id WHERE t.train_comedate BETWEEN %s AND %s"
            sql_alarm = """SELECT tx.szProblemType, count(tx.szProblemType)
FROM txdetail tx LEFT JOIN traindetail td on tx.traindetail_id=td.TrainDetail_ID LEFT JOIN train t on td.Train_ID=t.Train_ID
WHERE 1=1
and t.Train_ComeDate > %s
and tx.szProblemNum > 0
GROUP BY tx.szProblemType"""

        with connection.cursor() as cursor:
            result = dict()
            try:
                cursor.execute(sql_alarm, ('2017-01-01'))
                f = cursor.fetchall()
                for l in f:
                    result[l['problemtype']] = l['COUNT(problemtype)']
            except:
                result['报警'] = '数据异常'

            try:
                if sql_lie != '':
                    cursor.execute(sql_lie, ('2017-01-01', '2017-12-31'))
                    f_lie = cursor.fetchall()
                    result['列数'] = f_lie[0]['COUNT(0)']
            except:
                result['列数'] = '数据异常'

            try:
                if sql_liang != '':
                    cursor.execute(sql_liang, ('2017-01-01', '2017-12-31'))
                    f_liang = cursor.fetchall()
                    result['辆数'] = f_liang[0]['COUNT(td.traindetail_id)']
            except:
                result['辆数'] = '数据异常'

            return jsonify(result)
    except Exception as e:
        print(repr(e))
    finally:
        connection.close()
        request.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', int(config.get('API', 'port'))))
    app.run(host='0.0.0.0', port=port)