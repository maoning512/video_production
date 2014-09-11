# -*- coding:utf8 -*-
# created by Recker on 2014/07/07

from django.shortcuts import render
from django.http import HttpResponse
from video_task.models import VideoTask, TransCodeInfo 
import json

def home(request):
    '''
    接受视频转码请求
    http://192.168.1.106:8000/videoTaskCreate/?taskId=3&filePath=http://192.168.1.106/test.mp4&callBackUrl=http://127.0.0.1&priority=2&crop=0:0:0:0&aid=0&platform=1&versionId=1&iFps=25
    '''
    params = request.REQUEST
    warnings = check(params)
    if isinstance(warnings, str) or isinstance(warnings, list):
        return HttpResponse(result("A1001", warnings))
    data = {}
    warnings = filter(params)
    if warnings:
        return HttpResponse(result("A1005", warnings))
    warnings = uniq(params)
    if warnings:
        return HttpResponse(result("A1007", warnings))
    warnings = save(params)
    if warnings:
        return HttpResponse(result("A1003", warnings))
    return HttpResponse(result(data=data))

def uniq(params):
    '''
    任务去重
    '''
    if VideoTask.objects.filter(taskid=params['taskId']):
        return "repeated taskId %s"%params['taskId']
    return 0
    
def check(params, check_args = ['taskId', 'filePath', 'callBackUrl',
'priority', 'crop', 'aid', 'platform', 'versionId', 'iFps']):
    '''
    taskId, filePtah, callBackUrl
    '''
    for key in check_args:
        if not params.has_key(key) or not params[key]:
            return "%s not found"%key
    if len(check_args) == 1:
        return 0
#    tci = TransCodeInfo(params['transCodeInfo'])
#    if tci.warnings:
#        return "lost %s in transCodeInfo"%tci.warnings
    return 0 

def filter(params):
    '''
    检查参数是否合法
    '''
    if len(params['taskId']) > 64:
        return "taskId is not valid"
    return 0


def result(error_code=0, error_msg="", data={}):
    '''
    获取请求结果
    '''
    return json.dumps({"error_code":error_code, "error_msg":error_msg, "data":data})

def save(params):
    '''
    写入db
    ''' 
    try:
        videotask = VideoTask(taskid=params['taskId'], callback=params['callBackUrl'], filepath=params['filePath'], priority=params['priority'],
        srtfile=params.get('srtFile',''), logofile=params.get('logoFile',''), versionid=params['versionId'], crop=params['crop'], aid=params['aid'], platform=params['platform'], 
        logopos=params.get('logoPos',''), ifps=params['iFps'])
        videotask.save()
    except Exception, e:
        return str(e)
    return 0

def get(params):
    '''
    查询任务结果
    '''
    try:
        videoinfo = VideoTask.objects.get(taskid=params['taskId'])
    except Exception, e:
        return str(e)
    return videoinfo


def search(request):
    '''
    获取视频信息扫描结果
    http://192.168.1.104:8000/videoTaskSearch/?taskId=1
    '''
    params = request.REQUEST
    warnings = check(params, ['taskId'])
    if warnings:
        return HttpResponse(result("A1001", warnings))
    videoinfo = get(params)
    if isinstance(videoinfo, str):
        return HttpResponse(result("A1006", videoinfo))
    if videoinfo.status and videoinfo.status != 200:
        return HttpResponse(result("A1004", videoinfo.mediainfo))
    try:
        return HttpResponse(result(data=eval(videoinfo.mediainfo)))
    except:
        return HttpResponse(result("A1004", videoinfo.mediainfo))
