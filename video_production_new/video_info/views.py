# -*- coding:utf8 -*-
# created by Recker on 2014/07/07

from django.shortcuts import render
from django.http import HttpResponse
from video_info.models import VideoInfo
import json

def home(request):
    '''
    接受视频信息分析请求
    http://192.168.1.104:8000/videoInfo/?taskId=111&callBackUrl=111&filePath=127.0.0.1/f97166e03b3a746b6926d174649f3334.f4v
    '''
    params = request.REQUEST
    warnings = check(params)
    if warnings:
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
    if VideoInfo.objects.filter(taskid=params['taskId']):
        return "repeated taskId %s"%params['taskId']
    return 0
    
def check(params, check_args = ['taskId', 'filePath', 'callBackUrl']):
    '''
    taskId, filePtah, callBackUrl
    '''
    for key in check_args:
        if not params.has_key(key) or not params[key]:
            return "%s not found"%key
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
    return json.dumps({"error_code":error_code, "error_msg":error_msg,
    "data":data})

def save(params):
    '''
    写入db
    ''' 
    try:
        videoinfo = VideoInfo(taskid=params['taskId'],
        callback=params['callBackUrl'], filepath=params['filePath'])
        videoinfo.save()
    except Exception, e:
        return str(e)
    return 0

def get(params):
    '''
    查询任务结果
    '''
    try:
        videoinfo = VideoInfo.objects.get(taskid=params['taskId'])
    except Exception, e:
        return str(e)
    return videoinfo


def search(request):
    '''
    获取视频信息扫描结果
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
    return HttpResponse(result(data=eval(videoinfo.mediainfo)))
