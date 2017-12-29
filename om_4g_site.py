import os
import pymysql.cursors
import configparser
from multiprocessing import Process
import logging
import win32api
import win32service
import win32event
import win32serviceutil


class SmallestPythonService(win32serviceutil.ServiceFramework):
    _svc_name_ = "驻站数据传输服务"
    _svc_display_name_ = "驻站数据传输服务"
    #服务名
    _svc_name_ = "OM Service"
    #服务显示名称
    _svc_display_name_ = "驻站数据传输服务"
    #服务描述
    _svc_description_ = "驻站数据传输服务"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.isAlive = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

if __name__=='__main__':
    win32serviceutil.HandleCommandLine(SmallestPythonService)