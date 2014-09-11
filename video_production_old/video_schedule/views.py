# -*- coding:utf8 -*-
# created by Recker on 2014/07/18

from django.shortcuts import render
from video_info.models import VideoInfo
from video_task.models import VideoTask
from video_schedule.models import Worker

def schedule():
    '''
    调度任务
    '''
    sde = Schedule()
    return 0
