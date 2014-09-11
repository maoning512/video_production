# -*- coding:utf8 -*-
# created by Recker on 2014/09/11

from django.shortcuts import render
from django.http import HttpResponse
from video_pic.models import VideoPic

def home(request):
    '''
    接受视频截图请求
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
    if VideoPic.objects.filter(taskid=params['taskid']):
        return "repeated taskId %s"%params['taskId']
    return 0

def check(params, check_args = ['taskId', 'filePath', 'callBackUrl', 'cutTimes', 'pictureFormat', 'Dimensions'])
    '''
    检查参数
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

def save(params):
    '''
    写入db
    '''
    try:
        videopic =VideoPic(
                            taskid=params['taskId'], 
                            callback=params['callBackUrl'],
                            filepath=params['filePath'],
                            cuttime=params['cutTimes'],
                            pictureformat=params['pictureFormat'],
                            dimensions=params['Dimensions']
                          )
        videopic.save()
    except Exception, e:
        return str(e)
    return 0

def get(params):
    '''
    查询任务结果
    '''
    try:
        videopic = VideoPic.objects.get(taskid=params['taskId'])
    except Exception, e:
        return str(e)
    return videopic

def search(request):
    '''
    获取视频截图结果
    '''
    params = request.REQUEST
    warnings = check(params, ['taskId'])
    if warnings:
        return HttpResponse(result("A1001", warnings))
    videopic = get(params)
    if isinstance(videopic, str):
        return HttpResponse(result("A1006", videopic))
    if videopic.status and videopic.status != 200:
        return HttpResponse(result("A1004", videopic.mediainfo))
    return HttpResponse(result(data=eval(videopic.mediainfo)))
