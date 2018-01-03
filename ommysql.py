import pymysql.cursors
import configparser
import os
import ominit

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


    def carriages(self, _from, _to):
        if self.version == '25':
            sql = "SELECT COUNT(td.traindetail_id) FROM traindetail td LEFT JOIN train t on td.train_id = t.train_id WHERE t.train_comedate BETWEEN %s AND %s"
        if self.version == '26':
            sql = "SELECT COUNT(td.traindetail_id) FROM traindetail td LEFT JOIN train t on td.train_id = t.train_id WHERE t.train_comedate BETWEEN %s AND %s"
        return self._execute(sql, '车辆数', (_from, _to))

    def trains(self, _from, _to):
        if self.version == '25':
            sql = "SELECT COUNT(0) FROM train t WHERE t.train_comedate BETWEEN %s AND %s"
        if self.version == '26':
            sql = "SELECT COUNT(0) FROM train t WHERE t.train_comedate BETWEEN %s AND %s"
        return self._execute(sql, '车列数', (_from, _to))

    def warning(self, _from, _to):
        if self.version == '25':
            sql = """SELECT tx.szProblemType, count(tx.szProblemType)
FROM txdetail tx LEFT JOIN traindetail td on tx.traindetail_id=td.TrainDetail_ID LEFT JOIN train t on td.Train_ID=t.Train_ID
WHERE 1=1
and t.Train_ComeDate BETWEEN %s AND %s
and tx.szProblemNum > 0
GROUP BY tx.szProblemType"""
        if self.version == '26':
            sql = "SELECT problemtype, COUNT(problemtype) FROM alarmdetail WHERE inserttime BETWEEN %s AND %s group by problemtype"

        return self._execute(sql, '报警', (_from, _to))



    def _execute(self, sql, _key, *params):
        result = dict()
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(sql, params)
                f = cursor.fetchall()
                for l in f:
                    result[l[_key]] = l[_key]
            except Exception as e:
                ominit.log_error(repr(e))
                result[_key] = '数据异常'
            finally:
                self.connection.close()
        return result
