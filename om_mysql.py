import pymysql.cursors
import configparser
import os

class mysqldb():
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        config = configparser.ConfigParser()
        config.read(os.path.join(BASE_DIR, 'config.ini'))
        self.version = config.get('lan', 'mysql_version')
        self.connection = pymysql.connect(host=str(config.get('lan', 'mysql_ip')),
                                     port=int(config.get('lan', 'mysql_port')),
                                     user=str(config.get('lan', 'mysql_user')),
                                     password=str(config.get('lan', 'mysql_password')),
                                     db=str(config.get('lan', 'mysql_db')),
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

    def sitename(self):
        if self.version == '25':
            sql = "SELECT '站点', deptname as 'name' FROM sartas.userlogin.unit_dept WHERE connectstring like '%localhost%'"

        if self.version == '26':
            sql = "SELECT '站点', StationName as 'name' from sartas.account_t_station where ConnectString = 'localhost'"

        if self.version == '27':
            sql = "SELECT '站点', StationName as 'name' FROM sartas.account_t_station where ConnectString = 'localhost'"

        return self._execute(sql, ('站点', 'name'), None)


    def carriages(self, _from, _to):
        if self.version == '25':
            sql = "SELECT '车辆数', COUNT(td.traindetail_id) FROM traindetail td LEFT JOIN train t on td.train_id = t.train_id WHERE t.train_comedate BETWEEN %s AND %s"
        if self.version == '26':
            sql = "SELECT '车辆数', COUNT(td.traindetail_id) FROM traindetail td LEFT JOIN train t on td.train_id = t.train_id WHERE t.train_comedate BETWEEN %s AND %s"
        return self._execute(sql, ('车辆数', 'COUNT(td.traindetail_id)'), (_from, _to))

    def trains(self, _from, _to):
        if self.version == '25':
            sql = 'SELECT "车列数", COUNT(0) FROM train t WHERE t.train_comedate BETWEEN %s AND %s'
        if self.version == '26':
            sql = 'SELECT "车列数", COUNT(0) FROM train t WHERE t.train_comedate BETWEEN %s AND %s'
        return self._execute(sql, ('车列数', 'COUNT(0)'), (_from, _to))

    def warning(self, _from, _to):
        _r = None
        if self.version == '25':
            sql = """SELECT tx.szProblemType, count(tx.szProblemType)
FROM txdetail tx LEFT JOIN traindetail td on tx.traindetail_id=td.TrainDetail_ID LEFT JOIN train t on td.Train_ID=t.Train_ID
WHERE 1=1
and t.Train_ComeDate BETWEEN %s AND %s
and tx.szProblemNum > 0
GROUP BY tx.szProblemType"""
            _r = self._execute(sql, ('tx.szProblemType', 'count(tx.szProblemType)'), (_from, _to))
        if self.version == '26':
            sql = "SELECT problemtype, COUNT(problemtype) FROM alarmdetail WHERE inserttime BETWEEN %s AND %s group by problemtype"
            _r = self._execute(sql, ('problemtype', "COUNT(problemtype)"), (_from, _to))
        return _r

    def _execute(self, sql, _key, params):
        result = dict()
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(sql, params)
                f = cursor.fetchall()
                for l in f:
                    result[l[_key[0]]] = l[_key[1]]
                return result
            except Exception as e:
                self.logger.error(repr(e))
                self.logger.error(f)
                self.logger.error(repr(params))
                self.logger.error(repr(_key))
                result[_key[0]] = '数据异常'
            # return result