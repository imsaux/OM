import inspect
import logging
import pymysql.cursors
import configparser
import time
import os

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
        self.version = config.get('mysql', 'version')
        self.connection = pymysql.connect(host=str(config.get('mysql', 'ip')),
                                     port=int(config.get('mysql', 'port')),
                                     user=str(config.get('mysql', 'user')),
                                     password=str(config.get('mysql', 'password')),
                                     db=str(config.get('mysql', 'db')),
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        self.run = True

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
        _r = None
        if self.version == '25':
            sql = """SELECT tx.szProblemType, count(tx.szProblemType)
FROM txdetail tx LEFT JOIN traindetail td on tx.traindetail_id=td.TrainDetail_ID LEFT JOIN train t on td.Train_ID=t.Train_ID
WHERE 1=1
and t.Train_ComeDate BETWEEN %s AND %s
and tx.szProblemNum > 0
GROUP BY tx.szProblemType"""
        if self.version == '26':
            sql = "SELECT problemtype, COUNT(problemtype) FROM alarmdetail WHERE inserttime BETWEEN %s AND %s group by problemtype"
            _r = self._execute(sql, 'problemtype', (_from, _to))
        return _r

    def _execute(self, sql, _key, params):
        result = dict()
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(sql, params)
                f = cursor.fetchall()
                for l in f:
                    result[_key] = l[_key]
                self.logger.info(repr(result))
                return result
            except pymysql.MySQLError:
                self.connection.connect()
            except Exception as e:
                self.logger.error(repr(e))
                self.logger.error(f)
                result[_key] = '数据异常'
            # return result

    def SvcDoRun(self):
        while True:
            sql = "SELECT problemtype, COUNT(problemtype) FROM alarmdetail WHERE inserttime BETWEEN %s AND %s group by problemtype"
            _r = self._execute(sql, 'problemtype', ('20170101', '20171231'))
            self.logger.info(repr(_r))
            time.sleep(30)

    def SvcStop(self):
        self.logger.info("service is stop....")
        self.connection.close()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(omservice)