import inspect
import logging
import pymysql.cursors
import configparser
import time
import os
import datetime
from urllib.request import urlopen
import json

if os.name == 'nt':
    import win32service
    import win32event
    import win32serviceutil
elif os.name == 'posix':
    pass


class omservice(win32serviceutil.ServiceFramework):
    _svc_name_ = "OM Service"
    _svc_display_name_ = "OM Service"
    _svc_description_ = "DATA"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = self._getLogger()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        config = configparser.ConfigParser()
        config.read(os.path.join(BASE_DIR, 'config.ini'))
        self.stat_start_time = str(config.get('lan', 'stat_time')).zfill(2)
        self.version = config.get('lan', 'mysql_version')
        self.connection = pymysql.connect(host=str(config.get('lan', 'mysql_ip')),
                                     port=int(config.get('lan', 'mysql_port')),
                                     user=str(config.get('lan', 'mysql_user')),
                                     password=str(config.get('lan', 'mysql_password')),
                                     db=str(config.get('lan', 'mysql_db')),
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)


    def _getLogger(self):
        logger = logging.getLogger('[OM Service]')

        this_file = inspect.getfile(inspect.currentframe())
        dirpath = os.path.abspath(os.path.dirname(this_file))
        handler = logging.FileHandler(os.path.join(dirpath, "om.log"))

        formatter = logging.Formatter('%(asctime)s %(name)-12s [line:%(lineno)d] %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        return logger

    def carriages(self, _from, _to):
        if self.version == '25':
            sql = "SELECT '车辆数', COUNT(td.traindetail_id) FROM traindetail td LEFT JOIN train t on td.train_id = t.train_id WHERE t.train_comedate BETWEEN %s AND %s"
        if self.version == '26':
            sql = "SELECT '车辆数', COUNT(td.traindetail_id) FROM traindetail td LEFT JOIN train t on td.train_id = t.train_id WHERE t.train_comedate BETWEEN %s AND %s"
        return self._execute(sql, ('车辆数', 'COUNT(td.traindetail_id)'), (_from, _to))

    def trains(self, _from, _to):
        if self.version == '25':
            sql = "SELECT '车列数', COUNT(0) FROM train t WHERE t.train_comedate BETWEEN %s AND %s"
        if self.version == '26':
            sql = "SELECT '车列数', COUNT(0) FROM train t WHERE t.train_comedate BETWEEN %s AND %s"
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

    def SvcDoRun(self):
        while True:
            _now = datetime.datetime.now()
            _from = _now.strftime('%Y%m%d') + self.stat_start_time + '0000'
            _to = _now.strftime('%Y%m') + str(_now.day + 1).zfill(2) + self.stat_start_time + '0000'
            _r = self.warning(_from, _to)
            self.logger.info(repr(_r))
            urlopen('http://')
            time.sleep(30)

    def SvcStop(self):
        self.logger.info("服务正在关闭...")
        self.connection.close()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(omservice)