# -*- coding:utf8 -*-
# created by Recker on 2014/07/07

from django.shortcuts import render
from django.http import HttpResponse
from video_info.models import VideoInfo
from video_info.forms import VideoInfoForm
import json

def home(request):
    '''
    接受视频信息分析请求
    http://192.168.1.104:8000/videoInfo/?taskId=111&callBackUrl=111&filePath=127.0.0.1/f97166e03b3a746b6926d174649f3334.f4v
    http://192.168.1.107:8000/videoInfoCreate/?taskId=1&callBackUrl=111&filePath=http://192.168.1.107/test.mp4
    '''
    params = request.REQUEST
    warnings = check(params)
    if warnings:
        return HttpResponse(result("A1001", warnings))
    data = {}
    warnings = save(request)
    if warnings:
        return HttpResponse(result("A1003", warnings))
    return HttpResponse(result(data=data))

def list(request):
	'''
	获取后台数据
	'''
	params = request.REQUEST
	page = int(params.get("page",1))
	max_per_page = int(params.get("max",50))
	data = VideoInfo.objects.all().order_by("-id")[(page-1)*max_per_page : page*max_per_page]
	#_lst = [x for x in data.values("taskid", "status", "filepath", "videofile", "logUtil")]
	_lst = []
	for task in data:
		_dict = {}
		_dict['taskid'] = task.id
		_dict['status'] = task.status
		_dict['logurl'] = task.logUtil()
		_dict['totrans'] = task.createTask()
		_dict['createtime'] = task.strTime()
		_lst.append(_dict)
	return HttpResponse(result(data=_lst))

def uniq(params):
    '''
    任务去重
    '''
    if VideoInfo.objects.filter(taskid=params['taskId']):
        return "repeated taskId %s"%params['taskId']
    return 0
 
def check(params, check_args = ['videoname', 'videotype', 'videofile']):
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
    return json.dumps({"code":error_code, "msg":error_msg, "content":data})

def save(request):
    '''
    写入db
    ''' 
    try:
        videoinfoform = VideoInfoForm(request.POST, request.FILES)
        if videoinfoform.is_valid():
            videoname = videoinfoform.cleaned_data['videoname']
            videotype = videoinfoform.cleaned_data['videotype']
            videofile = videoinfoform.cleaned_data['videofile']
            videoinfo = VideoInfo(videoname=videoname, videotype=videotype, videofile=videofile)
            videoinfo.save()
        else:
            return "not valid form"
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
    if videoinfo.status:
        return HttpResponse(result("A1004", video.mediainfo))
    return HttpResponse(result(data=videoinfo.mediainfo))
