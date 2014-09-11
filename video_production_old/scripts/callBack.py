#!/usr/bin/python
# -*- coding:utf8 -*-

import pycurl
import urllib
import StringIO
import os
import sys
import time
import json
import commands
from uploadToDNS import runCmd


def toPost(url, post_data_dic):
    try:
        url = str(url)
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url);
        b = StringIO.StringIO()   
        c.setopt(pycurl.HTTPHEADER, ["Accept:"])
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.setopt(pycurl.FOLLOWLOCATION, 2)
        c.setopt(pycurl.MAXREDIRS, 5)
        c.setopt(pycurl.CONNECTTIMEOUT, 20)
        c.setopt(pycurl.TIMEOUT, 20)
        c.perform()   
        res = b.getvalue()
        RC.log(url + " | "  + res)
        return json.loads(res)
    except Exception, e:
        RC.log(url + " | " + str(e))
        return {"status":0, "message":str(e)}

def getPostData(limit=50):
    infos = VideoInfo.objects.filter(status__gte=0).exclude(status=200).exclude(status=100)[0:limit]
    for data in infos:
        postData = {"taskId":data.taskid, "status":data.status}
        res = toPost(data.callback, postData)
        if res.get("status",0) == 1:
            data.status = 200
            data.save()
    videos = VideoTask.objects.filter(status__gte=0).exclude(status=200).exclude(status=100)[0:limit]
    for data in videos:
        postData = {"taskId":data.taskid, "status":data.status}
        res = toPost(data.callback, postData)
        if res.get("status",0) == 1:
            data.status = 200
            data.save()

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
    from video_task.models import VideoTask
    from video_info.models import VideoInfo
    logname = "/root/workspace/log/callback_%s.log"%time.strftime("%Y%m%d")
    global RC
    RC = runCmd(logname)
    getPostData(50)
    chk_end(pidfile)
