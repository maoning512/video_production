#-*- coding:utf8 -*-
#created by Recker on 2014/07/06

from django.db import models
from json_field import JSONField
import json

class VideoTask(models.Model):
    '''
    视频信息
    '''
    taskid = models.CharField('任务id', max_length=64, null=True, db_index=True)
    filepath = models.URLField('片源地址', max_length=255, null=True)
    callback = models.URLField(max_length=255, null=True)
    createdtime = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    mediainfo = models.TextField(null=True)
    status = models.IntegerField('任务状态', max_length=1, null=True, db_index=True)
    priority = models.IntegerField(max_length=1 ,null=True, db_index=True)
    #编码组件参数
    srtfile = models.URLField(max_length=255, null=True)
    logofile = models.URLField(max_length=255, null=True)
    versionid = models.IntegerField(max_length=1, null=True)
    crop = models.CharField(max_length=32, null=True)
    aid = models.IntegerField(max_length=1, null=True)
    logopos = models.CharField(max_length=32, null=True)
    ifps = models.CharField(max_length=10, null=True)
    platform = models.IntegerField(max_length=1, null=True)
    ip = models.IPAddressField(null=True)




    class Meta:
        db_table = "video_task"
        verbose_name = u"转码任务"
        verbose_name_plural = u"转码任务"

    def getResult(self):
        return '<a href="/videoTaskSearch/?taskId=%s" target="_blank">open</a>'%self.taskid

    getResult.allow_tags = True
    getResult.short_description = "获取转码结果"

    def getIp(self):
        if self.status and not self.ip:
            ip = "42.62.69.10"
        else:
            ip = self.ip
        return ip

    getIp.short_description = "转码机地址"


    def convlog(self):
        ip = self.ip if self.ip else "42.62.69.10"
        return '<a href="http://%s:8000/%s_2.log" target="_blank">open</a>'%(ip, self.taskid)

    convlog.allow_tags = True
    convlog.short_description = "获取转码日志"

    def enclog(self):
        ip = self.ip if self.ip else "42.62.69.10"
        return '<a href="http://%s:8000/%s_flow.log" target="_blank">open</a>'%(ip, self.taskid)

    enclog.allow_tags = True
    enclog.short_description = "获取编码日志"


class TransCodeInfo(object):
    '''
    转码必须参数
    '''
    def __init__(self, params={}):
        self.params = TransCodeInfo._json_to_dict(params)
        self.warnings = self._check_args()

    @staticmethod
    def _json_to_dict(data):
        try:
            return json.loads(data)
        except Exception, e:
            return str(e)

    def _check_args(self):
        '''
        检查参数完整性
        '''
        args = ['version_id', 'platform', 'ifps','crop','aid','logo_pos','srtfile','logofile']
        lost_key = []
        for key in args:
            if not self.params.has_key(key):
                lost_key.append(key)
        return lost_key
