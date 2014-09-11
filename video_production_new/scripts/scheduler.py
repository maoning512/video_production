#!/usr/bin/python
# -*- coding:utf8 -*-
# 调度程序,启动方式crontab

import commands, sys, os, subprocess
from django.db import connection

SUBPROCESS_VIDEOINFO = 3 
SUBPROCESS_VIDEOTASK = 4 

def getWorkerIdle(ip):
    cmd = "ssh %s 'ps aux | grep runtime.py | grep python | wc -l'"%ip
    res0 = commands.getoutput("ssh %s 'ps aux | grep runtime.py | grep python | grep \'type=1\' |grep -v grep | grep -v bash | grep -v ssh | wc -l'"%ip)
    res1 = commands.getoutput("ssh %s 'ps aux | grep runtime.py | grep python | grep \'type=2\' |grep -v grep | grep -v bash | grep -v ssh | wc -l'"%ip)
    return int(res0), int(res1)

def startWorker(ip, taskid, tasktype):
    cmd = "ssh %s 'cd /root/workspace/video_production/scripts/ && nohup python runtime.py --task=%s --type=%s'"%(ip, taskid, tasktype)
    res = subprocess.Popen(cmd, shell=True)

def chk_start(pidfile):
    if os.path.exists(pidfile):
        sys.exit(0)
    else:
        commands.getstatusoutput("touch %s"%pidfile)
   
def chk_end(pidfile):
    if os.path.exists(pidfile):
        commands.getstatusoutput("rm -rf %s"%pidfile) 

if __name__ == "__main__":
    pidfile = __file__ + ".pid"
    chk_start(pidfile)
    sys.path.append('/root/workspace/video_production/')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'video_production.settings'
    try:
        #引入django models
        from video_info.models import VideoInfo
        from video_task.models import VideoTask
        from video_schedule.models import Worker
    except Exception, e:
        print e
        sys.exit()
    workers = Worker.objects.filter(status=0).order_by("-id")
    for worker in workers:
        process_info, process_task = getWorkerIdle(worker.ip)
        #调度视频扫描任务
        if not process_info < SUBPROCESS_VIDEOINFO:
            break
        videoinfos = VideoInfo.objects.filter(status=None).order_by("id")[0:SUBPROCESS_VIDEOINFO - process_info]
        for task in videoinfos:
            startWorker(worker.ip, task.taskid, 1)
            task.status=100
            task.ip = worker.ip
            task.save()
        #调度视频转码任务
        if not process_task < SUBPROCESS_VIDEOTASK:
            break
        videotasks = VideoTask.objects.filter(status=None).order_by("-priority","id")[0:SUBPROCESS_VIDEOTASK - process_task]
        for task in videotasks:
            startWorker(worker.ip, task.taskid, 2)
            task.status=100
            task.ip = worker.ip
            task.save()
    chk_end(pidfile)
