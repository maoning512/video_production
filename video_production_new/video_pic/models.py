# -*- coding:utf8 -*-
from django.db import models

class VideoPic(models.Model):
    '''
    视频图片
    '''
    taskid = models.CharField('任务id', max_length=64, null=True, db_index=True)
    filepath = models.CharField('片源地址', max_length=255, null=True)
    callback = models.CharField('回调地址', max_length=255, null=True)
    createdtime = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    mediainfo = models.TextField(null=True)
    status = models.IntegerField('任务状态', max_length=1, null=True, db_index=True)
    ip = models.IPAddressField(null=True)
    cuttimes = models.TextField('时间列表', null=True)
    pictureformat = models.IntegerField('图片类型', max_length=1, null=True, default=0)
    dimensions = models.CharField('图片分辨率', max_length=32, null=True)

    class Meta:
        db_table = "video_pic"
    
