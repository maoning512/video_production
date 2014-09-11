#!/usr/bin/python
# -*- coding:utf8 -*-

import subprocess
import commands
import os
import time

SCHEDULER = {"name":"scheduler.py" ,"num":1}
CALLBACK = {"name":"callBack.py" ,"num":1}
PIDS = ['scheduler.py.pid','callBack.py.pid']


def check(OBJ):
    cmd = "ps aux| grep %s | grep python | grep -v grep | wc -l"%OBJ['name']
    res = commands.getstatusoutput(cmd)
    if int(res[1]) < OBJ['num']:
        start(OBJ)

def start(OBJ):
    cmd = "/usr/bin/python %s"%OBJ['name']
    p = subprocess.Popen(cmd, shell=True)
    res = p.wait()

def checkPid():
    for pid in PIDS:
        if pid and time.time() - os.path.getctime(pid) > 300:
            commands.getstatusoutput("rm -f %s"%pid)


if __name__ == "__main__":
    #check(CALLBACK)
    #check(SCHEDULE)
    checkPid()
